# Hosted (Day 4) preparation, done early on 16 Nov 2026

Branch `demo-week-2026-11`, commits `676e974`, `032d69a`, `bb18e11`, `0dcaaa9`. Gates: 82 unit tests OK, `ruff check src tests` clean.

## What was verified and how (read this first)

| Item | Status |
|---|---|
| `supabase/c2.sql` changes | **Executed on a private PostgreSQL 18.4** (own data directory, unix socket only, started from the Mac's installed binaries) with `tests/c2_postgres.sql` + `tests/observation_postgres.sql`: all pass. This is plain Postgres with stand-in auth roles. **Not run on Supabase.** RLS, PostgREST and real JWT auth are untested. |
| Python adapters (`cloud.py`, `chat_api.py --hosted`) | Mocked HTTP only. |
| F12 (retry on disconnect) | Mock only: failed write is not reported saved, a retry after a lost reply returns `duplicate: true`. Needs a real disconnect on Day 4. |
| F13 (second user cannot see rows) | Postgres fixture with two owners passes (owner 2 sees nothing). Needs two real Supabase accounts. |
| Hosted acceptance | **None.** Needs your Supabase project and two demo accounts. |

To re-run the SQL fixtures: initdb a throwaway cluster, then run `tests/c2_postgres.sql` with `observation_postgres.sql` inserted before its final `rollback` (see the header comment of that file).

## Changes

1. **Hosted search fixed** (`676e974`): `plainto_tsquery` ANDed every word, so "When is the violet demonstration?" matched nothing. Now words are ORed like the local index (confirmed against Postgres before the fix).
2. **Forget parity** (`032d69a`, `0dcaaa9`): new `c2_forget_set` (internal, not callable by `authenticated`/`anon`). Preview and forget cover all versions of the file, all captures of the same screen window, then one hop to copies with the same content hash or the same whole chunk set (whitespace-normalised, only when 24+ characters). Newest surviving version is reactivated. The confirmation token covers the exact set, so a copy added after the preview makes it stale. Scope is the whole owner, matching owner-wide tombstones.
3. **Search collapses linked copies** into one hit with `linked`.
4. **screen-ocr**: each distinct capture is its own hosted source (same as local).
5. **`HostedMemory` + `chat_api --hosted`** (`bb18e11`): the chat bridge can answer from Supabase. Needs `NEUROBRAIN_USER_TOKEN` (short-lived), never prompts per request. **No local cache** (deliberate): a cache could serve a note forgotten elsewhere. The local-lock guard on delivery does not exist on the server, so the recheck before delivery is the only protection.

## Review findings (two checkers, CodeRabbit)

Fixed:
- Over-forgetting: a lone short note ("Approved.", "OK") made two distinct sources look identical, so forgetting one deleted and tombstoned the other (found by the privacy checker; the local path had the same flaw). Now needs 24+ characters, both in SQL and `core.py`; tests on both.
- A copy of the same content in another folder survived forget with its hash tombstoned. Hosted forget scope is now owner-wide.
- `ValueError` from a malformed hosted response now gives 503 instead of an unhandled error.

Rejected by CodeRabbit check:
- Forget/import race: every operation takes the owner advisory lock (`c2.sql`, before any set is built).
- Restore across folders: a file ID cannot span folders (`File belongs to another import folder`).

Deferred:
- Forgotten text can be re-imported with a whitespace variant (new hash; tombstones are exact-hash only). Same locally. Needs a normalised-hash tombstone.
- The confirmation token is computable by the caller (md5 of ids); it only covers the caller's own set. Low.
- The tests/edge checker had not reported when this was written (see end of file if updated).
