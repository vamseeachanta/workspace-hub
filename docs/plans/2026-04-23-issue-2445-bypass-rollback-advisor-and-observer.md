# Plan for #2445: implement bypass-rollback advisor + post-commit observer per #2289 policy

> **Status:** draft (pre-adversarial-review)
> **Complexity:** T2 (multi-script implementation, 20+ test suite, 4 modified files, hook chaining)
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2445
> **Parent (policy contract):** #2289 — `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` (v10 draft, Codex MAJOR / Gemini APPROVE as of 2026-04-22)
> **Grandparent:** #2018 (CLOSED — agent bypass resistance technical gates)
> **Review artifacts:** `scripts/review/results/2026-04-23-plan-2445-{claude,codex,gemini}.md`

---

## Hard precondition (binding)

This plan is a **T2 implementation** of the **policy contract** produced by #2289. Implementation of the scripts/tests described below MUST NOT begin until #2289 is `status:plan-approved` and `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists in `main`. Rationale:

- #2289 is still at v10 draft (Codex MAJOR as of `scripts/review/results/2026-04-22-plan-2289-codex-v10.md`).
- Two policy sections remain under active revision: `log_only_approved_later` approval-binding provenance and `log_only_remediated_later` eligibility boundary.
- If #2445 implementation begins against v10 and the policy tightens in v11+, the rework cost is multi-script + multi-test + a second round of cross-review.

**What this plan DOES deliver before #2289 approval:**
- A reviewable, locked implementation plan for #2445 that can be cross-reviewed now against the v10 policy contract.
- An explicit "policy revision absorption" checkpoint in the acceptance criteria.

