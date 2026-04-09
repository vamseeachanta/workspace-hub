# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
> **Review artifacts:** N/A — governance/onboarding task, adversarial review waived

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` — v3.0.0 stub with enforcement hooks but missing onboarding content (resource intel, adversarial review process, batch guidance)
- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` — full engineering workflow with pitfalls section
- Found: `docs/plans/_template-issue-plan.md` — comprehensive plan template (144 lines)
- Found: `docs/plans/README.md` — basic index with workflow summary but not a proper onboarding guide
- Found: `docs/standards/HARD-STOP-POLICY.md` — active hard-stop policy for engineering issues
- Found: `.claude/hooks/plan-approval-gate.sh` — PreToolUse hook blocking writes without approval marker
- Found: `scripts/enforcement/require-plan-approval.sh` — pre-commit enforcement
- Gap: `gh-work-planning` skill referenced by deprecated stub does NOT exist anywhere

### Standards
N/A — governance task, not engineering

### Documents consulted
- CLAUDE.md — references `issue-planning-mode` skill
- AGENTS.md — Hard Gate #1 references `issue-planning-mode`
- Issue #2046 compliance audit — found 0% compliance across all agents

### Gaps identified
- `issue-planning-mode` SKILL.md was a deprecated stub pointing to nonexistent `gh-work-planning`; recently updated to v3.0.0 but still missing onboarding content
- `docs/plans/README.md` was a bare index, not an onboarding guide
- CLAUDE.md and AGENTS.md referenced skill but lacked clear step-by-step workflow
- No example plans existed using the template with proper labels
- `.claude/skills/` path is NOT in the plan-approval gate safe list, requiring approval marker to edit

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` |
| CLAUDE.md update | `CLAUDE.md` |
| AGENTS.md update | `AGENTS.md` |
| README onboarding guide | `docs/plans/README.md` |
| Skill update | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |

---

## Deliverable

Updated onboarding documents and skill file so that all agents (Claude, Codex, Gemini, Hermes) can discover and follow the strict issue planning workflow, plus 3 real example plans demonstrating proper template usage.

---

## Pseudocode

```
# No code — this is a documentation/governance task
1. Update CLAUDE.md planning section: add explicit workflow steps, point to README guide
2. Update AGENTS.md Hard Gate #1: add resource intel and adversarial review steps
3. Rewrite docs/plans/README.md: transform from bare index to full onboarding guide
4. Update issue-planning-mode SKILL.md: add onboarding content, fix deprecated references
5. Create 3 example plans using template for issues #2045, #2046, #2047
6. Update README index table with new plan entries
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `CLAUDE.md` | Update planning workflow section with explicit steps |
| Modify | `AGENTS.md` | Update Hard Gate #1 with full workflow reference |
| Rewrite | `docs/plans/README.md` | Transform into comprehensive onboarding guide |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Add onboarding content, fix deprecated references |
| Create | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | This plan file |
| Create | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Example plan |
| Create | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Example plan |

---

## TDD Test List

N/A — documentation/governance task with no code changes.

Verification is manual: confirm each file exists and contains the required content.

---

## Acceptance Criteria

- [x] CLAUDE.md planning section updated with explicit workflow reference
- [x] AGENTS.md Hard Gate #1 updated with full workflow chain
- [x] docs/plans/README.md rewritten as comprehensive onboarding guide
- [ ] issue-planning-mode SKILL.md updated with onboarding content (blocked by plan-approval gate — safe path does not include .claude/skills/)
- [x] At least 3 real issue plans created using the template
- [x] docs/plans/README.md index table updated with new entries
- [ ] Committed and pushed with descriptive message referencing #2045
- [ ] Summary comment posted on issue #2045

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| N/A | WAIVED | Governance/onboarding task — no engineering code changes |

**Overall result:** WAIVED — documentation-only changes

---

## Risks and Open Questions

- **Risk:** `.claude/skills/` path is not in the plan-approval gate safe list, so editing the SKILL.md requires an approval marker. This creates a chicken-and-egg problem for governance tasks that update the planning infrastructure itself.
- **Risk:** The `gh-work-planning` skill referenced in the old deprecated stub never existed. The `engineering-issue-workflow` skill delegates planning steps to `issue-planning-mode`, creating a circular reference if `issue-planning-mode` is a stub.
- **Open:** Should `.claude/skills/` be added to the safe path list in `plan-approval-gate.sh`? Skills are configuration, not implementation.

---

## Complexity: T2

**T2** — multiple files across different directories, no code changes but significant documentation restructuring.
