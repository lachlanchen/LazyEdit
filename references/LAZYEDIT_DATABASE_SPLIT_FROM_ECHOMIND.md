# LazyEdit Database Split From EchoMind

## Summary

LazyEdit is supposed to use its own PostgreSQL database, `lazyedit_db`.

In the old deployment, the real LazyEdit data was accidentally written into `echomind_db` instead. The root cause was runtime configuration:

- a generic `DATABASE_URL` for EchoMind existed in the shell environment
- LazyEdit startup was not reliably loading the repo-local `.env`
- the backend therefore connected to `echomind_db`

The current fix in this repo is:

- `start_lazyedit.sh` now loads the repo `.env`
- `LAZYEDIT_DATABASE_URL` is promoted to the effective `DATABASE_URL`
- LazyEdit now starts against `lazyedit_db`, not `echomind_db`

## What Was Found

On the old Ubuntu PostgreSQL cluster:

- `lazyedit_db` existed but had no relations
- `echomind_db` contained the actual LazyEdit tables and data

Recovered table counts from the old data:

- `videos`: 107
- `generated_videos`: 31
- `transcriptions`: 178
- `video_metadata`: 185
- `ui_preferences`: 15

LazyEdit table set involved in the migration:

- `videos`
- `captions`
- `frame_captions`
- `generated_videos`
- `keyframe_extractions`
- `subtitle_burns`
- `subtitle_translations`
- `transcriptions`
- `ui_preferences`
- `venice_a2e_history`
- `video_metadata`

## Current Repo Behavior

The backend tmux pane started by [`start_lazyedit.sh`](../start_lazyedit.sh) now does this before launching Python:

1. source `~/.bashrc`
2. source repo `.env`
3. if `LAZYEDIT_DATABASE_URL` is set, export it as the effective `DATABASE_URL`

That keeps LazyEdit isolated from EchoMind DB settings.

## Safe Cross-System Migration Pattern

This is the safe pattern used to migrate from the old Ubuntu into the current machine without modifying the old system in place:

1. mount the old Ubuntu root, for example at `~/UbuntuSDA`
2. copy the old PostgreSQL cluster to a temporary working directory
3. start the copied cluster on another port
4. confirm old `lazyedit_db` is empty
5. confirm old `echomind_db` contains the LazyEdit tables
6. dump only the LazyEdit tables from old `echomind_db`
7. back up the current `lazyedit_db`
8. restore the LazyEdit dump into the current `lazyedit_db`
9. fix ownership of restored public tables and sequences to `lachlan`
10. restart LazyEdit and verify `/api/videos`

## Dump Command Example

```bash
pg_dump -h 127.0.0.1 -p 55432 -U postgres -Fc -d echomind_db \
  -t public.videos \
  -t public.captions \
  -t public.frame_captions \
  -t public.generated_videos \
  -t public.keyframe_extractions \
  -t public.subtitle_burns \
  -t public.subtitle_translations \
  -t public.transcriptions \
  -t public.ui_preferences \
  -t public.venice_a2e_history \
  -t public.video_metadata \
  -f /var/tmp/lazyedit_old_from_echomind.dump
```

## Restore Command Example

```bash
sudo systemctl stop lazyedit.service
sudo -u postgres pg_dump -Fc -d lazyedit_db -f /var/tmp/lazyedit_db_before_restore.dump
sudo -u postgres pg_restore --clean --if-exists --no-owner \
  -d lazyedit_db /var/tmp/lazyedit_old_from_echomind.dump
```

## Ownership Fix

After `pg_restore --no-owner`, public tables/sequences may end up owned by `postgres`. LazyEdit expects to manage schema changes as `lachlan`, so ownership should be reassigned:

```bash
sudo bash -lc "cat > /var/tmp/lazyedit_fix_owner_tables.sql <<'SQL'
SELECT format('ALTER TABLE public.%I OWNER TO lachlan;', tablename)
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
SQL
cat > /var/tmp/lazyedit_fix_owner_sequences.sql <<'SQL'
SELECT format('ALTER SEQUENCE public.%I OWNER TO lachlan;', sequence_name)
FROM information_schema.sequences
WHERE sequence_schema = 'public'
ORDER BY sequence_name;
SQL
sudo -u postgres psql -d lazyedit_db -At -f /var/tmp/lazyedit_fix_owner_tables.sql | sudo -u postgres psql -d lazyedit_db -v ON_ERROR_STOP=1 >/dev/null
sudo -u postgres psql -d lazyedit_db -At -f /var/tmp/lazyedit_fix_owner_sequences.sql | sudo -u postgres psql -d lazyedit_db -v ON_ERROR_STOP=1 >/dev/null"
```

## If You Want To Fix The Old Ubuntu In Place

Yes, that can be done too.

The in-place repair on the old Ubuntu is:

1. back up old `echomind_db`
2. back up old `lazyedit_db`
3. dump only the LazyEdit tables from old `echomind_db`
4. restore them into old `lazyedit_db`
5. fix ownership to `lachlan`
6. update old LazyEdit startup to use repo `.env`

That workflow should be done while booted into the old Ubuntu itself, not from the new machine.

## Verification

After a successful migration, these should hold:

- `lazyedit.service` is running
- `/api/videos` returns real data instead of an empty list
- `lazyedit_db` contains the LazyEdit tables
- the app no longer depends on `echomind_db`
