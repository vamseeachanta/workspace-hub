# Adversarial Re-Review Request: Issue #2045

You are an independent adversarial reviewer. This plan was revised again after prior MAJOR findings. Evaluate the current plan text only. Find any remaining gaps, unresolved decisions, weak retrieval, non-falsifiable tests/acceptance criteria, or workflow/governance violations. Do NOT rubber-stamp.

Return verdict as one of: APPROVE, MINOR, MAJOR.

Required output format:
1. Verdict
2. Ready for user approval: Yes/No
3. Retrieval adequacy: adequate/insufficient
4. Top blockers (numbered)
5. Critical findings
6. High findings
7. Medium findings
8. Low findings
9. Required revisions before user approval

Plan under review:

```markdown
     1|# Plan for #2045: Onboard All Agents to Strict Issue Planning Workflow
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
    25|- `docs/standards/HARD-STOP-POLICY.md` — hard-stop approval/implementation boundary authority.
    26|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
    27|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.
    28|
    29|### Documents consulted
    30|- `CLAUDE.md`
    31|- `AGENTS.md`
    32|- `GEMINI.md`
    33|- `.codex/CODEX.md`
    34|- `.codex/config.toml`
    35|- `config/agents/hermes/SOUL.md`
    36|- `docs/plans/README.md`
    37|- `docs/plans/_template-issue-plan.md`
    38|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    39|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    40|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    41|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    42|- `docs/plans/README.md` Step 5/6 + Status Meanings sections (authoritative approval-evidence and label workflow contract)
    43|- `.claude/skills/coordination/issue-planning-mode/SKILL.md` User Approval + status-precedence sections
    44|- GitHub labels `status:plan-review` and `status:plan-approved` (authoritative live workflow labels)
    45|- GitHub issue #2045 comments/labels as the fixed operational sample
    46|- related plans in `docs/plans/`, especially #2046 and #2047
    47|
    48|### Gaps identified
    49|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    50|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    51|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    52|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    53|
    54|### Authoritative in-repo onboarding surfaces
    55|
    56|"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.
    57|
    58|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    59||---|---|---|---|---|
    60|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    61|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
    62|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
    63|| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |
    64|
    65|### Three-real-plans workstream
    66|
    67|The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself counts only as the onboarding-spec artifact, not as one of the independent exemplar proofs.** The independent exemplars are #2046 and #2047, and the validation must prove more than formatting.
    68|
    69|| Plan role | File | Validation expectation |
    70||---|---|---|
    71|| Onboarding spec (this issue) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Must define the workflow and validation contract |
    72|| Independent exemplar 1 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Must satisfy normalized section contract and contain issue-specific, non-placeholder content |
    73|| Independent exemplar 2 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Must satisfy normalized section contract and contain issue-specific, non-placeholder content |
    74|
    75|**Validation rule:** all three files must contain one exact required heading set. Baseline section coverage comes from `_template-issue-plan.md`, but for #2045’s local validation contract the canonical review-section heading is explicitly `## Adversarial Review History`. The `test_issue_2045_example_plans.sh` script must check that exact heading set by explicit heading match, verify issue-specific/non-placeholder content, and require that the two independent exemplars (#2046, #2047) are not merely template-shaped stubs.
    76|
    77|---
    78|
    79|## Artifact Map
    80|
    81|| Artifact | Path |
    82||---|---|
    83|| CLAUDE entry surface | `CLAUDE.md` |
    84|| AGENTS entry surface | `AGENTS.md` |
    85|| Gemini entry surface | `GEMINI.md` |
    86|| Codex repo config surface | `.codex/config.toml` |
    87|| Onboarding/index guide | `docs/plans/README.md` |
    88|| Planning template | `docs/plans/_template-issue-plan.md` |
    89|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    90|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    91|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    92|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    93|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    94|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
    95|
    96|---
    97|
    98|## Deliverable
    99|
   100|Updated repo onboarding surfaces, core planning skill guidance, and three validated real plan artifacts (#2045, #2046, #2047) so Claude, Codex, Gemini, and Hermes all have a discoverable in-repo path to the same strict planning workflow, review routing expectations, and template/label conventions.
   101|
   102|---
   103|
   104|## Pseudocode
   105|
   106|```text
   107|# 1. Write validation scripts first (TDD)
   108|for each of the 6 test scripts:
   109|    write script that checks the specific condition (see TDD Test List)
   110|    run it — expect failures on unmodified repo where gaps exist
   111|
   112|# 2. Fix onboarding surfaces to pass validation
   113|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, .codex/CODEX.md, config/agents/hermes/SOUL.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   114|    if test_issue_2045_onboarding_docs.sh fails on this surface:
   115|        either add direct workflow markers OR add an explicit canonical-contract reference that the test accepts
   116|    if test_issue_2045_safe_path_assumption.sh fails on this surface:
   117|        remove the false ".claude/skills blocked" claim
   118|
   119|# 3. Validate three-plan set
   120|run test_issue_2045_example_plans.sh
   121|for each missing normalized heading in #2045, #2046, or #2047:
   122|    add the missing section to that plan file
   123|
   124|# 4. Validate policy alignment and skill alignment
   125|run test_issue_2045_policy_alignment.sh
   126|run test_issue_2045_skill_alignment.sh
   127|if contradiction found in .codex/CODEX.md, .codex/config.toml, GEMINI.md, or policy docs:
   128|    fix the contradiction; otherwise record no-op
   129|
   130|# 5. Validate operational GitHub workflow using issue #2045 as the fixed sample
   131|run test_issue_2045_operational_workflow.sh
   132|verify: plan comment exists, status:plan-review label exists, and no status:plan-approved label is treated as valid without explicit human approval evidence
   133|
   134|# 6. Confirm all 6 scripts exit 0; collect evidence artifacts
   135|```
   136|
   137|---
   138|
   139|## Files to Change
   140|
   141|### Implementation scope (onboarding surface alignment)
   142|
   143|| Action | Path | Decision rule | Reason |
   144||---|---|---|---|
   145|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   146|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   147|| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
   148|| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
   149|| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
   150|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   151|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
   152|| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   153|
   154|### Validation-only (no change unless contradiction found)
   155|
   156|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md` or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.
   157|
   158|| Action | Path | Decision rule |
   159||---|---|---|
   160|| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces |
   161|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   162|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   163|| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
   164|| Validate | Three plan files (#2045, #2046, #2047) | Checked by `test_issue_2045_example_plans.sh`; modify only if required template sections are missing |
   165|
   166|---
   167|
   168|## TDD Test List
   169|
   170|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   171||---|---|---|---|---|---|
   172|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface has a deterministic, actionable planning-workflow discovery path | exact accepted patterns are enumerated here: `AGENTS.md` must contain the full gate-order chain; `CLAUDE.md` must reference the planning workflow skill path or explicit gate order; `GEMINI.md` must either name `AGENTS.md` as canonical instructions or include explicit workflow markers; `.codex/CODEX.md` must include explicit gate/order language and must not reference deprecated WRK-* workflow surfaces; `config/agents/hermes/SOUL.md` must explicitly reference `AGENTS.md` or `docs/plans/README.md` as the planning workflow source | Each file matches its allowed exact pattern and provides an actionable path to the workflow source | Any file lacks its required direct marker or canonical-contract reference, or still points to deprecated workflow surfaces | `tests/evidence/2045-onboarding-docs.log` |
   173|| `test_issue_2045_example_plans.sh` | All three plan files exist and contain the normalized required section set with issue-specific content | For each of `2045`, `2046`, `2047` plan files: check `> **Status:**`, `> **Review artifacts:**`, `## Resource Intelligence Summary`, `## Artifact Map`, `## Deliverable`, `## Pseudocode`, `## Files to Change`, `## TDD Test List`, `## Acceptance Criteria`, `## Adversarial Review History`, `## Risks and Open Questions`, `## Complexity`; also verify issue-specific file naming and that placeholder template strings like `#NNN`, `YYYY-MM-DD`, or `<repo>` are absent | All required headings/markers present in all 3 files and no template placeholders remain | Any heading missing or any placeholder/template stub remains | `tests/evidence/2045-example-plans.log` with per-file heading + placeholder pass/fail matrix |
   174|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
   175|| `test_issue_2045_safe_path_assumption.sh` | No in-scope onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | search the full in-scope surface list: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `docs/plans/README.md`, `config/agents/hermes/SOUL.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`; fail on any text asserting that `.claude/skills/` or `.claude/*` edits are blocked by the plan gate | Zero prohibited claims across the full in-scope surface list | Any prohibited claim found in any in-scope onboarding surface | `tests/evidence/2045-safe-path.log` |
   176|| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
   177|| `test_issue_2045_operational_workflow.sh` | The operational GitHub workflow is validated against present, authoritative evidence | use issue #2045 as the fixed sample; retrieve `gh issue view 2045 --json comments,labels` plus consult `docs/plans/README.md` and `issue-planning-mode/SKILL.md`; verify: (a) a GitHub comment exists referencing the plan artifact path, (b) `status:plan-review` is the current live label state, and (c) the repo policy defines explicit human approval evidence as a user action/comment plus the `status:plan-approved` label + local marker, so label state alone is not treated as sufficient approval evidence | sample workflow passes all current-state checks and the approval-evidence rule is grounded in cited repo policy text | missing plan comment, missing label, or approval evidence rule not grounded in cited policy text | `tests/evidence/2045-operational-workflow.log` |
   178|
   179|### Execution
   180|
   181|```bash
   182|# Run all validation scripts; each writes its own evidence artifact
   183|bash tests/test_issue_2045_onboarding_docs.sh       | tee tests/evidence/2045-onboarding-docs.log
   184|bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
   185|bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
   186|bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
   187|bash tests/test_issue_2045_skill_alignment.sh       | tee tests/evidence/2045-skill-alignment.log
   188|bash tests/test_issue_2045_operational_workflow.sh  | tee tests/evidence/2045-operational-workflow.log
   189|```
   190|
   191|All six scripts must exit 0. Any non-zero exit blocks #2045 closure.
   192|
   193|---
   194|
   195|## Acceptance Criteria
   196|
   197|### Implementation completion (required to close #2045)
   198|
   199|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   200|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
   201|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   202|- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections, including `Pseudocode`, `Risks and Open Questions`, and `Complexity` (`test_issue_2045_example_plans.sh` exits 0).
   203|- [ ] Validation-only surfaces (policy docs, `GEMINI.md` stale references, `.codex/config.toml`) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   204|- [ ] Operational workflow validation proves issue #2045 has plan posted to GitHub, `status:plan-review` applied, and that any future `status:plan-approved` transition must require explicit human approval evidence (`test_issue_2045_operational_workflow.sh`).
   205|- [ ] All six evidence artifacts exist in `tests/evidence/` with pass/fail results.
   206|
   207|### Plan approval gate (required before implementation begins)
   208|
   209|- [ ] Three-provider adversarial review set is complete: Claude, Codex, and Gemini artifacts all exist for the current plan revision.
   210|- [ ] No unresolved MAJOR findings remain.
   211|- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract (`AGENTS.md` / `docs/plans/README.md`) in a testable way.
   212|- [ ] `.codex/CODEX.md` scope is no longer ambiguous: it is either updated in implementation scope or explicitly deferred by user-approved scope note.
   213|---
   214|
   215|## Adversarial Review History
   216|
   217|| Date | Provider | Verdict | Status |
   218||---|---|---|---|
   219|| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
   220|| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
   221|| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified: tighten Codex onboarding scope, strengthen test specificity, and make operational workflow test executable |
   222|
   223|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`
   224|
   225|**Current status:** Re-review required to confirm remaining MAJOR findings are resolved. Three-provider artifact set now exists.
   226|
   227|---
   228|
   229|## Risks and Open Questions
   230|
   231|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   232|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   233|- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
   234|- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
   235|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   236|- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.
   237|
   238|---
   239|
   240|## Complexity: T2
   241|
   242|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   243|
```
