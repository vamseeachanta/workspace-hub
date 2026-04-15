# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
> **Review artifacts:** scripts/review/results/2026-04-14-plan-2045-codex.md | scripts/review/results/2026-04-14-plan-2045-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` is the canonical repo skill for the workflow and must be treated as a primary onboarding surface.
- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` extends the planning workflow for engineering-critical issues.
- Found: `docs/plans/_template-issue-plan.md` defines the minimum plan structure and review-artifact convention.
- Found: `docs/plans/README.md` is both onboarding guide and plan index and must stay aligned with live workflow state.
- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` defines default multi-provider review expectations.
- Found: `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` constrains how agents and subagents should be framed.
- Found: `.claude/hooks/plan-approval-gate.sh` already whitelists `*/.claude/*`, so updating `.claude/skills/...` is not blocked by the plan-approval gate.

### Standards
- `AGENTS.md` — repo hard-gate order and mandatory workflow statement.
- `docs/plans/README.md` — plan workflow contract.
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.

### Documents consulted
- `CLAUDE.md`
- `AGENTS.md`
- `docs/document-intelligence/README.md`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`
- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
- related plans in `docs/plans/`, especially #2046 and #2047

### Gaps identified
- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.

### Authoritative in-repo onboarding surfaces
| Agent | Authoritative in-repo onboarding surface(s) for this issue | Notes |
|---|---|---|
| Claude Code | `CLAUDE.md`, `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Claude has both repo-global and Claude-scoped onboarding surfaces |
| Gemini | `GEMINI.md`, `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Gemini-specific entry doc exists in-repo |
| Codex | `AGENTS.md`, `docs/plans/README.md`, `.codex/config.toml`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Codex-specific repo config exists, but shared repo docs remain primary workflow carrier |
| Hermes | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Hermes currently relies on shared repo onboarding surfaces rather than a dedicated in-repo Hermes config file |

### Three-real-plans workstream
- Real plan #1: `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md`
- Real plan #2: `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md`
- Real plan #3: `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md`
- This issue must explicitly validate that all three exist, use the template structure, and reflect the expected status/review sections.

---

## Artifact Map

| Artifact | Path |
|---|---|
| CLAUDE entry surface | `CLAUDE.md` |
| AGENTS entry surface | `AGENTS.md` |
| Gemini entry surface | `GEMINI.md` |
| Codex repo config surface | `.codex/config.toml` |
| Onboarding/index guide | `docs/plans/README.md` |
| Planning template | `docs/plans/_template-issue-plan.md` |
| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |

---

## Deliverable

Updated repo onboarding surfaces, core planning skill guidance, and three validated real plan artifacts (#2045, #2046, #2047) so Claude, Codex, Gemini, and Hermes all have a discoverable in-repo path to the same strict planning workflow, review routing expectations, and template/label conventions.

---

## Pseudocode

```text
identify every in-repo onboarding surface that claims to guide agents
for each surface:
    verify whether it points to the same planning workflow, review routing, and label/template rules
rewrite stale or incomplete surfaces so they converge on one workflow
verify that #2045, #2046, and #2047 together satisfy the three-real-plans acceptance criterion and demonstrate template usage, review-artifact convention, and correct status/label semantics
update docs/plans README/index so onboarding guide and plan queue stay aligned
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `CLAUDE.md` | keep onboarding/reference path aligned |
| Modify | `AGENTS.md` | keep hard-gate statement aligned |
| Modify | `GEMINI.md` | keep Gemini onboarding/reference path aligned |
| Validate or modify when contradiction is found | `.codex/config.toml` | edit only if Codex repo config contradicts the shared workflow guidance |
| Modify | `docs/plans/README.md` | keep onboarding guide/index aligned |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | keep canonical skill guidance aligned |
| Modify if policy text actually diverges | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | only update when onboarding guidance and routing policy disagree |
| Modify if policy text actually diverges | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | only update when onboarding guidance and isolation policy disagree |
| Validate real plan | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | counts as real example plan #1 |
| Validate example | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | example plan correctness |
| Validate example | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | example plan correctness |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_issue_2045_onboarding_docs.sh` | CLAUDE.md, AGENTS.md, README, and issue-planning-mode all reference the same workflow keywords | repo docs | shell test passes |
| `test_issue_2045_example_plans.sh` | #2045, #2046, and #2047 plan files exist and include template/status/review sections | three plan files | shell test passes |
| `test_issue_2045_policy_alignment.sh` | onboarding docs do not contradict review-routing or subagent-isolation policy docs | docs/policy fixtures | shell test passes |
| `test_issue_2045_safe_path_assumption.sh` | no remaining text claims `.claude/*` is blocked by the plan gate | hook + plan fixtures | shell test passes |

Validation command surface:
- `bash tests/test_issue_2045_onboarding_docs.sh`
- `bash tests/test_issue_2045_example_plans.sh`
- `bash tests/test_issue_2045_policy_alignment.sh`
- `bash tests/test_issue_2045_safe_path_assumption.sh`

Exact section/label checks for the three-plan validation set:
- `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` must contain status header, review-artifact line, Resource Intelligence Summary, Artifact Map, Pseudocode, Files to Change, TDD Test List, Acceptance Criteria, and Adversarial Review Summary.
- `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` must contain the same required template sections.
- `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` must contain the same required template sections.
- For all three example plans, validation must explicitly record whether the plan body reflects `status:plan-review` / `status:plan-approved` semantics and review-artifact conventions correctly.

Decision rules for validation-only vs modification:
- Update `docs/standards/AI_REVIEW_ROUTING_POLICY.md` only if onboarding wording contradicts the current policy text.
- Update `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` only if onboarding wording contradicts the current isolation policy text.
- Update `.codex/config.toml` only if it contains repo-facing workflow guidance that conflicts with the shared planning workflow.
- Otherwise record a validation-only/no-op result in the evidence bundle.

Evidence artifacts expected from validation:
- command output logs showing pass/fail for each onboarding-surface script
- explicit pass/fail note for the #2045/#2046/#2047 three-plan validation set
- explicit pass/fail note for label/status section checks inside the three example plans

---

## Acceptance Criteria

- [ ] CLAUDE.md and AGENTS.md explicitly reference the issue-planning workflow and its required order.
- [ ] `docs/plans/README.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` point to the same planning and review-routing expectations.
- [ ] `GEMINI.md` and `.codex/config.toml` are either aligned to the shared workflow guidance or explicitly documented as validation-only/no-op surfaces with recorded evidence.
- [ ] The false claim that `.claude/skills/` is blocked by the plan gate is removed everywhere in this issue's governed onboarding surfaces.
- [ ] Three real plans — #2045, #2046, and #2047 — are validated as template-using examples with correct status/review sections, satisfying the issue's 3-plan requirement.
- [ ] Validation records exactly which label/status/review sections were checked on #2045, #2046, and #2047.
- [ ] Executable validation commands/scripts are named for onboarding-surface consistency, policy alignment, and example-plan checks.
- [ ] Claude, Codex, and Gemini plan-review evidence is recorded before the plan returns for user approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Codex | MAJOR | Plan self-approved, waived review, weak validation, incomplete “all agents” scope |
| Gemini | MAJOR | Plan violates its own universal-review goal, carries false safe-path blocker assumptions, and misses baseline retrieval |

**Overall result:** MAJOR — not approval-ready

---

## Risks and Open Questions

- **Risk:** “all agents” can become an empty claim unless the in-repo onboarding surfaces are explicitly enumerated.
- **Risk:** example plans can teach the wrong workflow if they are not validated against the current template and review/status conventions.
- **Open:** if additional provider-specific entry files are later introduced, they must be added to the authoritative onboarding-surface table before this issue can be considered a stable long-term reference.

---

## Complexity: T2

**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
