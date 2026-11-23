---
name: writing-plans
description: Turn a scoped objective into an implementation plan with affected files, dependencies, acceptance criteria and verification. Use the canonical issue template and shared lifecycle authority.
license: MIT
metadata:
  version: 1.3.0
  author: Hermes Agent (adapted from obra/superpowers)
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Authority and scope

Resolve repository-relative paths from the explicit owning checkout, not an
installed adapter directory. Use `docs/plans/_template-issue-plan.md` and
`.claude/skills/coordination/issue-planning-mode/SKILL.md` for issue plans.
`config/agents/SHARED_SOUL.md` owns lifecycle, authorization and review requirements;
this skill supplies planning technique, not another approval gate or plan format.

Read the issue, relevant implementation, tests and prior decisions before drafting.
Identify completed scope so the plan does not repeat existing work. Reproduce an
alleged runtime defect with a bounded check; record evidence and unresolved context.

## Plan content

- State the outcome, scope, owner and observable acceptance criteria.
- Name exact files to change, dependencies, assumptions and relevant source evidence.
- Break work into independently verifiable steps where useful; keep ordered steps
  when correctness depends on order. Do not impose a universal task duration.
- Describe test cases before implementation, expected results and affected regression
  checks. Include precise commands and prerequisites when they materially reduce ambiguity.
- Include pseudocode for nontrivial logic. Complete speculative implementations are
  unnecessary when interfaces, constraints and acceptance tests establish the design.
- State material risks, rollback and what would require scope reassessment.
- Describe proposed work in future tense; distinguish baseline evidence from deliverables.

## Review and handoff

Use the shared lifecycle for proportional adversarial review and authorization.
Proceed within independently established authority for unchanged routine scope;
verify matching plan/action approval for substantial or consequential work.
A saved plan or review verdict does not grant execution authority. Do not request
approval again merely because the plan was saved or an unchanged phase ended.

Choose sequential or parallel execution from task dependencies and resource
ownership. Related skills are optional techniques, not mandatory per-step agent
spawns. Handoff should identify the current plan revision, remaining work,
verification evidence and applicable authorization boundary.
