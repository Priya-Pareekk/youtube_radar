-- Run this once in Supabase → SQL Editor → New query → Run.
-- Creates the two tables TubeRadar needs, with Row Level Security so
-- each user can only ever see/edit their own rows.

create extension if not exists "pgcrypto";

-- Past scans, saved for signed-in users only.
create table if not exists scans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  mode text not null,               -- 'solo' | 'compare'
  topic text not null,
  topic_b text,                     -- only set for 'compare' scans
  avg_score numeric,
  total_comments int,
  item_count int,
  platforms text[],
  result jsonb,                     -- full scan payload, for re-rendering later
  created_at timestamptz default now()
);

alter table scans enable row level security;

create policy "select own scans" on scans
  for select using (auth.uid() = user_id);

create policy "insert own scans" on scans
  for insert with check (auth.uid() = user_id);

create policy "delete own scans" on scans
  for delete using (auth.uid() = user_id);

-- "Watch this topic" alerts.
create table if not exists watches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  topic text not null,
  mode text not null default 'solo',
  platforms text[] not null default array['youtube'],
  threshold numeric not null default 0.15,   -- sentiment drop that triggers an email
  email text not null,
  baseline_score numeric,
  last_score numeric,
  last_checked_at timestamptz,
  active boolean not null default true,
  created_at timestamptz default now()
);

alter table watches enable row level security;

create policy "select own watches" on watches
  for select using (auth.uid() = user_id);

create policy "insert own watches" on watches
  for insert with check (auth.uid() = user_id);

create policy "update own watches" on watches
  for update using (auth.uid() = user_id);

create policy "delete own watches" on watches
  for delete using (auth.uid() = user_id);
