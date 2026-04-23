# Plan for #2289: bypass rollback / recovery — policy contract for enforcement-gate bypass handling

> **Status:** draft (v8, post-v7 external review fixes applied; fresh re-review required)
> **Complexity:** T1 (policy document only)
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Follow-on (implementation):** #2445
> **Review artifacts:**
> - v1: `scripts/review/results/2026-04-21-plan-2289-{claude,gemini}.md` (MAJOR, MAJOR). Codex v1 timed out.
> - v2: `{claude,codex,gemini}-v2.md` (MINOR, MAJOR, MAJOR).
> - v3: `{claude,codex,gemini}-v3.md` (MINOR, MAJOR, MINOR).
> - v4: `{claude,codex,gemini}-v4.md` (MINOR, MAJOR, MINOR).
> - v5: `{claude,codex,gemini}-v5.md` (MINOR, MAJOR, MINOR).
> - v6: `{claude,codex,gemini}-v6.md` (MINOR, MAJOR, MINOR).
> - v7: `{claude,codex,gemini}-v7.md` (pending/next external rerun target after this v8 patch wave).

---

## Adversarial Review Summary

| Rev | Claude | Codex | Gemini | Disposition |
|---|---|---|---|---|
| v1 | MAJOR | (timed out) | MAJOR | → v2: hook split, dedup, dynamic pushed. |
| v2 | MINOR | MAJOR | MAJOR | → v3: observer, tri-state, normative approval-intent, dual safe-list. |
| v3 | MINOR | MAJOR (3H+4M) | MINOR | → v4: scope-narrow to policy-only. |
| v4 | MINOR | MAJOR (3H+3M+1L) | MINOR | → v5: precedence cascade, docs/standards removed, #2445 filed, branch context, operator interface. |
| v5 | MINOR | MAJOR (2H+3M+1L) | MINOR | → v6: timestamp-based precedence, canonical cause enum, simplified detached-HEAD, git-remote offline probe, AGENTS.md update dropped, scenario truth table. |
| v6 | MINOR | MAJOR (1H+4M) | MINOR | → v7: narrow approval-after-revert semantics, add UTC/tie-break timestamp contract, expand scenario matrix, name future docs home for `FORCE_PLAN_GATE=1`, tighten remote/offline handling. |
| v7 | (pending) | (pending) | (pending) | Re-dispatch after this revision. |

### v7 revision rationale (queue-audit + Codex v6 targeted fixes)

**Queue-audit blockers closed in v7:**
1. Added explicit canonical-plan section names expected by workflow reviews: this document now includes `## Pseudocode`, `## TDD Test List`, and `## Adversarial Review Summary` headings in addition to the policy sections.
2. Made the mechanism decision explicit: #2289 chooses an **advisor-only detection and recommendation mechanism** for bypass handling. It does **not** choose auto-revert. Operator/higher-scope execution remains out of scope and is deferred to #2445.
3. README row requirement is now explicit in both `Files to Change` and `Acceptance Criteria`; local index drift is no longer silent.

**Codex v6 (1 Major + 1 High + 4 Medium) targeted fixes:**
1. **MAJOR — approval after revert contradiction.** v7 narrows `log_only_approved_later`: later approval only counts while the bypassed SHA remains unreverted and still resolvable as the live subject under evaluation. If the SHA was already reverted, later plan approval does not override `log_only_reverted_later`; restoring the change requires a new SHA.
2. **HIGH — timestamp normalization underspecified.** v7 adds a normalization contract: every terminal-event timestamp is serialized to UTC RFC3339 with millisecond precision before comparison. Git evidence uses commit committer-date normalized to UTC; GitHub label evidence uses API event time; marker evidence uses filesystem mtime normalized to UTC.
3. **MEDIUM — scenario matrix incomplete.** v7 adds rows for `auth_failed`, same-timestamp ties, and "terminal event known, then branch becomes unreachable".
4. **MEDIUM — `terminal_event_timestamp` semantics.** v7 explicitly states nullability (`null` for timeless verdicts), normalized UTC string format, and source-type derivation.
5. **MEDIUM — documentation home for `FORCE_PLAN_GATE=1`.** v7 names the future operative home: `scripts/enforcement/require-plan-approval.sh --help` and the implementation/closeout docs added under #2445. No premature AGENTS.md change.
6. **MEDIUM — offline rule overbroad.** v7 tightens the predicate: offline exception applies only to true connectivity absence or explicit `--offline`, while auth failure maps to `auth_failed` and does not silently downgrade into offline.

