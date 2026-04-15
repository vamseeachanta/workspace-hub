# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
> **Review artifacts:** scripts/review/results/2026-04-14-plan-2045-codex.md | scripts/review/results/2026-04-14-plan-2045-gemini.md | scripts/review/results/2026-04-15-plan-2045-claude.md

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
- `GEMINI.md`
- `.codex/CODEX.md`
- `.codex/config.toml`
- `config/agents/hermes/SOUL.md`
- `docs/plans/README.md`
- `docs/plans/_template-issue-plan.md`
- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
- GitHub labels `status:plan-review` and `status:plan-approved` (authoritative live workflow labels)
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
| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |

### Three-real-plans workstream

The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself is one of the three.** This is intentionally self-referential: #2045 proves the workflow works by being a correctly-structured instance of it.

| Plan # | File | Role |
|---|---|---|
| 1 (this plan) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Onboarding spec AND validated template instance |
| 2 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Independent validated template instance |
| 3 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Independent validated template instance |

**Validation rule:** all three files must contain one exact required heading set (see `_template-issue-plan.md` plus this plan's normalization rule): status header, review-artifact line, Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (or "trivial" waiver for T1), Files to Change, TDD Test List, Acceptance Criteria, `## Adversarial Review History`, Risks and Open Questions, Complexity. The `test_issue_2045_example_plans.sh` script must check that exact heading set by explicit heading match and report per-file pass/fail.

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
for each of the 6 test scripts:
    write script that checks the specific condition (see TDD Test List)
    run it — expect failures on unmodified repo where gaps exist

# 2. Fix onboarding surfaces to pass validation
for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, .codex/CODEX.md, config/agents/hermes/SOUL.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
    if test_issue_2045_onboarding_docs.sh fails on this surface:
        either add direct workflow markers OR add an explicit canonical-contract reference that the test accepts
    if test_issue_2045_safe_path_assumption.sh fails on this surface:
        remove the false ".claude/skills blocked" claim

# 3. Validate three-plan set
run test_issue_2045_example_plans.sh
for each missing normalized heading in #2045, #2046, or #2047:
    add the missing section to that plan file

# 4. Validate policy alignment and skill alignment
run test_issue_2045_policy_alignment.sh
run test_issue_2045_skill_alignment.sh
if contradiction found in .codex/CODEX.md, .codex/config.toml, GEMINI.md, or policy docs:
    fix the contradiction; otherwise record no-op

# 5. Validate operational GitHub workflow using issue #2045 as the fixed sample
run test_issue_2045_operational_workflow.sh
verify: plan comment exists, status:plan-review label exists, and no status:plan-approved label is treated as valid without explicit human approval evidence

# 6. Confirm all 6 scripts exit 0; collect evidence artifacts
```

---

## Files to Change

### Implementation scope (onboarding surface alignment)

| Action | Path | Decision rule | Reason |
|---|---|---|---|
| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |

### Validation-only (no change unless contradiction found)

Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md` or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.

| Action | Path | Decision rule |
|---|---|---|
| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces |
| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
| Validate | Three plan files (#2045, #2046, #2047) | Checked by `test_issue_2045_example_plans.sh`; modify only if required template sections are missing |

---

## TDD Test List

| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
|---|---|---|---|---|---|
| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface has a deterministic, testable planning-workflow discovery path | define exact accepted patterns per file: `AGENTS.md` must contain the full gate order; `CLAUDE.md` / `GEMINI.md` / `.codex/CODEX.md` / `config/agents/hermes/SOUL.md` must either contain direct workflow markers (`status:plan-review`, `status:plan-approved`, `wait for explicit user approval`) or an explicit canonical reference line naming `AGENTS.md` and/or `docs/plans/README.md` as the source of truth | Each file matches one of its allowed exact patterns | Any file matches neither the direct-marker pattern nor the allowed canonical-reference pattern | `tests/evidence/2045-onboarding-docs.log` |
| `test_issue_2045_example_plans.sh` | All three plan files exist and contain the normalized required section set with issue-specific content | For each of `2045`, `2046`, `2047` plan files: check `> **Status:**`, `> **Review artifacts:**`, `## Resource Intelligence Summary`, `## Artifact Map`, `## Deliverable`, `## Pseudocode`, `## Files to Change`, `## TDD Test List`, `## Acceptance Criteria`, `## Adversarial Review History`, `## Risks and Open Questions`, `## Complexity`; also verify issue-specific file naming and that placeholder template strings like `#NNN`, `YYYY-MM-DD`, or `<repo>` are absent | All required headings/markers present in all 3 files and no template placeholders remain | Any heading missing or any placeholder/template stub remains | `tests/evidence/2045-example-plans.log` with per-file heading + placeholder pass/fail matrix |
| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
| `test_issue_2045_safe_path_assumption.sh` | No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | `grep -rn "blocked.*plan.*gate\|plan.*gate.*block" CLAUDE.md GEMINI.md .codex/CODEX.md docs/plans/README.md config/agents/hermes/SOUL.md .claude/skills/coordination/issue-planning-mode/SKILL.md` in context of `.claude/skills/` or `.claude/*` | Zero matches | Any match found | `tests/evidence/2045-safe-path.log` |
| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
| `test_issue_2045_operational_workflow.sh` | The operational GitHub workflow is validated against present, authoritative evidence | use issue #2045 as the fixed sample; require authenticated `gh`; verify via `gh issue view 2045 --json comments,labels` plus the local plan file that: (a) a plan comment exists referencing the plan artifact path, (b) `status:plan-review` label is present now, and (c) no `status:plan-approved` label is treated as valid approval evidence without a separate explicit human-approval comment/marker convention defined in repo policy | sample workflow passes all current-state checks; auth/tooling failures are reported separately as environment failures, not workflow failures | missing plan comment, missing label, or approval-state interpreted without explicit approval convention | `tests/evidence/2045-operational-workflow.log` |

### Execution

```bash
# Run all validation scripts; each writes its own evidence artifact
bash tests/test_issue_2045_onboarding_docs.sh       | tee tests/evidence/2045-onboarding-docs.log
bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
bash tests/test_issue_2045_skill_alignment.sh       | tee tests/evidence/2045-skill-alignment.log
bash tests/test_issue_2045_operational_workflow.sh  | tee tests/evidence/2045-operational-workflow.log
```

All six scripts must exit 0. Any non-zero exit blocks #2045 closure.

---

## Acceptance Criteria

### Implementation completion (required to close #2045)

- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections, including `Pseudocode`, `Risks and Open Questions`, and `Complexity` (`test_issue_2045_example_plans.sh` exits 0).
- [ ] Validation-only surfaces (policy docs, `GEMINI.md` stale references, `.codex/config.toml`) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
- [ ] Operational workflow validation proves issue #2045 has plan posted to GitHub, `status:plan-review` applied, and that any future `status:plan-approved` transition must require explicit human approval evidence (`test_issue_2045_operational_workflow.sh`).
- [ ] All six evidence artifacts exist in `tests/evidence/` with pass/fail results.

### Plan approval gate (required before implementation begins)

- [ ] Three-provider adversarial review set is complete: Claude, Codex, and Gemini artifacts all exist for the current plan revision.
- [ ] No unresolved MAJOR findings remain.
- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract (`AGENTS.md` / `docs/plans/README.md`) in a testable way.
- [ ] `.codex/CODEX.md` scope is no longer ambiguous: it is either updated in implementation scope or explicitly deferred by user-approved scope note.
---

## Adversarial Review History

| Date | Provider | Verdict | Status |
|---|---|---|---|
| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified: tighten Codex onboarding scope, strengthen test specificity, and make operational workflow test executable |

Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`

**Current status:** Re-review required to confirm remaining MAJOR findings are resolved. Three-provider artifact set now exists.

---

## Risks and Open Questions

- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.

---

## Complexity: T2

**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
