-- Apply after schema.sql in the dedicated mentor-demo project.
alter table public.sources add column if not exists folder_id text;
alter table public.sources add column if not exists observation jsonb;

-- Replace the previous signature so PostgREST does not see ambiguous overloads.
drop function if exists public.c2_memory(text,text,text,text,text,text,jsonb,text,uuid);

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
        select coalesce(jsonb_agg(to_jsonb(h)), '[]'::jsonb) into result from (
            select s.path, s.version, s.id as source_id, c.line_start, c.line_end,
                   c.text, concat(s.id, ':', c.ordinal) as citation,
                   case when s.observation is null then null else
                       jsonb_build_object('source',s.observation->>'source','route',s.observation->>'route')
                   end as observation
            from public.sources s join public.chunks c on s.id=c.source_id
            where s.owner_id=uid and c.owner_id=uid and s.folder_id=folder and s.active
              and c.search_vector @@ tsq
            order by ts_rank(c.search_vector, tsq) desc,
                     s.id, c.ordinal limit 5
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
    select count(distinct s.id),count(c.id) into versions,passages
        from public.sources s left join public.chunks c on c.source_id=s.id
        where s.owner_id=uid and s.drive_file_id=file_id;
    if op='preview' then
        return jsonb_build_object('versions',versions,'chunks',passages,'confirmation',latest.id);
    elsif op='forget' and latest.id=confirmation then
        insert into public.tombstones(owner_id,content_hash)
            select uid,content_hash from public.sources where owner_id=uid and drive_file_id=file_id
            on conflict do nothing;
        delete from public.sources where owner_id=uid and drive_file_id=file_id;
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
