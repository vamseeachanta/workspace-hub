# Session Handoff — #2801 Machine-Equality Family continuation (1 Linux + 1 Windows)

**Date:** 2026-05-30 • **Origin machine:** ace-linux-1 • **Continue on:** 1 Linux machine (gate code) + 1 Windows machine (`licensed-win-1` or `-2`: PowerShell validation).

---

## TL;DR — what shipped this session vs what remains

| Issue | What | State |
|---|---|---|
| [#2851](https://github.com/vamseeachanta/workspace-hub/issues/2851) | Checkout-freshness guard (provenance + STALE-CHECKOUT) | ✅ **merged + closed** (PR #2869) |
| [#2814](https://github.com/vamseeachanta/workspace-hub/issues/2814) | Fix stale context.md (siblings vs nested) | ✅ **merged + closed** (PR #2875) |
| [#2801](https://github.com/vamseeachanta/workspace-hub/issues/2801) | Machine-equality matrix (parent) | ✅ **closed** (95%, Windows population deferred to #2815/#2816/#2229) |
| [#2817](https://github.com/vamseeachanta/workspace-hub/issues/2817) | plan-approval → label-actor authority | 🟡 **PR1 merged** (PR #2876, shared `label_authority.py`); **PR2 = the core gate, NOT started** |
| [#2816](https://github.com/vamseeachanta/workspace-hub/issues/2816) | `collect-equality.ps1` Windows compute | ✅ **merged** (PR #2877); **owner-run validation on Windows REMAINS** |
| [#2815](https://github.com/vamseeachanta/workspace-hub/issues/2815) | Task Scheduler single-source + live-validate | 🟡 **plan-approved, NOT started** (renderer code = Linux; live-validate = Windows) |

**Plans + reviews + this handoff** are on branch `plans/2817-2815-2816` → **merge that PR first** so the docs are on `main` for both machines.

---

## ⚠️ Workflow gates (apply on BOTH machines — non-negotiable)

- Both #2817-PR2 and #2815 issues are already `status:plan-approved` — you may implement. **Do NOT re-plan.**
- **TDD-first.** Tests before implementation.
- **Adversarial review at the CODE stage** before merge: #2817 = T3 (Claude + Codex + Gemini), #2815 = T2 (Claude + Codex). Use `env -u CLAUDECODE bash scripts/review/submit-to-codex.sh --file <payload>` and `env GEMINI_CLI_TRUST_WORKSPACE=true bash scripts/review/submit-to-gemini.sh ...`.
- **Branch off fresh `origin/main`** in a worktree — never the local WIP branch (this machine's default tree is ~160 commits behind via auto-sync drift; see `feedback_recover_stale_branch_for_pr`).
- **Push with `--no-verify`** from a worktree (the pre-push cross-repo drift hook fails when sibling repos aren't checked out — environment artifact, Iron-Law-permitted for push).
- The **plan-approval marker** (`.planning/plan-approved/<N>.md`) hook is directory-level; the `status:plan-approved` label already on these issues is the real authorization.

---

## LANE A — Linux machine: #2817 PR2 (the core security gate)

**Read first:** `docs/plans/2026-05-30-issue-2817-plan-approval-label-authority.md` — especially the **Adversarial Review Resolution** table (R1–R6). The T3 review (Codex + Gemini) is DONE; the plan already encodes the fixes.

**Foundation already on `main`:** `scripts/workflow/label_authority.py` — `verified_label_event(repo, issue, label)`, `gh_json`, `parse_iso` (PR1, merged). Build the gate ON this; the completeness gate already imports it (don't regress `tests/workflow/test_completeness_gate_check.py`).

**Build (TDD), per the plan's Files-to-Change + the R1–R6 resolutions:**
1. `scripts/workflow/plan_approval_gate_check.py` — server decision. Critical review fixes:
   - **R2/R3 anti-substitution:** resolve the linked issue from the **branch name** (`feat/<N>-*`) and/or GitHub linked-issue metadata — NOT PR body/trailers for authority. Bind to the approved plan artifact path+revision **recorded on the issue by an authorized actor**, and check the PR touches that plan path.
   - **R2 freshness:** `label_applied_at >= plan_revision_time` ONLY (GitHub-observed timestamps). **Drop `pr_head_time` entirely** (it's both workflow-breaking and forgeable via `GIT_COMMITTER_DATE`). `synchronize` does NOT invalidate plan-approval.
   - **R1 fail-closed:** unverifiable owners-var / gh-auth / linked-issue / label-event ⇒ block.
   - **R4 PAT/bot:** reject `*[bot]`/`type: Bot` (detectable); PAT/machine-user mitigation is **policy** (human-only OWNERS allowlist + protected-label ruleset + audit), NOT a runtime check — narrow the claim.
2. `scripts/workflow/label_authority.py` — add `is_authorized_human(actor, owners, *, reject_bots=False)` + `label_is_fresh(applied_at, not_before)`. **R6: `reject_bots` is OPT-IN** so the completeness gate keeps its exact membership-only behavior.
3. `.github/workflows/enforcement-gate.yml` — **retarget** the existing `plan-approval` job (line ~117) to `plan_approval_gate_check.py`; add `synchronize` trigger. **R1/R5: keep `require-plan-approval.sh` HARD-active until the new check is a verified required status check** (no window where neither enforces). Gate behind `PLAN_APPROVAL_GATE_ENABLED`.
4. `.claude/hooks/plan-approval-gate.sh` + `.codex/hooks/plan-approval-gate.sh` → advisory (warn, exit 0); remove marker reads.
5. `scripts/workflow/migrate_plan_approval_markers.py` (R5/MAJOR-5 audit) + `docs/governance/2026-05-30-plan-approval-label-authority.md`.
6. Tests: `tests/workflow/test_plan_approval_gate_check.py` + extend `test_label_authority.py` (the plan's TDD list — ~18 cases incl. `test_synchronize_after_approval_does_not_invalidate`, `test_label_predates_plan_revision_fails`, `test_anti_substitution_unrelated_issue_fails`, `test_bot_actor_fails`, `test_completeness_gate_unchanged_after_refactor`).

**OWNERS decision (user-confirmed):** `PLAN_APPROVAL_OWNERS` = comma-separated human logins, bootstrap `vamseeachanta`.

**ADMIN PREREQUISITE (needs the repo admin — owner action, BEFORE final cutover):** make the "Plan Approval Check" a **required status check** on `main` (branch protection / ruleset) AND a **protected-label ruleset** restricting who may apply `status:plan-approved`. The gate fails-closed and leans on these; don't retire the old marker gate until both are confirmed. Recommend the `PLAN_APPROVAL_GATE_ENABLED` flag stays off until then.

**Suggested PR split:** PR2a = `plan_approval_gate_check.py` + helper additions + tests (no CI cutover); PR2b = CI retarget + hook demotion + migration + governance (the cutover, behind the flag).

---

## LANE B — Windows machine (`licensed-win-1`/`-2`): validate #2816, then #2815

**Read first:** `docs/plans/2026-05-30-issues-2816-2815-windows-equality-collector.md` (PART A done/merged; PART B = #2815) + its review-resolution (W1–W6).

### B1 — Validate the merged #2816 collector (owner-run; could not be Linux-tested)
On `D:\workspace-hub` checked out at current `main`:
1. `git pull` so `scripts/readiness/collect-equality.ps1` is present.
2. `pwsh -File scripts/readiness/collect-equality.ps1 -Stdout` (or `powershell`). Confirm: emits `schema_version: 3`, `os: windows`, a `provenance` block with **`dirty:false` / `behind_main:0` / `ahead_main:0`** (else the matrix grades STALE-CHECKOUT), and REAL `cores`/`ram_total_mib`/`ram_avail_mib`/`disk_avail_gb`/`gpu_model`.
3. **Freshness preflight (W3):** if it fails fast with a freshness error, the box is behind `origin/main` — run RepoSync / `git fetch origin main` first. It must REFUSE to write a stale report.
4. `Invoke-ScriptAnalyzer scripts/readiness/collect-equality.ps1` — fix any warnings.
5. **W4 — capture the RAM floor:** record the real `ram_total_mib`, then set `ram_gib_min` on `licensed-win-1`/`-2` in `scripts/readiness/harness-config.yaml` (look for the `TODO(#2816 W4 follow-up)` comments) at a value below the real spec with margin. Commit on a `feat/2816-ram-floor` branch off `main` → PR. Paste the `-Stdout` output in #2816.
6. Run `python scripts/readiness/build-equality-matrix.py` (Windows = `python`, NOT `uv`) and confirm the `licensed-win-1` column grades compute **CONFORMS** (not MISSING-EVIDENCE / STALE-CHECKOUT). Note: `solvers` will show BELOW-BASELINE by design until a Windows license probe lands (#2849 follow-up) — not a defect.

### B2 — Implement #2815 (Task Scheduler single-source; renderer code can be drafted on Linux, live-validated on Windows)
Per the approved plan (Strategy 1): teach `scripts/windows/setup-scheduler-tasks.ps1` to read `config/scheduled-tasks/schedule-tasks.yaml` and render the **EqualityReport** task from it (construct the Windows action from task metadata, use `python` not `uv`).
- **W1 (Codex MAJOR):** `collect-equality.sh`/`.ps1` only WRITE the report — they do NOT commit/push. The new `scripts/windows/equality-report.ps1` wrapper MUST commit+push `.claude/state/equality-*.yaml` after a successful collect+build (or delegate to a verified `win-session-state-commit` step), else the central matrix never sees the Windows report. Add a test.
- **W2:** Windows Python must have PyYAML (the matrix imports `yaml`); add a preflight/contract that fails fast with a clear message, or prefer a stdlib-only YAML read in the renderer.
- **W6:** add a parser-level test that the generated trigger is **weekly-Monday** (the current PS1 only does daily `-At`) — not just string presence.
- Live-validate: `setup-scheduler-tasks.ps1 -WhatIf` → register → `Start-ScheduledTask` → confirm a real fresh report + matrix CONFORMS; paste evidence in #2815 / #2229.

---

## Cross-machine coordination
- **Lanes are independent** (Lane A = `scripts/workflow/` + CI; Lane B = `scripts/readiness/`/`scripts/windows/`) — no file overlap, work them in parallel.
- Each lands as its **own reviewed PR** off fresh `origin/main`. Serialize commits per branch; `--no-verify` push from worktrees.
- After #2816's RAM floor + #2815 land, the matrix reaches 4/4 active machines — close out #2229.

## Repo state at handoff
- `main` HEAD includes PR #2876 (#2817 PR1) + PR #2877 (#2816). Clean.
- Origin-machine worktrees removed except this `plans/` one (carries the docs in this PR).
- This machine's default working tree is on `fix/statusline-codex-quota` (stale WIP, ~160 behind) — **do not build there**; always worktree off `origin/main`.
- Memory: `feedback_completeness_gate_close_flow_gotchas`, `feedback_recover_stale_branch_for_pr` are relevant; read them.
