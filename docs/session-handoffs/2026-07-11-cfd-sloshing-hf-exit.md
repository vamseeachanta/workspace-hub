# Session Handoff: CFD Sloshing and HF Publication

Date: 2026-07-11

## Current state

- `digitalmodel` CFD bridge merged in PR #1514.
- `gpu-claw` passed OpenFOAM v2312 smoke and the 216k-cell benchmark; it is the preferred CFD node up to 8 ranks.
- `digitalmodel` issue #1528 defines the gravity-driven sloshing tank study. Its implementation plan is user-approved; no implementation slice has landed.
- HF publication is correctly staged behind workspace-hub #3433 (projection engine, needs plan) and digitalmodel #1505 (pilot, needs plan/approval).
- Leibniz discovery recovered through an ext4 shallow sparse clone under `/tmp`; no files were changed by the subagent.
- `voice_transcription = true` is present in the canonical Codex template and verified in user configs on ace-linux-1, ace-linux-2, and gpu-claw. Repo-local coverage remains unverified.
- ace-linux-2 provisioning remains blocked by missing root/passwordless sudo.

## Active residue and blockers

- ace-linux-1 still has three overlapping `cron-repository-sync.sh` processes, plus long-running comprehensive-learning, wiki-ingest, session-analysis, provider-utilization, and import-timing processes. No cleanup was performed.
- The FUSE-backed `/mnt/local-analysis` filesystem causes Git and recursive scans to hang. Coding sessions must use local-disk ext4 shallow sparse clones under `/tmp` or another ext4 path.
- The canonical Codex template change is not yet committed/pushed.

## Dedicated-session work split

1. #1528 Slice 1: gravity conduit model and conservation tests.
2. #1528 Slice 2: natural period and deterministic sweep matrix.
3. #1528 Slice 3: synchronized CFD time-history extraction.
4. #1528 Slice 4: HTML engineering report and curve layer.
5. #3433: HF projection/staged-promotion plan only; keep needs-plan until review and approval.
6. Workspace hygiene: bounded cron/process audit; report exact PIDs before termination.

Each coding session will use a separate ext4 clone/worktree, own disjoint paths, run TDD, and return changed files plus test evidence. No session will implement direct HF upload inside #1528.

## Next checkpoint

Start Session 1 with an ext4 shallow sparse clone and implement only the gravity-conduit model/tests. After its verified branch/PR, proceed to the sweep matrix and extraction slices. Keep HF publication gated by #3433/#1505.

## Closeout classification

- EXPECTED: this handoff artifact is new session documentation.
- UNRESOLVED: stale cron processes, uncommitted canonical Codex config, and unverified repo-local voice-config coverage.