**Claude v6 minor fixes also absorbed:**
- Tie-break rule defined explicitly.
- `log_only_safe_paths` wording clarified as timeless but lower precedence than any timestamped terminal state.
- Discoverability gap for `FORCE_PLAN_GATE=1` recorded in Risks and future documentation home named.

**Gemini v6 minor fix also absorbed:**
- Remote selection now uses the current branch's configured push remote when available, else `origin` if present.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` logs push-gate bypass events (lines 149–167).
- Found: `scripts/enforcement/require-plan-approval.sh` — line 105 help text claims bypass via `FORCE_PLAN_GATE=1` but script never reads that var. Implementation in #2445.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) — agent-initiated rollback; distinct scope.
- Found: `needs_plan_approval()` in `require-plan-approval.sh` lines 26–44 — referenced as `COMMIT_GATE_SAFE_PATHS`.
- Found: `docs/standards/HARD-STOP-POLICY.md`, `docs/standards/AI_REVIEW_ROUTING_POLICY.md`, `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — governance-critical; never-safe-listed in v6.

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted
- GitHub issues #2289, #2018, #2445.
- `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules.
- `docs/standards/HARD-STOP-POLICY.md`, `AI_REVIEW_ROUTING_POLICY.md`, `SUBAGENT_CONTEXT_ISOLATION.md`.
- `scripts/enforcement/` — 5 scripts.
- Adversarial reviews v1–v5 (14 artifacts).

### Gaps identified
- No written bypass-rollback policy. This plan creates `docs/governance/BYPASS-ROLLBACK-POLICY.md`.
- Fresh external review surfaced two cleanup gaps: stale embedded issue-state evidence and an over-narrow `auth_failed` enum definition. v8 closes both before the next rerun.

### Evidence (embedded verification)

**Issue statuses** (historical snapshot from 2026-04-21 drafting pass; current approval evidence comes from fresh attested review blocks, not this embedded snapshot):
- `#2289` OPEN — priority:high, cat:harness, domain:workflow.
- `#2018` CLOSED — parent/umbrella historical reference; do not treat this bullet as live state authority.
- `#2445` OPEN — cat:harness, domain:workflow, priority:medium.

**File existence (historical drafting-pass snapshot):**
- EXISTS: TRUST-ARCHITECTURE.md, require-{plan-approval,review-on-push}.sh, HARD-STOP-POLICY.md, AI_REVIEW_ROUTING_POLICY.md, SUBAGENT_CONTEXT_ISOLATION.md.
- MISSING at draft time (this plan creates): `docs/governance/BYPASS-ROLLBACK-POLICY.md`.

**Source count:** 5 repo files + 3 GitHub issues + 14 review artifacts + 3 standards docs + 1 governance doc = 26 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| TRUST-ARCHITECTURE cross-ref | `docs/governance/TRUST-ARCHITECTURE.md` — add §Rollback Rules cross-reference to new policy |
| README index | `docs/plans/README.md` |
| v6 reviews (pending) | `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v6.md` |

**AGENTS.md is no longer modified by this plan.** The `FORCE_PLAN_GATE=1` documentation lands with #2445 implementation.

---

## Deliverable

A written policy document (`docs/governance/BYPASS-ROLLBACK-POLICY.md`) that codifies:
1. Trigger conditions (evidence-based, mechanism-agnostic)
2. Verdict taxonomy with timestamp-based precedence
3. Canonical `verdict_cause` enum
4. Dual safe-list semantics
5. Enforcement-surface protection
6. Branch context definition
7. Scenario matrix for mixed-history cases
8. Precedence vs TRUST-ARCHITECTURE.md
9. Audit contract
10. Advisory boundary
11. Operator interface requirements

**Mechanism decision (explicit):** #2289 chooses an **advisor-only rollback/recovery mechanism**. The mechanism is: detect logged bypass events, classify them into the six-verdict taxonomy, emit structured audit records and strict-mode exit signals, and leave any actual revert/quarantine action to a human operator or a future higher-scope tool. This issue does **not** authorize auto-revert.

Plus a cross-reference from `TRUST-ARCHITECTURE.md` §Rollback Rules to the new policy.

---

## Pseudocode

T1 policy/documentation plan. No production script is implemented here, but the chosen mechanism is concrete enough to sketch:

