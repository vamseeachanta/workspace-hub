# Adversarial Re-Review Request: Issue #2045

You are an independent adversarial reviewer. Evaluate the CURRENT plan text only. Find any remaining gaps, unresolved decisions, weak retrieval, non-falsifiable tests/acceptance criteria, or workflow/governance violations. Do NOT rubber-stamp.

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
     6|> **Last revised:** 2026-04-15
     7|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2045
     8|> **Review artifacts:** scripts/review/results/2026-04-14-plan-2045-codex.md | scripts/review/results/2026-04-14-plan-2045-gemini.md | scripts/review/results/2026-04-15-plan-2045-claude.md | scripts/review/results/2026-04-15-plan-2045-codex-rereview19.md
     9|
    10|---
    11|
    12|## Resource Intelligence Summary
    13|
    14|### Existing repo code
    15|- Found: `.claude/skills/coordination/issue-planning-mode/SKILL.md` is the canonical repo skill for the workflow and must be treated as a primary onboarding surface.
    16|- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` extends the planning workflow for engineering-critical issues.
    17|- Found: `docs/plans/_template-issue-plan.md` defines the canonical minimum plan structure and currently uses `## Adversarial Review Summary`, so #2045 must not invent a conflicting repo-wide heading rule without updating the template.
    18|- Found: `docs/plans/README.md` is both onboarding guide and plan index and defines the live approval sequence (`status:plan-review` -> user approval -> `status:plan-approved`).
    19|- Found: `docs/standards/HARD-STOP-POLICY.md` defines the hard boundary that implementation must not begin before approval.
    20|- Found: `.claude/hooks/plan-approval-gate.sh` is the live local gate enforcing the no-implementation-before-approval boundary; it is authoritative only for local gate behavior and safe-path assumptions, not for GitHub-side approval semantics.
    21|- Found: `.codex/CODEX.md` still contains legacy WRK-* / work-queue references that conflict with the GitHub issue planning workflow in `AGENTS.md`.
    22|- Found: `GEMINI.md` reaches workflow guidance via canonical shared-doc references and may still contain stale workflow references; under #2045 it should be validation-only unless a contradiction is found.
    23|- Found: `docs/standards/AI_REVIEW_ROUTING_POLICY.md` defines default multi-provider review expectations.
    24|- Found: `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` constrains how agents and subagents should be framed.
    25|- Found: GitHub labels `status:plan-review` and `status:plan-approved` are the authoritative live workflow labels, with semantics defined by `docs/plans/README.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md`.
    26|
    27|### Standards
    28|- `AGENTS.md` — repo hard-gate order and mandatory workflow statement.
    29|- `docs/plans/README.md` — plan workflow contract.
    30|- `docs/standards/HARD-STOP-POLICY.md` — hard-stop approval/implementation boundary authority.
    31|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — review routing and multi-provider expectations.
    32|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` — agent-context handling policy.
    33|
    34|### Documents consulted
    35|- GitHub issue #2045 body — scope and acceptance criteria (`all agents`, `at least 3 real issue plans created using the template and labels`)
    36|- `CLAUDE.md`
    37|- `AGENTS.md`
    38|- `GEMINI.md`
    39|- `.codex/CODEX.md`
    40|- `.codex/config.toml`
    41|- `config/agents/hermes/SOUL.md`
    42|- `docs/plans/README.md`
    43|- `docs/plans/_template-issue-plan.md`
    44|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    45|- `.claude/skills/coordination/engineering-issue-workflow/SKILL.md`
    46|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    47|- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`
    48|- `docs/standards/HARD-STOP-POLICY.md`
    49|- GitHub labels `status:plan-review` and `status:plan-approved` (authoritative live workflow labels)
    50|- GitHub issue #2045 comments/labels as the fixed operational sample
    51|- related plans in `docs/plans/`, especially #2046 and #2047
    52|
    53|### Gaps identified
    54|- Current onboarding coverage is uneven across agent-facing surfaces; the repo must explicitly define what “all agents” means in-repo.
    55|- The previous plan incorrectly assumed `.claude/skills/` edits were blocked by the plan gate.
    56|- The previous plan waived adversarial review even though the issue’s purpose is universal planning/review adoption.
    57|- Example-plan validation and label/template verification need concrete checks rather than “manual only” wording.
    58|
    59|### Authoritative in-repo onboarding surfaces
    60|
    61|"All agents" means the in-repo provider entry surfaces explicitly named by issue #2045 at planning time: Claude, Gemini, Codex, and Hermes. This issue closes when those four current providers have an actionable onboarding path; any provider added later is out of scope for #2045 and should trigger follow-up onboarding work.
    62|
    63|| Agent | Dedicated entry surface | Shared surfaces | How workflow reaches this agent | Onboarding gap |
    64||---|---|---|---|---|
    65|| Claude Code | `CLAUDE.md` (planning workflow, skill loading) | `AGENTS.md`, `docs/plans/README.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md` | `CLAUDE.md` → references `AGENTS.md` gates and skill path directly | None — most complete onboarding chain |
    66|| Gemini | `GEMINI.md` (retrieval-first, gate evidence anchors) | `AGENTS.md`, `docs/plans/README.md` | `GEMINI.md` may satisfy onboarding by an explicit canonical reference to the shared planning contract, but must not point to deprecated workflow docs; modify only if validation finds stale or contradictory guidance | Validation-only by default; explicit canonical-reference path is acceptable for closure |
    67|| Codex | `.codex/CODEX.md` (explicit Required Gates section), `.codex/config.toml` (TDD in role prompts) | `AGENTS.md`, `docs/plans/README.md` | `CODEX.md` carries gate order directly; `config.toml` role prompts reference TDD and `.claude/rules/` | `CODEX.md` is implementation-scope; `config.toml` validation-only unless contradiction found |
    68|| Hermes | `config/agents/hermes/SOUL.md` | `AGENTS.md`, `docs/plans/README.md` | today Hermes only reaches workflow context through shared repo docs and explicit prompt loading; `SOUL.md` itself contains no workflow contract | **Gap:** this issue will close that gap by adding an explicit planning-workflow reference to `config/agents/hermes/SOUL.md`. Shared-doc-only onboarding is not sufficient for closure. |
    69|
    70|### Three-real-plans workstream
    71|
    72|The issue body requires that at least three real issue plans are created using the template and labels. For #2045, that requirement is satisfied by the existence of three concrete issue-plan artifacts (#2045, #2046, #2047) plus a read-only validation pass that they are recognizable, issue-specific plans rather than empty template stubs. #2045 does **not** take ownership of remediating semantic defects inside #2046/#2047; any such defects become follow-up work on those issues rather than blockers on #2045.
    73|
    74|| Plan role | File | Validation expectation |
    75||---|---|---|
    76|| Onboarding spec (this issue) | `docs/plans/2026-04-09-issue-2045-agent-planning-onboarding.md` | Must define the workflow and validation contract |
    77|| Exemplar read 1 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` | Must exist as a real issue plan and pass the read-only minimum-bar validation; drift becomes follow-up work on #2046 |
    78|| Exemplar read 2 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` | Must exist as a real issue plan and pass the read-only minimum-bar validation; drift becomes follow-up work on #2047 |
    79|
    80|**Validation rule:** `test_issue_2045_example_plans.sh` uses the single authoritative heading list below and verifies issue-specific/non-placeholder content. Under #2045, failures in #2046/#2047 above the minimum bar are advisory prerequisite drift findings that trigger follow-up work rather than blocking #2045 through unauthorized edits.
    81|
    82|---
    83|
    84|## Artifact Map
    85|
    86|| Artifact | Path |
    87||---|---|
    88|| CLAUDE entry surface | `CLAUDE.md` |
    89|| AGENTS entry surface | `AGENTS.md` |
    90|| Gemini entry surface | `GEMINI.md` |
    91|| Codex repo config surface | `.codex/config.toml` |
    92|| Onboarding/index guide | `docs/plans/README.md` |
    93|| Planning template | `docs/plans/_template-issue-plan.md` |
    94|| Core skill | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
    95|| Engineering extension | `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` |
    96|| Review-routing policy | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` |
    97|| Subagent isolation policy | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` |
    98|| Example plan #2046 | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
    99|| Example plan #2047 | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
   100|
   101|---
   102|
   103|## Deliverable
   104|
   105|Updated repo onboarding surfaces, core planning skill guidance, and a validated onboarding contract so Claude, Codex, Gemini, and Hermes each have a discoverable path to the same strict planning workflow, with explicit gate-order expectations and actionable references to review-routing plus template/label conventions.
   106|
   107|---
   108|
   109|## Pseudocode
   110|
   111|```text
   112|# 1. Write validation scripts first (TDD)
   113|for each of the 5 repo-content validation scripts:
   114|    write script that checks the specific condition (see TDD Test List)
   115|    require RED evidence for at least these targeted gaps before remediation:
   116|        - `.codex/CODEX.md` legacy workflow contradiction check
   117|        - `.claude/skills/` safe-path false-blocker check if the stale claim is still present
   118|        - skill-alignment numbering/order check when duplicate/misnumbered workflow steps exist
   119|    validation-only checks may start green if the repo is already compliant; record that explicitly in evidence logs
   120|
   121|# 2. Fix onboarding surfaces to pass validation
   122|for surface in [CLAUDE.md, AGENTS.md, GEMINI.md, .codex/CODEX.md, config/agents/hermes/SOUL.md, docs/plans/README.md, issue-planning-mode SKILL.md]:
   123|    if repo-content validation fails on this surface:
   124|        apply the minimal in-scope fix needed for a deterministic pass
   125|
   126|# 3. Validate exemplar plan set (read-only for #2046/#2047)
   127|run test_issue_2045_example_plans.sh
   128|if the current #2045 plan is missing a normalized heading or issue-specific content:
   129|    fix this plan file
   130|if #2046 or #2047 fail minimum-bar validation:
   131|    record the failure as prerequisite drift to be corrected under their own governance path; do not rewrite them under #2045
   132|
   133|# 4. Validate policy alignment and skill alignment
   134|run test_issue_2045_policy_alignment.sh
   135|run test_issue_2045_skill_alignment.sh
   136|if contradiction found in .codex/CODEX.md, .codex/config.toml, GEMINI.md, or policy docs:
   137|    fix the contradiction in files that are in #2045 implementation scope; otherwise record no-op
   138|
   139|# 5. Confirm all 5 repo-content scripts exit 0 with pipefail-enabled execution; collect canonical evidence artifacts
   140|
   141|# 6. Optional operator validation (non-blocking for repo-content completion)
   142|if gh auth is available and live workflow verification is desired:
   143|    run test_issue_2045_operational_workflow.sh
   144|    record whether issue #2045 is in an allowed policy state and whether approval evidence is grounded in cited repo policy
   145|```
   146|
   147|---
   148|
   149|## Files to Change
   150|
   151|### Implementation scope (onboarding surface alignment)
   152|
   153|| Action | Path | Decision rule | Reason |
   154||---|---|---|---|
   155|| Modify | `CLAUDE.md` | If `CLAUDE.md` does not reference `AGENTS.md` or the planning workflow skill path, add the reference | Ensure Claude sessions discover the planning workflow |
   156|| Modify | `AGENTS.md` | If hard-gate statement does not match the canonical order (Issue → Plan → USER APPROVES → Implement → Cross-review → Close), correct it | `AGENTS.md` is the canonical source; it must be authoritative |
   157|| Modify | `.codex/CODEX.md` | Correct legacy WRK-* / work-queue references and align explicit gate-order / wait-for-approval wording with `AGENTS.md` | Codex onboarding currently contains active workflow contradictions, not just a passive missing reference |
   158|| Modify | `config/agents/hermes/SOUL.md` | Add explicit planning-workflow / `AGENTS.md` reference so Hermes has a dedicated onboarding surface | Close the Hermes onboarding gap concretely |
   159|| Modify only if contradiction found | `GEMINI.md` | Fix deprecated workflow references or missing canonical planning-contract reference only if validation finds them | Gemini is validation-first, not mandatory-edit-by-default |
   160|| Modify | `docs/plans/README.md` | Update plan index to include #2045, #2046, #2047 entries and ensure onboarding guide text matches `AGENTS.md` gate order | README is both index and onboarding guide |
   161|| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | If skill workflow steps diverge from `AGENTS.md` gate order, correct the skill and remove duplicate/misnumbered workflow blocks as needed | Canonical skill must match canonical contract cleanly |
   162|| Add tests | `tests/test_issue_2045_*.sh` (6 scripts) | Create the validation scripts listed in TDD Test List | Executable evidence of onboarding correctness |
   163|
   164|### Validation-only (no change unless contradiction found)
   165|
   166|Each file below is checked by `test_issue_2045_policy_alignment.sh`. The decision rule is: **modify only if the file states a gate order, approval rule, or subagent-context rule that directly contradicts `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, or `issue-planning-mode/SKILL.md`.** Example contradictions that must fail the test: a file saying implementation can begin before explicit user approval, a file reversing the workflow order, or a file routing agent work to deprecated WRK-* workflow surfaces instead of GitHub issue planning.
   167|
   168|| Action | Path | Decision rule |
   169||---|---|---|
   170|| Validate | `.codex/config.toml` | Modify only if role system prompts contradict `AGENTS.md` gate order or point to deprecated workflow surfaces; otherwise record why validation-only is acceptable despite CODEX.md being implementation-scope |
   171|| Validate | `docs/standards/AI_REVIEW_ROUTING_POLICY.md` | Modify only if review-routing text contradicts the onboarding surfaces' review expectations |
   172|| Validate | `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md` | Modify only if isolation policy contradicts how onboarding surfaces frame subagent context |
   173|| Validate | `GEMINI.md` stale workflow references | Modify only if referenced workflow surfaces are deprecated or contradict the current planning contract |
   174|| Validate only (no edits under #2045) | Three plan files (#2045, #2046, #2047) | `test_issue_2045_example_plans.sh` may inspect all three, but under #2045 only this plan file may be edited; issues #2046/#2047 are exemplar reads, not automatic rewrite targets |
   175|
   176|---
   177|
   178|### Exact required heading set for exemplar-plan validation
   179|
   180|The single authoritative heading list for `test_issue_2045_example_plans.sh` is derived from `docs/plans/_template-issue-plan.md` and, until the template itself is changed, uses the template's canonical review heading:
   181|1. `> **Status:**`
   182|2. `> **Review artifacts:**`
   183|3. `## Resource Intelligence Summary`
   184|4. `## Artifact Map`
   185|5. `## Deliverable`
   186|6. `## Pseudocode`
   187|7. `## Files to Change`
   188|8. `## TDD Test List`
   189|9. `## Acceptance Criteria`
   190|10. `## Adversarial Review Summary`
   191|11. `## Risks and Open Questions`
   192|12. `## Complexity`
   193|
   194|This list is the sole section oracle for #2045’s exemplar-plan validation; pseudocode, tests, and acceptance criteria must all point back to this exact list.
   195|
   196|## TDD Test List
   197|
   198|| Test name | What it checks | Concrete check method | Pass criteria | Fail criteria | Evidence artifact |
   199||---|---|---|---|---|---|
   200|| `test_issue_2045_onboarding_docs.sh` | Every provider entry surface has a deterministic, actionable planning-workflow discovery path | exact accepted patterns are enumerated here: `AGENTS.md` must contain the literal gate-order chain `Issue → Plan → USER APPROVES → Implement → Cross-review → Close`; `CLAUDE.md` must reference `.claude/skills/coordination/issue-planning-mode/SKILL.md` or contain the gate-order chain; `GEMINI.md` must either contain `Canonical instructions: AGENTS.md` or explicit workflow markers and must not reference deprecated workflow docs; `.codex/CODEX.md` must include explicit gate/order language and must not reference deprecated WRK-* workflow surfaces; `config/agents/hermes/SOUL.md` must explicitly reference `AGENTS.md` or `docs/plans/README.md` as the planning workflow source | Each file matches its allowed exact pattern and provides an actionable current path to the workflow source | Any file lacks its required direct marker or canonical-contract reference, or still points to deprecated workflow surfaces | `tests/evidence/2045-onboarding-docs.log` |
   201|| `test_issue_2045_example_plans.sh` | The exemplar plan set proves the issue-body minimum bar of three real plans created using the template/labels | Use the single authoritative heading list above. For #2045, #2046, and #2047: check that all 12 required headings are present; reject placeholder/template stubs; verify Deliverable mentions the issue-specific objective, Files to Change lists issue-relevant paths, and Acceptance Criteria contain issue-specific checks rather than generic boilerplate. Under #2045 this test is read-only for #2046/#2047 and must not mutate them. | #2045 passes the 12-heading oracle and exemplar reads #2046/#2047 each clear the minimum bar for a real issue plan (not a stub); any additional semantic drift beyond that minimum bar is logged as follow-up work, not a #2045 blocker | Any required heading missing in #2045, placeholder stub remains, or an exemplar is still only a template-like stub rather than a real issue plan | `tests/evidence/2045-example-plans.log` with per-file structural + minimum-bar semantic pass/fail matrix plus advisory drift notes for #2046/#2047 |
   202|| `test_issue_2045_policy_alignment.sh` | Onboarding docs do not contradict review-routing or subagent-isolation policies | compare canonical workflow order from `AGENTS.md`, `docs/standards/HARD-STOP-POLICY.md`, and `.claude/skills/coordination/issue-planning-mode/SKILL.md` against `CLAUDE.md`, `GEMINI.md`, `.codex/config.toml`, `config/agents/hermes/SOUL.md`; fail if any surface permits implementation before explicit user approval or routes work to deprecated workflow surfaces | No contradictions found; each file either matches or is updated to match | Any file states a conflicting gate order, approval rule, or deprecated workflow route | `tests/evidence/2045-policy-alignment.log` |
   203|| `test_issue_2045_safe_path_assumption.sh` | No in-scope onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate | search the full in-scope surface list: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`, `docs/plans/README.md`, `config/agents/hermes/SOUL.md`, `.claude/skills/coordination/issue-planning-mode/SKILL.md`; fail on any text asserting that `.claude/skills/` or `.claude/*` edits are blocked by the plan gate | Zero prohibited claims across the full in-scope surface list | Any prohibited claim found in any in-scope onboarding surface | `tests/evidence/2045-safe-path.log` |
   204|| `test_issue_2045_skill_alignment.sh` | `.claude/skills/coordination/issue-planning-mode/SKILL.md` matches `AGENTS.md` gate order without duplicate/misnumbered workflow steps | compare explicit workflow chain in `AGENTS.md` to the skill’s step/order text and assert no duplicate step numbers remain in the planning workflow section | skill order matches canonical order and duplicate/misnumbered workflow steps are absent | order mismatch or duplicated numbering remains | `tests/evidence/2045-skill-alignment.log` |
   205|| `test_issue_2045_operational_workflow.sh` | Optional operator-run verification of live GitHub workflow state | require authenticated `gh`; verify via `gh issue view 2045 --json comments,labels` plus `docs/plans/README.md` and `issue-planning-mode/SKILL.md` that: (a) a GitHub plan comment exists referencing the plan artifact path, and (b) the issue is in one of two allowed policy states — pre-approval (`status:plan-review` present, `status:plan-approved` absent) or post-approval (`status:plan-approved` plus explicit human approval evidence as defined by repo policy) | when run, the sample workflow passes one allowed policy state and the approval-evidence rule is grounded in cited repo policy text | missing plan comment, invalid label state, approval evidence rule not grounded in cited policy text, or missing `gh` auth prerequisite | `tests/evidence/2045-operational-workflow.log` |
   206|
   207|### Evidence ownership
   208|
   209|- The `tests/evidence/*.log` files created by the execution block are the canonical evidence artifacts.
   210|- Individual test scripts should print deterministic stdout for piping, but should not separately write conflicting artifact files unless explicitly documented.
   211|
   212|### Execution
   213|
   214|```bash
   215|set -euo pipefail
   216|
   217|# Run all validation scripts; each writes its own evidence artifact
   218|bash tests/test_issue_2045_onboarding_docs.sh      | tee tests/evidence/2045-onboarding-docs.log
   219|bash tests/test_issue_2045_example_plans.sh        | tee tests/evidence/2045-example-plans.log
   220|bash tests/test_issue_2045_policy_alignment.sh     | tee tests/evidence/2045-policy-alignment.log
   221|bash tests/test_issue_2045_safe_path_assumption.sh | tee tests/evidence/2045-safe-path.log
   222|bash tests/test_issue_2045_skill_alignment.sh      | tee tests/evidence/2045-skill-alignment.log
   223|bash tests/test_issue_2045_operational_workflow.sh | tee tests/evidence/2045-operational-workflow.log
   224|```
   225|
   226|All six scripts must exit 0. Any non-zero exit blocks #2045 closure.
   227|
   228|---
   229|
   230|## Acceptance Criteria
   231|
   232|### Implementation completion (required to close #2045)
   233|
   234|Repo-content validations:
   235|- [ ] `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.codex/CODEX.md`, and `config/agents/hermes/SOUL.md` each reference the planning workflow such that `test_issue_2045_onboarding_docs.sh` exits 0.
   236|- [ ] `.claude/skills/coordination/issue-planning-mode/SKILL.md` workflow steps match `AGENTS.md` gate order and pass `test_issue_2045_skill_alignment.sh`.
   237|- [ ] No onboarding surface falsely claims `.claude/skills/` is blocked by the plan gate (`test_issue_2045_safe_path_assumption.sh` exits 0).
   238|- [ ] Three plan artifacts exist and are validated against the single 12-heading oracle above; #2045 itself must pass and #2046/#2047 must each clear the minimum bar for a real issue plan, while any additional drift is recorded as follow-up work rather than unauthorized edit scope (`test_issue_2045_example_plans.sh`).
   239|- [ ] Validation-only surfaces (policy docs, validation-only Gemini/config prompts) either pass `test_issue_2045_policy_alignment.sh` with no contradictions, or contradictions are fixed and re-tested.
   240|- [ ] All six canonical evidence artifacts exist in `tests/evidence/` and record PASS / exit-0 results for the executed repo-content validation scripts.
   241|
   242|Optional operator validation before closing live issue state:
   243|- [ ] If run during live workflow verification, `test_issue_2045_operational_workflow.sh` confirms the GitHub issue is in one allowed policy state (pre-approval or post-approval with explicit human approval evidence) and that the result is grounded in cited repo policy text. Missing `gh` auth blocks this operator check, but does not change repo-content completion.
   244|- It is not part of the six repo-content validation scripts and does not block repo-content completion when `gh` auth is unavailable.
   245|- When run with valid auth, it must report whether issue #2045 is in an allowed policy state and whether approval evidence is grounded in cited repo policy.
   246|
   247|### Plan approval gate (required before implementation begins)
   248|
   249|- [ ] Three-provider adversarial review set is complete for the current plan revision identified by `Last revised: 2026-04-15` and the exact `Review artifacts` line above; each required provider artifact must be listed there and cover the current revision by explicit inclusion in that authoritative artifact set, not by date alone.
   250|- [ ] No unresolved MAJOR findings remain.
   251|- [ ] The onboarding standard is explicit: each provider entry surface either contains the required workflow markers directly or names the canonical shared contract in a testable way.
   252|- [ ] `.codex/CODEX.md` contradictions are fixed in implementation scope; `.codex/config.toml` remains validation-only only if `test_issue_2045_policy_alignment.sh` shows no contradictory workflow behavior.
   253|- [ ] The issue-body `3 real plans` requirement is satisfied by the existence + minimum-bar validation of #2045/#2046/#2047 for the four providers named in the issue body at planning time; additional exemplar drift beyond that minimum bar becomes follow-up work on the owning issues rather than #2045 rewrite scope.
   254|---
   255|
   256|## Adversarial Review Summary
   257|
   258|| Date | Provider | Verdict | Status |
   259||---|---|---|---|
   260|| 2026-04-14 | Codex | MAJOR | Superseded by later re-review waves; initial blocker set addressed in subsequent revisions |
   261|| 2026-04-14 | Gemini | MAJOR | Superseded by later re-review waves; initial blocker set addressed in subsequent revisions |
   262|| 2026-04-15 | Claude | MINOR | Bounded follow-ups identified and incorporated in later revisions |
   263|| 2026-04-15 | Codex re-review waves | MAJOR | Remaining blockers narrowed over waves from broad governance defects to localized contract-precision items; latest active blockers should be taken from the newest artifact, not these older summary rows |
   264|
   265|Full review artifacts: `scripts/review/results/2026-04-14-plan-2045-codex.md`, `scripts/review/results/2026-04-14-plan-2045-gemini.md`, `scripts/review/results/2026-04-15-plan-2045-claude.md`, latest Codex rereview artifact `scripts/review/results/2026-04-15-plan-2045-codex-rereview19.md`, plus any newer current-revision provider rereviews collected before approval.
   266|
   267|**Current status:** Re-review required until the newest authoritative provider artifact set reduces the blocker set to MINOR/APPROVE for the current revision.
   268|
   269|---
   270|
   271|## Risks and Open Questions
   272|
   273|- **Risk:** “all agents” scope creep — a new provider added to the repo without updating the onboarding-surface table silently breaks the completeness claim. Mitigation: the table header states new providers must be added before #2045 is complete.
   274|- **Risk:** example plans (#2046, #2047) may drift from the template after #2045 closes. Mitigation: `test_issue_2045_example_plans.sh` can be rerun as a regression check; consider promoting to CI if drift becomes a pattern.
   275|- **Risk:** provider onboarding can still drift if one adapter only references canonical shared docs while another embeds the workflow directly. Mitigation: `test_issue_2045_onboarding_docs.sh` and `test_issue_2045_policy_alignment.sh` accept either direct workflow markers or an explicit canonical-contract reference, but reject deprecated workflow routes.
   276|- **Risk:** `.codex/CODEX.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` contain legacy/structural drift beyond simple gate-order wording. Mitigation: both are now in implementation scope or explicit skill-alignment coverage.
   277|- **Resolved:** false safe-path blocker claim — corrected in resource intelligence; `test_issue_2045_safe_path_assumption.sh` prevents regression.
   278|- **Resolved:** missing Claude review artifact — `scripts/review/results/2026-04-15-plan-2045-claude.md` now exists and is included in the three-provider review set.
   279|
   280|---
   281|
   282|## Complexity: T2
   283|
   284|**T2** — multi-surface governance/onboarding alignment across docs, skills, and example-plan validation.
   285|
```
