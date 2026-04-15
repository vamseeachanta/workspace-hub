# Plan for #2018: agent bypass resistance -- enforce workflow with technical gates, not text instructions

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2018
> **Review artifacts:** scripts/review/results/2026-04-14-plan-2018-codex.md | scripts/review/results/2026-04-14-plan-2018-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/plan-approval-gate.sh` is the runtime write gate and currently permits several bypass-sensitive environment variables and broad safe-path exemptions.
- Found: `scripts/enforcement/require-plan-approval.sh` is the pre-commit gate and currently excludes multiple control-plane paths from implementation detection.
- Found: `scripts/enforcement/require-review-on-push.sh` is the push/review gate and must remain in the effective fail-fast chain.
- Found: `.claude/hooks/cross-review-gate.sh` is a separate review-enforcement surface that this parent plan must account for instead of treating review as push-only.
- Found: `.github/workflows/enforcement-gate.yml` is the CI/PR enforcement surface and is required retrieval for any claim of end-to-end bypass resistance.
- Found: `scripts/enforcement/compliance-dashboard.sh` already exists as an advisory compliance surface; this plan must explicitly decide whether dashboarding remains advisory or becomes a stronger control signal.
- Found: `tests/work-queue/test_session_governor.py` already covers parts of runtime and review-gate behavior but does not, by itself, prove full bypass resistance.
- Found: issue comments and related governance issues show the repo already has landed enforcement slices, but the parent issue still lacks a clean bypass matrix and closure criteria.

### Standards
- `docs/standards/HARD-STOP-POLICY.md` — hard-stop sequencing and no-implementation-before-approval policy.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — default three-agent adversarial review expectations.
- `docs/plans/README.md` — planning workflow contract and required review/approval ordering.
- `AGENTS.md` — repo hard-gate order and TDD-first expectation.

### Documents consulted
- GitHub issue #2018 — required control set, acceptance criteria, and governance intent.
- GitHub issue #1839 — umbrella governance/enforcement context this issue must preserve.
- `.claude/hooks/plan-approval-gate.sh`
- `scripts/enforcement/require-plan-approval.sh`
- `scripts/enforcement/require-review-on-push.sh`
- `.claude/hooks/cross-review-gate.sh`
- `.github/workflows/enforcement-gate.yml`
- `scripts/enforcement/compliance-dashboard.sh`
- `docs/governance/TRUST-ARCHITECTURE.md`
- `docs/standards/HARD-STOP-POLICY.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `tests/work-queue/test_session_governor.py`

### Gaps identified
- No single plan artifact currently maps each live enforcement surface to known bypasses, desired end state, owner issue, and required tests.
- Current plan review evidence shows unresolved scope around rollback and agent bootstrap/prefill validation.
- Existing tests are not yet a true bypass-resistance suite across runtime hook, commit, push, CI, and agent surfaces.
- Sibling issue boundaries are not yet explicit enough to prevent #2018 from being closed by documentation alone.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-13-issue-2018-agent-bypass-resistance-technical-gates.md` |
| Runtime plan gate | `.claude/hooks/plan-approval-gate.sh` |
| Commit gate | `scripts/enforcement/require-plan-approval.sh` |
| Push/review gate | `scripts/enforcement/require-review-on-push.sh` |
| Cross-review hook | `.claude/hooks/cross-review-gate.sh` |
| CI gate | `.github/workflows/enforcement-gate.yml` |
| Compliance dashboard | `scripts/enforcement/compliance-dashboard.sh` |
| Existing governance tests | `tests/work-queue/test_session_governor.py` |
| Planned new/expanded tests | `tests/enforcement/` or `tests/work-queue/` |
| Trust contract | `docs/governance/TRUST-ARCHITECTURE.md` |
| Planning index update | `docs/plans/README.md` |

---

## Implementation Decision: Rollback Handling

**Decision:** Rollback is **out of scope** for #2018 and is delegated to a mandatory child issue.

