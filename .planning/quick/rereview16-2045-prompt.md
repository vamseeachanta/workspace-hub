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
    16|- Found: `docs/plans/_template-issue-plan.md` defines the canonical minimum plan structure and currently uses `## Adversarial Review Summary`, so #2045 must not invent a conflicting repo-wide heading rule without updating the template.
    17|- Found: `docs/plans/README.md` is both onboarding guide and plan index and defines the live approval sequence (`status:plan-review` -> user approval -> `status:plan-approved`).
    18|- Found: `docs/standards/HARD-STOP-POLICY.md` defines the hard boundary that implementation must not begin before approval.
    19|- Found: `.claude/hooks/plan-approval-gate.sh` is the live local gate enforcing the no-implementation-before-approval boundary; it is authoritative only for local gate behavior and safe-path assumptions, not for GitHub-side approval semantics.
    20|- Found: `.codex/CODEX.md` still contains legacy WRK-* / work-queue references that conflict with the GitHub issue planning workflow in `AGENTS.md`.
    21|- Found: `GEMINI.md` reaches workflow guidance via canonical shared-doc references and may still contain stale workflow references; under #2045 it should be validation-only unless a contradiction is found.
    22|- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` defines default multi-provider review expectations.
    23|- Found: `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` constrains how agents and subagents should be framed.
    24|- Found: GitHub labels `status:plan-review` and `status:plan-approved` are the authoritative live workflow labels, with semantics defined by `docs/plans/README.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md`.
    25|
    26|### Standards
    27|- `AGENTS.md` — repo hard-gate order and mandatory workflow statement.
    28|- `docs/plans/README.md` — plan workflow contract.
    29|- `docs/standards/HARD-STOP-POLICY.md` — hard-stop approval/implementation boundary authority.
    30|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
    31|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.
    32|
    33|### Documents consulted
    34|- `CLAUDE.md`
    35|- `AGENTS.md`
    36|- `GEMINI.md`
    37|- `.codex/CODEX.md`
    38|- `.codex/config.toml`
    39|- `config/agents/hermes/SOUL.md`
    40|- `docs/plans/README.md`
    41|- `docs/plans/_template-issue-plan.md`
    42|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    43|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    44|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    45|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    46|- `docs/plans/README.md` Step 5/6 + Status Meanings sections (authoritative approval-evidence and label workflow contract)
    47|- `.claude/skills/coordination/issue-planning-mode/SKILL.md` User Approval + status-precedence sections
    48|- GitHub labels `status:plan-review` and `status:plan-approved` (authoritative live workflow labels)
    49|- GitHub issue #2045 comments/labels as the fixed operational sample
    50|- related plans in `docs/plans/`, especially #2046 and #2047
    51|
    52|### Gaps identified
    53|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    54|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    55|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    56|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    57|
    58|### Authoritative in-repo onboarding surfaces
    59|
    60|"All agents" means the finite set of providers with in-repo entry surfaces: Claude, Gemini, Codex, and Hermes. If a new provider is added, it must be added to this table before #2045 can be considered complete.
    61|
    62|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    63||---|---|---|---|---|
    64|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    65|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` → references `AGENTS.md` for canonical contract | None — functional via `AGENTS.md` reference |
    66|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | None — most explicit gate wording |
    67|| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |
    68|
    69|### Three-real-plans workstream
    70|
    71|The issue's acceptance criterion requires three real plans that demonstrate template usage and review conventions. For #2045, the exemplar-plan sweep is an advisory/read-only validation pass, not a closure-blocking dependency on rewriting other issues.
    72|
    73|| Plan role | File | Validation expectation |
    74||---|---|---|
    75|| Onboarding spec (this issue) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Must define the workflow and validation contract |
    76|| Exemplar read 1 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Read-only exemplar check; failures become follow-up governance work, not #2045 rewrite scope |
    77|| Exemplar read 2 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Read-only exemplar check; failures become follow-up governance work, not #2045 rewrite scope |
    78|
    79|**Validation rule:** `test_issue_2045_example_plans.sh` uses the single authoritative heading list below and verifies issue-specific/non-placeholder content. Under #2045, failures in #2046/#2047 are advisory prerequisite drift findings that trigger follow-up work rather than blocking #2045 through unauthorized edits.
    80|
    81|---
    82|
    83|## Artifact Map
    84|
    85|| Artifact | Path |
    86||---|---|
    87|| CLAUDE entry surface | `CLAUDE.md` |
    88|| AGENTS entry surface | `AGENTS.md` |
    89|| Gemini entry surface | `GEMINI.md` |
    90|| Codex repo config surface | `.codex/config.toml` |
    91|| Onboarding/index guide | `docs/plans/README.md` |
    92|| Planning template | `docs/plans/_template-issue-plan.md` |
    93|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    94|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    95|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    96|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    97|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    98|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
    99|
   100|---
   101|
   102|## Deliverable
   103|
   104|Updated repo onboarding surfaces, core planning skill guidance, and a validated onboarding contract so Claude, Codex, Gemini, and Hermes each have a discoverable path to the same strict planning workflow, with explicit gate-order expectations and actionable references to review-routing plus template/label conventions.
   105|
   106|---
   107|
   108|## Pseudocode
   109|
   110|```text
   111|# 1. Write validation scripts first (TDD)
   112|for each of the 6 test scripts:
   113|    write script that checks the specific condition (see TDD Test List)
   114|    expect at least one targeted failing check before remediation where a known gap exists
   115|
   116|# 2. Fix onboarding surfaces to pass validation
   117|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, .codex/CODEX.md, config/agents/hermes/SOUL.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   118|    if test_issue_2045_onboarding_docs.sh fails on this surface:
   119|        either add direct workflow markers OR add an explicit canonical-contract reference that the test accepts
   120|    if test_issue_2045_safe_path_assumption.sh fails on this surface:
   121|        remove the false ".claude/skills blocked" claim
   122|
   123|# 3. Validate exemplar plan set (read-only for #2046/#2047)
   124|run test_issue_2045_example_plans.sh
   125|if the current #2045 plan is missing a normalized heading or issue-specific content:
   126|    fix this plan file
   127|if #2046 or #2047 fail validation:
   128|    record the failure as prerequisite drift to be corrected under their own governance path; do not rewrite them under #2045
   129|
   130|# 4. Validate policy alignment and skill alignment
   131|run test_issue_2045_policy_alignment.sh
   132|run test_issue_2045_skill_alignment.sh
   133|if contradiction found in .codex/CODEX.md, .codex/config.toml, GEMINI.md, or policy docs:
   134|    fix the contradiction in files that are in #2045 implementation scope; otherwise record no-op
   135|
   136|# 5. Validate operational GitHub workflow using issue #2045 as the fixed sample
   137|run test_issue_2045_operational_workflow.sh
   138|verify: plan comment exists, issue is in an allowed policy state, and approval evidence rules come from cited repo policy
   139|
   140|# 6. Confirm all 6 scripts exit 0 with pipefail-enabled execution; collect evidence artifacts
   141|```
   142|
   143|---
   144|
   145|## Files to Change
   146|
   147|### Implementation scope (onboarding surface alignment)
   148|
   149|| Action | Path | Decision rule | Reason |
   150||---|---|---|---|
   151|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   152|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   153|| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
   154|| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
   155|| Modify only if contradiction found | `GEMINI.md` | Fix deprecated workflow references or missing canonical planning-contract reference only if validation finds them | Gemini is validation-first, not mandatory-edit-by-default |
   156|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   157|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
   158|| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   159|
   160|### Validation-only (no change unless contradiction found)
   161|
   162|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.
   163|
   164|| Action | Path | Decision rule |
   165||---|---|---|
   166|| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces; otherwise record why validation-only is acceptable despite CODEX.md being implementation-scope |
   167|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   168|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   169|| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
   170|| Validate only (no edits under #2045) | Three plan files (#2045, #2046, #2047) | `test_issue_2045_example_plans.sh` may inspect all three, but under #2045 only this plan file may be edited; issues #2046/#2047 are exemplar reads, not automatic rewrite targets |
   171|
   172|---
   173|
   174|### Exact required heading set for exemplar-plan validation
   175|
   176|The single authoritative heading list for `test_issue_2045_example_plans.sh` is derived from `docs/plans/_template-issue-plan.md` and, until the template itself is changed, uses the template's canonical review heading:
   177|1. `> **Status:**`
   178|2. `> **Review artifacts:**`
   179|3. `## Resource Intelligence Summary`
   180|4. `## Artifact Map`
   181|5. `## Deliverable`
   182|6. `## Pseudocode`
   183|7. `## Files to Change`
   184|8. `## TDD Test List`
   185|9. `## Acceptance Criteria`
   186|10. `## Adversarial Review Summary`
   187|11. `## Risks and Open Questions`
   188|12. `## Complexity`
   189|
   190|This list is the sole section oracle for #2045’s exemplar-plan validation; pseudocode, tests, and acceptance criteria must all point back to this exact list.
   191|
   192|## TDD Test List
   193|
   194|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   195||---|---|---|---|---|---|
   196|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface has a deterministic, actionable planning-workflow discovery path | exact accepted patterns are enumerated here: `AGENTS.md` must contain the full gate-order chain; `CLAUDE.md` must reference the planning workflow skill path or explicit gate order; `GEMINI.md` must either name `AGENTS.md` as canonical instructions or include explicit workflow markers and must not point to deprecated workflow docs; `.codex/CODEX.md` must include explicit gate/order language and must not reference deprecated WRK-* workflow surfaces; `config/agents/hermes/SOUL.md` must explicitly reference `AGENTS.md` or `docs/plans/README.md` as the planning workflow source | Each file matches its allowed exact pattern and provides an actionable current path to the workflow source | Any file lacks its required direct marker or canonical-contract reference, or still points to deprecated workflow surfaces | `tests/evidence/2045-onboarding-docs.log` |
   197|| `test_issue_2045_example_plans.sh` | The exemplar plan set is structurally complete and semantically issue-specific | Use the single authoritative heading list above. For #2045, #2046, and #2047: check that all 12 required headings are present; reject placeholder/template stubs; verify Deliverable mentions the issue-specific objective, Files to Change lists issue-relevant paths, and Acceptance Criteria contain issue-specific checks rather than generic boilerplate. Under #2045 this test is read-only for #2046/#2047 and must not mutate them. | #2045 passes the 12-heading oracle and exemplar reads #2046/#2047 yield either pass or advisory prerequisite-drift findings; exemplar drift does not by itself block #2045 closure | Any required heading missing in #2045, placeholder stub remains, or #2045 content is still generic/template-like | `tests/evidence/2045-example-plans.log` with per-file structural + semantic pass/fail matrix plus advisory drift notes for #2046/#2047 |
   198|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
   199|| `test_issue_2045_safe_path_assumption.sh` | No in-scope onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | search the full in-scope surface list: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `docs/plans/README.md`, `config/agents/hermes/SOUL.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`; fail on any text asserting that `.claude/skills/` or `.claude/*` edits are blocked by the plan gate | Zero prohibited claims across the full in-scope surface list | Any prohibited claim found in any in-scope onboarding surface | `tests/evidence/2045-safe-path.log` |
   200|| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
   201|| `test_issue_2045_operational_workflow.sh` | The operational GitHub workflow is validated against bounded policy-compliant state transitions | use issue #2045 as the fixed sample; require authenticated `gh` as a blocker prerequisite for running this test; verify via `gh issue view 2045 --json comments,labels` plus `docs/plans/README.md` and `issue-planning-mode/SKILL.md` that: (a) a GitHub plan comment exists referencing the plan artifact path, and (b) the issue is in one of two allowed policy states — pre-approval (`status:plan-review` present, `status:plan-approved` absent) or post-approval (`status:plan-approved` plus explicit human approval evidence as defined by repo policy). If `gh` auth is unavailable, the test is not runnable and the environment must be fixed before claiming #2045 complete. | sample workflow passes one allowed policy state and the approval-evidence rule is grounded in cited repo policy text | missing plan comment, invalid label state, approval evidence rule not grounded in cited policy text, or missing `gh` auth prerequisite | `tests/evidence/2045-operational-workflow.log` |
   202|
   203|### Evidence ownership
   204|
   205|- The `tests/evidence/*.log` files created by the execution block are the canonical evidence artifacts.
   206|- Individual test scripts should print deterministic stdout for piping, but should not separately write conflicting artifact files unless explicitly documented.
   207|
   208|### Execution
   209|
   210|```bash
   211|set -euo pipefail
   212|
   213|# Run all validation scripts; each writes its own evidence artifact
   214|bash tests/test_issue_2045_onboarding_docs.sh      | tee tests/evidence/2045-onboarding-docs.log
   215|bash tests/test_issue_2045_example_plans.sh        | tee tests/evidence/2045-example-plans.log
   216|bash tests/test_issue_2045_policy_alignment.sh     | tee tests/evidence/2045-policy-alignment.log
   217|bash tests/test_issue_2045_safe_path_assumption.sh | tee tests/evidence/2045-safe-path.log
   218|bash tests/test_issue_2045_skill_alignment.sh      | tee tests/evidence/2045-skill-alignment.log
   219|bash tests/test_issue_2045_operational_workflow.sh | tee tests/evidence/2045-operational-workflow.log
   220|```
   221|
   222|All six scripts must exit 0. Any non-zero exit blocks #2045 closure.
   223|
   224|---
   225|
   226|## Acceptance Criteria
   227|
   228|### Implementation completion (required to close #2045)
   229|
   230|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   231|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
   232|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   233|- [ ] Three plan files are validated against the single 12-heading oracle above; #2045 itself must pass and any #2046/#2047 drift is recorded as prerequisite follow-up work rather than unauthorized edit scope (`test_issue_2045_example_plans.sh`).
   234|- [ ] Validation-only surfaces (policy docs, validation-only Gemini/config prompts) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   235|- [ ] Operational workflow validation proves issue #2045 is in one allowed policy state (pre-approval or post-approval with explicit human approval evidence) and that the result is grounded in cited repo policy text (`test_issue_2045_operational_workflow.sh`).
   236|- [ ] All six canonical evidence artifacts exist in `tests/evidence/` with pass/fail results.
   237|
   238|### Plan approval gate (required before implementation begins)
   239|
   240|- [ ] Three-provider adversarial review set is complete for the current plan revision: Claude, Codex, and Gemini artifacts all exist and correspond to the latest plan text.
   241|- [ ] No unresolved MAJOR findings remain.
   242|- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract in a testable way.
   243|- [ ] `.codex/CODEX.md` contradictions are fixed in implementation scope; `.codex/config.toml` remains validation-only only if `test_issue_2045_policy_alignment.sh` shows no contradictory workflow behavior.
   244|- [ ] Exemplar-plan validation is advisory/read-only for #2046/#2047 under #2045; any failures there produce prerequisite drift follow-up work, not unauthorized edits under #2045.
   245|---
   246|
   247|## Adversarial Review Summary
   248|
   249|| Date | Provider | Verdict | Status |
   250||---|---|---|---|
   251|| 2026-04-14 | Codex | MAJOR | Superseded by later re-review waves; initial blocker set addressed in subsequent revisions |
   252|| 2026-04-14 | Gemini | MAJOR | Superseded by later re-review waves; initial blocker set addressed in subsequent revisions |
   253|| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified and incorporated in later revisions |
   254|| 2026-04-15 | Codex re-review waves | MAJOR | Remaining blockers narrowed over waves from broad governance defects to localized contract-precision items; latest active blockers should be taken from the newest artifact, not these older summary rows |
   255|
   256|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`
   257|
   258|**Current status:** Re-review required to confirm remaining MAJOR findings are resolved. Three-provider artifact set now exists.
   259|
   260|---
   261|
   262|## Risks and Open Questions
   263|
   264|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   265|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   266|- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
   267|- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
   268|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   269|- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.
   270|
   271|---
   272|
   273|## Complexity: T2
   274|
   275|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   276|
```
