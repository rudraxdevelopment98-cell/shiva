-- ============================================================
-- Shiva Portal — Supabase schema + Row-Level Security
-- Run this in your Supabase project: SQL Editor → New query → paste → Run.
-- See docs/supabase-setup.md for the full walkthrough.
-- ============================================================

-- ---------- tables ----------
create table if not exists profiles (
  id         uuid primary key references auth.users(id) on delete cascade,
  name       text not null,
  username   text unique not null,
  role       text not null default 'Member',
  access     text[] not null default '{}',
  status     text not null default 'Active',
  created_at timestamptz not null default now()
);

create table if not exists tasks (
  id         uuid primary key default gen_random_uuid(),
  title      text not null,
  descr      text,
  assignee   text,                 -- username
  due        date,
  priority   text default 'Medium',
  status     text default 'To do',
  phase      text default 'P0',
  created_at timestamptz not null default now()
);

create table if not exists documents (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  category    text,
  size        text,
  url         text,
  uploaded_by text,
  created_at  timestamptz not null default now()
);

create table if not exists research (
  id         uuid primary key default gen_random_uuid(),
  title      text not null,
  url        text,
  category   text,
  note       text,
  created_by text,
  created_at timestamptz not null default now()
);

create table if not exists activity (
  id         uuid primary key default gen_random_uuid(),
  actor      text,
  action     text not null,
  created_at timestamptz not null default now()
);

-- ---------- helper: is the current user an Owner/Admin? ----------
create or replace function is_admin() returns boolean
language sql security definer stable as $$
  select exists(
    select 1 from profiles
    where id = auth.uid() and role in ('Owner','Admin') and status = 'Active'
  );
$$;

create or replace function can_manage() returns boolean
language sql security definer stable as $$
  select exists(
    select 1 from profiles
    where id = auth.uid() and role in ('Owner','Admin','Manager') and status = 'Active'
  );
$$;

-- ---------- enable RLS ----------
alter table profiles  enable row level security;
alter table tasks     enable row level security;
alter table documents enable row level security;
alter table research  enable row level security;
alter table activity  enable row level security;

-- profiles: everyone signed-in can read (to show names); only admins write
-- (account creation/removal happens via the admin-create-user Edge Function,
--  which uses the service_role key and bypasses RLS).
drop policy if exists p_sel on profiles;  create policy p_sel on profiles for select to authenticated using (true);
drop policy if exists p_upd on profiles;  create policy p_upd on profiles for update to authenticated using (id = auth.uid() or is_admin());

-- tasks: read all; managers+ create/update/delete; assignee can update own task status
drop policy if exists t_sel on tasks; create policy t_sel on tasks for select to authenticated using (true);
drop policy if exists t_ins on tasks; create policy t_ins on tasks for insert to authenticated with check (can_manage());
drop policy if exists t_upd on tasks; create policy t_upd on tasks for update to authenticated
  using (can_manage() or assignee = (select username from profiles where id = auth.uid()));
drop policy if exists t_del on tasks; create policy t_del on tasks for delete to authenticated using (can_manage());

-- documents: read all; any active user can add/remove
drop policy if exists d_sel on documents; create policy d_sel on documents for select to authenticated using (true);
drop policy if exists d_ins on documents; create policy d_ins on documents for insert to authenticated with check (true);
drop policy if exists d_del on documents; create policy d_del on documents for delete to authenticated using (true);

-- research: read all; any active user can add
drop policy if exists r_sel on research; create policy r_sel on research for select to authenticated using (true);
drop policy if exists r_ins on research; create policy r_ins on research for insert to authenticated with check (true);

-- activity: read all; any user can append
drop policy if exists a_sel on activity; create policy a_sel on activity for select to authenticated using (true);
drop policy if exists a_ins on activity; create policy a_ins on activity for insert to authenticated with check (true);

-- ---------- storage bucket for documents ----------
insert into storage.buckets (id, name, public) values ('documents','documents', true)
on conflict (id) do nothing;
drop policy if exists s_read on storage.objects;
create policy s_read on storage.objects for select using (bucket_id = 'documents');
drop policy if exists s_write on storage.objects;
create policy s_write on storage.objects for insert to authenticated with check (bucket_id = 'documents');

-- ============================================================
-- NOTE: create your first Owner account via the Edge Function
-- (admin-create-user) or seed it manually — see docs/supabase-setup.md.
-- ============================================================
