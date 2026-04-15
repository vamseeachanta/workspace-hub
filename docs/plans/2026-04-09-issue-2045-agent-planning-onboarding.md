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

"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.

| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
|---|---|---|---|---|
| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
| Hermes | **None** — `config/agents/hermes/SOUL.md` is a generic system prompt with no workflow references | `AGENTS.md`, `docs/plans/README.md` | **Shared docs only.** Hermes has no dedicated surface that references the planning workflow or `AGENTS.md` | **Gap:** Hermes relies entirely on shared repo docs. If Hermes is invoked without explicit context loading, it has no gate awareness. This is the supported mechanism for Hermes today — document it explicitly rather than treating it as a defect requiring a new config file |

### Three-real-plans workstream

The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself is one of the three.** This is intentionally self-referential: #2045 proves the workflow works by being a correctly-structured instance of it.

| Plan # | File | Role |
|---|---|---|
| 1 (this plan) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Onboarding spec AND validated template instance |
| 2 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Independent validated template instance |
| 3 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Independent validated template instance |

**Validation rule:** all three files must contain every required template section (see `_template-issue-plan.md`): status header, review-artifact line, Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (or "trivial" waiver for T1), Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review Summary, Risks, Complexity. The `test_issue_2045_example_plans.sh` script must check each section by heading match and report per-file pass/fail.

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
# 1. Write validation scripts first (TDD)
for each of the 5 test scripts:
    write script that checks the specific condition (see TDD Test List)
    run it — expect failures on unmodified repo where gaps exist

# 2. Fix onboarding surfaces to pass validation
for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
    if test_issue_2045_onboarding_docs.sh fails on this surface:
        add/correct the AGENTS.md reference or planning workflow mention
    if test_issue_2045_safe_path_assumption.sh fails on this surface:
        remove the false ".claude/skills blocked" claim

# 3. Validate three-plan set
run test_issue_2045_example_plans.sh
for each missing heading in #2045, #2046, or #2047:
    add the missing template section to that plan file

# 4. Validate policy alignment (validation-only surfaces)
run test_issue_2045_policy_alignment.sh
if contradiction found in .codex/CODEX.md or policy docs:
    fix the contradiction; otherwise record no-op

# 5. Confirm all 5 scripts exit 0; collect evidence artifacts
```

---

## Files to Change

### Implementation scope (onboarding surface alignment)

| Action | Path | Decision rule | Reason |
|---|---|---|---|
| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill | Canonical skill must match canonical contract |
| Add tests | `tests/test_issue_2045_*.sh` (5 scripts) | Create all five validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |

### Validation-only (no change unless contradiction found)

Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order or workflow step that directly contradicts `AGENTS.md`**. If the file simply does not mention the planning workflow, that is not a contradiction — record "no-op, no contradiction" in the evidence log.

| Action | Path | Decision rule |
|---|---|---|
| Validate | `.codex/CODEX.md` + `.codex/config.toml` | Modify only if Required Gates section or role system_prompt contradicts `AGENTS.md` gate order |
| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
| Validate | Three plan files (#2045, #2046, #2047) | Checked by `test_issue_2045_example_plans.sh`; modify only if required template sections are missing |

---

## TDD Test List

| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
|---|---|---|---|---|---|
| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface references the planning workflow | `grep -l` for `AGENTS.md` or `issue-planning-mode` or `plan.*approval` in each of: `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `AGENTS.md` | All four files match at least one keyword | Any file returns zero matches | `tests/evidence/2045-onboarding-docs.log` |
| `test_issue_2045_example_plans.sh` | All three plan files exist and contain every required template section | For each of `2045`, `2046`, `2047` plan files: `grep -c` for headings: `## Resource Intelligence`, `## Artifact Map`, `## Deliverable`, `## Files to Change`, `## TDD Test List`, `## Acceptance Criteria`, `## Adversarial Review`, `> **Status:**`, `> **Review artifacts:**` | All 9 headings/markers present in all 3 files (27/27 checks pass) | Any heading missing in any file | `tests/evidence/2045-example-plans.log` with per-file per-heading pass/fail matrix |
| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | Extract workflow-order keywords from `AGENTS.md` (the canonical source); verify `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md` do not state a different gate order or skip a gate | No contradictions found; each file either matches or does not mention gate order | Any file states a gate order that conflicts with `AGENTS.md` | `tests/evidence/2045-policy-alignment.log` |
| `test_issue_2045_safe_path_assumption.sh` | No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | `grep -rn "blocked.*plan.*gate\|plan.*gate.*block" CLAUDE.md GEMINI.md .codex/CODEX.md docs/plans/README.md` in context of `.claude/skills/` or `.claude/*` | Zero matches | Any match found | `tests/evidence/2045-safe-path.log` |
| `test_issue_2045_hermes_documented.sh` | Hermes shared-docs-only onboarding mechanism is explicitly documented | `grep -l "shared.*docs\|shared.*surfaces\|no dedicated" docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` OR check that `config/agents/hermes/SOUL.md` now references `AGENTS.md` | Either this plan documents the shared-docs mechanism OR Hermes SOUL.md has been updated | Neither condition met | `tests/evidence/2045-hermes-documented.log` |

### Execution

```bash
# Run all validation scripts; each writes its own evidence artifact
bash tests/test_issue_2045_onboarding_docs.sh      | tee tests/evidence/2045-onboarding-docs.log
bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
bash tests/test_issue_2045_hermes_documented.sh     | tee tests/evidence/2045-hermes-documented.log
```

All five scripts must exit 0. Any non-zero exit blocks #2045 closure.

---

## Acceptance Criteria

### Implementation completion (required to close #2045)

- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `docs/plans/README.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order.
- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections (`test_issue_2045_example_plans.sh` exits 0 with 27/27 heading checks).
- [ ] Validation-only surfaces (`.codex/CODEX.md`, policy docs) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
- [ ] Hermes shared-docs-only mechanism is explicitly documented in this plan and verified by `test_issue_2045_hermes_documented.sh`.
- [ ] All five evidence artifacts exist in `tests/evidence/` with pass/fail results.

### Plan approval gate (required before implementation begins)

- [ ] Adversarial review from Codex and Gemini returns APPROVE or MINOR (no unresolved MAJOR findings).
- [ ] **Claude plan-review evidence is missing.** A Claude review artifact (`scripts/review/results/2026-04-14-plan-2045-claude.md` or equivalent) must be generated before this plan enters `status:plan-approved`. The plan is intelligible without it, but the three-provider review contract from `AI_REVIEW_ROUTING_POLICY.md` requires all three providers. If Claude review cannot be obtained, document the reason in the review summary and obtain user sign-off on the two-provider exception.

---

## Adversarial Review History

| Date | Provider | Verdict | Status |
|---|---|---|---|
| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
| — | Claude | **Missing** | No Claude review artifact exists. Required before `status:plan-approved` (see Acceptance Criteria) |

Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`

**Current status:** Re-review required to confirm MAJOR findings are resolved. Claude review still needed.

---

## Risks and Open Questions

- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
- **Risk:** Hermes shared-docs-only mechanism means Hermes gate awareness depends on the caller loading `AGENTS.md` or `docs/plans/README.md` into context. This is weaker than a dedicated entry surface but is the current supported mechanism.
- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
- **Resolved:** missing Claude review — now an explicit plan-approval-gate requirement with documented exception path.

---

## Complexity: T2

**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
