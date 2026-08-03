# Exit report — machine equivalence reconcile + cron upkeep chain

**Date:** 2026-07-29 → 2026-07-30
**Session host:** `macbook-portable` (Claude), dispatching to ace-linux-1 / ace-linux-2 / gpu-claw
**Entry ask:** *"run reconcile machine equivalence on this and all other machines in the ecosystem"*

---

## Outcome

The reconcile completed. The cron-upkeep chain it exposed did **not** — it is planned, reviewed, and blocked on owner actions.

| Machine | Start | End |
|---|---|---|
| dev-primary (ace-linux-1) | 0/27 masked | **27/27** |
| dev-secondary (ace-linux-2) | 0/27 masked | 26/27 |
| gpu-claw | 0/27 masked | 25/27 |
| ace-win-1 / ace-win-2 | 18/27 | 18/27 (no SSH, operator-only) |
| macbook-portable | not evaluated | out of roster by design |

Zero `STALE-CHECKOUT` fleet-wide. Fleet dirty paths ~150 → ~24 (all generated churn). ace1 stashes 15 → 0.

---

## What shipped

**#3702 — merged as `02f5cfa87` (PR #3710).** Equality artifacts now generate out of the tracked tree behind an `EQ_STATE_DIR`/`EQ_REPORT_DIR` seam. Verified in the field on 2026-07-30: ace-linux-1 carries **zero** equality artifacts in its dirty set; gpu-claw still shows 2 only because it is 14 commits behind and has not pulled the fix.

Implementation landed 23 RED tests before any implementation commit, all 17 pre-existing `test_publish_equality.py` cases still pass, zero new failures across 11 test directories.

**Communication-voice standard** — `aceengineer-strategy` PR #241, with the agent-facing skill at `.claude/skills/_internal/guidelines/communication-voice/` propagated by `propagate-ecosystem.sh` into all 6 sibling repos (verified linking, zero tree impact).

---

## The diagnosis — what was actually wrong

None of this was visible before this session.

