# Code-stage adversarial review — #2864 SOUL clobber fix

> **Stage:** code/artifact · **Issue:** [#2864](https://github.com/vamseeachanta/workspace-hub/issues/2864) · **Date:** 2026-05-28 · **Complexity:** T2
> **Branch:** feat/2864-soul-clobber-impl

## Method
Independent fresh-context subagent (cross-provider dispatch unavailable from a Claude-Code session; degraded T2→1). Reviewed the full diff + all modified files + the invoked installer + the coupled pytest. Findings main-verified.

## Verdict: APPROVE (1 LOW hardening applied)

| # | Result | Note |
|---|--------|------|
| 1 | PASS | `HERMES_SOUL_TEMPLATE`/`HERMES_SOUL_TARGET` removal clean (zero residual refs); config.yaml sync untouched |
| 2 | PASS | dead `sync_hermes_plain_file` retention is correct — `test_sync_agent_configs_pyyaml_fallback.py:33` uses its def line as a slice delimiter (verified; deleting it would raise ValueError) |
| 3 | PASS | install-soul-runtime (no `--dry-run`) correctly gated: dry-run only logs, never invokes |
| 4 | PASS | `grep`-no-match exit 1 cannot abort the cron run (`set -uo pipefail`, no `-e`; script ends `exit 0`); installer failure is non-fatal |
| 5 | PASS | fresh-machine SKIP is benign (installer returns 0 on missing source / absent ~/.hermes) |
| 6 | PASS | **regression test proven genuinely RED** — reviewer reconstructed the pre-fix script; the fixture clobbered the symlink into a regular file containing the delta. Not vacuous (fixture creates the template the old guard required). |
| 7 | LOW → **fixed** | installer resolves repo via `git rev-parse` from cwd; harness-update now wraps it in `( cd "$WORKSPACE_HUB" && … )` so a manual run from any cwd is robust (cron path already cd'd in) |
| 8 | INFO | plan-review's F1 two-owner race structurally dissolved under Option B (single writer) |
| 9 | PASS | grep across scripts/ + config/ confirms **no remaining copy-writer** of `~/.hermes/SOUL.md`; delta retained + still consumed by build-soul-runtime.sh:10 |

## Verification evidence
- `bash -n` clean (both scripts); shell suite 24 PASS/0 FAIL; pytest readiness 12 passed.
- Live single-owner idempotency on ace-linux-1: `install-soul-runtime.sh` ×2 → "already points" both, backups 4→4 (no churn), symlink → `SOUL.runtime.md` intact.
- Reviewer independently reproduced RED on reconstructed pre-fix code.

No HIGH/MED defects. #2864 fully resolved with a single remaining symlink owner.
