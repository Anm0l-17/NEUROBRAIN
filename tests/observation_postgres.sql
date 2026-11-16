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