1. **`daily-cleanup` has never disposed of anything** (#3707). Four independent defects, each sufficient alone: its branch filter matches **0 of 388** fleet branches and `git branch --merged` cannot see squash merges; it resolves siblings at `$WORKSPACE_ROOT/<repo>` when they live at `$(dirname $WORKSPACE_ROOT)/<repo>`, so all four tier-1 repos were skipped on every one of its 27 runs; worktree disposal is deny-by-default against **zero** `.wt-owner` markers; no `git stash drop`/`clear` exists anywhere in `scripts/`.

2. **Its scheduler died 2026-06-16 and nobody noticed for 45 days.** `daily-cleanup` was never a system cron job — only a Hermes gateway job. The gateway was cleanly shut down two days after #3059 (the drift sentinel) was closed `completeness-verified`, and survived three reboots without returning. `update-harness-tools.sh` kept updating the Hermes *package* nightly, so its log kept receiving entries — **the logs kept moving while the scheduler was dead.**

3. **`plan_cutover` silently drops managed-block lines** (#3709). It classifies only `before + after`; all 47 uncataloged ace1 lines sit inside the managed block and are discarded by `_rebuild_lines` without classification. On the real ace1 crontab it returns `abort_reason=None, uncataloged=0` while dropping live lines the audit flags.

4. **ace-linux-2 is 3/14 by identity** though 14/14 by line count, and has **no** `cron-health/` or `repo-ecosystem-hygiene/` state at all — its hygiene tasks are scoped `machines: [dev-primary, ...]`. Invisible since onboarding.

5. **No CI check on this repository is merge-blocking** (#3712). Ruleset `17369764` carries only `deletion` and `non_fast_forward`; branch protection returns 404. Every "required gate" enforceability claim in the ecosystem is currently false.

6. **`build-cron-identity-inventory.py` is host-dependent** (#3711) with no guard. A macOS-rendered inventory carries a **correct `input_digest` with wrong identity rows**, and the enforcement checker passes it.

**Through-line: detection works, nothing consumes it.** `repo-ecosystem-hygiene-audit.sh` and `cron-health-check.sh` have been correctly reporting this debt daily for 8+ days.

---

## Open work

| Issue | State | Note |
|---|---|---|
| #3702 | `plan-approved`, **merged** | on-box verification outstanding (owner) |
| #3059 | **reopened**, `machine:ace-linux-1` | control-surface scope; see its 2026-07-30 comment |
| #3712 | `needs-plan` | **the real blocker** — 2 MAJOR: #3709's job not in required set; no rollback path |
| #3711 | `plan-review` | MINOR ×2 addressed; **bundles a rule amendment** |
| #3709 | `needs-plan` | 8 rounds, 14 evasions; recommend stopping at tripwire framing |
| #3708 | `needs-plan` | premise disproven; re-scope after #3709 |
| #3707 | `needs-plan` | 7 MAJOR; `SAFE_BRANCH_RE` auto-merge must be addressed first |

Plan branches `plan/3709-…-v1..v6`, `plan/3711-…`, `plan/3711-…-v2`, `plan/3712-…` all carry their review artifacts.

### Owner actions — nothing proceeds without these

1. **Require `Run Tests`** — independently verified safe: green on all 18 open PR heads and latest `main`. Delivers real enforcement immediately, no prerequisites.
2. **Set `LEGAL_SCAN_AUTH_CURRENT`** — absent from repo secrets; `legal-rule-authority-reusable.yml` maps it into `AUTH_ENVELOPE` and fails `test -n`. Blocks requiring `strict-scan / authority`.
3. **Decide #3711's bundled rule amendment** to `.claude/rules/scheduler-mutation-safety.md` (branch-only; `origin/main` unchanged; confirmed not to conflict with #3712).
4. **Decide #3709's framing** — accept S1 as a tripwire with documented residue, or keep hardening.
5. **Windows boxes** at 18/27 — RDP-only, real config divergence, ace-win-2 evidence now 11+ days stale.

---

## Repo states at exit

| Host | Branch | Dirty | Stashes |
|---|---|---|---|
| macbook-portable | `main` in sync | 0 | 0 |
| ace-linux-1 | `main` in sync | 21 | 0 |
| ace-linux-2 | `main` ahead 2 / behind 4 | 1 | 7 |
| gpu-claw | `main` behind 14 | 2 | 1 |

Mac siblings: all clean.

### Dirty exceptions — all EXPECTED

- **ace1's 21** are generated churn from collectors #3702 did *not* cover: `config/ai-tools/*` provider dashboards (6), `docs/reports/provider-*` (6), plus memory topics, session-signals, reflect-history, research notes. **Zero equality artifacts** — #3702 working as designed.
- **gpu-claw's 2** *are* equality artifacts, present only because it is 14 behind and lacks the fix. Resolves on pull.
- **ace2's 1** is single-file churn; its 7 stashes and 2 unpushed auto-sync commits are the known `repository_sync` failure loop (#3705), untouched deliberately.

### Preserved deliberately

- `~/preserved-reconcile-20260729/` on ace1 — 6 keeper files, a 38-file tar of local-only tracked paths, and stash SHAs (recoverable via `git stash apply <sha>`).
- `~/preserved-acma-20260730/` on ace1 — 11 llm-wiki-acma files.
- Branch `feat/gif-pipeline-assets` on deckhand-sandbox — 35 MB of assets kept out of git history; LFS unavailable (#3706).
- Skills-link infrastructure (`.codex/`, `.gemini/`, `.worktrees/`) on all boxes — never touched, per the junction-restore incident rule.

**No external action is pending.** No unmerged local commits on the Mac. No scheduler, crontab, or ruleset was mutated on any host. Hermes remains down by owner decision.

---

## Process findings worth keeping

**Self-review is not an adversarial gate.** Three plans self-reviewed MINOR and failed independent review MAJOR — 3/3. The mechanism is consistent: a self-review checks internal consistency; an independent pass reads the code the plan proposes to change.

**Require per-test today-status with a proving command.** Plans shipped 6/20 and 9/18 rows already green; one audit found 3 of 9 RED claims false, including two "unverifiable on macOS" excuses that were simply wrong.

**Commit the prototype.** A review that reimplements the artifact it is reviewing tests its own reading, not the author's design.

**A parse-only check cannot verify that a test ran.** Eight rounds and fourteen evasions demonstrated it; each fix widened the pinned surface without converging. Runtime facts need runtime controls.