**Rationale:** #2018's scope is detection and prevention of bypasses. Rollback (reverting changes that were committed despite bypass) is a distinct recovery mechanism requiring its own design (selective revert vs. full reset, audit-trail preservation, multi-file atomicity). Bundling it here would dilute the gate-hardening focus and delay approval.

**Mandatory child issue:** Create `#NNNN — Bypass rollback: automated or guided revert of changes that bypassed enforcement gates` before #2018 enters `status:plan-approved`. The child issue must define: (1) rollback trigger conditions, (2) rollback mechanism, (3) audit trail requirements, (4) tests proving rollback correctness.

**Closure dependency:** #2018 **cannot close** until the rollback child issue is created, assigned an owner, and has at minimum a plan in `status:plan-review`. The child issue need not be *implemented* before #2018 closes, but it must exist and be tracked. This prevents rollback from being silently dropped.

---

## Provider Bootstrap Surface Inventory

Each agent provider has a repo-local entry surface that shapes its initial context. For bypass resistance, each surface must carry or reference the gate order from `AGENTS.md`.

| Provider | Entry surface | Current constraint content | Gap |
|---|---|---|---|
| Claude | `CLAUDE.md` (root) | Planning workflow mandatory, skill loading, plan template/guide references, issue-planning-mode skill | References `AGENTS.md` for canonical gates — indirect but functional |
| Gemini | `GEMINI.md` (root) | Retrieval-first, references `AGENTS.md` for canonical contract, cross-review command, gate evidence anchored to `AGENTS.md` + governance docs | References `AGENTS.md` — indirect but functional |
| Codex | `.codex/CODEX.md` + `.codex/config.toml` | `CODEX.md` has explicit Required Gates section (plan+approval, cross-review, TDD, legal scan). `config.toml` has `roles.default` system_prompt with TDD reference and `.claude/rules/` reference | Most explicit gate wording of any provider adapter |
| Hermes | `config/agents/hermes/SOUL.md` | Generic Nous Research system prompt only. No repo-specific workflow constraints, no gate references, no link to `AGENTS.md` | **Gap:** Hermes has no enforcement surface. If Hermes is used for implementation, it has zero gate awareness |
| All (canonical) | `AGENTS.md` (root) | Hard Gates section: Issue → Plan → USER APPROVES → Implement → Cross-review → Close. TDD mandatory. | Authoritative source; per-provider adapters must reference or replicate |

**Implementation requirement:** The Hermes gap must be closed by either (a) adding gate/workflow references to `config/agents/hermes/SOUL.md`, or (b) documenting that Hermes is not authorized for implementation tasks and therefore does not require gate enforcement. The test `test_agent_bootstrap_surfaces_receive_constraints` must verify whichever decision is made.

---

## Workflow Scope: CI/PR vs Direct-Push

This repo uses two commit-to-main paths with different enforcement surfaces:

| Path | Enforcement chain | Responsibility |
|---|---|---|
| **Direct push to main** | pre-commit gate → pre-push gate → cross-review hook (local) | Local hooks are the only defense. All three must fire and must not be silently skippable. |
| **PR to main** | pre-commit gate → push to branch → CI enforcement gate (3 jobs: stage-prompt-drift, review-evidence, plan-approval) + compliance dashboard (advisory) | CI provides a second layer. The compliance dashboard job runs with `continue-on-error: true` — it is advisory, not blocking. |

**Key implications for #2018:**
- Direct-push path has no CI backstop. Local hook hardening is the primary bypass-resistance investment for this path.
- CI `compliance-dashboard` job is advisory (`continue-on-error: true`). This plan explicitly keeps it advisory; promoting it to blocking is a separate decision outside #2018 scope.
- `SKIP_REVIEW_GATE=1` env var is documented in the CI step summary as a local bypass. This env var must be covered by `test_env_var_bypass_behavior_is_explicit`.

---

## Deliverable

Harden the enforcement surfaces listed in the bypass matrix so that each surface either blocks the identified weakness or explicitly delegates it to a named child issue. Deliver functional tests proving each hardened surface rejects the documented bypass vector. Update `AGENTS.md`-derived provider adapters where gaps exist (specifically Hermes).

