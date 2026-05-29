# Plan for #2864: nightly sync-agent-configs.sh clobbers the Hermes SOUL symlink with the 4 KB delta

> **Status:** plan-review (adversarial-reviewed; awaiting USER approval — agent does not self-approve)
> **Complexity:** T2
> **Date:** 2026-05-28
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2864
> **Client:** N/A
> **Review artifacts:** scripts/review/results/2026-05-28-plan-2864-claude-subagent.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/_core/sync-agent-configs.sh` — L47 `HERMES_SOUL_TEMPLATE=config/agents/hermes/SOUL.md` (the **4 KB delta source**, wrong file), L53 target `~/.hermes/SOUL.md`, L1248-1249 calls `sync_hermes_plain_file` which (L1164) does `cmp -s` then `cp`+`mv -f "$tmp" "$target"` — **replacing the symlink with a plain copy of the delta** every run.
- Found: `scripts/agents/install-soul-runtime.sh` — `link_if_needed()` (L30) is the canonical symlink installer: checks `[[ -L ]]`, compares `readlink`, **backs up** a pre-existing non-symlink (`*.pre-install-backup.*`), then `ln -s config/agents/hermes/SOUL.runtime.md ~/.hermes/SOUL.md` (L63). This is the **single owner** of the SOUL symlink.
- Found: `scripts/cron/harness-update.sh:346` invokes **only** `sync-agent-configs.sh` (no `install-soul-runtime.sh` call) on the **01:15 daily** cron → nothing re-installs the symlink → clobber is permanent until a manual re-install.
- Found (test surface): `scripts/_core/tests/test_sync_agent_configs.sh` (shell), `scripts/_core/tests/test_sync_agent_helpers.sh`, `tests/readiness/test_sync_agent_configs_sso.py` + `..._pyyaml_fallback.py` (pytest). Extendable for TDD.
- **Scope confirmed narrow:** only Hermes SOUL.md is affected. `~/.codex/AGENTS.md` (also symlinked by install-soul-runtime) is **NOT** touched by sync (CODEX_TARGET is `config.toml`); Claude/Gemini use `sync_json_merge` to different targets. So `sync_hermes_plain_file` for SOUL.md is the sole clobber path.

### Standards
Not applicable (harness/infrastructure).

### LLM Wiki / Documents consulted
- Issue #2864 (body) — root cause + 3 fix options; recommends option 2 (single-owner).
- Issue #2841 (parent) — orchestrator consistency; Hermes identity delivery is a core gap.
- Memory `feedback_sync_agent_configs_clobbers_soul_symlink` — the recurring-drift root cause.
- Evidence from this session: repeated `~/.hermes/SOUL.md.pre-install-backup.*` files all 4061 bytes, mtimes ~01:16-01:18 (post-01:15 cron); the 4061-byte content == `config/agents/hermes/SOUL.md`.

### Gaps identified
- `sync-agent-configs.sh` is not symlink-aware for SOUL.md and targets the wrong template (delta vs runtime).
- No nightly self-heal of the SOUL symlink.

### Evidence (embedded verification)
**Issue statuses** (verified 2026-05-28): `#2864` OPEN; `#2841` OPEN (parent).
**File/line** (verified): sync-agent-configs.sh L47/L53/L1164/L1248-1249; install-soul-runtime.sh L30/L63; harness-update.sh L346.
**Gap proof:** `grep install-soul-runtime scripts/cron/harness-update.sh` → no match → symlink never re-installed nightly.
**Reproduction:** the clobber is observable, not just alleged — `ls -la ~/.hermes/SOUL.md.pre-install-backup.*` shows three 4061-byte backups on 05-19/23/28; `diff <(backup) config/agents/hermes/SOUL.md` → identical. (This session restored the symlink; it will be re-clobbered at the next 01:15 run until this lands.)

*Distinct sources: 5 (issue + sync script + install script + harness-update + session evidence/memory).* 

---

## Artifact Map
| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-28-issue-2864-soul-clobber.md |
| Implementation | scripts/_core/sync-agent-configs.sh (modify) |
| Tests | scripts/_core/tests/test_sync_agent_configs.sh (extend) |
| Plan review | scripts/review/results/2026-05-28-plan-2864-claude-subagent.md |

---

