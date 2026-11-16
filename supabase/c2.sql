-- Apply after schema.sql in the dedicated mentor-demo project.
alter table public.sources add column if not exists folder_id text;
alter table public.sources add column if not exists observation jsonb;

-- Replace the previous signature so PostgREST does not see ambiguous overloads.
drop function if exists public.c2_memory(text,text,text,text,text,text,jsonb,text,uuid);

-- Everything one forget removes, mirroring MemoryStore.preview_forget: all versions of the file,
-- every capture of the same screen window, then one hop to copies reached by another route
-- whose content hash matches, or whose whole chunk set matches after whitespace normalising.
-- Whole-chunk-set matches count only for substantial text (24+ chars): a lone "Approved." or
-- "OK" must not take another note with it. Scope is the whole owner, like tombstones.
create or replace function public.c2_forget_set(uid uuid, folder text, file_id text)
returns table(id uuid, content_hash text) language sql stable security definer set search_path = '' as $f$
    with s as (
        select src.id, src.drive_file_id, src.content_hash, src.version, src.observation,
               coalesce((select array_agg(n order by n) from (
                   select distinct btrim(regexp_replace(c.text, '\s+', ' ', 'g')) as n
                   from public.chunks c where c.source_id = src.id) x), '{}'::text[]) as cs
        from public.sources src where src.owner_id = uid),
    target as (select * from s where s.drive_file_id = file_id order by s.version desc limit 1),
    base as (
        select b.* from s b, target t
        where b.drive_file_id = file_id
           or (t.observation->>'route' = 'screen-ocr' and b.observation->>'route' = 'screen-ocr'
               and b.observation->>'source' = t.observation->>'source'))
    select distinct s.id, s.content_hash from s
    where s.id in (select base.id from base)
       or s.content_hash in (select base.content_hash from base)
       or s.cs in (select base.cs from base where length(array_to_string(base.cs, '')) >= 24)
$f$;
revoke all on function public.c2_forget_set(uuid,text,text) from public, anon, authenticated;

