# Adversarial plan review — #3424 privacy/transaction r7

Provider: Codex parallel reviewer

Verdict: MAJOR

## Findings

1. The owned index lock was created before rollback/cleanup traps were armed.
2. A signal between `update-ref` and a later installed flag could leave the candidate installed without rollback.
3. Traps were disabled before owned-lock cleanup, leaving a signal window for orphan residue.
4. Rollback swallowed CAS failure instead of recording the observed ref.

## Required disposition

- Arm traps before lock acquisition.
- Derive rollback state from the actual ref instead of a post-CAS flag.
- Remove the owned lock before disarming traps and report any rollback CAS/ref conflict.

No files were edited by the reviewer.