## Bypass Matrix

| Surface | Current control | Known bypass / weakness | Target state | Owner | Proof / test |
|---|---|---|---|---|---|
| Runtime write gate | `.claude/hooks/plan-approval-gate.sh` | env-var bypasses and broad safe paths can weaken runtime enforcement | runtime semantics narrowed and tested | #2018 | `test_runtime_write_blocked_without_marker` |
| Pre-commit gate | `scripts/enforcement/require-plan-approval.sh` | broad exclusions can miss behavior-changing control-plane files | implementation classification narrowed or justified | #2018 | `test_precommit_blocks_unapproved_implementation_change` |
| Pre-push gate | `scripts/enforcement/require-review-on-push.sh` | broken chain ordering or stale inline block can preserve weak review defaults | push gate remains in fail-fast chain with preserved stdin/ref data | #2018 / related hook work | `test_prepush_blocks_missing_review_evidence` |
| Cross-review hook | `.claude/hooks/cross-review-gate.sh` | local review enforcement can drift from push/CI expectations | review semantics aligned with push and CI | #2018 | `test_cross_review_hook_behavior` |
| CI / PR gate | `.github/workflows/enforcement-gate.yml` | CI/local parity drift | CI rejects same missing-plan/missing-review states as local gates | #2018 | `test_ci_gate_rejects_missing_plan_or_review` |
| Approval-state signaling | GitHub labels + `.planning/plan-approved/` | stale markers, stale labels, self-approval spoofing | stale-state drift surfaced and spoofing rejected | #2018 + #2129 | `test_self_approved_marker_spoofing_rejected` |
| Env-var bypasses | hook / script env variables | advisory/skip flags can silently disable controls | every env var has explicit scope, precedence, and logging/test coverage | #2018 | `test_env_var_bypass_behavior_is_explicit` |
| Safe-path abuse | hook safe-path exemptions | control-plane paths can be used to mutate enforcement behavior without approval | safe-path policy narrowed or explicitly justified | #2018 | `test_control_plane_safe_path_cannot_mask_bypass` |
| Manual git/manual shell path | direct git/manual execution | manual operator path may bypass expected workflow sequence | explicit classification and tested behavior | #2018 | `test_manual_git_manual_shell_path` |
| Agent bootstrap surfaces | `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md` + `.codex/config.toml`, `config/agents/hermes/SOUL.md`, `AGENTS.md` (canonical) | Claude/Gemini reference `AGENTS.md` indirectly; Codex has explicit gates in `CODEX.md`; **Hermes `SOUL.md` has zero gate/workflow references** | every provider adapter either contains or references the `AGENTS.md` gate order; Hermes gap closed or Hermes excluded from implementation | #2018 | `test_agent_bootstrap_surfaces_receive_constraints` |
| Rollback | none — no automated rollback mechanism exists | bypassed changes persist after detection with no recovery path | **out of scope for #2018**; delegated to mandatory child issue `#NNNN` (see Implementation Decision above). Child must be created before #2018 enters `status:plan-approved`. #2018 cannot close until child exists and is in `status:plan-review` or later. | child issue `#NNNN` (owner TBD at creation) | `test_rollback_child_issue_exists` (plan-level gate: verify child issue is created and tracked) |

## Sibling / Boundary Table

| Issue | Relationship to #2018 | Boundary | Closure dependency |
|---|---|---|---|
| #1839 | umbrella governance/enforcement context | #2018 must preserve umbrella intent and report residual bypasses, not redefine umbrella scope | None — #2018 contributes to #1839 but does not block on it |
| #1876 | related implementation-detail/testing stream | #2018 owns parent bypass-resistance closure criteria; #1876 may own narrower implementation slices | None — #1876 slices are independent; #2018 closes on its own bypass matrix |
| #2012 | compliance backlog / measurement context | #2018 consumes compliance signals but does not replace backlog reporting | None — advisory input only |
| #2045 | onboarding workflow adoption | #2018 assumes onboarding exists but does not replace onboarding scope | None — no cross-dependency |
| #2046 | compliance audit | #2018 consumes audit outputs but does not replace the audit plan itself | None — advisory input only |
| #2047 | escalation follow-on | if controls remain weak, escalation is linked rather than silently absorbed | None — #2047 is downstream of #2018 findings |
| `#NNNN` (rollback child) | mandatory child issue for bypass rollback | #2018 owns detection/prevention; child owns recovery/revert | **Blocking:** child must exist and reach `status:plan-review` before #2018 can close |

