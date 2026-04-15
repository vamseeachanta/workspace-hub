     1|# Adversarial Re-Review Request: Issue #2045
     2|
     3|You are an independent adversarial reviewer. This plan was revised again after prior MAJOR findings. Evaluate the current plan text only. Find any remaining gaps, unresolved decisions, weak retrieval, non-falsifiable tests/acceptance criteria, or workflow/governance violations. Do NOT rubber-stamp.
     4|
     5|Return verdict as one of: APPROVE, MINOR, MAJOR.
     6|
     7|Required output format:
     8|1. Verdict
     9|2. Ready for user approval: Yes/No
    10|3. Retrieval adequacy: adequate/insufficient
    11|4. Top blockers (numbered)
    12|5. Critical findings
    13|6. High findings
    14|7. Medium findings
    15|8. Low findings
    16|9. Required revisions before user approval
    17|
    18|Context:
    19|- Repository: workspace-hub
    20|- Review type: plan-stage adversarial re-review
    21|- Focus on whether the revised plan is now actually approval-ready.
    22|
    23|GitHub issue metadata:
    24|- Issue: #2045
    25|- Title: Onboard all agents to strict issue planning workflow
    26|
    27|Plan under review:
    28|
    29|```markdown
    30|     1|# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow
     2|
     3|> **Status:** draft
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-09
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
     7|> **Review artifacts:** scripts/review/results/2026-04-14-plan-2045-codex.md | scripts/review/results/2026-04-14-plan-2045-gemini.md | scripts/review/results/2026-04-15-plan-2045-claude.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` is the canonical repo skill for the workflow and must be treated as a primary onboarding surface.
    15|- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` extends the planning workflow for engineering-critical issues.
    16|- Found: `docs/plans/_template-issue-plan.md` defines the minimum plan structure and review-artifact convention.
    17|- Found: `docs/plans/README.md` is both onboarding guide and plan index and must stay aligned with live workflow state.
    18|- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` defines default multi-provider review expectations.
    19|- Found: `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` constrains how agents and subagents should be framed.
    20|- Found: `.claude/hooks/plan-approval-gate.sh` already whitelists `*/.claude/*`, so updating `.claude/skills/...` is not blocked by the plan-approval gate.
    21|
    22|### Standards
    23|- `AGENTS.md` — repo hard-gate order and mandatory workflow statement.
    24|- `docs/plans/README.md` — plan workflow contract.
    25|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
    26|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.
    27|
    28|### Documents consulted
    29|- `CLAUDE.md`
    30|- `AGENTS.md`
    31|- `GEMINI.md`
    32|- `.codex/CODEX.md`
    33|- `.codex/config.toml`
    34|- `config/agents/hermes/SOUL.md`
    35|- `docs/document-intelligence/README.md`
    36|- `docs/plans/README.md`
    37|- `docs/plans/_template-issue-plan.md`
    38|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    39|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    40|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    41|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    42|- related plans in `docs/plans/`, especially #2046 and #2047
    43|
    44|### Gaps identified
    45|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    46|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    47|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    48|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    49|
    50|### Authoritative in-repo onboarding surfaces
    51|
    52|"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.
    53|
    54|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    55||---|---|---|---|---|
    56|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    57|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
    58|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
    59|| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |
    60|
    61|### Three-real-plans workstream
    62|
    63|The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself is one of the three.** This is intentionally self-referential: #2045 proves the workflow works by being a correctly-structured instance of it.
    64|
    65|| Plan # | File | Role |
    66||---|---|---|
    67|| 1 (this plan) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Onboarding spec AND validated template instance |
    68|| 2 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Independent validated template instance |
    69|| 3 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Independent validated template instance |
    70|
    71|**Validation rule:** all three files must contain every required template section (see `_template-issue-plan.md`): status header, review-artifact line, Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (or "trivial" waiver for T1), Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review Summary, Risks and Open Questions, Complexity. The `test_issue_2045_example_plans.sh` script must check each section by explicit heading match and report per-file pass/fail.
    72|
    73|---
    74|
    75|## Artifact Map
    76|
    77|| Artifact | Path |
    78||---|---|
    79|| CLAUDE entry surface | `CLAUDE.md` |
    80|| AGENTS entry surface | `AGENTS.md` |
    81|| Gemini entry surface | `GEMINI.md` |
    82|| Codex repo config surface | `.codex/config.toml` |
    83|| Onboarding/index guide | `docs/plans/README.md` |
    84|| Planning template | `docs/plans/_template-issue-plan.md` |
    85|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    86|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    87|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    88|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    89|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    90|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
    91|
    92|---
    93|
    94|## Deliverable
    95|
    96|Updated repo onboarding surfaces, core planning skill guidance, and three validated real plan artifacts (#2045, #2046, #2047) so Claude, Codex, Gemini, and Hermes all have a discoverable in-repo path to the same strict planning workflow, review routing expectations, and template/label conventions.
    97|
    98|---
    99|
   100|## Pseudocode
   101|
   102|```text
   103|# 1. Write validation scripts first (TDD)
   104|for each of the 6 test scripts:
   105|    write script that checks the specific condition (see TDD Test List)
   106|    run it — expect failures on unmodified repo where gaps exist
   107|
   108|# 2. Fix onboarding surfaces to pass validation
   109|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   110|    if test_issue_2045_onboarding_docs.sh fails on this surface:
   111|        add/correct the AGENTS.md reference or planning workflow mention
   112|    if test_issue_2045_safe_path_assumption.sh fails on this surface:
   113|        remove the false ".claude/skills blocked" claim
   114|
   115|# 3. Validate three-plan set
   116|run test_issue_2045_example_plans.sh
   117|for each missing heading in #2045, #2046, or #2047:
   118|    add the missing template section to that plan file
   119|
   120|# 4. Validate policy alignment (validation-only surfaces)
   121|run test_issue_2045_policy_alignment.sh
   122|if contradiction found in .codex/CODEX.md or policy docs:
   123|    fix the contradiction; otherwise record no-op
   124|
   125|# 5. Confirm all 6 scripts exit 0; collect evidence artifacts
   126|```
   127|
   128|---
   129|
   130|## Files to Change
   131|
   132|### Implementation scope (onboarding surface alignment)
   133|
   134|| Action | Path | Decision rule | Reason |
   135||---|---|---|---|
   136|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   137|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   138|| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
   139|| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
   140|| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
   141|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   142|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
   143|| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   144|
   145|### Validation-only (no change unless contradiction found)
   146|
   147|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md` or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.
   148|
   149|| Action | Path | Decision rule |
   150||---|---|---|
   151|| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces |
   152|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   153|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   154|| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
   155|| Validate | Three plan files (#2045, #2046, #2047) | Checked by `test_issue_2045_example_plans.sh`; modify only if required template sections are missing |
   156|
   157|---
   158|
   159|## TDD Test List
   160|
   161|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   162||---|---|---|---|---|---|
   163|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface references the planning workflow with the required sequence | check explicit phrases for resource intelligence / plan drafting, `status:plan-review`, wait-for-user-approval, and `status:plan-approved` in each of: `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `AGENTS.md`, `config/agents/hermes/SOUL.md` | All five files contain the required workflow/gate-order markers, or the file explicitly points to `AGENTS.md` / `docs/plans/README.md` as the canonical contract in a way the script can verify | Any file lacks a verifiable onboarding path | `tests/evidence/2045-onboarding-docs.log` |
   164|| `test_issue_2045_example_plans.sh` | All three plan files exist and contain every required template section | For each of `2045`, `2046`, `2047` plan files: check `> **Status:**`, `> **Review artifacts:**`, `## Resource Intelligence Summary`, `## Artifact Map`, `## Deliverable`, `## Pseudocode`, `## Files to Change`, `## TDD Test List`, `## Acceptance Criteria`, `## Adversarial Review`, `## Risks and Open Questions`, `## Complexity` | All required headings/markers present in all 3 files | Any heading missing in any file | `tests/evidence/2045-example-plans.log` with per-file per-heading pass/fail matrix |
   165|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
   166|| `test_issue_2045_safe_path_assumption.sh` | No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | `grep -rn "blocked.*plan.*gate\|plan.*gate.*block" CLAUDE.md GEMINI.md .codex/CODEX.md docs/plans/README.md config/agents/hermes/SOUL.md .claude/skills/coordination/issue-planning-mode/SKILL.md` in context of `.claude/skills/` or `.claude/*` | Zero matches | Any match found | `tests/evidence/2045-safe-path.log` |
   167|| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
   168|| `test_issue_2045_operational_workflow.sh` | The operational workflow pieces are validated, not just static docs | use issue #2045 as the sample issue; verify via `gh issue view 2045 --json comments,labels` plus local plan file that: plan was posted to GitHub, `status:plan-review` is present, and any future `status:plan-approved` transition must occur only after explicit human approval evidence | sample workflow passes all ordering checks | missing GitHub post, label, or approval-order evidence | `tests/evidence/2045-operational-workflow.log` |
   169|
   170|### Execution
   171|
   172|```bash
   173|# Run all validation scripts; each writes its own evidence artifact
   174|bash tests/test_issue_2045_onboarding_docs.sh       | tee tests/evidence/2045-onboarding-docs.log
   175|bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
   176|bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
   177|bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
   178|bash tests/test_issue_2045_skill_alignment.sh       | tee tests/evidence/2045-skill-alignment.log
   179|bash tests/test_issue_2045_operational_workflow.sh  | tee tests/evidence/2045-operational-workflow.log
   180|```
   181|
   182|All six scripts must exit 0. Any non-zero exit blocks #2045 closure.
   183|
   184|---
   185|
   186|## Acceptance Criteria
   187|
   188|### Implementation completion (required to close #2045)
   189|
   190|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   191|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
   192|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   193|- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections, including `Pseudocode`, `Risks and Open Questions`, and `Complexity` (`test_issue_2045_example_plans.sh` exits 0).
   194|- [ ] Validation-only surfaces (policy docs, `GEMINI.md` stale references, `.codex/config.toml`) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   195|- [ ] Operational workflow validation proves issue #2045 has plan posted to GitHub, `status:plan-review` applied, and that any future `status:plan-approved` transition must require explicit human approval evidence (`test_issue_2045_operational_workflow.sh`).
   196|- [ ] All six evidence artifacts exist in `tests/evidence/` with pass/fail results.
   197|
   198|### Plan approval gate (required before implementation begins)
   199|
   200|- [ ] Three-provider adversarial review set is complete: Claude, Codex, and Gemini artifacts all exist for the current plan revision.
   201|- [ ] No unresolved MAJOR findings remain.
   202|- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract (`AGENTS.md` / `docs/plans/README.md`) in a testable way.
   203|- [ ] `.codex/CODEX.md` scope is no longer ambiguous: it is either updated in implementation scope or explicitly deferred by user-approved scope note.
   204|---
   205|
   206|## Adversarial Review History
   207|
   208|| Date | Provider | Verdict | Status |
   209||---|---|---|---|
   210|| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
   211|| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
   212|| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified: tighten Codex onboarding scope, strengthen test specificity, and make operational workflow test executable |
   213|
   214|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`
   215|
   216|**Current status:** Re-review required to confirm remaining MAJOR findings are resolved. Three-provider artifact set now exists.
   217|
   218|---
   219|
   220|## Risks and Open Questions
   221|
   222|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   223|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   224|- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
   225|- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
   226|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   227|- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.
   228|
   229|---
   230|
   231|## Complexity: T2
   232|
   233|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   234|
```
