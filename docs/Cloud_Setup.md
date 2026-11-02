# NeuroBrain cloud prototype setup

## What goes where

- Google Drive: original TXT/Markdown note files.
- Supabase PostgreSQL: source versions, chunks, citations, tombstones and deletion receipts.
- The application: validates and chunks downloaded Drive content before writing it to Supabase.

Google One provides the Drive storage quota; it is not itself a PostgreSQL database.

## Supabase

1. Create a Supabase project.
2. Open **SQL Editor** and run [`supabase/schema.sql`](../supabase/schema.sql).
3. Enable an authentication provider for the prototype, preferably email/password.
4. Copy the project URL and the publishable/anon key into a local `.env` file. Never commit a service-role key.

The schema enables row-level security. Every row is owned by the signed-in Supabase user.

## Google Drive

1. Create a Google Cloud project.
2. Enable the Google Drive API.
3. Configure an OAuth consent screen and a desktop OAuth client.
4. Use the narrowest practical Drive scope and select one NeuroBrain folder.
5. Keep the downloaded OAuth client JSON outside this repository.

The first import prototype should read only TXT/Markdown files from that selected folder. It should not sync the whole Drive.

## Prototype order

1. Add environment loading and Supabase authentication.
2. Implement a cloud `MemoryStore` adapter using the schema.
3. Add Google Drive file listing/download for the selected folder.
4. Reuse the existing `NotePolicy` before uploading content to Supabase.
5. Port search, inspection and source-scoped deletion tests.
6. Keep the current SQLite store as a local test/reference backend until cloud parity passes.

Required behavior stays unchanged: duplicate imports are idempotent, current versions are searchable, citations point to exact chunks, and forgetting removes every stored version and its derived chunks.
