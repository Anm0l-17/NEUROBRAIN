-- Disposable empty PostgreSQL database only. Stand in for Supabase Auth.
\set ON_ERROR_STOP on
begin;
create role anon;
create role authenticated;
create schema auth;
create table auth.users(id uuid primary key);
create function auth.uid() returns uuid language sql stable as
$$ select current_setting('test.owner',true)::uuid $$;
insert into auth.users values ('00000000-0000-0000-0000-000000000001'),
                              ('00000000-0000-0000-0000-000000000002');
\ir ../supabase/schema.sql
\ir ../supabase/c2.sql
set local role authenticated;
set local test.owner='00000000-0000-0000-0000-000000000001';
do $$
declare
    v jsonb;
    preview uuid;
begin
    v := public.c2_memory('import','folder','file','note.md','1',repeat('a',64),'[["violet",0,6,1,1]]');
    assert v->>'version'='1';
    preview := (public.c2_memory('preview','folder','file')->>'confirmation')::uuid;
    assert public.c2_memory('import','folder','file','note.md','1',repeat('a',64),'[["violet",0,6,1,1]]')->>'duplicate'='true';
    v := public.c2_memory('import','folder','file','note.md','2',repeat('b',64),'[["amber",0,5,1,1]]');
    assert v->>'version'='2';
    assert jsonb_array_length(public.c2_memory('inspect','folder','file'))=2;
    assert public.c2_memory('search','folder',query_text=>'violet')='[]';
    assert public.c2_memory('search','folder',query_text=>'amber')->0->>'line_start'='1';
    begin
        perform public.c2_memory('forget','folder','file',confirmation=>preview);
        raise exception 'accepted stale preview';
    exception when raise_exception then
        if sqlerrm <> 'Invalid operation or stale confirmation' then raise; end if;
    end;
    perform set_config('test.owner','00000000-0000-0000-0000-000000000002',true);
    assert public.c2_memory('search','folder',query_text=>'amber')='[]';
    perform set_config('test.owner','00000000-0000-0000-0000-000000000001',true);
    perform public.c2_memory('import','folder','other','other.txt','1',repeat('c',64),'[["retained",0,8,1,1]]');
    preview := (public.c2_memory('preview','folder','file')->>'confirmation')::uuid;
    v := public.c2_memory('forget','folder','file',confirmation=>preview);
    assert v->>'versions'='2' and v->>'chunks'='2';
    assert public.c2_memory('search','folder',query_text=>'amber')='[]';
    assert jsonb_array_length(public.c2_memory('search','folder',query_text=>'retained'))=1;
    begin
        perform public.c2_memory('import','folder','copy','note.md','1',repeat('a',64),'[["violet",0,6,1,1]]');
        raise exception 'accepted tombstone';
    exception when raise_exception then
        if sqlerrm <> 'Content previously forgotten' then raise; end if;
    end;
end $$;
rollback;
