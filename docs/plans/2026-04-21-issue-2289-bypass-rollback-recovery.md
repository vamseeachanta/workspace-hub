# Plan for #2289: bypass rollback / recovery — policy contract for enforcement-gate bypass handling

> **Status:** draft (v5, post-v4-adversarial-review revision)
> **Complexity:** T1 (policy document only)
> **Date:** 2026-04-21
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2289
> **Parent:** #2018
> **Follow-on (implementation):** #2445 — advisor script, post-commit correlator, all-commits observer, TDD suite, enforcement-script modifications. Filed 2026-04-21 concurrent with this plan's v5 revision.
> **Review artifacts:**
> - v1: `scripts/review/results/2026-04-21-plan-2289-{claude,gemini}.md` (MAJOR, MAJOR). Codex v1 timed out.
> - v2: `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v2.md` (MINOR, MAJOR, MAJOR).
> - v3: `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v3.md` (MINOR, MAJOR, MINOR).
> - v4: `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v4.md` (MINOR, MAJOR, MINOR).
> - v5: pending re-dispatch.

---

## Adversarial Review History

| Rev | Date | Claude | Codex | Gemini | Disposition |
|---|---|---|---|---|---|
| v1 | 2026-04-21 | MAJOR | (timed out) | MAJOR | v2: hook split, dedup, dynamic pushed. |
| v2 | 2026-04-21 | MINOR | MAJOR | MAJOR | v3: observer, tri-state, normative approval-intent, dual safe-list. |
| v3 | 2026-04-21 | MINOR | MAJOR | MINOR | v4: scope-narrowed to policy-only. |
| v4 | 2026-04-21 | MINOR | MAJOR (3H+3M+1L) | MINOR | v5: targeted fixes (see rationale). |
| v5 | 2026-04-21 | (pending) | (pending) | (pending) | Re-dispatch after this commit. |

### v5 revision rationale

**Codex v4 (3 High + 3 Medium + 1 Low):**
1. **Taxonomy not exclusive (H1).** v5 adds explicit §Verdict precedence cascade with strict evaluation order. Ties broken deterministically.
2. **`docs/standards/` loophole (H2).** v5 removes `docs/standards/` from `ADVISOR_SAFE_PATHS` entirely. All files under `docs/standards/` are now rollback-eligible by default; governance-critical ones (`HARD-STOP-POLICY.md`, `AI_REVIEW_ROUTING_POLICY.md`) are explicitly listed in the never-safe-listed enforcement-surface set.
3. **Follow-on issue TBD (H3).** v5 references concrete issue #2445 (filed 2026-04-21). AGENTS.md framing changed per Codex M3 below.
4. **Synthesis wording leakage (M1).** v5 rephrases trigger conditions in evidence-only terms; removes "synthesized observer-vs-gate-events delta" mechanism-specific language.
5. **Commit-already-gone audit (M2).** v5 adds §Audit for commit-already-removed case.
6. **AGENTS.md framing (M3).** v5 changes AGENTS.md update to use "reserved — not yet implemented as a bypass path; see #2445" framing that cannot be mistaken for an active workflow command.
7. **Branch context for mixed history (L).** v5 adds §Branch context definition covering cherry-picks, merges, branch deletion.

**Gemini v4 (2 MINOR):**
1. **Verdict precedence** — addressed per Codex H1 above (unified fix).
2. **Path syntax inconsistency** — v5 standardizes all path specifications to `**` glob form.

**Claude v4 (2 MINOR):**
1. **Operator-interface requirements absent (N1)** — v5 adds §Operator interface requirements section defining default non-blocking exit and optional strict-mode contract.
2. **Placeholder `#NNNN` (N2)** — addressed by filing #2445.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/enforcement/require-review-on-push.sh` logs push-gate bypass events (lines 149–167).
- Found: `scripts/enforcement/require-plan-approval.sh` — line 105 help text claims `FORCE_PLAN_GATE=1` bypass but script never reads that var. Implementation in #2445.
- Found: `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules (lines 216–248) — agent-initiated rollback; distinct scope.
- Found: `needs_plan_approval()` classifier in `require-plan-approval.sh` lines 26–44. This is the `COMMIT_GATE_SAFE_PATHS` referenced below.
- Found: `docs/standards/HARD-STOP-POLICY.md`, `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — governance-critical enforcement docs. v5 classifies these as never-safe-listed.