create or replace function public.c2_memory(
    op text, folder text, file_id text default null, filename text default null,
    revision text default null, body_hash text default null, pieces jsonb default null,
    query_text text default null, confirmation uuid default null,
    observation jsonb default null
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare
    uid uuid := auth.uid();
    latest public.sources%rowtype;
    result jsonb;
    versions integer;
    passages integer;
    receipt uuid;
    tsq tsquery;
    ids uuid[];
    token uuid;
begin
    if uid is null or folder is null or folder !~ '^[a-zA-Z0-9_-]+$' then
        raise exception 'Invalid session or folder';
    end if;
    if op = 'search' then
        -- OR the words like the local FTS: plainto_tsquery ANDs every word, so a natural
        -- question ("When is the violet demonstration?") would match nothing.
        select to_tsquery('simple', string_agg(t, ' | ')) into tsq from (
            select m[1] as t from regexp_matches(left(coalesce(query_text,''),2000),
                '([[:alnum:]]+)', 'g') as m limit 32) w;
        if tsq is null then return '[]'::jsonb; end if;
        -- Whitespace-equal chunks reached through another route collapse into one hit with `linked`.
        select coalesce(jsonb_agg(to_jsonb(h) - 'rk' - 'ord' - 'rn' order by h.rk desc, h.source_id, h.ord),
                        '[]'::jsonb) into result from (
            select * from (
                select s.path, s.version, s.id as source_id, c.line_start, c.line_end,
                       c.text, concat(s.id, ':', c.ordinal) as citation,
                       case when s.observation is null then null else
                           jsonb_build_object('source',s.observation->>'source','route',s.observation->>'route')
                       end as observation,
                       array_remove(array_agg(concat(s.id, ':', c.ordinal)) over w,
                                    concat(s.id, ':', c.ordinal)) as linked,
                       ts_rank(c.search_vector, tsq) as rk, c.ordinal as ord,
                       row_number() over (w order by ts_rank(c.search_vector, tsq) desc, s.id, c.ordinal) as rn
                from public.sources s join public.chunks c on s.id=c.source_id
                where s.owner_id=uid and c.owner_id=uid and s.folder_id=folder and s.active
                  and c.search_vector @@ tsq
                window w as (partition by btrim(regexp_replace(c.text, '\s+', ' ', 'g')))
            ) x where rn=1 order by rk desc, source_id, ord limit 5
        ) h;
        return result;
    end if;
    if file_id is null or file_id !~ '^[a-zA-Z0-9_-]+$' then
        raise exception 'Invalid file ID';
    end if;
    -- Serialize writes per owner, including tombstone checks across different files.
    perform pg_advisory_xact_lock(hashtextextended(uid::text, 0));
    select * into latest from public.sources where owner_id=uid and drive_file_id=file_id
        order by version desc limit 1;
    if latest.id is not null and latest.folder_id is distinct from folder then
        raise exception 'File belongs to another import folder';
    end if;
    if op='import' then
        if body_hash is null or body_hash !~ '^[0-9a-f]{64}$' or
           jsonb_typeof(pieces) is distinct from 'array' then
            raise exception 'Invalid note payload';
        end if;
        if observation is not null then
            if jsonb_typeof(observation) is distinct from 'object'
               or observation->>'route' not in ('selected-file','page-api','screen-ocr')
               or coalesce(observation->>'route','')=''
               or coalesce(observation->>'source','')=''
               or observation->>'source_sha256' is distinct from body_hash
               or coalesce(observation->>'model','')=''
               or coalesce(observation->>'observed_at','')=''
               or jsonb_typeof(observation->'notes') is distinct from 'array'
               or jsonb_array_length(observation->'notes')<>jsonb_array_length(pieces)
               or jsonb_array_length(pieces)>12 then
                raise exception 'Invalid observation payload';
            end if;
        elsif jsonb_array_length(pieces)=0 then
            raise exception 'Invalid note payload';
        end if;
        if exists(select 1 from public.tombstones where owner_id=uid and content_hash=body_hash) then
            raise exception 'Content previously forgotten';
        end if;
        if latest.content_hash=body_hash and
           (latest.observation - 'observed_at') is not distinct from (observation - 'observed_at') then
            return jsonb_build_object('source_id',latest.id,'version',latest.version,'duplicate',true);
        end if;
        update public.sources set active=false where id=latest.id;
        insert into public.sources(owner_id,folder_id,drive_file_id,drive_revision_id,path,content_hash,version,observation)
            values(uid,folder,file_id,revision,filename,body_hash,coalesce(latest.version,0)+1,observation)
            returning * into latest;
        insert into public.chunks(owner_id,source_id,ordinal,text,char_start,char_end,line_start,line_end)
            select uid,latest.id,(n-1)::int,p->>0,(p->>1)::int,(p->>2)::int,(p->>3)::int,(p->>4)::int
            from jsonb_array_elements(pieces) with ordinality as t(p,n);
        return jsonb_build_object('source_id',latest.id,'version',latest.version,'duplicate',false);
    end if;
    if latest.id is null then raise exception 'Unknown source'; end if;
    if op='inspect' then
        select jsonb_agg(jsonb_build_object('source_id',id,'version',version,'active',active,'path',path,'observation',sources.observation)
                         order by version) into result from public.sources
            where owner_id=uid and drive_file_id=file_id;
        return result;
    end if;
    select coalesce(array_agg(f.id order by f.id), '{}') into ids
        from public.c2_forget_set(uid, folder, file_id) f;
    select count(*) into passages from public.chunks where owner_id=uid and source_id = any(ids);
    versions := cardinality(ids);
    -- The token covers the exact set, so a copy added after the preview makes it stale.
    token := md5(array_to_string(ids, ',') || ':' || passages)::uuid;
    if op='preview' then
        return jsonb_build_object('versions',versions,'chunks',passages,'confirmation',token);
    elsif op='forget' and token=confirmation then
        insert into public.tombstones(owner_id,content_hash)
            select uid,s.content_hash from public.sources s where s.owner_id=uid and s.id = any(ids)
            on conflict do nothing;
        delete from public.sources where owner_id=uid and id = any(ids);
        -- A removed copy's active version must not hide an older version of another file.
        update public.sources s set active=true where s.owner_id=uid and not exists (
                select 1 from public.sources a where a.owner_id=uid and a.drive_file_id=s.drive_file_id and a.active)
            and s.version=(select max(m.version) from public.sources m
                           where m.owner_id=uid and m.drive_file_id=s.drive_file_id);
        insert into public.deletion_receipts(owner_id,source_count,chunk_count)
            values(uid,versions,passages) returning id into receipt;
        return jsonb_build_object('receipt',receipt,'versions',versions,'chunks',passages);
    end if;
    raise exception 'Invalid operation or stale confirmation';
end;
$$;
revoke all on function public.c2_memory(text,text,text,text,text,text,jsonb,text,uuid,jsonb) from public, anon;
grant execute on function public.c2_memory(text,text,text,text,text,text,jsonb,text,uuid,jsonb) to authenticated;
revoke insert,update,delete,truncate on public.sources,public.chunks,public.tombstones,public.deletion_receipts from public,anon,authenticated;
