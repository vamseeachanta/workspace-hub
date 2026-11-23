# Issue creation denied: packet fallback

Use when `gh issue create` fails because the current credentials cannot create issues in the target repo, but the user asked to create a concrete issue set and there is enough information to draft it.

## Pattern
1. Do not stop at the permission error.
2. Preserve the work as a durable issue packet in the target repo when writes are allowed:
   - `docs/<topic>-issue-packet.md` for human-readable review and copy/paste.
   - Include each proposed issue title, label, body, success test, and any ordering/dependency notes.
3. Also write per-issue body files and a small `gh issue create --body-file ...` script in the session scratch area so creation is one command after auth is fixed.
4. Attempt exactly one real `gh issue create` first if safe; capture the exact failure string in the packet header only as current evidence, not as a durable claim that GitHub is broken.
5. Verify the packet exists with a file read/status before reporting completion.

## Why
For private client/workspace repos, token scope problems are common. The useful deliverable is still the issue design and a reproducible creation bundle. Avoid losing the issue decomposition just because online creation is blocked.

## Report shape
- State: online creation blocked; packet preserved.
- Evidence: packet path, script path, exact one-line `gh` error.
- Gap: GitHub issue-creation access needs correction.
- Next action: run the generated script after auth/scope is corrected.

## Avoid
- Do not encode environment-specific token state as a permanent rule.
- Do not invent issue URLs when creation failed.
- Do not claim issues were created unless `gh issue create` returned URLs or `gh issue view/list` verifies them.