1. Read bypass log events and derive `commit_sha` when possible.
2. Resolve branch context from the event-time branch if present.
3. Evaluate post-bypass terminal states in this order:
   - revert/remediation/approval evidence collection
   - timestamp normalization to UTC RFC3339 with millisecond precision
   - precedence resolution (`latest terminal state wins`, with explicit tie-break rules)
4. If no terminal state applies, evaluate `log_only_safe_paths`.
5. If commit/branch/push state cannot be resolved confidently, emit `log_only_observability_gap` with canonical `verdict_cause`.
6. Otherwise emit `revert_recommended`.
7. Write JSONL audit record and optional strict-mode non-zero exit when policy says so.

This pseudocode exists to make the selected advisor-only mechanism reviewable; implementation details remain in follow-on issue #2445.

---

## Policy: canonical `verdict_cause` enum

Referenced by §Taxonomy, §Branch context, §Precedence, §Audit contract, §Operator interface. Exactly five values:

| Value | Meaning |
|---|---|
| `unresolved_sha` | Bypass event exists but no `commit_sha` can be derived. |
| `auth_failed` | Authentication or permission failure prevented authoritative state lookup for a required evidence source (for example GitHub label lookup or push-remote reachability/auth check). |
| `pushed_unknown` | `git branch -r --contains` cannot distinguish unpushed from stale-ref state. |
| `branch_unreachable` | Event-time branch is no longer present (deleted / detached-HEAD with no event-time branch logged). |
| `commit_unresolvable_locally` | Bypass event references a SHA that exists in event history but no longer exists in the working tree (agent-initiated rollback, force-push). |

