# Cross-Review — WRK-1049 Plan (Claude)

### Verdict: APPROVE

**Scope**: process.md Step 4 retire, start_stage.py session lock, claim-item.sh working/ guard.

**Assessment**:
- P1 (process.md): Correct. Removing inline bash and mandating `claim-item.sh` eliminates the bypass path cleanly. Single source principle applied.
- P2 (start_stage.py): Stage 1 session-lock write is minimal and non-blocking. No impact on existing stage flow.
- P3 (claim-item.sh): Guard placement (before FILE_PATH resolution) is correct — fails fast before any git/quota checks.
- Tests: T1-T4 cover the collision scenario, lock field presence, and lock detail reporting. 6/6 pass.

**No P1/P2/P3 findings.**

[P3] Minor: session-lock.yaml is never cleaned up after archive — stale locks could accumulate. Acceptable for now; lock check in claim-item.sh only fires when working/ exists (the real gate), so stale locks are harmless.
