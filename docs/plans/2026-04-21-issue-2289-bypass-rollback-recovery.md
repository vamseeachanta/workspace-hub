# Plan for #2289: bypass rollback / recovery — policy contract for enforcement-gate bypass handling

> **Status:** draft (v4, scope-narrowed after v3 adversarial review)
> **Complexity:** T1 (policy document only)
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Follow-on (implementation):** TBD — to be filed at plan-approval time; covers advisor script, post-commit correlator, all-commits observer, TDD suite, and enforcement-script modifications.
> **Review artifacts:**
> - v1: `scripts/review/results/2026-04-21-plan-2289-{claude,gemini}.md` (both MAJOR). Codex v1 dispatch timed out; no artifact produced.
> - v2: `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v2.md` (Claude MINOR, Codex MAJOR, Gemini MAJOR).
> - v3: `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v3.md` (Claude MINOR, Codex MAJOR, Gemini MINOR).
> - v4: pending re-dispatch.

---

## Adversarial Review History

| Rev | Date | Claude | Codex | Gemini | Disposition |
|---|---|---|---|---|---|
| v1 | 2026-04-21 | MAJOR | (timed out) | MAJOR | Revised to v2: hook split, dedup, dynamic pushed. |
| v2 | 2026-04-21 | MINOR | MAJOR | MAJOR | Revised to v3: --no-verify observer, tri-state pushed, normative approval-intent, dual safe-list. |
| v3 | 2026-04-21 | MINOR | MAJOR (3H+4M) | MINOR | **Scope-narrowed to v4 policy-only** (see v4 rationale). |
| v4 | 2026-04-21 | (pending) | (pending) | (pending) | Re-dispatch on narrowed scope. |

### v4 revision rationale — scope narrow to policy-only

v3 achieved 2-of-3-provider MINOR verdicts, but Codex v3 surfaced three logic defects in the **advisor implementation details** (blocked-vs-bypassed event conflation in `synthesize_observer_events`; 3-way contradiction in `has_approval_intent` contract text; undefined detached-HEAD observer semantics). These defects are all in implementation scope, not policy scope. The policy parts of v3 — verdict taxonomy, dual safe-list, precedence vs TRUST-ARCHITECTURE.md, audit contract, trigger conditions — have been clean since v2.