### Standards
| Standard | Status | Source |
|---|---|---|
| Rollback policy | partial — agent-initiated defined | `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules |
| Hard-stop policy | established | `docs/standards/HARD-STOP-POLICY.md` |
| Review routing | established | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |

### Documents consulted
- GitHub issues #2289, #2018, #2445.
- `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules.
- `docs/standards/HARD-STOP-POLICY.md`, `docs/standards/AI_REVIEW_ROUTING_POLICY.md` (governance-critical files).
- `scripts/enforcement/require-{plan-approval,review-on-push}.sh`, `enforcement-env.sh`, `compliance-dashboard.sh`.
- Adversarial reviews v1–v4 (11 artifacts under `scripts/review/results/`).

### Gaps identified
- No written bypass-rollback policy exists. v5 creates `docs/governance/BYPASS-ROLLBACK-POLICY.md`.
- `AGENTS.md` lacks documentation of the reserved `FORCE_PLAN_GATE=1` env var (intended for implementation in #2445).
- Follow-on implementation: #2445.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-21):
- `#2289` OPEN — priority:high, cat:harness, domain:workflow.
- `#2018` OPEN — includes `status:plan-review`.
- `#2445` OPEN — cat:harness, domain:workflow, priority:medium. Filed concurrent with v5.

**File existence:**
- EXISTS: TRUST-ARCHITECTURE.md, AGENTS.md, require-{plan-approval,review-on-push}.sh, HARD-STOP-POLICY.md, AI_REVIEW_ROUTING_POLICY.md.
- MISSING (v5 creates): `docs/governance/BYPASS-ROLLBACK-POLICY.md`.

**Source count:** 5 repo files + 3 GitHub issues + 11 review artifacts + 3 governance/standards docs = 22 distinct sources.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-21-issue-2289-bypass-rollback-recovery.md` |
| Policy doc (new) | `docs/governance/BYPASS-ROLLBACK-POLICY.md` |
| AGENTS.md update | `AGENTS.md` — document `FORCE_PLAN_GATE=1` as **reserved — not yet implemented; implementation tracked in #2445** |
| TRUST-ARCHITECTURE cross-ref | `docs/governance/TRUST-ARCHITECTURE.md` — cross-reference to `BYPASS-ROLLBACK-POLICY.md` §Precedence |
| README index | `docs/plans/README.md` |
| v5 reviews (pending) | `scripts/review/results/2026-04-21-plan-2289-{claude,codex,gemini}-v5.md` |

---

## Deliverable

A written policy document (`docs/governance/BYPASS-ROLLBACK-POLICY.md`) that codifies:
1. Trigger conditions (evidence-based, mechanism-agnostic)
2. Verdict taxonomy with strict precedence cascade
3. Dual safe-list semantics (standardized `**` glob syntax)
4. Enforcement-surface protection (explicit list of NEVER-safe-listed files)
5. Branch context definition (cherry-picks, merges, branch deletion)
6. Precedence vs TRUST-ARCHITECTURE.md with commit-already-gone case
7. Audit contract (including commit-disappeared handling)
8. Advisory boundary (never auto-revert)
9. Operator interface requirements (default exit; strict mode contract)

Plus `AGENTS.md` updated with **reserved-not-implemented** framing for `FORCE_PLAN_GATE=1`, explicitly pointing to #2445 for implementation status.

---

## Policy: verdict taxonomy with precedence cascade

When a logged bypass is evaluated against a commit SHA, EXACTLY ONE verdict applies per the following strict precedence cascade. The first rule that matches determines the verdict; later rules are skipped:

1. **`log_only_approved_later`** — commit SHA has explicit post-commit approval evidence (marker file with approval phrase, OR GitHub label transition to `status:plan-approved` with timestamp after the bypass event). Wins over revert/remediation because explicit approval is the strongest post-hoc signal.
2. **`log_only_reverted_later`** — commit SHA has been reverted via `git revert` (or equivalent mechanism defined in #2445). Wins over remediation because revert is a stronger corrective action.
3. **`log_only_remediated_later`** — a later commit on the same branch (per §Branch context) carries review evidence for the bypassed change.
4. **`log_only_safe_paths`** — commit touches only paths within `ADVISOR_SAFE_PATHS` (per §Dual safe-list), AND none of the touched paths match the never-safe-listed set.
5. **`log_only_observability_gap`** — advisor cannot make a confident determination due to environmental constraint. Carries a `cause` sub-field: `unresolved_sha` | `auth_failed` | `pushed_unknown`.
6. **`revert_recommended`** — default when no preceding verdict applies. Bypass is advisory for human action.

**Rationale for precedence order:**
- Approval beats everything: if approval landed post-hoc, the bypass is retroactively acceptable.
- Revert beats remediation: a revert undoes the change; remediation merely reviews it.
- Remediation beats safe-paths: if review evidence landed, the safe-paths exemption is moot.
- Safe-paths beats observability-gap: path exemption is a policy decision; observability is a measurement limit.
- Observability-gap beats revert-recommended: we do not recommend destructive action under uncertainty.

---

## Policy: dual safe-list semantics (standardized glob syntax)

### `COMMIT_GATE_SAFE_PATHS` (existing)
- **Defined in:** `scripts/enforcement/require-plan-approval.sh` lines 26–44.
- **Governs:** whether a commit requires plan-approval evidence at pre-commit time.
- **Paths (converted to glob form):** `scripts/**`, `.github/**`, `docs/**`, `config/**`, `.claude/skills/**`, `.claude/hooks/**`, `tests/**`, `specs/**`.

### `ADVISOR_SAFE_PATHS` (new, narrower, v5-tightened)
- **Defined in:** `docs/governance/BYPASS-ROLLBACK-POLICY.md`.
- **Governs:** whether a bypass of a commit in these paths is verdict `log_only_safe_paths`.
- **Paths:** `docs/plans/**`, `docs/reports/**`, `.planning/**`.
- **Removed from v4's list:** `docs/standards/**` — v5 excludes this entire directory because it contains governance-critical enforcement documents.
- **Rationale:** changes to these remaining paths are definitionally non-executable and non-governance; a bypassed commit touching only these cannot harm runtime behavior or weaken enforcement.

### Enforcement-surface paths (NEVER-SAFE-LISTED, v5-expanded)
- **Explicit list:**
  - `.claude/hooks/**`
  - `scripts/enforcement/**`
  - `.github/workflows/enforcement-gate.yml`
  - `docs/governance/**`
  - `docs/standards/HARD-STOP-POLICY.md`
  - `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
  - `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
  - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`
- **Expanded from v4:** added `docs/standards/HARD-STOP-POLICY.md`, `AI_REVIEW_ROUTING_POLICY.md`, `SUBAGENT_CONTEXT_ISOLATION.md`; expanded `docs/governance/TRUST-ARCHITECTURE.md` to `docs/governance/**`.
- **Rationale:** these are the governance infrastructure. A bypass modifying enforcement itself is the most dangerous class.

### Paths outside all three lists
- **Treatment:** full advisor evaluation (safe-paths exemption does not apply). If bypassed and unresolved by higher-precedence verdicts, `revert_recommended`.
- **Rationale:** default position is rollback-eligible; safe-listing requires positive justification.

---

## Policy: branch context (new v5 — addresses Codex v4 Low)

"Same branch" in the `log_only_remediated_later` and `log_only_reverted_later` verdicts is determined by the following rules:

1. **Primary branch:** if the bypass event's `branch` field identifies a branch currently active in the repo, "same branch" means commits reachable from that branch head.
2. **Cherry-picks:** a cherry-pick commit on a different branch that carries the bypassed change does NOT count as remediation on the bypass's branch. Each branch tracks its own bypass state.
3. **Merge commits:** if a merge commit on the bypass's branch brings in review evidence (either via the merge message or via any ancestor commit reachable only through the merge), it counts as remediation.
4. **Branch deletion:** if the bypass's branch no longer exists (deleted or renamed), the advisor emits `log_only_observability_gap` with cause `branch_unreachable` rather than forcing a verdict. The bypass audit record stands.
5. **Detached HEAD bypasses:** commits made in detached-HEAD state are evaluated against the branch ref that was checked out most recently and contains the bypass SHA; if none, verdict is `log_only_observability_gap` with cause `branch_unreachable`.

---

## Policy: advisory boundary

1. The advisor emits recommendations; it does NOT execute reverts.
2. Execution belongs to human operators or to a future higher-scope tool that extends this policy (tracked as a separate issue when built).
3. Future auto-revert (if ever built) must extend this policy by adding a new verdict class with its own audit contract, not by mutating existing verdicts.

---

## Policy: precedence vs TRUST-ARCHITECTURE.md §Rollback Rules

`TRUST-ARCHITECTURE.md` §Rollback Rules defines agent-initiated rollback (agent's own commit breaks tests → auto-revert or human-confirmed). This is distinct from bypass-initiated rollback.

Precedence when both apply:
1. Agent-initiated rollback runs first when the commit is the agent's own and tests fail.
2. **If agent-initiated rollback removes the local commit (`git reset HEAD~1`) before advisor evaluation:** the bypass event still exists in bypass logs, but the referenced commit SHA no longer resolves in the working tree. The advisor emits `log_only_observability_gap` with cause `commit_unresolvable_locally`, and the audit record notes "commit_removed_pre_evaluation: true, likely_cause: agent_initiated_rollback_per_TRUST-ARCHITECTURE" for traceability. The bypass audit trail is preserved even though the advisor cannot evaluate.
3. If agent-initiated rollback reverted via `git revert` on a pushed commit, advisor's revert-detection (mechanism in #2445) finds it → verdict `log_only_reverted_later`.
4. If agent-initiated rollback was NOT invoked, advisor emits its verdict per the taxonomy.

In all cases, both policies write audit records. Neither deletes the other's audit trail.

---

## Policy: audit contract

For every evaluated (or unevaluable) bypass event, the advisor writes a record to `logs/hooks/bypass-rollback-proposals.jsonl` containing:
- `timestamp` — ISO-8601 UTC with millisecond precision
- `source_event_refs` — list of originating bypass-log entries by `{log_file, line_offset}`
- `commit_sha` — resolved SHA when available, otherwise `null`
- `commit_resolvable` — `true` | `false` | `unknown`
- `verdict` — one of the six
- `verdict_cause` — populated for `log_only_observability_gap` only
- `pushed_state` — `true` | `false` | `unknown`
- `branch_context` — branch identifier (or `null` for detached-head / deleted-branch cases)
- `touched_paths` — output of `git diff-tree --no-commit-id --name-only -r <sha>` when resolvable
- `evaluation_rule_applied` — name of the precedence-cascade rule that fired
- `commit_removed_pre_evaluation` (optional) — `true` when the commit existed at bypass-event time but not at advisor-run time
- `likely_cause` (optional) — populated alongside `commit_removed_pre_evaluation` for traceability (e.g., `agent_initiated_rollback_per_TRUST-ARCHITECTURE`)

Audit records outlive any downstream action.

---

## Policy: trigger conditions (evidence-based, mechanism-agnostic — v5)

A commit SHA produces `revert_recommended` iff ALL of the following hold:

1. **Bypass evidence exists** — at least one record in any of the bypass logs (`review-gate-bypass.jsonl`, `plan-gate-bypass.jsonl`, or future `runtime-write-bypass.jsonl`) resolves to this SHA.
2. **No higher-precedence verdict applies** — none of `log_only_approved_later`, `log_only_reverted_later`, `log_only_remediated_later`, `log_only_safe_paths`, `log_only_observability_gap` fire first per the precedence cascade.
3. **Commit is resolvable** — `commit_resolvable: true` (commit exists locally and SHA can be inspected).
4. **Pushed state is confidently determined** — `pushed_state: true` or `pushed_state: false`.

Any other combination produces one of the five `log_only_*` verdicts per the taxonomy.

The HOW of bypass detection (which log, how events are synthesized, observer vs correlator mechanisms) is in #2445's implementation scope, not this policy.

---

## Policy: operator interface requirements (new v5 — addresses Claude v4 N1)

The implementation (#2445) MUST provide:
1. **Default non-blocking exit:** advisor defaults to exit 0 with structured output, suitable for nightly cron and dashboard surfaces.
2. **Optional strict mode:** advisor MUST support a `--strict` flag (or equivalent) that causes non-zero exit when any verdict of `revert_recommended` is present.
3. **Strict-mode offline exception:** `log_only_observability_gap` verdicts with cause `pushed_unknown` MUST NOT cause non-zero exit if the repo has no remote configured or the user is offline. This prevents breaking local-only workflows (Gemini v3 finding).
4. **Structured output:** verdict records must be emittable in JSON form for downstream tooling.

The policy does not constrain implementation choices (shell vs Python, single-invocation vs daemon); only the operator-facing contract.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/governance/BYPASS-ROLLBACK-POLICY.md` | Codify all policy sections above |
| Modify | `AGENTS.md` | Add §Enforcement subsection entry: `FORCE_PLAN_GATE=1` — **reserved, not yet implemented**; implementation tracked in #2445. Do NOT attempt to use as a bypass today. |
| Modify | `docs/governance/TRUST-ARCHITECTURE.md` | Add cross-reference to `BYPASS-ROLLBACK-POLICY.md` §Precedence in §Rollback Rules. |
| Update | `docs/plans/README.md` | Add this plan's row |

No script creation, no test creation, no hook wiring — #2445 scope.

---

## Acceptance Criteria

- [ ] `docs/governance/BYPASS-ROLLBACK-POLICY.md` exists and contains all 9 policy sections (taxonomy with precedence, dual safe-list, enforcement-surface, branch context, advisory boundary, precedence vs TRUST-ARCHITECTURE, audit contract, trigger conditions, operator-interface requirements).
- [ ] `AGENTS.md` references `FORCE_PLAN_GATE=1` with the exact text "**reserved — not yet implemented; implementation tracked in #2445**" (or equivalent no-false-affordance phrasing).
- [ ] `docs/governance/TRUST-ARCHITECTURE.md` §Rollback Rules includes a cross-reference to `BYPASS-ROLLBACK-POLICY.md` §Precedence.
- [ ] Follow-on implementation issue #2445 exists and is reachable (verified 2026-04-21).
- [ ] v5 adversarial review returns APPROVE or MINOR across all three providers.
- [ ] `docs/plans/README.md` index row added.

---

## Risks and Open Questions

- **Resolved (v5):** `AGENTS.md` misleading framing — now explicit "reserved — not yet implemented" per Codex v4 M3.
- **Resolved (v5):** verdict taxonomy exclusivity — precedence cascade added.
- **Resolved (v5):** governance-doc loophole — `docs/standards/` removed from `ADVISOR_SAFE_PATHS`; governance-critical standards files explicitly never-safe-listed.
- **Resolved (v5):** `#NNNN` placeholder — replaced by concrete `#2445`.
- **Resolved (v5):** branch context undefined — new §Branch context section.
- **Resolved (v5):** commit-already-gone audit — new §Audit contract fields (`commit_removed_pre_evaluation`, `likely_cause`).
- **Open:** should the policy itself include concrete example pseudocode for illustrative purposes, or stay purely prose? Current stance: pure prose; the implementation (#2445) defines the normative pseudocode there.
- **Open:** under what conditions should the compliance dashboard's `bypass_pending_review` count include `log_only_observability_gap` verdicts? Current stance: yes, include with cause label — operator attention required. Implementation choice in #2445.

---

## Complexity: T1

**T1** — one new policy document (`BYPASS-ROLLBACK-POLICY.md` ~250 lines), plus targeted modifications to `AGENTS.md`, `TRUST-ARCHITECTURE.md`, and `docs/plans/README.md`. No scripts, no tests, no hooks. Each policy section is contestable on its own terms; four rounds of adversarial review have settled the core design questions.
