# Review dispositions — 13 November

CodeRabbit ran four code-scoped reviews. The initial whole-worktree upload was rejected; source/scripts scopes were approved and exclude datasets and reports.

- Initial source, seven issues: fixed interactive recovery, listing provenance, unresolved-reference rejection, final delivery/deletion coordination, extraction-aware versions, cloud reset handling. Focus delay already exists in Swift.
- Follow-up source, seven issues: interactive fix landed after its snapshot; provisioning is documented in ollama/README.md; empty snapshot replacement is intentional and now documented/tested; retrieval provenance fixed; extract_notes and NoRedirect exports exist; extract_notes revalidates full text before persistence.
- Final source, three issues: evidence selector uses the same lexical top-five set as delivery validation, so conditional semantic mismatch is inapplicable; language-model disclosure corrected; full-text policy is enforced again inside import_observation through extract_notes.
- Scripts, three issues: checkpoint verifier requires only state_dict, so smaller diagnostic checkpoint is supported (existing reload evidence); paraphrase references now connect to the original row; frozen artifacts use exclusive binary UTF-8 writes. Existing frozen bytes and grouping remain unchanged.

No broad accuracy or security-audit claim follows. The final disclosure and two small script fixes were checked locally after the remote review. Live cloud/account/window gates remain distinct.
