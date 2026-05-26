# Plan for #2813: Roll out the Codex-under-Claude route to remaining ecosystem machines

> **Status:** draft (needs adversarial review → user approval) · **Complexity:** T2 · **Date:** 2026-05-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2813 · **Refs:** #2804 (route, merged #2809) · **Client:** N/A

## Resource Intelligence Summary
- Route validated + codified on `main`: `scripts/install/{codex-bwrap.aa,setup-codex-sandbox.sh,teardown-codex-sandbox.sh}`; `docs/reports/2026-05-26-codex-under-claude-pilot.md`; memory `feedback_codex_sandbox_write_blocked`.
- Installer is **guarded**: `--check` default (no mutation), `--dry-run`, explicit `--accept-userns-lpe-risk` to write, Ubuntu/AppArmor detection (fail-fast on others), sentinel refuse-overwrite, `codex --version` log.
- Currently applied **only on `ace-linux-1`**. Memory: `feedback_cross_machine_execution` (per-machine via shared git, not fleet-push); the "verify coverage empirically" rule (don't assume a machine list).

## Problem
The fix is reproducible but deployed on one box. Other Ubuntu machines that want Codex-under-Claude orchestration need the one-time, user-authorized install; non-Ubuntu machines (e.g. Windows `D:\workspace-hub`) must no-op cleanly.

## Approach
1. **Enumerate the live ecosystem machines** (verify on the filesystem / machine registry — do not assume a fixed list).
2. Per Ubuntu machine where wanted: `git pull` → `setup-codex-sandbox.sh --check` → `--accept-userns-lpe-risk` (user sudo, per-machine). Verify with a broker `task --write` smoke test.
3. Non-Ubuntu / not-wanted: document **N/A** with reason (installer already fail-fasts).
4. **No silent/batch privileged auto-run** — each install is an explicit per-machine, user-authorized action.

## Risks & mitigations
| Risk | Mitigation |
|---|---|
| Security tradeoff (bwrap-wide userns) re-decided per machine | installer requires `--accept-userns-lpe-risk`; teardown documented; same tradeoff the user accepted on ace-linux-1 |
| Batch agent runs the privileged installer | installer defaults to `--check`; refuses to write without the explicit flag; no-ops on non-Ubuntu |
| Coverage claim overstated | enumerate live machines; per-machine smoke test; coverage table |

## Acceptance criteria
1. Live machines enumerated (not assumed). Per machine: Ubuntu+wanted → installed, `--check` shows profile + `network_access`, broker smoke test passes; else documented N/A.
2. Per-machine coverage table committed (append to the pilot report).
3. No silent privileged auto-runs; each install explicit + user-authorized.

## Dependencies
Independent of the kanban issues. Sequenced after the route proved out on ace-linux-1 (done).