---

## Files to Change

### Implementation scope (gate hardening + tests)

| Action | Path | Reason |
|---|---|---|
| Harden | `.claude/hooks/plan-approval-gate.sh` | narrow env-var bypasses and safe-path exemptions |
| Harden | `scripts/enforcement/require-plan-approval.sh` | narrow exclusion list to reject control-plane mutations without approval |
| Harden | `scripts/enforcement/require-review-on-push.sh` | preserve fail-fast chain, ensure stdin/ref data flows correctly |
| Harden | `.claude/hooks/cross-review-gate.sh` | align review semantics with push and CI expectations |
| Verify/align | `.github/workflows/enforcement-gate.yml` | confirm CI rejects same states as local gates; no code change unless parity gap found |
| Clarify role | `scripts/enforcement/compliance-dashboard.sh` | confirm advisory-only role; no promotion to blocking within #2018 |
| Close gap | `config/agents/hermes/SOUL.md` | add `AGENTS.md` gate references or document Hermes as non-implementation provider |
| Add tests | `tests/enforcement/` (new directory) | functional bypass-resistance test suite per TDD list below |

### Out of implementation scope (plan-only or conditional)

| Action | Path | Reason |
|---|---|---|
| Update (if needed) | `docs/governance/TRUST-ARCHITECTURE.md` | only if runtime semantics change during hardening |
| No change expected | `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md` | already reference `AGENTS.md` gates; verify only, change only if verification fails |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_runtime_write_blocked_without_marker` | runtime write gate blocks non-safe implementation writes without approval | write attempt fixture | blocked |
| `test_control_plane_safe_path_cannot_mask_bypass` | control-plane path exemptions cannot be abused to bypass enforcement intent | path fixture touching exempt/control-plane paths | explicit allowed/blocked result |
| `test_precommit_blocks_unapproved_implementation_change` | strict pre-commit gate blocks qualifying changes without approval evidence | staged change fixture | commit blocked |
| `test_prepush_blocks_missing_review_evidence` | push gate blocks missing review evidence | push fixture | push blocked |
| `test_ci_gate_rejects_missing_plan_or_review` | PR/CI gate enforces same invariants as local gates | CI fixture | CI failure |
| `test_env_var_bypass_behavior_is_explicit` | env-var bypasses are either rejected or explicitly scoped/logged | env-var matrix | deterministic behavior |
| `test_self_approved_marker_spoofing_rejected` | stale/self-approved marker spoofing does not satisfy gate | spoofed marker fixture | rejected |
| `test_manual_git_manual_shell_path` | a `git commit` run outside the hook chain (e.g., `--no-verify`) or a direct `bash scripts/enforcement/*.sh` invocation produces a detectable signal (non-zero exit or logged warning) rather than silently succeeding | fixture: staged impl change + `git commit --no-verify`; fixture: direct script call without expected env | commit succeeds but compliance dashboard detects missing hook evidence; direct script call exits non-zero or logs explicit skip |
| `test_agent_bootstrap_surfaces_receive_constraints` | each provider entry surface (`CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `config/agents/hermes/SOUL.md`) either contains the string `AGENTS.md` or contains the literal gate-order keywords (`plan`, `approval`, `TDD`) | fixture: read each file, grep for gate references | all four surfaces pass; if Hermes is excluded from implementation, a documented exclusion marker is present instead |
| `test_cross_review_hook_behavior` | `.claude/hooks/cross-review-gate.sh` blocks a write when review evidence is missing, and passes when evidence exists, matching the same acceptance criteria as `require-review-on-push.sh` | fixture: simulated hook invocation with/without review marker file | blocked without marker; passed with marker; exit codes match push gate equivalents |
| `test_compliance_dashboard_reports_real_enforcement_signals` | `scripts/enforcement/compliance-dashboard.sh` output includes gate-outcome fields (plan-approval rate, review-evidence rate) derived from actual commit/push history, not hardcoded | fixture: a repo with known commit history (N approved, M unapproved) | dashboard output percentages match expected N/(N+M) within tolerance; output includes at minimum: compliance rate, verdict |
| `test_rollback_child_issue_exists` | plan-level gate: the rollback child issue number is recorded in this plan and the issue exists on GitHub with status `status:plan-review` or later | fixture: parse this plan file for child issue reference; query GitHub API | child issue exists and has required label; if not, test fails with actionable message |

---

## Acceptance Criteria

### Implementation completion (required to close #2018)

- [ ] Every bypass matrix row owned by #2018 has a passing test in `tests/enforcement/`.
- [ ] `.claude/hooks/plan-approval-gate.sh` env-var bypasses are narrowed and tested (`test_env_var_bypass_behavior_is_explicit`).
- [ ] `scripts/enforcement/require-plan-approval.sh` exclusion list is narrowed or each exclusion is justified in a code comment (`test_precommit_blocks_unapproved_implementation_change`).
- [ ] Cross-review hook and push gate produce equivalent pass/fail for the same review-evidence state (`test_cross_review_hook_behavior`).
- [ ] CI enforcement gate rejects the same missing-plan/missing-review states as local gates (`test_ci_gate_rejects_missing_plan_or_review`).
- [ ] Hermes bootstrap gap is closed: either `config/agents/hermes/SOUL.md` references `AGENTS.md` gates, or Hermes is documented as non-implementation provider (`test_agent_bootstrap_surfaces_receive_constraints`).
- [ ] Rollback child issue exists on GitHub and is in `status:plan-review` or later (`test_rollback_child_issue_exists`).

### Plan approval gate (required before implementation begins)

- [ ] Bypass matrix covers all 11 surfaces listed above.
- [ ] Rollback child issue is created and linked in this plan (placeholder `#NNNN` replaced with real issue number).
- [ ] Adversarial review returns APPROVE or MINOR (no unresolved MAJOR findings).

---

## Adversarial Review History

| Date | Provider | Verdict | Status |
|---|---|---|---|
| 2026-04-14 | Codex | MAJOR | Addressed in current revision: bypass matrix added, live retrieval done, rollback delegated to child issue |
| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: provider bootstrap concrete, CI scope explicit, functional TDD expanded |

Full review artifacts: `scripts/review/results/2026-04-14-plan-2018-codex.md`, `scripts/review/results/2026-04-14-plan-2018-gemini.md`

**Current status:** Re-review required to confirm MAJOR findings are resolved.

---

## Risks and Open Questions

- **Risk:** CI/local parity can drift silently. Mitigation: `test_ci_gate_rejects_missing_plan_or_review` must be kept in sync with local gate logic; consider a shared test fixture.
- **Risk:** broad safe-path or env-var exceptions can leave nominally “strict” enforcement advisory in practice. Mitigation: each exception must be justified in code comments and covered by `test_control_plane_safe_path_cannot_mask_bypass` / `test_env_var_bypass_behavior_is_explicit`.
- **Risk:** Hermes bootstrap gap means any Hermes-driven implementation session has zero gate awareness today. Mitigation: closing this gap is in implementation scope for #2018.
- **Resolved:** rollback ownership — delegated to mandatory child issue with explicit closure dependency (see Implementation Decision above).
- **Resolved:** provider bootstrap concreteness — actual file inventory and gap analysis now in Provider Bootstrap Surface Inventory above.

---

## Complexity: T3

**T3** — cross-surface enforcement/governance plan spanning runtime hooks, git gates, CI, compliance measurement, and multi-agent bootstrap behavior.