**What this plan explicitly does NOT do:**
- Broaden scope into governance redesign (#2289 is the policy authority; implementation choices that contradict the policy revise the policy first, not the implementation).
- Implement auto-revert (#2289 advisory boundary: the advisor emits recommendations; execution belongs to a human operator or higher-scope tool).
- Modify `docs/governance/TRUST-ARCHITECTURE.md` or `docs/standards/HARD-STOP-POLICY.md`.
- Touch any file in the enforcement-surface never-safe-listed set (`.claude/hooks/**`, other `scripts/enforcement/**`, `docs/governance/**`, `docs/standards/*`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`) except the four targeted modifications named in §Files to Change.

---

## Resource Intelligence Summary

### Existing repo code
- **Found:** `scripts/enforcement/require-plan-approval.sh` (124 lines). Line 105 help text claims bypass via `FORCE_PLAN_GATE=1` but the script only reads `FORCE_PLAN_GATE_STRICT` (line 12) and the bypass-log write on line 113 emits `"action":"plan-gate-blocked"` (not `plan-gate-bypassed`). Implementation of the real `FORCE_PLAN_GATE=1` read and the bypass-event log-record shape is this plan's scope.
- **Found:** `scripts/enforcement/require-review-on-push.sh` (push-gate bypass logging at lines 149–167) — reference pattern for JSONL event emission.
- **Found:** `scripts/enforcement/install-hooks.sh` (269 lines). Already wires: pre-commit plan-gate + size guard; pre-push enforcement-env + review gate + drift guard + size guard + cadence sync; post-commit learning pipeline. This plan appends a single **post-commit observer/correlator chain** to the existing post-commit hook — it does NOT replace the learning-pipeline wiring.
- **Found:** `scripts/enforcement/compliance-dashboard.sh` — must be extended to surface `bypass_pending_review` derived from advisor output.
- **Found:** `logs/hooks/plan-gate-events.jsonl` is the existing (partial) sink for pre-commit plan-gate events. The correlator resolves those pre-commit events into `commit_sha`.
- **Found:** `tests/enforcement/` uses Python pytest (`test_compliance_dashboard.py`, `test_install_hooks_stage_prompt_drift.py`, `test_require_stage_prompt_drift.py`, `test_stage_prompt_drift_status.py`). Bash-only tests live at `scripts/enforcement/tests/` but the dominant convention is Python — new advisor tests MUST be pytest.
- **Found:** `scripts/review/cross-review.sh` + `plan-review-fanout.sh` is the cross-review infrastructure for adversarial plan review of this plan itself.

### Standards
| Standard | Status | Source |
|---|---|---|
| BYPASS-ROLLBACK policy | pending (v10 draft; MAJOR from Codex) | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` (policy file not yet in git) |
| TRUST-ARCHITECTURE rollback rules | established | `docs/governance/TRUST-ARCHITECTURE.md` (§Rollback Rules, lines 216–248 per #2289 plan) |
| HARD-STOP policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted
- `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` (v10 policy contract — 412 lines).
- `scripts/review/results/2026-04-22-plan-2289-codex-v10.md` (MAJOR — approval-binding + remediation-boundary ambiguity).
- `scripts/review/results/2026-04-22-plan-2289-gemini-v10.md` (APPROVE).
- `scripts/review/results/2026-04-21-plan-2289-codex-v{2,3,4,5,6}.md` — implementation risk catalog that seeded the 8 deferred concerns.
- `scripts/enforcement/require-plan-approval.sh`, `require-review-on-push.sh`, `install-hooks.sh`, `compliance-dashboard.sh`.
- `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` (grandparent plan).
- GitHub issues: #2445 body, #2289 body, #2018 body.

### Gaps identified
- No bash implementation of the 6-verdict taxonomy exists — `scripts/enforcement/bypass-rollback-advisor.sh` must be built from scratch.
- `--no-verify` bypass is currently undetectable in this repo — no observer exists. `scripts/enforcement/all-commits-observer.sh` is new.
- Pre-commit `plan-gate-events.jsonl` entries cannot be correlated to a `commit_sha` because the log is written **before** the commit succeeds. `scripts/enforcement/post-commit-bypass-logger.sh` is the correlator that reconciles them.
- `require-plan-approval.sh` lines 26–44 `needs_plan_approval()` computes `COMMIT_GATE_SAFE_PATHS` implicitly via grep. There is no `ADVISOR_SAFE_PATHS` function or helper. This plan introduces a shared shell library `scripts/enforcement/lib/bypass-advisor-lib.sh` to centralize safe-list predicates.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2445` — OPEN — labels: priority:medium, cat:harness, domain:workflow. Title: "Implement bypass-rollback advisor and post-commit observer per #2289 policy".
- `#2289` — OPEN — labels: priority:high, cat:harness, domain:workflow, **status:plan-review**.
- `#2018` — CLOSED — title: "feat: agent bypass resistance -- enforce workflow with technical gates, not text instructions".

**File existence** (verified 2026-04-23):
- EXISTS: `scripts/enforcement/require-plan-approval.sh`, `require-review-on-push.sh`, `install-hooks.sh`, `compliance-dashboard.sh`.
- EXISTS: `docs/governance/TRUST-ARCHITECTURE.md`, `docs/governance/SESSION-GOVERNANCE.md`.
- EXISTS: `tests/enforcement/{test_compliance_dashboard.py,test_install_hooks_stage_prompt_drift.py,test_require_stage_prompt_drift.py,test_stage_prompt_drift_status.py}`.
- MISSING (new — this plan creates): `docs/governance/BYPASS-ROLLBACK-POLICY.md` (created by #2289, not this plan).
- MISSING (new — this plan creates): `scripts/enforcement/bypass-rollback-advisor.sh`, `post-commit-bypass-logger.sh`, `all-commits-observer.sh`, `lib/bypass-advisor-lib.sh`.
- MISSING (new — this plan creates): `tests/enforcement/test_bypass_rollback_advisor.py`, `test_post_commit_bypass_logger.py`, `test_all_commits_observer.py`, `test_install_hooks_bypass_chain.py`.

**`FORCE_PLAN_GATE` grep** (verified 2026-04-23):
```
$ grep -n 'FORCE_PLAN_GATE' scripts/enforcement/require-plan-approval.sh
12:STRICT_MODE="${FORCE_PLAN_GATE_STRICT:-0}"
105:    echo "To bypass (logged): FORCE_PLAN_GATE=1 git commit"
```
Confirms: the *strict* flag is read; the *bypass* flag is only mentioned in help text. Implementation gap validated.

**Source count:** 4 enforcement scripts + 4 review artifacts + 3 GitHub issues + 1 policy plan + 4 existing test files + 1 grandparent plan = **17 distinct sources**.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2445-bypass-rollback-advisor-and-observer.md` |
| Advisor script (new) | `scripts/enforcement/bypass-rollback-advisor.sh` |
| Correlator script (new) | `scripts/enforcement/post-commit-bypass-logger.sh` |
| Observer script (new) | `scripts/enforcement/all-commits-observer.sh` |
| Shared shell lib (new) | `scripts/enforcement/lib/bypass-advisor-lib.sh` |
| Advisor tests (new) | `tests/enforcement/test_bypass_rollback_advisor.py` |
| Correlator tests (new) | `tests/enforcement/test_post_commit_bypass_logger.py` |
| Observer tests (new) | `tests/enforcement/test_all_commits_observer.py` |
| Hook-chaining tests (new) | `tests/enforcement/test_install_hooks_bypass_chain.py` |
| Plan-gate modification | `scripts/enforcement/require-plan-approval.sh` — add real `FORCE_PLAN_GATE=1` handling + content-hash digest |
| Installer modification | `scripts/enforcement/install-hooks.sh` — wire post-commit observer+correlator chain (append; preserve learning pipeline) |
| Dashboard modification | `scripts/enforcement/compliance-dashboard.sh` — add `bypass_pending_review` row from advisor output |
| AGENTS.md modification | `AGENTS.md` — upgrade `FORCE_PLAN_GATE=1` from "reserved" to "active logged-bypass env var" (only when policy lands) |
| Review — Claude | `scripts/review/results/2026-04-23-plan-2445-claude.md` |
| Review — Codex | `scripts/review/results/2026-04-23-plan-2445-codex.md` |
| Review — Gemini | `scripts/review/results/2026-04-23-plan-2445-gemini.md` |
| README index | `docs/plans/README.md` — add row (index update is **not** this worker's responsibility; integration worker updates it after approval) |

---

## Deliverable

After #2445 lands:
1. `FORCE_PLAN_GATE=1 git commit ...` is a **detectable, logged, classifiable** bypass event — no longer a silent override.
2. `git commit --no-verify` on a pre-commit-gated path is detected by the observer + correlator pipeline and classified into one of the six policy verdicts.
3. `scripts/enforcement/bypass-rollback-advisor.sh [--strict] [--offline] [--json]` evaluates every logged bypass event, emits structured JSONL audit records to `logs/hooks/bypass-rollback-proposals.jsonl`, and (under `--strict`) exits non-zero when any verdict is `revert_recommended`.
4. `scripts/enforcement/compliance-dashboard.sh` surfaces the `bypass_pending_review` count with verdict breakdown.
5. `AGENTS.md` documents `FORCE_PLAN_GATE=1` as an active, logged bypass mechanism (not reserved).

---

## Pseudocode

### `scripts/enforcement/bypass-rollback-advisor.sh`

```
parse args: --strict, --offline, --json, --since=<timestamp>
load policy: source docs/governance/BYPASS-ROLLBACK-POLICY.md constants via lib
read bypass-event sources:
  - logs/hooks/plan-gate-events.jsonl      (pre-commit advisor events)
  - logs/hooks/bypass-correlator.jsonl     (post-commit correlations)
  - logs/hooks/all-commits-observer.jsonl  (--no-verify detections)

for each bypass_event:
  derive commit_sha via correlator join-key (content_hash of staged diff)
  if sha missing: verdict = log_only_observability_gap, cause = unresolved_sha
  else:
    resolve branch_context (event-time branch if logged, else live HEAD if not detached)
    resolve pushed_state in {true, false, unknown} via git branch -r --contains
    collect terminal evidence:
      T_revert     = git log --grep 'revert "<subject>"' --format=%cI ... normalized to UTC ms
      T_remediation = later same-branch commits with explicit remediation binding (per §Remediation binding)
      T_approval   = approval marker mtime (.planning/plan-approved/NNN.md) OR
                     GitHub label API event for status:plan-approved,
                     bound to commit_sha_set that includes this sha while unreverted
    T_max = max(T_approval_bound, T_revert, T_remediation)
    if T_max is T_revert:       verdict = log_only_reverted_later
    elif T_max is T_approval:   verdict = log_only_approved_later
    elif T_max is T_remediation:verdict = log_only_remediated_later
    else if only safe-paths apply:
      verdict = log_only_safe_paths
    else:
      check commit_resolvable + pushed_state:
        if commit_resolvable and pushed_state in {true, false}:
          verdict = revert_recommended
        else:
          verdict = log_only_observability_gap (with canonical cause)
  emit JSONL record per §Audit contract of BYPASS-ROLLBACK-POLICY.md
  if --strict and verdict == revert_recommended: flag for exit-1
  if --strict and verdict == log_only_observability_gap with cause=pushed_unknown:
    exempt-from-exit-1 only if --offline explicit or probe-ls-remote confirms true absence

if any revert_recommended flagged and --strict: exit 1
else: exit 0
```

### `scripts/enforcement/post-commit-bypass-logger.sh`

```
on post-commit, HEAD is already advanced:
  resolved_sha = git rev-parse HEAD
  content_hash = git show HEAD --format=%H --patch --no-color | sha256sum
                 # NOTE: correlator uses the SAME digest that require-plan-approval.sh
                 # wrote at pre-commit time: `git diff --cached --patch --no-color | sha256sum`
                 # This hash is stable across the pre→post transition because staged diff becomes HEAD diff.
  scan logs/hooks/plan-gate-events.jsonl for the most recent event whose
    content_hash matches AND timestamp < resolved_sha's committer_date AND commit_sha is null
  if match:
    append logs/hooks/bypass-correlator.jsonl with
      {"timestamp":..., "pre_event_ref":{...}, "commit_sha":resolved_sha, "content_hash":...}
    do NOT rewrite the pre-event (preserve provenance; correlations are additive)
  if no match and HEAD's committer trailer contains the FORCE_PLAN_GATE=1 marker
     (injected by require-plan-approval.sh bypass path): emit a fresh correlation record
     with cause=direct_bypass_no_pre_event (future enum extension — out of current scope)
exit 0  (never blocks)
```

### `scripts/enforcement/all-commits-observer.sh`

```
on post-commit, runs unconditionally (chained after the correlator):
  resolved_sha   = git rev-parse HEAD
  committer_date = git log -1 --format=%cI HEAD  (normalized UTC RFC3339 ms)
  branch         = git rev-parse --abbrev-ref HEAD  (string "HEAD" => detached-HEAD tag)
  staged_paths   = git diff-tree --no-commit-id --name-only -r HEAD
  needs_approval = invoke lib::commit_gate_needs_approval on staged_paths
  advisor_safe   = invoke lib::is_advisor_safe on staged_paths (returns ADVISOR_SAFE_PATHS-only match)
  pre_event      = scan plan-gate-events.jsonl for correlated content_hash (same rule as correlator)
  append logs/hooks/all-commits-observer.jsonl:
    {"timestamp": committer_date,
     "commit_sha": resolved_sha,
     "branch": branch,              # literal "HEAD" captured when detached
     "needs_plan_approval": needs_approval,
     "pre_event_present": bool(pre_event),
     "advisor_safe": advisor_safe,
     "touched_paths": staged_paths}
# Observer does NOT classify. Advisor reads this file during evaluation.
# "blocked-then-later-committed" is detected by: plan-gate-events has matching content_hash
#   marked blocked, BUT this file has a later record with pre_event_present=false for the same
#   content_hash (user retried with --no-verify). Advisor treats this as bypass evidence for the
#   successful commit SHA, even though the original pre-commit was blocked not bypassed.
exit 0  (never blocks)
```

### `scripts/enforcement/lib/bypass-advisor-lib.sh`

```
# Centralized predicates shared by advisor + correlator + observer + tests.
COMMIT_GATE_SAFE_PATHS=('scripts/**' '.github/**' 'docs/**' 'config/**'
                        '.claude/skills/**' '.claude/hooks/**' 'tests/**' 'specs/**')
ADVISOR_SAFE_PATHS=('docs/plans/**' 'docs/reports/**' '.planning/**')
NEVER_SAFE_PATHS=('.claude/hooks/**' 'scripts/enforcement/**'
                  '.github/workflows/enforcement-gate.yml' 'docs/governance/**'
                  'docs/standards/HARD-STOP-POLICY.md'
                  'docs/standards/AI_REVIEW_ROUTING_POLICY.md'
                  'docs/standards/SUBAGENT_CONTEXT_ISOLATION.md'
                  'AGENTS.md' 'CLAUDE.md' 'GEMINI.md' '.codex/CODEX.md')

lib::is_never_safe_path   path -> 0|1
lib::is_advisor_safe      paths -> 0|1   (all paths in ADVISOR_SAFE_PATHS AND none in NEVER_SAFE_PATHS)
lib::commit_gate_needs_approval paths -> 0|1  (mirrors needs_plan_approval() semantics)
lib::content_hash_staged  (no args; reads `git diff --cached`) -> sha256
lib::content_hash_head    (no args; reads `git show HEAD --patch`) -> sha256
lib::resolve_pushed_state sha -> "true"|"false"|"unknown"
lib::probe_connectivity   remote -> "online"|"offline"|"auth_failed"
lib::detect_revert_of     sha -> revert_sha|""  (parses 'revert "<subject>"' + This reverts commit <sha>)
```

### Resolutions to the 8 deferred concerns

| # | Concern (issue body) | Design decision |
|---|---|---|
| 1 | `--no-verify` detection | Observer runs unconditionally on post-commit; advisor synthesizes "blocked-then-successful-bypass" via content_hash cross-reference between `plan-gate-events.jsonl` and `all-commits-observer.jsonl`. No confusion between blocked and bypassed: observer records the SHA that actually landed; advisor marks it as bypass only if no bound approval exists. |
| 2 | `has_approval_intent` contract | Approval evidence sources: (a) `.planning/plan-approved/NNN.md` mtime, (b) GitHub `status:plan-approved` label event timestamp. Binding requires `commit_sha` ∈ persisted `bound_commit_sha_set`. If both sources exist and agree on binding, T_approval = max(normalized timestamps). If binding is ambiguous or sources contradict, emit `log_only_observability_gap` with `verdict_cause = auth_failed` (for API-side) or drop approval candidacy (for marker ambiguity, which is a policy bug not auth bug). `gh` auth failure maps to `auth_failed`, not silent success. Marker regex: `^\.planning/plan-approved/(\d+)\.md$` with `<issue_number>` capture. |
| 3 | `pushed` tri-state | Use `lib::resolve_pushed_state`: (a) run `git branch -r --contains <sha> 2>/dev/null`; (b) if stdout non-empty, return `"true"`; (c) if stdout empty AND `git remote -v` lists the branch's configured push remote AND `git ls-remote --exit-code <remote>` succeeds, return `"false"`; (d) otherwise return `"unknown"`. Shallow clones (`.git/shallow` exists) force `"unknown"`. |
| 4 | Revert detection | `git log --grep='^Revert ' --format='%H %cI %s' <branch>` + `git log <sha>..HEAD --grep='This reverts commit <sha>' --format='%H %cI'`. Revert-of-revert handling: each revert increments a parity counter; net-odd reverts = reverted, net-even = restored. Implementation walks linearly from the bypass SHA forward; a restore (revert-of-revert) emits `log_only_observability_gap` with `verdict_cause = unresolved_sha` and likely_cause note (v11+ policy extension may introduce `log_only_revert_of_revert`). |
| 5 | Detached-HEAD observer | Observer writes literal `"HEAD"` string when `git rev-parse --abbrev-ref HEAD` returns `HEAD`. Advisor maps branch `"HEAD"` to `verdict_cause = branch_unreachable` consistent with policy §Branch context. |
| 6 | Hook chaining | Single generated `.git/hooks/post-commit` invoking observer THEN correlator THEN existing learning pipeline, each with `|| true` isolation so one failure does not block others. `install-hooks.sh` uses the same idempotent `grep -q` pattern already in place (lines 210–257). |
| 7 | Correlation key | `git diff --cached --patch --no-color \| sha256sum \| awk '{print $1}'` at pre-commit time, written into the bypass event; post-commit correlator computes `git show HEAD --patch --no-color \| sha256sum \| awk '{print $1}'` and matches. Same-digest collision is possible across unrelated commits and is handled by joining on `(content_hash, nearest-preceding-timestamp, branch)` — collision test case required. |
| 8 | `--strict` exit semantics | `exit 1` iff any verdict is `revert_recommended` OR any `log_only_observability_gap` with a cause in `{unresolved_sha, commit_unresolvable_locally}`. Offline-local-workflow exception: `log_only_observability_gap` with `cause=pushed_unknown` does NOT exit 1 when (a) `--offline` is passed explicitly, or (b) `lib::probe_connectivity` returns `"offline"` (not `"auth_failed"`). Cron/dashboard default: no `--strict`; exit 0 unconditionally. |

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/enforcement/bypass-rollback-advisor.sh` | 6-verdict classifier + audit emitter |
| Create | `scripts/enforcement/post-commit-bypass-logger.sh` | correlate pre-commit events to resolved SHA |
| Create | `scripts/enforcement/all-commits-observer.sh` | universal post-commit observer (unconditional) |
| Create | `scripts/enforcement/lib/bypass-advisor-lib.sh` | shared predicates: safe-list, content-hash, pushed-state, connectivity, revert detection |
| Create | `tests/enforcement/test_bypass_rollback_advisor.py` | 20+ pytest cases per §TDD Test List |
| Create | `tests/enforcement/test_post_commit_bypass_logger.py` | correlator unit tests |
| Create | `tests/enforcement/test_all_commits_observer.py` | observer unit tests |
| Create | `tests/enforcement/test_install_hooks_bypass_chain.py` | hook-chaining idempotence + isolation tests |
| Modify | `scripts/enforcement/require-plan-approval.sh` | add `FORCE_PLAN_GATE=1` read; change bypass log record shape to include `content_hash`, `bypass_mechanism`, and `action:plan-gate-bypassed` (new) while preserving existing `action:plan-gate-blocked` shape for blocked case |
| Modify | `scripts/enforcement/install-hooks.sh` | append observer+correlator wiring to post-commit chain using existing idempotent pattern; preserve learning pipeline |
| Modify | `scripts/enforcement/compliance-dashboard.sh` | add `bypass_pending_review` count derived from advisor output (row with verdict breakdown by canonical cause) |
| Modify | `AGENTS.md` | ONE targeted edit: change the "reserved / not yet implemented" note for `FORCE_PLAN_GATE=1` to active-bypass documentation. Gated on #2289 approval; not touched until policy lands. |

No other files are modified. `docs/plans/README.md` index-row update is out of this worker's write scope per mission instructions.

---

## TDD Test List

**All tests are authored BEFORE the implementation scripts.** Tests drive script shape.

### Advisor classification tests (scenario matrix from BYPASS-ROLLBACK-POLICY.md §Scenario matrix)

| # | Test name | Maps to policy matrix row | Expected verdict |
|---|---|---|---|
| 1 | `test_bypass_then_approval_then_revert` | bypass → approval → revert | `log_only_reverted_later` |
| 2 | `test_bypass_then_revert_then_plan_reapproval` | bypass → revert → re-approval | `log_only_reverted_later` |
| 3 | `test_bypass_then_remediation_then_approval` | bypass → remediation → approval | `log_only_approved_later` |
| 4 | `test_bypass_then_branch_deletion` | bypass → branch deleted | `log_only_observability_gap` cause=`branch_unreachable` |
| 5 | `test_bypass_in_detached_head_no_event_branch` | detached-HEAD bypass | `log_only_observability_gap` cause=`branch_unreachable` |
| 6 | `test_bypass_then_agent_reset_head` | `git reset HEAD~1` after bypass | `log_only_observability_gap` cause=`commit_unresolvable_locally` |
| 7 | `test_bypass_shallow_clone_pushed_unknown` | shallow clone advisor run | `log_only_observability_gap` cause=`pushed_unknown` |
| 8 | `test_bypass_docs_plans_only` | only `docs/plans/` touched | `log_only_safe_paths` |
| 9 | `test_bypass_claude_hooks_never_safe` | `.claude/hooks/` touched | `revert_recommended` (no safe-list override) |
| 10 | `test_bypass_unresolved_sha` | no `commit_sha` derivable | `log_only_observability_gap` cause=`unresolved_sha` |
| 11 | `test_bypass_github_label_auth_failed` | `gh` API 403 | `log_only_observability_gap` cause=`auth_failed` |
| 12 | `test_equal_timestamp_approval_vs_revert_prefers_revert` | tie-break rule | `log_only_reverted_later` |
| 13 | `test_terminal_event_survives_later_branch_deletion` | evidence known then branch deleted | terminal verdict still wins |

### Approval-binding tests (Codex v10 open concern)

| # | Test name | What it verifies |
|---|---|---|
| 14 | `test_approval_marker_mtime_binds_to_exact_sha` | approval marker binds iff `commit_sha` ∈ persisted `bound_commit_sha_set` |
| 15 | `test_approval_binding_ambiguous_two_sources_contradict` | marker says sha_A, GitHub label says sha_B → `log_only_observability_gap` |
| 16 | `test_approval_after_revert_does_not_unrevert` | approval timestamp > revert timestamp → still `log_only_reverted_later` |

### Remediation-boundary tests (Codex v10 open concern)

| # | Test name | What it verifies |
|---|---|---|
| 17 | `test_ordinary_later_commit_is_not_remediation` | later reviewed work without explicit binding → NOT `log_only_remediated_later` |
| 18 | `test_cherry_pick_on_other_branch_is_not_remediation` | cherry-pick on other branch does NOT count |
| 19 | `test_merge_based_remediation_requires_explicit_binding` | merge commit counts only with binding in merge msg or uniquely introduced ancestors |

### Offline and connectivity tests

| # | Test name | What it verifies |
|---|---|---|
| 20 | `test_strict_offline_flag_suppresses_pushed_unknown_exit_code` | `--offline` suppresses exit 1 for `pushed_unknown` only |
| 21 | `test_strict_auth_failed_does_NOT_suppress_exit_code` | `auth_failed` is NOT offline; exits 1 under `--strict` |

### Hook-chaining tests (new test file)

| # | Test name | What it verifies |
|---|---|---|
| 22 | `test_install_hooks_wires_observer_and_correlator_idempotent` | running `install-hooks.sh` twice produces identical post-commit content |
| 23 | `test_post_commit_chain_isolation_observer_failure_does_not_block_correlator` | observer exit 1 does NOT block correlator or learning pipeline |
| 24 | `test_learning_pipeline_wiring_preserved_across_install` | existing learning-pipeline wiring survives the install that adds observer+correlator |

### Correlator tests (new test file)

| # | Test name | What it verifies |
|---|---|---|
| 25 | `test_correlator_joins_pre_event_to_resolved_sha_via_content_hash` | happy-path join |
| 26 | `test_correlator_handles_same_digest_collision_via_timestamp_branch` | collision resolved by `(content_hash, timestamp, branch)` |
| 27 | `test_correlator_preserves_pre_event_provenance` | correlation is additive, not destructive |

### Observer tests (new test file)

| # | Test name | What it verifies |
|---|---|---|
| 28 | `test_observer_records_detached_head_as_literal_HEAD` | Codex v3 detached-HEAD finding |
| 29 | `test_observer_does_not_block_when_log_path_unwritable` | never blocks the commit |
| 30 | `test_observer_synthesizes_blocked_then_successful_as_bypass` | issue body concern #1 |

**Total: 30 tests** (exceeds issue-body minimum of 20+).

All tests use the repository's existing pytest conventions, `tmp_path` fixtures for git repo fixtures, and direct subprocess invocation of the shell scripts (no mocking of `git`).

---

## Acceptance Criteria

- [ ] All 30 tests exist and are RED before any advisor/correlator/observer code is written (TDD-first).
- [ ] All 30 tests pass: `uv run pytest tests/enforcement/test_bypass_rollback_advisor.py tests/enforcement/test_post_commit_bypass_logger.py tests/enforcement/test_all_commits_observer.py tests/enforcement/test_install_hooks_bypass_chain.py -v`.
- [ ] No regression: `uv run pytest tests/enforcement/ -v` passes (existing 4 test files still green).
- [ ] `scripts/enforcement/bypass-rollback-advisor.sh --help` documents `--strict`, `--offline`, `--json`, `--since`.
- [ ] `scripts/enforcement/install-hooks.sh` run twice (idempotent) against a fresh repo wires observer + correlator + learning pipeline without duplication.
- [ ] `scripts/enforcement/require-plan-approval.sh` treats `FORCE_PLAN_GATE=1 git commit` as a bypass (logs `action:plan-gate-bypassed` with `content_hash`, `bypass_mechanism:env_var`).
- [ ] `scripts/enforcement/compliance-dashboard.sh` emits a `bypass_pending_review` row with verdict breakdown derived from `logs/hooks/bypass-rollback-proposals.jsonl`.
- [ ] `AGENTS.md` `FORCE_PLAN_GATE=1` section is updated from "reserved" to active documentation (only after #2289 lands).
- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists in `main` (created by #2289) BEFORE any implementation commit in #2445 lands.
- [ ] 3-provider adversarial plan review of THIS plan returns no unresolved MAJOR.
- [ ] `status:plan-review` label applied after the last review round produces unanimous APPROVE or MINOR.
- [ ] Policy-revision absorption checkpoint: if #2289 v11+ revises `log_only_approved_later` or `log_only_remediated_later` between plan-approval and implementation, the affected tests (tests 14–19) are re-authored BEFORE the corresponding implementation code; a note is added to the plan's Adversarial Review section.

---

## Risks and Open Questions

- **Risk (sequencing):** #2289 is still MAJOR (Codex v10). If policy tightens the approval-binding contract, tests 14–16 will need revision before implementation begins. Mitigation: plan names the absorption checkpoint in Acceptance Criteria.
- **Risk (correlation key stability):** `git diff --cached` at pre-commit vs `git show HEAD --patch` at post-commit must produce identical output. Context headers and line-ending normalization are potential sources of divergence. Mitigation: `--no-color` plus `-U3` are implied by default; a guard test (test 25) exercises the exact invocation pair against a realistic commit.
- **Risk (revert-of-revert):** the linear-parity model is a v1 approximation. Net-odd-reverts → `log_only_observability_gap` with a `likely_cause` note is the conservative choice. A v11+ policy enum extension would introduce `log_only_revert_of_revert`; NOT introduced in this implementation.
- **Risk (FORCE_PLAN_GATE discoverability):** the #2289 plan explicitly moved `AGENTS.md` out of scope. This plan re-introduces the AGENTS.md edit. Mitigation: the edit is a single-section documentation update, gated on #2289 approval, and does NOT modify any enforcement behavior described in the policy. If Codex flags this as scope creep during review, the fallback is `scripts/enforcement/require-plan-approval.sh --help` only.
- **Open:** should the advisor's `--since=<timestamp>` default be `24h` (daily cron) or `7d` (weekly report)? Current stance: default unset (evaluate all events); cron wrapper passes `--since=24h`. Decision deferred to integration worker.
- **Open:** should `logs/hooks/bypass-rollback-proposals.jsonl` be rotated? Current stance: NO (size is bounded by bypass frequency; rotation is a separate ops concern).
- **Open:** should the advisor exit non-zero when the policy file is missing (fail-closed) or skip with a warning (fail-open)? Current stance: fail-closed on `--strict`, fail-open on default. Flagged for reviewer scrutiny.

---

## Adversarial Review Summary

<!-- Populated after §Step 3 review round completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | — |
| Codex | pending | — |
| Gemini | pending | — |

**Overall result:** pending

---

## Complexity: T2

**T2** — four new scripts (advisor ~180 LOC, correlator ~60 LOC, observer ~50 LOC, shared lib ~120 LOC), four new pytest files (~400 LOC total, 30 tests), four in-place modifications to enforcement infrastructure (require-plan-approval.sh, install-hooks.sh, compliance-dashboard.sh, AGENTS.md). No cross-repo changes. No new infrastructure (git hooks, logs/hooks directory, JSONL conventions already exist). Hook chaining is purely additive to the existing post-commit pattern in install-hooks.sh.
