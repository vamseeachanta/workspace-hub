     1|# Adversarial Claude Plan Review Request: Issue #2045
     2|
     3|You are an independent adversarial reviewer. Evaluate the current plan text only. Do not rubber-stamp. Find any remaining weak retrieval, non-falsifiable tests, governance contradictions, or scope gaps.
     4|
     5|Return exactly this structure:
     6|1. Verdict
     7|2. Ready for user approval: Yes/No
     8|3. Retrieval adequacy: adequate/insufficient
     9|4. Top blockers (numbered)
    10|5. Critical findings
    11|6. High findings
    12|7. Medium findings
    13|8. Low findings
    14|9. Required revisions before user approval
    15|
    16|Repository: workspace-hub
    17|Issue: #2045
    18|Issue title: Onboard all agents to strict issue planning workflow
    19|Issue URL: https://github.com/vamseeachanta/workspace-hub/issues/2045
    20|
    21|GitHub issue body:
    22|The new strict planning workflow is now formalized in-repo and must be adopted consistently by all agents for all issues.
    23|
    24|Scope:
    25|- Load and use `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    26|- Copy `docs/plans/_template-issue-plan.md` for every new issue plan
    27|- Run resource intelligence before drafting
    28|- Include artifact map + pseudocode in every plan
    29|- Run adversarial plan review with Claude, Codex, and Gemini before user review
    30|- Post plan to GitHub and apply `status:plan-review`
    31|- Wait for explicit user approval before implementation
    32|- Mark approved issues `status:plan-approved`
    33|
    34|Artifacts already in place:
    35|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    36|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    37|- `docs/plans/README.md`
    38|- `docs/plans/_template-issue-plan.md`
    39|
    40|Acceptance criteria:
    41|- Agent onboarding docs explicitly reference the planning workflow
    42|- New issues created/handled by agents follow the new workflow
    43|- At least 3 real issue plans are created using the template and labels
    44|
    45|Plan under review:
    46|
    47|```markdown
    48|     1|# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow
     2|
     3|> **Status:** draft
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-09
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
     7|> **Review artifacts:** scripts/review/results/2026-04-14-plan-2045-codex.md | scripts/review/results/2026-04-14-plan-2045-gemini.md
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
    31|- `docs/document-intelligence/README.md`
    32|- `docs/plans/README.md`
    33|- `docs/plans/_template-issue-plan.md`
    34|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    35|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    36|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    37|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    38|- related plans in `docs/plans/`, especially #2046 and #2047
    39|
    40|### Gaps identified
    41|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    42|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    43|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    44|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    45|
    46|### Authoritative in-repo onboarding surfaces
    47|
    48|"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.
    49|
    50|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    51||---|---|---|---|---|
    52|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    53|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
    54|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
    55|| Hermes | **None** — `config/agents/hermes/SOUL.md` is a generic system prompt with no workflow references | `AGENTS.md`, `docs/plans/README.md` | **Shared docs only.** Hermes has no dedicated surface that references the planning workflow or `AGENTS.md` | **Gap:** Hermes relies entirely on shared repo docs. If Hermes is invoked without explicit context loading, it has no gate awareness. This is the supported mechanism for Hermes today — document it explicitly rather than treating it as a defect requiring a new config file |
    56|
    57|### Three-real-plans workstream
    58|
    59|The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself is one of the three.** This is intentionally self-referential: #2045 proves the workflow works by being a correctly-structured instance of it.
    60|
    61|| Plan # | File | Role |
    62||---|---|---|
    63|| 1 (this plan) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Onboarding spec AND validated template instance |
    64|| 2 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Independent validated template instance |
    65|| 3 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Independent validated template instance |
    66|
    67|**Validation rule:** all three files must contain every required template section (see `_template-issue-plan.md`): status header, review-artifact line, Resource Intelligence Summary, Artifact Map, Deliverable, Pseudocode (or "trivial" waiver for T1), Files to Change, TDD Test List, Acceptance Criteria, Adversarial Review Summary, Risks, Complexity. The `test_issue_2045_example_plans.sh` script must check each section by heading match and report per-file pass/fail.
    68|
    69|---
    70|
    71|## Artifact Map
    72|
    73|| Artifact | Path |
    74||---|---|
    75|| CLAUDE entry surface | `CLAUDE.md` |
    76|| AGENTS entry surface | `AGENTS.md` |
    77|| Gemini entry surface | `GEMINI.md` |
    78|| Codex repo config surface | `.codex/config.toml` |
    79|| Onboarding/index guide | `docs/plans/README.md` |
    80|| Planning template | `docs/plans/_template-issue-plan.md` |
    81|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    82|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    83|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    84|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    85|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    86|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
    87|
    88|---
    89|
    90|## Deliverable
    91|
    92|Updated repo onboarding surfaces, core planning skill guidance, and three validated real plan artifacts (#2045, #2046, #2047) so Claude, Codex, Gemini, and Hermes all have a discoverable in-repo path to the same strict planning workflow, review routing expectations, and template/label conventions.
    93|
    94|---
    95|
    96|## Pseudocode
    97|
    98|```text
    99|# 1. Write validation scripts first (TDD)
   100|for each of the 5 test scripts:
   101|    write script that checks the specific condition (see TDD Test List)
   102|    run it — expect failures on unmodified repo where gaps exist
   103|
   104|# 2. Fix onboarding surfaces to pass validation
   105|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   106|    if test_issue_2045_onboarding_docs.sh fails on this surface:
   107|        add/correct the AGENTS.md reference or planning workflow mention
   108|    if test_issue_2045_safe_path_assumption.sh fails on this surface:
   109|        remove the false ".claude/skills blocked" claim
   110|
   111|# 3. Validate three-plan set
   112|run test_issue_2045_example_plans.sh
   113|for each missing heading in #2045, #2046, or #2047:
   114|    add the missing template section to that plan file
   115|
   116|# 4. Validate policy alignment (validation-only surfaces)
   117|run test_issue_2045_policy_alignment.sh
   118|if contradiction found in .codex/CODEX.md or policy docs:
   119|    fix the contradiction; otherwise record no-op
   120|
   121|# 5. Confirm all 5 scripts exit 0; collect evidence artifacts
   122|```
   123|
   124|---
   125|
   126|## Files to Change
   127|
   128|### Implementation scope (onboarding surface alignment)
   129|
   130|| Action | Path | Decision rule | Reason |
   131||---|---|---|---|
   132|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   133|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   134|| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
   135|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   136|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill | Canonical skill must match canonical contract |
   137|| Add tests | `tests/test_issue_2045_*.sh` (5 scripts) | Create all five validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   138|
   139|### Validation-only (no change unless contradiction found)
   140|
   141|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order or workflow step that directly contradicts `AGENTS.md`**. If the file simply does not mention the planning workflow, that is not a contradiction — record "no-op, no contradiction" in the evidence log.
   142|
   143|| Action | Path | Decision rule |
   144||---|---|---|
   145|| Validate | `.codex/CODEX.md` + `.codex/config.toml` | Modify only if Required Gates section or role system_prompt contradicts `AGENTS.md` gate order |
   146|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   147|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   148|| Validate | Three plan files (#2045, #2046, #2047) | Checked by `test_issue_2045_example_plans.sh`; modify only if required template sections are missing |
   149|
   150|---
   151|
   152|## TDD Test List
   153|
   154|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   155||---|---|---|---|---|---|
   156|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface references the planning workflow | `grep -l` for `AGENTS.md` or `issue-planning-mode` or `plan.*approval` in each of: `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `AGENTS.md` | All four files match at least one keyword | Any file returns zero matches | `tests/evidence/2045-onboarding-docs.log` |
   157|| `test_issue_2045_example_plans.sh` | All three plan files exist and contain every required template section | For each of `2045`, `2046`, `2047` plan files: `grep -c` for headings: `## Resource Intelligence`, `## Artifact Map`, `## Deliverable`, `## Files to Change`, `## TDD Test List`, `## Acceptance Criteria`, `## Adversarial Review`, `> **Status:**`, `> **Review artifacts:**` | All 9 headings/markers present in all 3 files (27/27 checks pass) | Any heading missing in any file | `tests/evidence/2045-example-plans.log` with per-file per-heading pass/fail matrix |
   158|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | Extract workflow-order keywords from `AGENTS.md` (the canonical source); verify `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md` do not state a different gate order or skip a gate | No contradictions found; each file either matches or does not mention gate order | Any file states a gate order that conflicts with `AGENTS.md` | `tests/evidence/2045-policy-alignment.log` |
   159|| `test_issue_2045_safe_path_assumption.sh` | No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | `grep -rn "blocked.*plan.*gate\|plan.*gate.*block" CLAUDE.md GEMINI.md .codex/CODEX.md docs/plans/README.md` in context of `.claude/skills/` or `.claude/*` | Zero matches | Any match found | `tests/evidence/2045-safe-path.log` |
   160|| `test_issue_2045_hermes_documented.sh` | Hermes shared-docs-only onboarding mechanism is explicitly documented | `grep -l "shared.*docs\|shared.*surfaces\|no dedicated" docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` OR check that `config/agents/hermes/SOUL.md` now references `AGENTS.md` | Either this plan documents the shared-docs mechanism OR Hermes SOUL.md has been updated | Neither condition met | `tests/evidence/2045-hermes-documented.log` |
   161|
   162|### Execution
   163|
   164|```bash
   165|# Run all validation scripts; each writes its own evidence artifact
   166|bash tests/test_issue_2045_onboarding_docs.sh      | tee tests/evidence/2045-onboarding-docs.log
   167|bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
   168|bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
   169|bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
   170|bash tests/test_issue_2045_hermes_documented.sh     | tee tests/evidence/2045-hermes-documented.log
   171|```
   172|
   173|All five scripts must exit 0. Any non-zero exit blocks #2045 closure.
   174|
   175|---
   176|
   177|## Acceptance Criteria
   178|
   179|### Implementation completion (required to close #2045)
   180|
   181|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `docs/plans/README.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   182|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order.
   183|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   184|- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections (`test_issue_2045_example_plans.sh` exits 0 with 27/27 heading checks).
   185|- [ ] Validation-only surfaces (`.codex/CODEX.md`, policy docs) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   186|- [ ] Hermes shared-docs-only mechanism is explicitly documented in this plan and verified by `test_issue_2045_hermes_documented.sh`.
   187|- [ ] All five evidence artifacts exist in `tests/evidence/` with pass/fail results.
   188|
   189|### Plan approval gate (required before implementation begins)
   190|
   191|- [ ] Adversarial review from Codex and Gemini returns APPROVE or MINOR (no unresolved MAJOR findings).
   192|- [ ] **Claude plan-review evidence is missing.** A Claude review artifact (`scripts/review/results/2026-04-14-plan-2045-claude.md` or equivalent) must be generated before this plan enters `status:plan-approved`. The plan is intelligible without it, but the three-provider review contract from `AI_REVIEW_ROUTING_POLICY.md` requires all three providers. If Claude review cannot be obtained, document the reason in the review summary and obtain user sign-off on the two-provider exception.
   193|
   194|---
   195|
   196|## Adversarial Review History
   197|
   198|| Date | Provider | Verdict | Status |
   199||---|---|---|---|
   200|| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
   201|| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
   202|| — | Claude | **Missing** | No Claude review artifact exists. Required before `status:plan-approved` (see Acceptance Criteria) |
   203|
   204|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`
   205|
   206|**Current status:** Re-review required to confirm MAJOR findings are resolved. Claude review still needed.
   207|
   208|---
   209|
   210|## Risks and Open Questions
   211|
   212|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   213|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   214|- **Risk:** Hermes shared-docs-only mechanism means Hermes gate awareness depends on the caller loading `AGENTS.md` or `docs/plans/README.md` into context. This is weaker than a dedicated entry surface but is the current supported mechanism.
   215|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   216|- **Resolved:** missing Claude review — now an explicit plan-approval-gate requirement with documented exception path.
   217|
   218|---
   219|
   220|## Complexity: T2
   221|
   222|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   223|
```
