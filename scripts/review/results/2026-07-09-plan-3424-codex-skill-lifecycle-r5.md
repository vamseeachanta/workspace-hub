# Adversarial plan review — #3424 skill lifecycle r5

Provider: Codex parallel reviewer

Verdict: MAJOR

## Findings

1. The required approval transaction was not executable on the active Windows host because `approve-provider-plan.py` imported POSIX-only `fcntl` unconditionally; a transaction on another checkout would not create evidence in this worktree.
2. Approval-bootstrap security checks used Python `assert`, which disappears with `PYTHONOPTIMIZE=1` or `python -O`.
3. Mutable local journal/marker evidence did not prove the remote label actor, freshness, authorized binding, comment identity, or exact marker bytes.
4. The exact 11-skill migration set and expected ranking changes were not frozen before approval; the baseline fixture was scheduled for post-approval creation.
5. Step 12 instructed mutation of a manifest whose bytes and digest were declared frozen.

## Required disposition

- Compose the existing canonical remote authority/binding loaders directly in a read-only Windows-capable bootstrap and use explicit failures under optimized Python.
- Freeze the exact candidate identities, description hashes, current ranks, and expected ranks as a pre-approval artifact.
- Use the predeclared manifest phases without modifying the manifest.

No files were edited by the reviewer.
