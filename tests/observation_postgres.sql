-- Run after c2_postgres.sql setup, before its rollback, in a disposable database.
do $$
declare
    meta jsonb := jsonb_build_object('source','Fictional Notion page','route','page-api',
        'source_sha256',repeat('d',64),'model','fixture','observed_at','2026-11-13T00:00:00Z',
        'notes','[{"kind":"fact","text":"violet"}]'::jsonb);
    first jsonb;
    second jsonb;
    preview uuid;
begin
    first := public.c2_memory('import','observations','obs_fixture','Fictional Notion page',
        body_hash=>repeat('d',64),pieces=>'[["violet",0,6,1,1]]',observation=>meta);
    assert first->>'version'='1';
    assert public.c2_memory('search','observations',query_text=>'violet')->0->'observation'->>'route'='page-api';
    -- A natural question must reach the note even though most of its words are not in it.
    assert public.c2_memory('search','observations',query_text=>'When is the violet demonstration?')->0->>'text'='violet';
    assert public.c2_memory('search','observations',query_text=>'?!')='[]';
    assert public.c2_memory('search','observations',query_text=>$q$violet' & !x:* \ "$q$) is not null;
    meta := jsonb_set(meta,'{observed_at}','"2026-11-13T01:00:00Z"');
    assert public.c2_memory('import','observations','obs_fixture','Fictional Notion page',
        body_hash=>repeat('d',64),pieces=>'[["violet",0,6,1,1]]',observation=>meta)->>'duplicate'='true';
    meta := jsonb_set(meta,'{notes}','[]');
    second := public.c2_memory('import','observations','obs_fixture','Fictional Notion page',
        body_hash=>repeat('d',64),pieces=>'[]',observation=>meta);
    assert second->>'version'='2';
    assert public.c2_memory('search','observations',query_text=>'violet')='[]';
    assert jsonb_array_length(public.c2_memory('inspect','observations','obs_fixture'))=2;
    perform set_config('test.owner','00000000-0000-0000-0000-000000000002',true);
    begin
        perform public.c2_memory('inspect','observations','obs_fixture');
        raise exception 'other owner accessed observation';
    exception when raise_exception then
        if sqlerrm <> 'Unknown source' then raise; end if;
    end;
    perform set_config('test.owner','00000000-0000-0000-0000-000000000001',true);
    preview := (public.c2_memory('preview','observations','obs_fixture')->>'confirmation')::uuid;
    assert public.c2_memory('forget','observations','obs_fixture',confirmation=>preview)->>'versions'='2';
    begin
        perform public.c2_memory('import','observations','obs_copy','Fictional Notion page',
            body_hash=>repeat('d',64),pieces=>'[]',observation=>meta);
        raise exception 'forgotten observation reimported';
    exception when raise_exception then
        if sqlerrm <> 'Content previously forgotten' then raise; end if;
    end;
end $$;

-- Forget parity with MemoryStore.preview_forget (Day 1 review findings).
create function pg_temp.obs(file text, route text, source text, hash text, quotes text[])
returns jsonb language plpgsql as $$
declare pieces jsonb; meta jsonb;
begin
    select jsonb_agg(jsonb_build_array(q,0,length(q),1,1)) into pieces from unnest(quotes) q;
    select jsonb_build_object('source',source,'route',route,'source_sha256',hash,'model','fixture',
        'observed_at','2026-11-16T00:00:00Z',
        'notes',(select jsonb_agg(jsonb_build_object('kind','fact','text',q)) from unnest(quotes) q)) into meta;
    return public.c2_memory('import','observations',file,source,body_hash=>hash,pieces=>pieces,observation=>meta);
end $$;
create function pg_temp.forget(file text) returns jsonb language sql as $$
    select public.c2_memory('forget','observations',file,confirmation=>
        (public.c2_memory('preview','observations',file)->>'confirmation')::uuid) $$;
create function pg_temp.hits(q text) returns int language sql as $$
    select jsonb_array_length(public.c2_memory('search','observations',query_text=>q)) $$;
do $$
declare r jsonb;
begin
    perform set_config('test.owner','00000000-0000-0000-0000-000000000001',true);
    -- Two captures of one window forget together; a file copy of one (trailing newline) goes too.
    perform pg_temp.obs('obs_a','screen-ocr','win',repeat('1',64),array['Cedar417 is the amber room']);
    perform pg_temp.obs('obs_b','screen-ocr','win',repeat('2',64),array['Zebra99 other capture']);
    perform pg_temp.obs('obs_f','selected-file','/n/a.md',repeat('3',64),array[E'Cedar417  is the amber room\n']);
    perform pg_temp.obs('obs_x','selected-file','/n/x.md',repeat('4',64),array['Unrelated keepword']);
    assert pg_temp.hits('Cedar417')=1, 'whitespace-equal copies collapse into one hit';
    assert jsonb_array_length(public.c2_memory('search','observations',query_text=>'Cedar417')->0->'linked')=1;
    r := pg_temp.forget('obs_a');
    assert r->>'versions'='3', r::text;
    assert pg_temp.hits('Cedar417')=0 and pg_temp.hits('Zebra99')=0 and pg_temp.hits('keepword')=1;
    -- A single shared short chunk must not take an unrelated note.
    perform pg_temp.obs('obs_t','selected-file','/n/t.md',repeat('5',64),array['Trip Pune','Approved.']);
    perform pg_temp.obs('obs_u','selected-file','/n/u.md',repeat('6',64),array['Budget lakh for the Q4 review','Approved.']);
    r := pg_temp.forget('obs_t');
    assert r->>'versions'='1', r::text;
    assert pg_temp.hits('lakh')=1;
    -- Forgetting a copy must not leave another file with no active version.
    perform pg_temp.obs('multi','selected-file','/n/m.md',repeat('7',64),array['Monday review']);
    perform pg_temp.obs('multi','selected-file','/n/m.md',repeat('8',64),array['Thursday review']);
    perform pg_temp.obs('obs_c','screen-ocr','w2',repeat('8',64),array['Thursday review']);
    r := pg_temp.forget('obs_c');
    assert r->>'versions'='2', r::text;
    assert pg_temp.hits('Monday')=1 and pg_temp.hits('Thursday')=0;
    -- Lone short notes ("Approved.", "OK") never link distinct pages; windows do not drag them in.
    perform pg_temp.obs('p1','selected-file','Trip page',repeat('a1',32),array['Approved.']);
    perform pg_temp.obs('p2','selected-file','Budget page',repeat('b2',32),array['Approved.']);
    perform pg_temp.obs('w1','screen-ocr','Slack',repeat('c3',32),array['Real secret Cedarmark here']);
    perform pg_temp.obs('w2','screen-ocr','Slack',repeat('d4',32),array['OK']);
    perform pg_temp.obs('u1','selected-file','/n/u1.md',repeat('e5',32),array['OK']);
    assert pg_temp.forget('p1')->>'versions'='1';
    assert pg_temp.hits('Approved')=1;
    assert pg_temp.forget('w1')->>'versions'='2';
    assert pg_temp.hits('OK')=1;
    -- Identical content in another folder goes too: tombstones are owner-wide.
    perform public.c2_memory('import','folderY','y1','y.md',body_hash=>repeat('f6',32),pieces=>'[["gamma three",0,12,1,1]]');
    perform public.c2_memory('import','observations','x1','x.md',body_hash=>repeat('f6',32),pieces=>'[["gamma three",0,12,1,1]]');
    assert pg_temp.forget('x1')->>'versions'='2';
    assert jsonb_array_length(public.c2_memory('search','folderY',query_text=>'gamma'))=0;
    -- Punctuated terms stay searchable as whole lexemes (index and query share one parser).
    perform pg_temp.obs('dots','selected-file','/n/dots.md',repeat('c7',32),array['Cost 3.14 at a@b.com see example.com v2.0']);
    assert pg_temp.hits('3.14')=1 and pg_temp.hits('a@b.com')=1 and pg_temp.hits('v2.0')=1;
    -- Forgetting through one folder must not reactivate a tombstoned copy in another.
    perform public.c2_memory('import','folderA','fa','fa.md',body_hash=>repeat('a8',32),pieces=>'[["resurface me please now",0,24,1,1]]');
    perform public.c2_memory('import','folderB','fb','fb.md',body_hash=>repeat('a8',32),pieces=>'[["resurface me please now",0,24,1,1]]');
    perform public.c2_memory('import','folderB','fb','fb.md',body_hash=>repeat('b9',32),pieces=>'[["second version text here",0,25,1,1]]');
    perform public.c2_memory('import','folderB','fk','fk.md',body_hash=>repeat('b9',32),pieces=>'[["second version text here",0,25,1,1]]');
    perform public.c2_memory('forget','folderA','fa',confirmation=>(public.c2_memory('preview','folderA','fa')->>'confirmation')::uuid);
    perform public.c2_memory('forget','folderB','fk',confirmation=>(public.c2_memory('preview','folderB','fk')->>'confirmation')::uuid);
    assert jsonb_array_length(public.c2_memory('search','folderB',query_text=>'resurface'))=0;
    -- A copy added after the preview makes the confirmation stale.
    declare tok uuid := (public.c2_memory('preview','observations','obs_u')->>'confirmation')::uuid;
    begin
        perform pg_temp.obs('obs_late','selected-file','/n/late.md',repeat('9',64),array['Budget lakh for the Q4 review','Approved.']);
        begin
            perform public.c2_memory('forget','observations','obs_u',confirmation=>tok);
            raise exception 'accepted stale preview';
        exception when raise_exception then
            if sqlerrm <> 'Invalid operation or stale confirmation' then raise; end if;
        end;
    end;
end $$;
