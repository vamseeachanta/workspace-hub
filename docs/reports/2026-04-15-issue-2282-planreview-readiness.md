# Plan-Review Readiness Brief: Issue #2282

> Issue: Lock classification and ranking policy for weekly skills audit
> Plan: `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md`
> Date: 2026-04-15
> Status: draft (not yet plan-approved)

---

## Current-State Summary

Issue #2282 defines the policy contract that #2281's weekly skills-audit implementation will consume. The plan went through a full adversarial cross-review (Claude: MAJOR, Codex: MAJOR, Gemini: MINOR) and was subsequently revised within the same plan file. The revisions address all substantive findings raised by the three reviewers: canonical source of truth is fixed at `config/skills/weekly-audit-policy.yaml`, ambiguity routing defaults to `needs-human-review`, precedence rules are required for multi-bucket matches, carry-forward behavior (including changed-but-unresolved findings) is explicitly scoped, escalation is binary in v1, and the finding schema defines 11 required fields. The plan remains tightly bounded to policy definition only -- it does not implement the weekly audit script (that is #2281).

---

## Resolved Review Blockers

These items were flagged by reviewers and have been addressed in the latest plan revision:

1. **Canonical source of truth** (Claude, Codex) -- Fixed at `config/skills/weekly-audit-policy.yaml`; Markdown companion is explicitly subordinate.
2. **Ambiguity routing** (Claude, Codex) -- Minimum deterministic posture added: unresolvable cases fall to `needs-human-review` instead of ad hoc heuristics.
3. **Precedence rules** (Claude, Codex) -- Acceptance criteria now require explicit precedence when multiple buckets match, with mutual-exclusivity test added.
4. **Finding object schema** (Gemini) -- 11 required fields defined (`finding_key`, `classification`, `severity`, `confidence`, `canonical_names`, `paths`, `summary`, `recommended_action`, `escalation_state`, `is_new`, `is_changed`).
5. **Changed-but-unresolved carry-forward** (Claude, Codex, Gemini) -- Explicit rule: materially changed findings surface in `changed findings`, not hidden in carry-forward.
6. **Escalation idempotence** (Claude, Codex) -- Test added; binary escalation model (`no-escalation` / `candidate`) locks v1 scope.
7. **Invalid policy schema handling** (Claude, Codex) -- `test_policy_rejects_invalid_policy_schema` added to TDD list.
8. **Weekly summary sections** (Codex) -- Five minimum sections defined as a downstream consumer contract.
9. **Scope containment** (all reviewers) -- Plan explicitly defers richer taxonomy redesign and multi-tier escalation to future issues.

---

## Remaining Blockers

None identified. All substantive findings from all three reviewers have been addressed in the plan revision. The following are acknowledged risks (not blockers):

- **Fixture realism risk** (Codex, Gemini): Curated test fixtures may not cover messy real-world cases. Mitigated by the `needs-human-review` fallback and noted in the plan's risks section.
- **Prose-to-machine translation risk** (Codex): Policy could remain too prose-heavy for #2281 consumption. Mitigated by fixing the canonical source as machine-readable YAML and requiring fixture-backed tests.

---

## Recommendation

**READY_FOR_PLAN_REVIEW**

All three reviewers' substantive findings have been incorporated. The plan is tightly scoped, has a comprehensive 14-test TDD list, 12 acceptance criteria, and clear separation of concerns with its sibling issue #2281. No further revision is needed before plan-review.

---

## Approval-Ready GitHub Comment

```markdown
## Plan review: #2282 -- Ready for approval

The plan for **lock classification and ranking policy for weekly skills audit** has completed adversarial cross-review (Claude, Codex, Gemini) and all substantive findings have been addressed in the latest revision.

**Key revisions made:**
- Canonical source of truth fixed at `config/skills/weekly-audit-policy.yaml`
- Ambiguity routing defaults to `needs-human-review`
- Precedence, carry-forward, and escalation idempotence explicitly scoped
- Finding schema locked with 11 required fields
- 14 TDD tests and 12 acceptance criteria defined

**Readiness brief:** `docs/reports/2026-04-15-issue-2282-planreview-readiness.md`
**Plan:** `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md`

Requesting `status:plan-approved` to proceed with implementation.
```
