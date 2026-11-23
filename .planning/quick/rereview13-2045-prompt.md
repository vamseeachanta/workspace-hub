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
    18|- Found: `docs/standards/HARD-STOP-POLICY.md` defines the hard boundary that implementation must not begin before approval.
    19|- Found: `.claude/hooks/plan-approval-gate.sh` is the live local gate enforcing the no-implementation-before-approval boundary and should be treated as authoritative for safe-path assumptions.
    20|- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` defines default multi-provider review expectations.
    21|- Found: `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` constrains how agents and subagents should be framed.
    22|- Found: issue #2046 remains OPEN in `status:plan-review`; issue #2047 is CLOSED/completed, so #2045 may validate those artifacts but should not assume it is authorized to rewrite #2046 as part of #2045 closure without separate governance handling.
    23|
    24|### Standards
    25|- `AGENTS.md` — repo hard-gate order and mandatory workflow statement.
    26|- `docs/plans/README.md` — plan workflow contract.
    27|- `docs/standards/HARD-STOP-POLICY.md` — hard-stop approval/implementation boundary authority.
    28|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
    29|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.
    30|
    31|### Documents consulted
    32|- `CLAUDE.md`
    33|- `AGENTS.md`
    34|- `GEMINI.md`
    35|- `.codex/CODEX.md`
    36|- `.codex/config.toml`
    37|- `config/agents/hermes/SOUL.md`
    38|- `docs/plans/README.md`
    39|- `docs/plans/_template-issue-plan.md`
    40|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    41|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    42|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    43|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    44|- `docs/plans/README.md` Step 5/6 + Status Meanings sections (authoritative approval-evidence and label workflow contract)
    45|- `.claude/skills/coordination/issue-planning-mode/SKILL.md` User Approval + status-precedence sections
    46|- GitHub labels `status:plan-review` and `status:plan-approved` (authoritative live workflow labels)
    47|- GitHub issue #2045 comments/labels as the fixed operational sample
    48|- related plans in `docs/plans/`, especially #2046 and #2047
    49|
    50|### Gaps identified
    51|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    52|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    53|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    54|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    55|
    56|### Authoritative in-repo onboarding surfaces
    57|
    58|"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.
    59|
    60|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    61||---|---|---|---|---|
    62|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    63|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
    64|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
    65|| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |
    66|
    67|### Three-real-plans workstream
    68|
    69|The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. **#2045 itself counts only as the onboarding-spec artifact, not as one of the independent exemplar proofs.** The independent exemplars are #2046 and #2047, and the validation must prove more than formatting.
    70|
    71|| Plan role | File | Validation expectation |
    72||---|---|---|
    73|| Onboarding spec (this issue) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Must define the workflow and validation contract |
    74|| Independent exemplar 1 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Pre-existing prerequisite exemplar: must be read/validated, but not rewritten under #2045 |
    75|| Independent exemplar 2 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Pre-existing prerequisite exemplar: must be read/validated, but not rewritten under #2045 |
    76|
    77|**Validation rule:** all three files must contain one exact required heading set. Baseline section coverage comes from `_template-issue-plan.md`, but for #2045’s local validation contract the canonical review-section heading is explicitly `## Adversarial Review History`. The `test_issue_2045_example_plans.sh` script must check that exact heading set by explicit heading match, verify issue-specific/non-placeholder content, and treat #2046/#2047 as prerequisite read-only exemplars rather than automatic repair targets.
    78|
    79|---
    80|
    81|## Artifact Map
    82|
    83|| Artifact | Path |
    84||---|---|
    85|| CLAUDE entry surface | `CLAUDE.md` |
    86|| AGENTS entry surface | `AGENTS.md` |
    87|| Gemini entry surface | `GEMINI.md` |
    88|| Codex repo config surface | `.codex/config.toml` |
    89|| Onboarding/index guide | `docs/plans/README.md` |
    90|| Planning template | `docs/plans/_template-issue-plan.md` |
    91|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    92|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    93|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    94|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    95|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    96|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
    97|
    98|---
    99|
   100|## Deliverable
   101|
   102|Updated repo onboarding surfaces, core planning skill guidance, and three validated real plan artifacts (#2045, #2046, #2047) so Claude, Codex, Gemini, and Hermes all have a discoverable in-repo path to the same strict planning workflow, review routing expectations, and template/label conventions.
   103|
   104|---
   105|
   106|## Pseudocode
   107|
   108|```text
   109|# 1. Write validation scripts first (TDD)
   110|for each of the 6 test scripts:
   111|    write script that checks the specific condition (see TDD Test List)
   112|    run it — expect failures on unmodified repo where gaps exist
   113|
   114|# 2. Fix onboarding surfaces to pass validation
   115|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, .codex/CODEX.md, config/agents/hermes/SOUL.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   116|    if test_issue_2045_onboarding_docs.sh fails on this surface:
   117|        either add direct workflow markers OR add an explicit canonical-contract reference that the test accepts
   118|    if test_issue_2045_safe_path_assumption.sh fails on this surface:
   119|        remove the false ".claude/skills blocked" claim
   120|
   121|# 3. Validate three-plan set
   122|run test_issue_2045_example_plans.sh
   123|for each missing normalized heading in #2045, #2046, or #2047:
   124|    add the missing section to that plan file
   125|
   126|# 4. Validate policy alignment and skill alignment
   127|run test_issue_2045_policy_alignment.sh
   128|run test_issue_2045_skill_alignment.sh
   129|if contradiction found in .codex/CODEX.md, .codex/config.toml, GEMINI.md, or policy docs:
   130|    fix the contradiction; otherwise record no-op
   131|
   132|# 5. Validate operational GitHub workflow using issue #2045 as the fixed sample
   133|run test_issue_2045_operational_workflow.sh
   134|verify: plan comment exists, status:plan-review label exists, and no status:plan-approved label is treated as valid without explicit human approval evidence
   135|
   136|# 6. Confirm all 6 scripts exit 0; collect evidence artifacts
   137|```
   138|
   139|---
   140|
   141|## Files to Change
   142|
   143|### Implementation scope (onboarding surface alignment)
   144|
   145|| Action | Path | Decision rule | Reason |
   146||---|---|---|---|
   147|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   148|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   149|| Modify | `GEMINI.md` | If `GEMINI.md` does not reference `AGENTS.md` for gate order, add the reference | Ensure Gemini sessions discover the planning workflow |
   150|| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
   151|| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
   152|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   153|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
   154|| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   155|
   156|### Validation-only (no change unless contradiction found)
   157|
   158|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.
   159|
   160|| Action | Path | Decision rule |
   161||---|---|---|
   162|| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces; otherwise record why validation-only is acceptable despite CODEX.md being implementation-scope |
   163|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   164|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   165|| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
   166|| Validate only (no edits under #2045) | Three plan files (#2045, #2046, #2047) | `test_issue_2045_example_plans.sh` may inspect all three, but under #2045 only this plan file may be edited; issues #2046/#2047 are exemplar reads, not automatic rewrite targets |
   167|
   168|---
   169|
   170|## TDD Test List
   171|
   172|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   173||---|---|---|---|---|---|
   174|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface has a deterministic, actionable planning-workflow discovery path | exact accepted patterns are enumerated here: `AGENTS.md` must contain the full gate-order chain; `CLAUDE.md` must reference the planning workflow skill path or explicit gate order; `GEMINI.md` must either name `AGENTS.md` as canonical instructions or include explicit workflow markers and must not point to deprecated workflow docs; `.codex/CODEX.md` must include explicit gate/order language and must not reference deprecated WRK-* workflow surfaces; `config/agents/hermes/SOUL.md` must explicitly reference `AGENTS.md` or `docs/plans/README.md` as the planning workflow source | Each file matches its allowed exact pattern and provides an actionable current path to the workflow source | Any file lacks its required direct marker or canonical-contract reference, or still points to deprecated workflow surfaces | `tests/evidence/2045-onboarding-docs.log` |
   175|| `test_issue_2045_example_plans.sh` | The exemplar plan set is structurally complete and semantically issue-specific | For #2045, #2046, and #2047: check normalized heading set; reject placeholder/template stubs; verify Deliverable mentions the issue-specific objective, Files to Change lists issue-relevant paths, and Acceptance Criteria contain issue-specific checks rather than generic boilerplate. Under #2045 this test is read-only for #2046/#2047 and must not mutate them. | All three plans pass structural checks and the two independent exemplars (#2046, #2047) contain issue-specific deliverables/files/acceptance criteria | Any heading missing, placeholder stub remains, or exemplar content is still generic/template-like | `tests/evidence/2045-example-plans.log` with per-file structural + semantic pass/fail matrix |
   176|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
   177|| `test_issue_2045_safe_path_assumption.sh` | No in-scope onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | search the full in-scope surface list: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `docs/plans/README.md`, `config/agents/hermes/SOUL.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`; fail on any text asserting that `.claude/skills/` or `.claude/*` edits are blocked by the plan gate | Zero prohibited claims across the full in-scope surface list | Any prohibited claim found in any in-scope onboarding surface | `tests/evidence/2045-safe-path.log` |
   178|| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
   179|| `test_issue_2045_operational_workflow.sh` | The operational GitHub workflow is validated against bounded policy-compliant state transitions | use issue #2045 as the fixed sample; require authenticated `gh` as a blocker prerequisite for running this test; verify via `gh issue view 2045 --json comments,labels` plus `docs/plans/README.md` and `issue-planning-mode/SKILL.md` that: (a) a GitHub plan comment exists referencing the plan artifact path, and (b) the issue is in one of two allowed policy states — pre-approval (`status:plan-review` present, `status:plan-approved` absent) or post-approval (`status:plan-approved` plus explicit human approval evidence as defined by repo policy). If `gh` auth is unavailable, the test is not runnable and the environment must be fixed before claiming #2045 complete. | sample workflow passes one allowed policy state and the approval-evidence rule is grounded in cited repo policy text | missing plan comment, invalid label state, approval evidence rule not grounded in cited policy text, or missing `gh` auth prerequisite | `tests/evidence/2045-operational-workflow.log` |
   180|
   181|### Execution
   182|
   183|```bash
   184|# Run all validation scripts; each writes its own evidence artifact
   185|bash tests/test_issue_2045_onboarding_docs.sh       | tee tests/evidence/2045-onboarding-docs.log
   186|bash tests/test_issue_2045_example_plans.sh         | tee tests/evidence/2045-example-plans.log
   187|bash tests/test_issue_2045_policy_alignment.sh      | tee tests/evidence/2045-policy-alignment.log
   188|bash tests/test_issue_2045_safe_path_assumption.sh  | tee tests/evidence/2045-safe-path.log
   189|bash tests/test_issue_2045_skill_alignment.sh       | tee tests/evidence/2045-skill-alignment.log
   190|bash tests/test_issue_2045_operational_workflow.sh  | tee tests/evidence/2045-operational-workflow.log
   191|```
   192|
   193|All six scripts must exit 0. Any non-zero exit blocks #2045 closure.
   194|
   195|---
   196|
   197|## Acceptance Criteria
   198|
   199|### Implementation completion (required to close #2045)
   200|
   201|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   202|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
   203|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   204|- [ ] Three plan files (#2045, #2046, #2047) each contain all required template sections, including `Pseudocode`, `Risks and Open Questions`, and `Complexity` (`test_issue_2045_example_plans.sh` exits 0).
   205|- [ ] Validation-only surfaces (policy docs, `GEMINI.md` stale references, `.codex/config.toml`) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   206|- [ ] Operational workflow validation proves issue #2045 has plan posted to GitHub, `status:plan-review` applied, and that any future `status:plan-approved` transition must require explicit human approval evidence (`test_issue_2045_operational_workflow.sh`).
   207|- [ ] All six evidence artifacts exist in `tests/evidence/` with pass/fail results.
   208|
   209|### Plan approval gate (required before implementation begins)
   210|
   211|- [ ] Three-provider adversarial review set is complete: Claude, Codex, and Gemini artifacts all exist for the current plan revision.
   212|- [ ] No unresolved MAJOR findings remain.
   213|- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract (`AGENTS.md` / `docs/plans/README.md`) in a testable way.
   214|- [ ] `.codex/CODEX.md` scope is no longer ambiguous: it is either updated in implementation scope or explicitly deferred by user-approved scope note.
   215|---
   216|
   217|## Adversarial Review History
   218|
   219|| Date | Provider | Verdict | Status |
   220||---|---|---|---|
   221|| 2026-04-14 | Codex | MAJOR | Addressed in current revision: “all agents” enumerated, validation concrete, self-approval removed |
   222|| 2026-04-14 | Gemini | MAJOR | Addressed in current revision: safe-path assumption corrected, baseline retrieval done, three-plan workstream explicit |
   223|| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified: tighten Codex onboarding scope, strengthen test specificity, and make operational workflow test executable |
   224|
   225|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`
   226|
   227|**Current status:** Re-review required to confirm remaining MAJOR findings are resolved. Three-provider artifact set now exists.
   228|
   229|---
   230|
   231|## Risks and Open Questions
   232|
   233|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   234|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   235|- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
   236|- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
   237|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   238|- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.
   239|
   240|---
   241|
   242|## Complexity: T2
   243|
   244|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   245|
```
