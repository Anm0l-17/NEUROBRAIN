# Stage C2 mentor demonstration · 23 November 2026

The CLI reads a selected TXT or Markdown file from a Google Drive folder. Supabase stores versioned chunks, line references and deletion receipts under the signed-in demo account. Use two fictional notes and a dedicated project. The CLI prints each service result during the demonstration.

## Prepare the accounts

1. Create a dedicated Supabase project. In SQL Editor, run `supabase/schema.sql` once on the empty project, then `supabase/c2.sql`. For a project with the base schema already installed, run only the second file. Use a confirmed email/password demo user. Copy the hosted project URL and **publishable** key from project settings.
2. Create a Drive folder in a demo Google account. Upload two ordinary text files, keeping their Drive IDs stable. A Google Docs document needs to be exported to TXT before upload.
3. Obtain a short-lived Google **user access token** with Drive read-only access. One rehearsal route is the [Google OAuth Playground](https://developers.google.com/oauthplayground/). For your own credentials, enable Drive API in a Google Cloud project, add the demo user as a test user, and create a web OAuth client with the Playground URL as its authorized redirect URI. In Playground settings select your own credentials, authorize `https://www.googleapis.com/auth/drive.readonly`, and exchange the code. Keep the token and client secret local. This scope can read the demo account’s Drive. NeuroBrain restricts its operations to direct children of the selected folder.
4. Set the following in the demo terminal. Replace the public identifiers with your values. The hidden zsh prompt keeps the Drive token out of command history. The CLI prompts for the Supabase demo password for each database command. Environments with an existing user access token can set `NEUROBRAIN_USER_TOKEN` instead. Credentials belong in the terminal session. The CLI reads environment variables directly.

```zsh
export SUPABASE_URL='https://PROJECT.supabase.co'
export SUPABASE_PUBLISHABLE_KEY='YOUR_PUBLISHABLE_KEY'
export NEUROBRAIN_DEMO_EMAIL='YOUR_DEMO_ACCOUNT_EMAIL'
export NEUROBRAIN_DRIVE_FOLDER='ID_FROM_DRIVE_FOLDER_URL'
read -rs 'NEUROBRAIN_DRIVE_TOKEN?Google access token: '; echo
export NEUROBRAIN_DRIVE_TOKEN
c2() { PYTHONPATH=src .venv/bin/python -m neurobrain.cloud "$@"; }
```

## Five-minute mentor walkthrough

1. Put a unique fictional phrase such as `violet dispatch 407` in the first file. Put `retained lighthouse 407` in the second. Run `c2 list`, then `c2 import FILE_ID` for each. Repeat the first import and show the same source ID and version with `duplicate: true`.
2. Run `c2 search 'violet dispatch 407'`. Show the matching text, source ID, citation and start/end lines. Show the corresponding source and chunk in the Supabase dashboard.
3. Use Drive’s **Manage versions → Upload new version** on the first file. Change the phrase to `amber dispatch 407`. Import the same Drive ID again. Show both versions with `c2 inspect FILE_ID`. Search for `violet` and then `amber` to demonstrate that search uses the current version.
4. Run `c2 preview FILE_ID` and read the version and chunk counts aloud. On the demo file only, run `c2 forget FILE_ID --confirm UUID_FROM_PREVIEW`. Show the receipt. Every CLI invocation starts a fresh process. Repeat both searches, verify the first note’s evidence is gone, then search `retained lighthouse 407` and show the second note still returns. Open Drive to show the original file is still there.
5. Reimport the forgotten content to demonstrate the tombstone rejection. For subsequent rehearsals, use new fictional text with a new marker in **both versions**. Renew the short-lived Drive token before presenting.

## Verification boundary

The local PostgreSQL lifecycle fixture is `tests/c2_postgres.sql`. Run it only on an empty disposable PostgreSQL database with psql. It supplies test Auth roles inside a rolled-back transaction. Python adapter tests use simulated HTTP responses. Record the date, observed versions, receipt and fresh-process search results after the first **hosted** rehearsal. The C2 demo is ready for the mentor once that hosted rehearsal succeeds. A 401/403 requires checking the user session, Drive account or project permissions.

[Drive downloads](https://developers.google.com/workspace/drive/api/guides/manage-downloads) · [Supabase database functions](https://supabase.com/docs/guides/database/functions)