## Deliverable
**Single-owner design (Option B — chosen after plan-stage review killed Option A's two-owner race).** `sync-agent-configs.sh` **stops touching `~/.hermes/SOUL.md` entirely** (the offending `cp`+`mv -f` of the delta is removed); the SOUL symlink has exactly one owner — `install-soul-runtime.sh` — which `harness-update.sh` invokes on the nightly cron so the symlink is (re)installed/self-healed by its sole owner. The delta file `config/agents/hermes/SOUL.md` is **retained** (it is the build input for `build-soul-runtime.sh`). Hermes loads the full 19 KB identity+gates; no two tools resolve the link target by different mechanisms, so there is no flip-flop/backup churn.

### Why Option B over Option A
Plan-stage review (verified vs code): `install-soul-runtime.sh:23` resolves the target via `git rev-parse --show-toplevel` (absolute, symlink-resolved); `sync-agent-configs.sh:8` uses `cd "$SCRIPT_DIR/../.." && pwd` (logical, not `-P`). Under a worktree / symlinked checkout / the `~/workspace-hub` sparse overlay these **diverge**, so an Option-A symlink-aware sync would fight install-soul-runtime every run (each sees the other's link as "wrong" and re-backs-up/repoints). Option B removes the second owner, eliminating the race at the design level.

---

## Pseudocode

```
# --- sync-agent-configs.sh: REMOVE the SOUL.md clobber (do NOT replace with a 2nd owner) ---
#   delete L1248-1249 (the `sync_hermes_plain_file "$HERMES_SOUL_TEMPLATE" "$HERMES_SOUL_TARGET" ...` call)
#   delete the now-unused HERMES_SOUL_TEMPLATE (L47) and HERMES_SOUL_TARGET (L53) vars
#   KEEP the file config/agents/hermes/SOUL.md on disk — it is the build delta (build-soul-runtime.sh:10)
#   (Hermes config.yaml sync via sync_hermes_yaml_config is UNCHANGED.)

# --- harness-update.sh: make install-soul-runtime.sh the nightly self-healer ---
#   after the existing sync-agent-configs.sh call (L346 area):
run scripts/agents/install-soul-runtime.sh            # sole owner (re)installs the symlink
#   honor harness-update's dry-run/quiet mode: if DRY_RUN, pass it through / skip the install
#   (install-soul-runtime already backs up a pre-existing non-symlink and is idempotent on a correct link)
```

---

## Files to Change
| Action | Path | Reason |
|---|---|---|
| Modify | scripts/_core/sync-agent-configs.sh | **Remove** the SOUL.md clobber: delete the L1248-1249 `sync_hermes_plain_file` call + the unused `HERMES_SOUL_TEMPLATE` (L47) / `HERMES_SOUL_TARGET` (L53) vars. **Keep** `config/agents/hermes/SOUL.md` on disk (build delta). Hermes `config.yaml` sync unchanged. |
| Modify | scripts/cron/harness-update.sh | In `sync_hermes_config` (L344), after the sync call, invoke `scripts/agents/install-soul-runtime.sh` (sole symlink owner). **Gate under `--dry-run`**: since install-soul-runtime has no dry-run mode, under DRY_RUN log "would (re)install SOUL symlink" and skip; otherwise run it. |
| (Optional) Modify | scripts/agents/install-soul-runtime.sh | add a `--dry-run` flag (log intended LINK/BACKUP, mutate nothing) for testability — recommended hardening so harness-update can pass it through uniformly. |
| Extend | scripts/_core/tests/test_sync_agent_configs.sh | assert sync no longer writes `~/.hermes/SOUL.md`; fixture must add `config/agents/hermes/` (current `make_workspace` lacks it) |
| Extend | scripts/agents/tests/ (or scripts/_core/tests/) | install-soul-runtime idempotency + stale-copy-backup tests |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List
| Test name | Verifies |
|---|---|
| test_sync_no_longer_touches_hermes_soul | after a full sync run, `~/.hermes/SOUL.md` is unchanged — a pre-existing symlink stays a symlink (NOT replaced by a copy); an absent target stays absent |
| test_sync_keeps_delta_file_on_disk | `config/agents/hermes/SOUL.md` is NOT deleted (build input preserved — F3) |
| test_install_soul_idempotent_on_correct_link | install-soul-runtime twice on a correct symlink → "already points" / unchanged, **no new `.pre-install-backup.*`** (single-owner, no churn) |
| test_install_soul_backs_up_stale_copy_and_relinks | a 4 KB delta copy at target → backed up + repointed to `SOUL.runtime.md` |
| test_install_soul_dry_run_no_mutation | (if --dry-run added) logs intent, mutates nothing |
| test_harness_update_dryrun_skips_soul_install | harness-update `--dry-run` does NOT mutate `~/.hermes/SOUL.md` (logs intent only) — guards F5 against the no-dry-run install |
| test_other_agent_targets_unaffected | Claude/Codex/Gemini/Hermes-config sync paths unchanged (regression guard) |

---

## Acceptance Criteria
- [ ] `bash scripts/_core/tests/test_sync_agent_configs.sh` passes (new + existing).
- [ ] install-soul-runtime idempotency/backup tests pass; no regression in `uv run pytest tests/readiness/test_sync_agent_configs_*.py -v` (note: those SSO/pyyaml suites don't exercise SOUL — the SOUL gate is the new tests, not them).
- [ ] After a real `harness-update.sh` (non-dry) run on ace-linux-1: `~/.hermes/SOUL.md` is a symlink → `config/agents/hermes/SOUL.runtime.md` (19 KB); a **second** run leaves it unchanged with **no new** `.pre-install-backup.*` (single-owner idempotency — the bug's recurrence signature is gone).
- [ ] A `sync-agent-configs.sh` run **alone** never creates or modifies `~/.hermes/SOUL.md`.
- [ ] `config/agents/hermes/SOUL.md` still on disk and `build-soul-runtime.sh` still produces the 19 KB `SOUL.runtime.md` (build unbroken).
- [ ] `harness-update.sh --dry-run` mutates nothing; `bash -n` clean on all modified scripts.
- [ ] Review artifact posted.

---

## Adversarial Review Summary

Plan-stage review by an independent fresh-context subagent (cross-provider dispatch unavailable from a Claude-Code session; T2→degraded, documented). All load-bearing findings main-verified against live code.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (subagent, r1) | CHANGES REQUIRED | F1 HIGH (two-owner divergent path → flip-flop), F2 HIGH (idempotency test missed cross-owner case), F3 MED ("drop template" ambiguity could delete build delta), F4 MED (backup-semantics divergence), F5 MED (DRY_RUN not in control flow), F6/F8 LOW, F7 confirmed scope correct |

**Verified findings + resolution:**
- **F1 (verified):** install-soul-runtime `git rev-parse --show-toplevel` (L23) vs sync `cd…&&pwd` (L8) → divergent target strings under worktree/symlink/overlay. → **Pivoted to Option B (single owner)**, which removes the second owner entirely. Eliminates the race rather than mitigating it.
- **F2:** the original two-sync idempotency test couldn't see the cross-owner flip-flop. → Option B has one owner; test asserts install-soul-runtime idempotency (no new backup on re-run) — the true recurrence signature.
- **F3 (verified):** `config/agents/hermes/SOUL.md` is the build delta (build-soul-runtime.sh:10). → Plan now explicitly **keeps** the file; only the sync call site + vars are removed.
- **F4:** backup-semantics divergence is moot under Option B (only install-soul-runtime backs up, using its existing logic).
- **F5 (verified):** install-soul-runtime has no dry-run; harness-update does (passes `--dry-run` to sync, L349). → harness-update **gates** the install under DRY_RUN (skip+log); optional `--dry-run` added to install-soul-runtime; explicit dry-run test added.
- **F6/F8:** the SSO/pyyaml pytest suites don't exercise SOUL (not cited as the gate); Option-A/B fork **resolved → B**; review table filled.
- **F7:** scope confirmed narrow (Hermes SOUL.md only) — the plan's strongest point.

**Overall result:** PASS after revision (Option B structurally resolves the BLOCKER-class F1). A second review pass on the revised plan is reasonable but the design simplification removes the contested surface.

---

## Risks and Open Questions
- **Risk — ordering/missing artifact:** install-soul-runtime SKIPs gracefully if `SOUL.runtime.md` is absent (L34-38). harness-update should run it after the repo `git pull` so the artifact is current; if a machine never ran `build-soul-runtime.sh`, the symlink points at a present (pulled) artifact — fine.
- **Risk — dry-run mutation (F5):** install-soul-runtime has no dry-run; harness-update MUST gate it (skip+log under `--dry-run`). Covered by `test_harness_update_dryrun_skips_soul_install`.
- **Risk — per-machine rollout:** git-tracked fix; each machine self-heals on next `git pull` + 01:15 run. Coverage is per-machine, not instantaneous (verify empirically per the coverage-claims rule).
- **Open:** add `--dry-run` to install-soul-runtime.sh (cleaner, uniform) vs gate only in harness-update? Recommend adding it (small, improves testability); confirm at approval.
- **Open:** emit a one-line cron-log line when install-soul-runtime had to back up a clobbered copy, so any future recurrence is visible. Recommend yes.

## Complexity: T2
Two harness scripts modified (one removal, one small addition), existing test files extended, no new module. Cross-review: T2 = 2 providers ideally; cross-provider dispatch unavailable from a Claude-Code session → fresh-context subagent fallback documented (degraded T2→1). Recommend the user add a Codex pass out-of-session given it touches a cron-critical path.
