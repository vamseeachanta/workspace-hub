# Post-Commit Hook Metadata Follow-Up

Use this when a commit, merge, or push appears to succeed but the working tree is still dirty because hooks or agent tooling appended metadata.

## Pattern

1. After every mutating git operation, immediately run a porcelain status check before reporting success.
2. If the only dirt is expected metadata (for example `logs/orchestrator/hermes/skill-patches.jsonl` after a skill edit), inspect the added lines rather than restoring them blindly.
3. Confirm the metadata points to the just-created commit or expected tool action.
4. Commit the metadata in a small follow-up commit with a direct message such as `chore: record <topic> skill ledger`.
5. Re-run remote parity verification if the user asked for push/closeout: local `HEAD`, `origin/<branch>`, and `git ls-remote` must match.

## Pitfall

Do not claim clean closeout immediately after the primary commit. In Hermes/workspace-hub sessions, hooks and skill tooling can legitimately append ledger lines after the commit hook runs. A clean status before the commit is not evidence of a clean status after the commit.