Rather than cycle a v4 that patches implementation pseudocode while Codex iteratively finds narrower implementation defects (an anti-pattern documented in the #2045 24-rereview loop), v4 narrows #2289's scope to the **policy contract only**. Implementation moves to a distinct follow-on issue where it can get proper TDD-first treatment with a concrete test harness driving design.

**What v4 keeps:**
- The 6-verdict taxonomy (with rationale for each)
- The dual safe-list split (COMMIT_GATE_SAFE_PATHS vs ADVISOR_SAFE_PATHS)
- The enforcement-surface protection (paths that are NEVER safe-listed for advisor purposes)
- The advisor-not-auto-revert boundary decision
- The audit contract (records outlive any rollback)
- Precedence with TRUST-ARCHITECTURE.md §Rollback Rules
- The AGENTS.md update for `FORCE_PLAN_GATE=1` logged-bypass documentation

**What v4 removes:**
- Advisor script pseudocode (implementation detail)
- TDD test list (part of follow-on TDD-first implementation)
- `synthesize_observer_events`, `has_approval_intent`, `resolve_pushed_state`, `has_been_reverted_via_revert_commit` helper-function contracts (these are what Codex repeatedly found defects in; move to follow-on)
- `scripts/enforcement/bypass-rollback-advisor.sh`, `post-commit-bypass-logger.sh`, `all-commits-observer.sh` creation (follow-on)
- `tests/enforcement/test_bypass_rollback_advisor.py` (follow-on)
- Log schema detail for the new logs (follow-on specifies per its TDD)

**What v4 defers explicitly to the follow-on issue:**
- How `--no-verify` is detected (the implementation path — observer + synthesis vs alternatives)
- How `pushed` state is resolved reliably (the tri-state implementation)
- How approval-intent is determined (the normative rule's exact mechanics)
- How revert-of-revert and other revert-detection edge cases are handled
- Hook chaining mechanism in `install-hooks.sh`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` logs push-gate bypass events to `logs/hooks/review-gate-bypass.jsonl` when `SKIP_REVIEW_GATE=1` is set (lines 149–167).
- Found: `scripts/enforcement/require-plan-approval.sh` is the pre-commit gate. Its line 105 help text `"To bypass: FORCE_PLAN_GATE=1 git commit"` is currently misleading — the script never reads `$FORCE_PLAN_GATE`. The follow-on implementation issue closes this gap.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) defines agent-initiated auto-rollback for failing tests. Distinct from bypass-initiated rollback; v4 §Precedence covers the handoff.
- Found: `needs_plan_approval()` in `require-plan-approval.sh` lines 26–44 classifies commits via path-based safe-list. v4 policy clarifies this commit-gate safe-list is NOT the same as the advisor's safe-list (which must be narrower).

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted
- GitHub issue #2289 body — parent=#2018; scope per issue: "trigger conditions, mechanism comparison, audit trail requirements, correctness tests." v4 addresses the first three; tests move to follow-on.
- GitHub issue #2018 closure dependency: child must be in `status:plan-review` or later. v4 plan is the qualifying artifact.
- `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules — distinct from this scope; §Precedence explicit.
- Adversarial reviews v1/v2/v3 (9 artifacts under `scripts/review/results/`) — informed scope-narrow decision.

### Gaps identified
- No written bypass-rollback policy exists today. v4 creates `docs/governance/BYPASS-ROLLBACK-POLICY.md`.
- `AGENTS.md` does not document the intended `FORCE_PLAN_GATE=1` logged-bypass env var. v4 adds the documentation.
- Follow-on (separate issue): implementation of the advisor script, observer hook, correlator, tests, and enforcement-script modifications per this policy.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21):
- `#2289` OPEN — labels: priority:high, cat:harness, domain:workflow.
- `#2018` OPEN — labels include `status:plan-review`.

**File existence**:
- EXISTS: `docs/governance/TRUST-ARCHITECTURE.md`, `AGENTS.md`, `scripts/enforcement/require-{plan-approval,review-on-push}.sh`.
- MISSING (v4 creates): `docs/governance/BYPASS-ROLLBACK-POLICY.md`.

**Source count:** 3 repo files + 2 GitHub issues + 9 review artifacts + 2 governance docs = 16 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| AGENTS.md update | `AGENTS.md` — document `FORCE_PLAN_GATE=1` as intended logged-bypass env var (implementation in follow-on) |
| TRUST-ARCHITECTURE cross-ref | `docs/governance/TRUST-ARCHITECTURE.md` — add cross-reference to BYPASS-ROLLBACK-POLICY.md §Precedence |
| README index | `docs/plans/README.md` |
| v4 reviews (pending) | `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v4.md` |

---

## Deliverable

A written policy document (`docs/governance/BYPASS-ROLLBACK-POLICY.md`) that codifies:
1. **Trigger conditions** — when a logged bypass produces a `revert_recommended` verdict (and when it does not).
2. **Verdict taxonomy** — six dispositions with rationale.
3. **Dual safe-list semantics** — commit-gate vs advisor safe-list, and the governance consequence.
4. **Precedence** — handoff between agent-initiated rollback (TRUST-ARCHITECTURE.md) and bypass-initiated rollback (this policy).
5. **Audit contract** — records that must be written regardless of downstream action.
6. **Advisory boundary** — the policy does not authorize automatic revert on pushed state; human or higher-scope tool executes.

Plus `AGENTS.md` updated to document `FORCE_PLAN_GATE=1` as the intended logged-bypass env var (parity with push-gate `SKIP_REVIEW_GATE=1`), and a cross-reference from `TRUST-ARCHITECTURE.md` §Rollback Rules to the new policy.

---

## Policy: verdict taxonomy (to be codified in BYPASS-ROLLBACK-POLICY.md)

When a logged bypass is evaluated against a commit SHA, exactly one of the following verdicts applies:

| Verdict | When it applies | Operator action |
|---|---|---|
| `log_only_approved_later` | Explicit post-commit approval evidence exists (marker file or GitHub label transition) ordered after the bypass event. | None required — approval landed out-of-band. |
| `log_only_safe_paths` | Commit touches only `ADVISOR_SAFE_PATHS` (narrower than commit-gate safe-list). | None required — path-based exemption. |
| `log_only_remediated_later` | A later commit on the same branch carries review evidence (verdict, cross-review sign-off) for the bypassed change. | None required — remediation already landed. |
| `log_only_reverted_later` | A later commit reverts the bypassed SHA via `git revert` or equivalent. | None required — reverted. |
| `log_only_observability_gap` | Advisor cannot make a confident call due to environmental constraint (unresolved SHA, `gh` auth failure, shallow/no-remote clone). Has a `cause` sub-field (`unresolved_sha` / `auth_failed` / `pushed_unknown`). | Operator investigates cause; `--strict` exits non-zero. |
| `revert_recommended` | Commit bypassed gates, touches non-safe paths, no post-hoc approval/remediation/revert, advisor can confidently determine pushed state. | Human review; may execute `git revert` for pushed or `git reset HEAD~1` for local. |

**Rationale for a single `log_only_observability_gap` verdict (v4 consolidation):** v3 had three separate verdicts (`log_only_unresolved`, `log_only_auth_failed`, `log_only_pushed_unknown`). Claude v3 flagged this as a granularity overreach — operators look for "operator attention required" as a single semantic state. v4 collapses to one verdict with a `cause` field, resolving Claude v3 N2. The distinction is preserved in the audit record for debugging without cluttering the operator-facing verdict set.

---

## Policy: dual safe-list semantics (to be codified in BYPASS-ROLLBACK-POLICY.md)

Two distinct path-based safe-lists govern different decisions:

### COMMIT_GATE_SAFE_PATHS
- **Defined in:** `scripts/enforcement/require-plan-approval.sh` (`needs_plan_approval()` exclusion logic, lines 26–44).
- **Governs:** whether a commit requires plan-approval evidence at pre-commit time.
- **Paths:** `scripts//`, `.github/`, `docs/`, `config/`, `.claude/skills/`, `.claude/hooks/`, `tests/`, `specs/`.
- **Rationale:** these are low-risk-to-functionality paths where plan approval adds friction without proportionate governance value.

### ADVISOR_SAFE_PATHS (new, narrower)
- **Defined in:** `docs/governance/BYPASS-ROLLBACK-POLICY.md` (new policy doc).
- **Governs:** whether a bypass of a commit in these paths is verdict `log_only_safe_paths` or gets full evaluation.
- **Paths:** `docs/plans/`, `docs/reports/`, `docs/standards/`, `.planning/` ONLY.
- **Rationale:** changes to these paths are definitionally non-executable; a bypassed commit touching only these cannot harm runtime behavior.

### Enforcement-surface paths (NEVER safe-listed by advisor)
- **Explicit list:** `.claude/hooks/**`, `scripts/enforcement/**`, `.github/workflows/enforcement-gate.yml`, `docs/governance/TRUST-ARCHITECTURE.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`.
- **Governs:** commits modifying these paths are NEVER classified `log_only_safe_paths` regardless of other criteria — they receive the full advisor evaluation (remediation, revert, observability checks), and if unresolved, `revert_recommended` stands.
- **Rationale:** these are the governance infrastructure. A bypass that modifies enforcement itself is the most dangerous class of bypass; path-based exemption would create a self-weakening loop.

### Paths outside all three lists
- **Treatment:** full advisor evaluation, no path-based exemption. If bypassed and unresolved, `revert_recommended`.
- **Rationale:** default position is rollback-eligible; safe-listing requires positive justification, not absence.

This addresses Codex v3 Medium finding (dual safe-list policy edges undefined).

---

## Policy: advisory boundary (to be codified in BYPASS-ROLLBACK-POLICY.md)

1. The advisor emits recommendations; it does NOT execute reverts.
2. Execution belongs to human operators or to a future higher-scope tool that extends this policy (tracked as a separate issue at the time such tool is built).
3. Rationale: `git reset --hard` or `git revert` on main is high-blast-radius. Executing destructive rollback based on advisor logic risks compounding one error (bypass) with another (wrong revert). Explicit human-in-the-loop for execution is the governance choice.
4. Future auto-revert (if ever built) must extend this policy by adding a new verdict class (e.g., `auto_reverted_by_tool`) with its own audit contract, not by mutating existing verdicts.

---

## Policy: precedence vs TRUST-ARCHITECTURE.md §Rollback Rules (to be codified in BYPASS-ROLLBACK-POLICY.md)

`TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) defines **agent-initiated** rollback: when an agent's own commit breaks tests, the agent auto-reverts (local, unpushed) or seeks human confirmation (pushed, or multi-agent change). This is fundamentally distinct from bypass-initiated rollback (this policy), which applies when *any actor's* commit bypassed the enforcement gates.

Precedence when both apply:
1. Agent-initiated rollback runs first when the commit is the agent's own and tests fail. The agent executes `git reset HEAD~1` (for local, pushed=false) or proposes revert options for pushed commits per TRUST-ARCHITECTURE.md.
2. If agent-initiated rollback reverted the commit successfully (local), the commit no longer exists on the branch — this policy's advisor run would find nothing to evaluate for that SHA.
3. If agent-initiated rollback reverted via `git revert` on a pushed commit, this policy's advisor detects it via revert-chain analysis (implementation detail in follow-on) → verdict `log_only_reverted_later`.
4. If agent-initiated rollback was NOT invoked (agent not the author, or tests passed), this policy's advisor emits its verdict per the taxonomy.

In all cases, both policies write audit records. Neither policy deletes the other's audit trail.

---

## Policy: audit contract (to be codified in BYPASS-ROLLBACK-POLICY.md)

For every evaluated commit SHA, the advisor writes a record to `logs/hooks/bypass-rollback-proposals.jsonl` containing:
- `timestamp` (ISO-8601 UTC)
- `commit_sha` (resolved)
- `verdict` (one of the six)
- `verdict_cause` (for `log_only_observability_gap` only)
- `pushed_state` (`true` / `false` / `unknown`)
- `source_event_refs` (list of originating bypass-log entries by `{log_file, line}`)
- `touched_paths` (output of `git diff-tree --no-commit-id --name-only -r <sha>`)
- `evaluation_rule_applied` (which branch of the taxonomy fired)

Audit records outlive any downstream action. They are the canonical evidence of policy application.

---

## Policy: trigger conditions (summary)

A commit SHA produces `revert_recommended` iff ALL of the following hold:
1. At least one bypass event references the SHA (via `commit_sha` field, resolved `local_oid`, or synthesized observer-vs-gate-events delta).
2. No post-commit approval evidence exists ordered after the bypass event.
3. The commit does not touch ONLY `ADVISOR_SAFE_PATHS`.
4. No later commit on the same branch carries review evidence or reverts the SHA.
5. Pushed state is confidently determined (not `unknown`).

Any other combination produces one of the five `log_only_*` verdicts per the taxonomy.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Codify all policy sections above with full prose, examples, and cross-references |
| Modify | `AGENTS.md` | §Hard Gates or §Enforcement — document `FORCE_PLAN_GATE=1` as intended logged-bypass env var (parity with `SKIP_REVIEW_GATE=1`); implementation lands in follow-on |
| Modify | `docs/governance/TRUST-ARCHITECTURE.md` | §Rollback Rules — add cross-reference to `BYPASS-ROLLBACK-POLICY.md` §Precedence |
| Update | `docs/plans/README.md` | Add this plan row |

No script creation, no test creation, no hook wiring — those are follow-on scope.

---

## Acceptance Criteria

- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists and contains all seven policy sections (taxonomy, dual safe-list, enforcement-surface protection, advisory boundary, precedence, audit contract, trigger conditions).
- [ ] `AGENTS.md` references `FORCE_PLAN_GATE=1` with note "implemented in follow-on issue [#NNNN]."
- [ ] `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules includes a cross-reference to `BYPASS-ROLLBACK-POLICY.md` §Precedence.
- [ ] Follow-on implementation issue filed (referencing this policy by number).
- [ ] v4 adversarial review returns APPROVE or MINOR across Claude, Codex, and Gemini (no unresolved MAJOR).
- [ ] `docs/plans/README.md` index row added.

---

## Risks and Open Questions

- **Risk:** a policy-only plan produces a governance artifact without working enforcement. Mitigation: follow-on implementation issue is filed at plan-approval time; until follow-on lands, `FORCE_PLAN_GATE=1` remains documentation-only (no actual bypass path exists — commits using it today would still be blocked or passed by the existing gate logic unchanged).
- **Risk:** `AGENTS.md` documenting `FORCE_PLAN_GATE=1` before the follow-on implements it could mislead readers. Mitigation: the AGENTS.md update must include the note "implemented in follow-on issue [#NNNN]" explicitly.
- **Resolved v1/v2/v3:** scope of this plan is clarified as policy-only.
- **Resolved:** implementation-detail defects from v1/v2/v3 (synthesize_observer_events, has_approval_intent, pushed tri-state, detached HEAD, etc.) are all moved to follow-on where TDD-first implementation will surface them against running tests.
- **Open:** should the policy doc include concrete pseudocode for illustrative purposes, or stay purely prose? Current stance: illustrative pseudocode is acceptable but marked as non-normative; the follow-on's implementation is the normative contract.

---

## Complexity: T1

**T1** — one new policy document, one modification to `AGENTS.md`, one modification to `docs/governance/TRUST-ARCHITECTURE.md`, one row in `docs/plans/README.md`. No scripts, no tests, no hooks. Total ~200 lines of policy prose in `BYPASS-ROLLBACK-POLICY.md` plus a few dozen lines of modifications elsewhere. Each section above is contestable but the policy decisions are well-scoped from three rounds of adversarial review.