No other values are permitted. Implementation (#2445) must use this exact set.

---

## Policy: verdict taxonomy with timestamp-based precedence

When a logged bypass is evaluated against a commit SHA, exactly one of six verdicts applies. Multiple verdict conditions may match the same SHA; the precedence rule below resolves ties.

### Verdict definitions

| Verdict | Applies when |
|---|---|
| `log_only_approved_later` | Post-commit approval evidence exists at time T_approval > T_bypass **and the bypassed SHA remains unreverted and still resolvable as the live subject under evaluation**. Evidence: marker file with `^Approved by: \S+` at mtime T_approval, OR GitHub label transition to `status:plan-approved` at T_approval. If the SHA was already reverted, later plan approval does not retroactively approve that reverted SHA; a new commit is required. |
| `log_only_reverted_later` | Commit SHA has been reverted via `git revert` or equivalent at time T_revert > T_bypass. |
| `log_only_remediated_later` | A later commit on the same branch at time T_remediation > T_bypass carries review evidence for the bypassed change. |
| `log_only_safe_paths` | Commit touches only paths in `ADVISOR_SAFE_PATHS` AND no path in never-safe-listed set. (Timeless — not subject to precedence ordering.) |
| `log_only_observability_gap` | Cannot determine a confident verdict. Carries a `verdict_cause` per the canonical enum above. (Timeless.) |
| `revert_recommended` | None of the above. Bypass stands; human decision required. |

### Precedence rule: latest terminal state wins (timestamp-based)

When multiple of `approved_later`, `reverted_later`, or `remediated_later` apply to the same SHA:

1. **Normalize all candidate timestamps to UTC RFC3339 with millisecond precision before comparison.**
   - marker evidence → filesystem mtime normalized to UTC
   - GitHub label evidence → API event timestamp
   - git evidence → commit committer-date normalized to UTC
2. **Determine the max timestamp** among matching terminal-state verdicts: `T_max = max(T_approval, T_revert, T_remediation)` (considering only those that apply).
3. **Emit the verdict corresponding to T_max.** The latest corrective/approval action is the current state of the bypass.
4. **Tie-break rule:** if timestamps are exactly equal after normalization, prefer `log_only_reverted_later` > `log_only_approved_later` > `log_only_remediated_later`.

When `log_only_safe_paths` applies AND any terminal-state verdict applies, the terminal state wins. `log_only_safe_paths` has no timestamp of its own and is lower precedence than any timestamped terminal verdict. If only `log_only_safe_paths` and no terminal state, emit `log_only_safe_paths`.

When `log_only_observability_gap` applies (cannot resolve SHA, branch, or pushed state) AND no terminal-state verdict can be computed, emit `log_only_observability_gap` with the appropriate `verdict_cause`. Observability gaps do not override resolvable terminal verdicts — if we CAN see that the commit was approved or reverted despite the gap, that verdict wins.

When none of the above apply, emit `revert_recommended`.

### Rationale for timestamp-based precedence (v6 change from v5)

v5 used fixed category priority where `approved_later` always beat `reverted_later`. Codex v5 flagged this as producing wrong dispositions for "approved then reverted" cases (current state is reverted, not approved). v6's timestamp-based rule correctly represents the LATEST state of the bypass, which is operationally what advisors/operators need.

---

## Policy: scenario matrix (new v6)

Concrete mixed-history cases and their v6 verdicts:

| Scenario | Timeline | v7 verdict | Rationale |
|---|---|---|---|
| Bypass → approval → revert | T1 bypass, T2 approved, T3 reverted (T3 > T2 > T1) | `log_only_reverted_later` | Revert is latest terminal state |
| Bypass → revert → re-approval of plan | T1 bypass, T2 revert, T3 plan approved | `log_only_reverted_later` | Approval of the plan does not un-revert the original SHA; restoring the change requires a new SHA |
| Bypass → remediation → approval | T1 bypass, T2 remediation, T3 approval | `log_only_approved_later` | Approval is latest while the SHA remains unreverted |
| Bypass → branch deletion | T1 bypass, T2 branch deleted | `log_only_observability_gap` with cause `branch_unreachable` | Cannot evaluate remediation/revert without branch |
| Bypass in detached HEAD | T1 bypass made in detached HEAD, event-time branch not logged | `log_only_observability_gap` with cause `branch_unreachable` | No reliable branch; v7 does not reconstruct from reflog |
| Bypass → agent local rollback (`git reset HEAD~1`) | T1 bypass, T2 commit removed locally | `log_only_observability_gap` with cause `commit_unresolvable_locally` | Commit no longer in working tree |
| Bypass only, no post-hoc events, pushed unknown (shallow clone) | T1 bypass, advisor runs with shallow clone | `log_only_observability_gap` with cause `pushed_unknown` | Cannot confidently determine pushed state |
| Bypass only, commit touches `docs/plans/` | T1 bypass, docs/plans/ only | `log_only_safe_paths` | Safe-list exemption, no terminal event |
| Bypass only, commit touches `.claude/hooks/` | T1 bypass, never-safe path | `revert_recommended` | Never-safe path; no exemption |
| Bypass only, unresolved | T1 bypass, no commit_sha derivable | `log_only_observability_gap` with cause `unresolved_sha` | No SHA to evaluate |
| Bypass, GitHub approval check auth fails | T1 bypass, label lookup denied | `log_only_observability_gap` with cause `auth_failed` | Approval intent cannot be confidently determined |
| Equal-timestamp approval vs revert | T1 bypass, T2 approval and revert normalize to identical timestamp | `log_only_reverted_later` | Tie-break rule prefers revert over approval |
| Terminal event known, then branch becomes unreachable | T1 bypass, T2 revert/approval/remediation known, T3 branch deleted | terminal verdict from T2 still wins | Later branch disappearance does not erase already observed terminal evidence |

This matrix is normative. Implementation (#2445) tests MUST cover each row.

---

## Policy: dual safe-list semantics (unchanged from v5)

### `COMMIT_GATE_SAFE_PATHS`
- Defined in `scripts/enforcement/require-plan-approval.sh` `needs_plan_approval()` (lines 26–44).
- Governs commit-approval requirement at pre-commit time.
- Paths (glob form): `scripts/**`, `.github/**`, `docs/**`, `config/**`, `.claude/skills/**`, `.claude/hooks/**`, `tests/**`, `specs/**`.

### `ADVISOR_SAFE_PATHS`
- Defined in `docs/governance/BYPASS-ROLLBACK-POLICY.md`.
- Governs `log_only_safe_paths` verdict eligibility.
- Paths: `docs/plans/**`, `docs/reports/**`, `.planning/**`.

### Enforcement-surface paths (NEVER-safe-listed)
- `.claude/hooks/**`, `scripts/enforcement/**`, `.github/workflows/enforcement-gate.yml`, `docs/governance/**`, `docs/standards/HARD-STOP-POLICY.md`, `docs/standards/AI_REVIEW_ROUTING_POLICY.md`, `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`.

### Paths outside all three lists
- Full advisor evaluation; default rollback-eligible.

### Redundancy note (addresses Gemini v5 suggestion)

`ADVISOR_SAFE_PATHS` and the never-safe-listed set are currently disjoint. The "AND no path in never-safe-listed set" clause in the `log_only_safe_paths` definition is defense-in-depth: if a future revision expands `ADVISOR_SAFE_PATHS` without removing the expanded region from never-safe-listed, the clause prevents accidental safe-listing of governance files.

---

## Policy: branch context

"Same branch" in `log_only_remediated_later` is determined by:

1. **Event-time branch (primary):** the `branch` field recorded in the bypass event. If present and still exists in repo, "same branch" means commits reachable from that branch head.
2. **Cherry-picks:** a cherry-pick on a different branch does NOT count as remediation on the bypass's branch. Each branch tracks its own bypass state.
3. **Merge commits:** if a merge commit on the event-time branch brings in review evidence (via merge message or any ancestor reachable only through the merge), it counts as remediation.
4. **Branch deletion / detached-HEAD with no event-time branch:** emit `log_only_observability_gap` with cause `branch_unreachable`. v6 does NOT reconstruct branch identity from reflog or local history.

This is simpler than v5 — v6 does not attempt reconstruction heuristics (Codex v5 M1 finding).

---

## Policy: advisory boundary

1. Advisor emits recommendations; does NOT execute reverts.
2. Execution belongs to human operators or to a future higher-scope tool.
3. Future auto-revert extensions MUST add new verdict classes, not mutate existing ones.

---

## Policy: precedence vs TRUST-ARCHITECTURE.md §Rollback Rules

`TRUST-ARCHITECTURE.md` §Rollback Rules defines agent-initiated rollback (agent's own commit breaks tests). Distinct from bypass-initiated rollback (this policy).

Interaction:
1. Agent-initiated rollback runs first when applicable (agent + failing tests).
2. **If agent-initiated rollback removes the local commit (`git reset HEAD~1`):** advisor's bypass event references a SHA that no longer exists. Verdict: `log_only_observability_gap` with cause `commit_unresolvable_locally`. Audit record notes `likely_cause: agent_initiated_rollback_per_TRUST-ARCHITECTURE`.
3. **If agent-initiated rollback reverts a pushed commit via `git revert`:** advisor detects via revert-detection (implementation in #2445). Verdict: `log_only_reverted_later`.
4. **If agent-initiated rollback was not invoked:** advisor emits per timestamp-based taxonomy.

Both policies write audit records; neither deletes the other's trail.

---

## Policy: audit contract

For every evaluated (or unevaluable) bypass event, the advisor writes `logs/hooks/bypass-rollback-proposals.jsonl` with:
- `timestamp` — ISO-8601 UTC, millisecond precision
- `source_event_refs` — `[{log_file, line_offset}]`
- `commit_sha` — resolved SHA or `null`
- `commit_resolvable` — `true` | `false` | `unknown`
- `verdict` — one of six
- `verdict_cause` — value from canonical enum when verdict is `log_only_observability_gap`; else `null`
- `terminal_event_timestamp` — for `approved_later` / `reverted_later` / `remediated_later`, the winning event timestamp normalized to UTC RFC3339 with millisecond precision; `null` for timeless verdicts (`log_only_safe_paths`, `log_only_observability_gap`, `revert_recommended`)
- `pushed_state` — `true` | `false` | `unknown`
- `branch_context` — event-time branch, or `null` for `branch_unreachable`
- `touched_paths` — `git diff-tree` output when commit resolvable; else `null`
- `evaluation_rule_applied` — name of precedence rule that fired
- `commit_removed_pre_evaluation` — optional `true` for the agent-rollback case
- `likely_cause` — optional, traceability string

---

## Policy: trigger conditions (evidence-based)

`revert_recommended` requires ALL:
1. Bypass evidence exists for this SHA (any bypass log).
2. No higher-precedence verdict applies (per §Precedence).
3. `commit_resolvable: true`.
4. `pushed_state` in `{true, false}` (not `unknown`).

Any other combination produces one of the five `log_only_*` verdicts.

Mechanism for bypass detection (observer vs correlator vs other) is in #2445 scope.

---

## Policy: operator interface requirements

Implementation (#2445) MUST provide:
1. **Default exit 0** — structured output suitable for cron / dashboards.
2. **`--strict` flag** — exits non-zero when any verdict is `revert_recommended`.
3. **`--strict` offline exception** — `log_only_observability_gap` with cause `pushed_unknown` MUST NOT cause non-zero exit only when either (a) operator passed explicit `--offline`, or (b) true connectivity absence is established for the selected push remote.
4. **Runtime remote selection:** use the current branch's configured push remote if present; otherwise fall back to `origin` when it exists.
5. **Runtime connectivity predicate:** `git ls-remote --exit-code <selected-remote> HEAD` returning non-zero because the host is unreachable / network is absent counts as offline. Authentication failures or permission-denied responses MUST map to `auth_failed`, not offline.
6. **Structured output:** verdicts emittable as JSON for downstream tooling.

---

## TDD Test List

This is a policy-only T1 plan, so the TDD surface is specification validation rather than code execution. The follow-on implementation issue (#2445) must encode these as executable tests before any script changes land.

Required test list for #2445 implementation:

1. `test_verdict_enum_exact_values` — only the five canonical `verdict_cause` values are accepted.
2. `test_latest_terminal_state_wins` — approval/revert/remediation precedence follows normalized timestamps.
3. `test_equal_timestamp_tie_break_prefers_revert` — explicit tie handling.
4. `test_post_revert_plan_approval_does_not_override_revert` — the Codex v6 MAJOR contradiction stays closed.
5. `test_auth_failed_maps_to_observability_gap` — auth failure is not treated as offline.
6. `test_offline_exception_requires_connectivity_absence_or_flag` — true offline only.
7. `test_terminal_event_survives_later_branch_deletion` — observed terminal evidence still wins.
8. `test_detached_head_without_event_branch_is_branch_unreachable`.
9. `test_safe_paths_never_override_timestamped_terminal_state`.
10. `test_audit_record_terminal_timestamp_nullability_and_format` — `terminal_event_timestamp` is `null` for timeless verdicts, UTC RFC3339 with millisecond precision otherwise.
11. `test_readme_and_policy_paths_documented` — implementation docs mention the operative home for `FORCE_PLAN_GATE=1` help/discoverability.

These tests are part of the acceptance contract for #2445, even though they are not authored in this policy-only issue.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Codify all policy sections |
| Modify | `docs/governance/TRUST-ARCHITECTURE.md` | §Rollback Rules — add cross-reference to BYPASS-ROLLBACK-POLICY.md |
| Update | `docs/plans/README.md` | Add this plan row |

**No AGENTS.md modification** (Codex v5 concern). The future discoverability home for `FORCE_PLAN_GATE=1` is `scripts/enforcement/require-plan-approval.sh --help` plus the implementation/closeout docs shipped under #2445.

---

## Acceptance Criteria

- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists and codifies: canonical `verdict_cause` enum; timestamp-based precedence; 6-verdict taxonomy; scenario matrix (10 rows minimum); dual safe-list; enforcement-surface protection; branch context; precedence vs TRUST-ARCHITECTURE.md; audit contract; advisory boundary; operator interface requirements.
- [ ] `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules includes cross-reference to `BYPASS-ROLLBACK-POLICY.md`.
- [ ] Follow-on implementation issue #2445 exists.
- [ ] v8 adversarial review returns APPROVE or MINOR across all three providers.
- [ ] `docs/plans/README.md` index row added and synced to the live plan maturity (draft until fresh v8 review artifacts exist).

---

## Risks and Open Questions

- **Resolved (v8):** precedence semantics — timestamp-based, latest-terminal-state wins, with explicit tie-breaks.
- **Resolved (v8):** cause enum inconsistency — single canonical enum, now broad enough to cover both GitHub and push-remote auth failures.
- **Resolved (v8):** detached-HEAD unreliable reconstruction — default to observability_gap.
- **Resolved (v8):** offline detection — selected push remote + true-connectivity predicate; auth failures map to `auth_failed`.
- **Resolved (v8):** AGENTS.md skim-risk — update dropped entirely from scope; future discoverability home named.
- **Resolved (v8):** post-revert approval contradiction — later plan approval does not override a reverted SHA; restoration requires a new SHA.
- **Resolved (v8):** stale embedded issue-state evidence — #2018 snapshot corrected and explicitly marked historical.
- **Open:** whether the future #2445 implementation should materialize remote-selection logic strictly from branch config only, or allow an operator override flag for unusual multi-remote repos.
- **Open:** should the compliance dashboard's `bypass_pending_review` count include `log_only_observability_gap` verdicts? Current stance: yes, with cause-label grouping. Implementation choice in #2445.

---

## Complexity: T1

**T1** — one new policy document (~280 lines including scenario matrix), two targeted cross-references (TRUST-ARCHITECTURE.md, docs/plans/README.md). No scripts, no tests, no hooks, no AGENTS.md changes. Five rounds of adversarial review have settled the core design questions; v6 locks timestamp-based precedence and canonical enum.
