-- NeuroBrain cloud prototype schema.
-- Run this in the Supabase SQL editor after creating a project.

create extension if not exists pgcrypto;

create table if not exists public.sources (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    drive_file_id text not null,
    drive_revision_id text,
    path text not null,
    content_hash text not null,
    version integer not null check (version > 0),
    imported_at timestamptz not null default now(),
    active boolean not null default true,
    unique (owner_id, drive_file_id, version)
);

create unique index if not exists one_active_source_per_drive_file
    on public.sources (owner_id, drive_file_id) where active;

create table if not exists public.chunks (
    id bigint generated always as identity primary key,
    owner_id uuid not null references auth.users(id) on delete cascade,
    source_id uuid not null references public.sources(id) on delete cascade,
    ordinal integer not null check (ordinal >= 0),
    text text not null,
    char_start integer not null check (char_start >= 0),
    char_end integer not null check (char_end >= char_start),
    line_start integer not null check (line_start >= 1),
    line_end integer not null check (line_end >= line_start),
    search_vector tsvector generated always as (to_tsvector('simple', text)) stored,
    unique (source_id, ordinal)
);

create index if not exists chunks_search_idx on public.chunks using gin(search_vector);
create index if not exists chunks_owner_source_idx on public.chunks(owner_id, source_id);

create table if not exists public.tombstones (
    owner_id uuid not null references auth.users(id) on delete cascade,
    content_hash text not null,
    deleted_at timestamptz not null default now(),
    primary key (owner_id, content_hash)
);

create table if not exists public.deletion_receipts (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id) on delete cascade,
    completed_at timestamptz not null default now(),
    source_count integer not null check (source_count >= 0),
    chunk_count integer not null check (chunk_count >= 0)
);

alter table public.sources enable row level security;
alter table public.chunks enable row level security;
alter table public.tombstones enable row level security;
alter table public.deletion_receipts enable row level security;

create policy "owners manage sources" on public.sources
    for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "owners manage chunks" on public.chunks
    for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "owners manage tombstones" on public.tombstones
    for all using (auth.uid() = owner_id) with check (auth.uid() = owner_id);
create policy "owners read receipts" on public.deletion_receipts
    for select using (auth.uid() = owner_id);
