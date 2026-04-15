     1|# Adversarial Claude Plan Review Request: Issue #2046
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
    17|Issue: #2046
    18|Issue title: Audit compliance of strict issue planning workflow after rollout
    19|Issue URL: https://github.com/vamseeachanta/workspace-hub/issues/2046
    20|
    21|GitHub issue body:
    22|After the new strict planning workflow has been used for a short period, audit compliance across agent activity.
    23|
    24|Audit focus:
    25|- Was `issue-planning-mode` used for all issues?
    26|- Were plans created in `docs/plans/` using the template?
    27|- Were adversarial reviews completed before user review?
    28|- Were labels `status:plan-review` and `status:plan-approved` used correctly?
    29|- Did any agent begin coding before approval?
    30|
    31|Deliverables:
    32|- Markdown report under `docs/reports/`
    33|- Compliance summary with examples
    34|- Gaps, failure modes, and recommendations
    35|- Decision: keep current approach or escalate enforcement
    36|
    37|Suggested trigger:
    38|- Run after 1-2 weeks of usage or after at least 10 issues have gone through the new workflow
    39|
    40|Plan under review:
    41|
    42|```markdown
    43|     1|# Plan for #2046: Audit Compliance of Strict Issue Planning Workflow After Rollout
     2|
     3|> **Status:** draft
     4|> **Complexity:** T2
     5|> **Date:** 2026-04-09
     6|> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2046
     7|> **Review artifacts:** scripts/review/results/2026-04-14-plan-2046-codex.md | scripts/review/results/2026-04-14-plan-2046-gemini.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `.claude/skills/coordination/workflow-compliance-audit/` already documents a broader evidence model than the previous plan used.
    15|- Found: `.claude/hooks/plan-approval-gate.sh` and `scripts/enforcement/require-plan-approval.sh` are enforcement surfaces whose logs/state should be treated as audit evidence where available.
    16|- Found: `docs/plans/README.md` defines status ordering and plan-review/plan-approved semantics that this audit must verify explicitly.
    17|- Found: `.planning/plan-approved/<issue>.md` marker files are local evidence only and must be reconciled against GitHub timeline state rather than treated as sufficient on their own.
    18|- Found: `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` already exists as the canonical report surface and should be refreshed, not duplicated.
    19|- Gap: there is still no script that builds a per-issue evidence matrix proving chronology between review, approval, and implementation.
    20|
    21|### Standards
    22|- `AGENTS.md` — hard-gate order and TDD expectation.
    23|- `docs/plans/README.md` — planning workflow contract and status precedence.
    24|- `docs/standards/HARD-STOP-POLICY.md` — engineering-critical enforcement policy.
    25|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — adversarial review expectations.
    26|
    27|### Documents consulted
    28|- GitHub issue #2045 — onboarding baseline / rollout origin
    29|- GitHub issue #2047 — likely escalation path if audit fails
    30|- `docs/plans/README.md`
    31|- `docs/standards/HARD-STOP-POLICY.md`
    32|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    33|- `docs/governance/TRUST-ARCHITECTURE.md`
    34|- `docs/reports/2026-04-09-planning-workflow-compliance-audit.md`
    35|- `.claude/skills/coordination/workflow-compliance-audit/SKILL.md`
    36|- `.claude/hooks/plan-approval-gate.sh`
    37|- `scripts/enforcement/require-plan-approval.sh`
    38|
    39|### Gaps identified
    40|- Current plan logic still over-relies on artifact presence and commit timestamps instead of chronology and evidence confidence.
    41|- No authoritative policy matrix is yet defined for engineering-critical, non-engineering, mixed, and legacy issue cohorts.
    42|- No fixture corpus yet covers retroactive labels, malformed review artifacts, marker/label mismatches, or commits without issue references.
    43|
    44|### Cohort policy matrix
    45|| Cohort | Inclusion rule | Compliance rule |
    46||---|---|---|
    47|| Engineering-critical | Issue has engineering-critical labels and entered planning workflow after #2045 rollout | Must prove plan artifact, adversarial review, `status:plan-review`, `status:plan-approved`, approval marker, and no implementation evidence before approval |
    48|| Non-engineering | Non-engineering issue entered planning workflow after #2045 rollout | Must prove same planning/review/approval sequence, but report separately from engineering-critical cohort |
    49|| Legacy / pre-rollout | Issue activity predates rollout or cannot be shown to have entered planning after rollout | Excluded from primary denominator; report separately |
    50|| Mixed / ambiguous | Conflicting evidence on cohort or sequencing | Included only as `indeterminate` unless stronger evidence resolves classification |
    51|
    52|### Evidence model for `issue-planning-mode` usage
    53|
    54|| Tier | Source | What it proves | Outcome if present | Outcome if absent |
    55||---|---|---|---|---|
    56|| **Authoritative** | Session transcript or hook log showing `/skill issue-planning-mode` or `.claude/skills/coordination/issue-planning-mode/SKILL.md` load event | Skill was invoked in the session | **compliant** for skill-usage dimension | Fall to secondary |
    57|| **Secondary** | Plan artifact in `docs/plans/` matching `*-issue-NNNN-*.md` that contains all required template sections (status header, Resource Intelligence, Artifact Map, TDD Test List, Acceptance Criteria, Adversarial Review) AND correctly sequenced review/approval artifacts exist | Workflow was followed even if skill invocation cannot be directly proven | **compliant** (inferred) for skill-usage dimension | Fall to fallback |
    58|| **Fallback** | GitHub issue comment or audit report text describing workflow steps performed, with timestamps consistent with plan/review/approval order | Workflow intent was present but artifacts are incomplete | **indeterminate** — count separately, do not count as compliant or non-compliant | **non-compliant** for skill-usage dimension |
    59|
    60|**Rule:** an issue classified as `indeterminate` on skill-usage is still evaluated on all other compliance dimensions (chronology, approval, review). Indeterminate on one dimension does not exempt the issue from the audit.
    61|
    62|### Audited population definition
    63|
    64|**Rollout boundary:** 2026-04-08 21:54 CST — commit `2bc0f4673` (full onboarding per #2045). This is the canonical cutoff; issues with implementation activity before this timestamp are pre-rollout.
    65|
    66|**Trigger threshold:** run the audit once at least 10 issues have received implementation commits post-rollout, OR 14 calendar days after rollout, whichever comes first. Per the existing audit report, 10 issues were already identified by 2026-04-09.
    67|
    68|**In-scope query:**
    69|```bash
    70|# All issues with implementation commits after rollout
    71|git log --oneline --after="2026-04-08T21:54:00" --no-merges --format="%s" \
    72|  | grep -oP '#\d+' | sort -u
    73|# Cross-reference with GitHub issue state
    74|gh issue list --state all --limit 500 --json number,labels,createdAt
    75|```
    76|
    77|**Inclusion rule:** an issue is in-scope if it has at least one implementation commit (non-docs, non-plan, non-config-only) after the rollout boundary.
    78|
    79|**Exclusion rules:**
    80|- Issues with only documentation or plan-file commits (no implementation code) — excluded as non-implementation.
    81|- Issues created and closed entirely before the rollout boundary — excluded as pre-rollout.
    82|- Issues with mixed pre/post-rollout activity: include only post-rollout commits in the chronology check. If all implementation commits are pre-rollout, exclude.
    83|
    84|**Minimum issue-count rule:** if fewer than 10 issues are in-scope at audit time, the audit still runs but the report must note the low sample size and flag that statistical conclusions are unreliable.
    85|
    86|### Approval signal precedence
    87|1. GitHub timeline evidence showing `status:plan-approved` added after review/user-approval event.
    88|2. Local `.planning/plan-approved/<issue>.md` marker as corroborating local evidence only.
    89|3. If GitHub and local signals disagree, classify by the stronger timeline evidence and report the conflict explicitly.
    90|
    91|### `status:plan-approved` usage and misuse checks
    92|
    93|The label `status:plan-approved` has specific semantics defined in `docs/plans/README.md`. The audit must check:
    94|
    95|| Check | What it detects | Classification if failed |
    96||---|---|---|
    97|| `status:plan-approved` applied without prior `status:plan-review` | Approval without review phase | **non-compliant** |
    98|| `status:plan-approved` applied by an agent (not the user) | Self-approval / no human gate | **non-compliant** |
    99|| `status:plan-approved` applied but no review artifacts exist in `scripts/review/results/` | Approval without adversarial review evidence | **non-compliant** |
   100|| `status:plan-approved` applied retroactively after implementation commits already exist | Post-hoc approval (label applied to legitimize already-done work) | **non-compliant** |
   101|| `status:plan-approved` never applied to an issue that has implementation commits | Missing approval entirely | **non-compliant** |
   102|| `.planning/plan-approved/<issue>.md` marker exists but `status:plan-approved` label was never applied | Local-only approval, not visible on GitHub | **indeterminate** — report the discrepancy |
   103|
   104|**Note from existing audit:** as of 2026-04-09, `status:plan-approved` has never been applied to any issue in the repository. The audit must verify whether this has changed at audit execution time.
   105|
   106|### Definition: "agent began coding before approval"
   107|
   108|An issue is classified as having **implementation before approval** if any of the following are true:
   109|
   110|1. **Commit evidence:** a commit referencing `#NNNN` touches files outside the safe-path list (not `docs/plans/`, not `scripts/review/results/`, not `.planning/`, not `CLAUDE.md`/`GEMINI.md`/`AGENTS.md`) AND the commit timestamp is earlier than the earliest approval evidence (either `status:plan-approved` label event or `.planning/plan-approved/<issue>.md` marker commit).
   111|2. **File-change evidence:** files in `src/`, `scripts/enforcement/`, `.claude/hooks/`, `tests/` (implementation paths) were modified in commits referencing the issue before any approval signal.
   112|3. **Session evidence (when available):** agent session transcript shows code generation or file writes for the issue before plan approval was granted.
   113|
   114|**Safe-path exclusion:** changes to plan files, review artifacts, documentation, and adapter configs (`CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`) are not implementation — they are planning activity and do not trigger implementation-before-approval classification.
   115|
   116|### Plan-revision matching rules
   117|
   118|Review artifacts must correspond to the plan revision that was actually approved. The audit must check:
   119|
   120|1. **Revision date match:** the review artifact filename contains a date (`YYYY-MM-DD`) that is on or after the plan file's most recent substantive edit (determined by `git log -1 --format="%ai" -- docs/plans/*-issue-NNNN-*.md`).
   121|2. **Content hash match (when available):** if the review artifact references a plan hash or revision identifier, it must match the approved plan's content at the time of review.
   122|3. **Stale review detection:** if the plan was substantively edited after the review artifact was created (new sections added, acceptance criteria changed, TDD list modified), the review is **stale** and the issue is classified as **indeterminate** on the review dimension until re-reviewed.
   123|4. **No review artifact at all:** if no review artifact exists for the issue, the review dimension is **non-compliant** regardless of other evidence.
   124|
   125|### Decision rubric
   126|
   127|After the audit completes, the report must include an explicit recommendation using this rubric:
   128|
   129|| Compliance rate | Indeterminate rate | Recommendation |
   130||---|---|---|
   131|| ≥80% compliant AND <10% indeterminate | Low | **Keep current approach** — workflow is adopted and enforcement is working |
   132|| 50–79% compliant OR 10–25% indeterminate | Moderate | **Tighten guidance** — update onboarding surfaces, add enforcement logging, re-audit in 2 weeks |
   133|| <50% compliant OR >25% indeterminate | High | **Escalate enforcement** — trigger #2047 escalation, consider promoting `compliance-dashboard` from advisory to blocking, add CI-level hard gates |
   134|
   135|The rubric applies per-cohort. Engineering-critical issues failing at any level trigger escalation regardless of the overall rate. The report must state which rubric row was selected and why.
   136|
   137|---
   138|
   139|## Artifact Map
   140|
   141|| Artifact | Path |
   142||---|---|
   143|| This plan | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
   144|| Audit script | `scripts/enforcement/audit_planning_compliance.py` |
   145|| Fixture corpus | `tests/fixtures/planning-compliance/` |
   146|| Script tests | `tests/enforcement/test_audit_planning_compliance.py` |
   147|| Canonical report | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` |
   148|| Workflow audit reference | `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` |
   149|| Review artifacts | `scripts/review/results/2026-04-14-plan-2046-codex.md` and `scripts/review/results/2026-04-14-plan-2046-gemini.md` |
   150|
   151|---
   152|
   153|## Deliverable
   154|
   155|A reproducible compliance-audit plan that defines a per-issue evidence matrix, verifies timeline sequencing for plan-review/review/approval/implementation, and produces a canonical report with explicit included/excluded issue lists and compliant/non-compliant/indeterminate outcomes by cohort.
   156|
   157|---
   158|
   159|## Pseudocode
   160|
   161|```text
   162|load all candidate issues and classify them by cohort policy matrix:
   163|    engineering-critical
   164|    non-engineering
   165|    mixed / legacy
   166|for each in-scope issue:
   167|    retrieve issue timeline/events
   168|    retrieve plan artifact and status
   169|    retrieve review artifacts and parse verdict/date
   170|    retrieve approval marker state
   171|    retrieve implementation evidence:
   172|        commits
   173|        session evidence when available
   174|        bypass evidence when available
   175|    build per-issue evidence matrix including skill-usage confidence
   176|    verify chronology:
   177|        status:plan-review before approval
   178|        status:plan-approved applied only after user approval evidence
   179|        adversarial review before approval
   180|        approval before implementation evidence
   181|    classify result as:
   182|        compliant
   183|        non-compliant
   184|        indeterminate
   185|generate canonical report with:
   186|    included issue list
   187|    excluded issue list with reasons
   188|    per-issue evidence summary
   189|    cohort counts for compliant/non-compliant/indeterminate
   190|    final decision: keep current approach or escalate enforcement
   191|    gaps, failure modes, and recommendations section
   192|```
   193|
   194|---
   195|
   196|## Files to Change
   197|
   198|### Implementation scope
   199|
   200|| Action | Path | Reason |
   201||---|---|---|
   202|| Create | `scripts/enforcement/audit_planning_compliance.py` | Audit script: evidence matrix builder, chronology checker, cohort classifier, report generator |
   203|| Create | `tests/fixtures/planning-compliance/` | Frozen fixtures: compliant issue, non-compliant issue (each misuse pattern), indeterminate issue, mixed cohort set, stale review, malformed artifact |
   204|| Create | `tests/enforcement/test_audit_planning_compliance.py` | 21 TDD tests per test list above |
   205|| Refresh | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | Overwrite with new audit output; preserve report path (no new file) |
   206|
   207|### Out of implementation scope
   208|
   209|| Path | Reason for exclusion |
   210||---|---|
   211|| This plan file | Plan revision is not an implementation deliverable |
   212|| `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` | Reference only; no changes planned unless skill conflicts with audit logic |
   213|
   214|---
   215|
   216|## TDD Test List
   217|
   218|| Test name | What it verifies | Expected input | Expected output |
   219||---|---|---|---|
   220|| `test_evidence_matrix_records_all_required_signals` | each issue record contains: plan artifact path, review artifact paths, `status:plan-review` timestamp, `status:plan-approved` timestamp, approval marker path, implementation commit list, skill-usage tier | fixture: issue with all signals present | all fields populated; no `None` for required fields |
   221|| `test_status_plan_review_precedes_approval` | `status:plan-review` label event timestamp < `status:plan-approved` label event timestamp | fixture: timeline with both labels in correct order; fixture: reversed order | correct → compliant; reversed → non-compliant |
   222|| `test_review_precedes_approval` | review artifact file modification date < `status:plan-approved` timestamp | fixture: review dated before approval; fixture: review dated after | before → compliant; after → non-compliant |
   223|| `test_status_plan_approved_applied_after_user_approval` | `status:plan-approved` was applied by a human (not an agent) and after user approval evidence | fixture: label applied by user after review; fixture: label applied by agent | user → compliant; agent → non-compliant |
   224|| `test_plan_approved_without_prior_plan_review` | `status:plan-approved` applied but `status:plan-review` was never applied | fixture: issue with only `plan-approved` label | non-compliant |
   225|| `test_plan_approved_retroactive_after_implementation` | `status:plan-approved` applied after implementation commits already exist | fixture: impl commit at T1, label at T2 where T2 > T1 | non-compliant (post-hoc approval) |
   226|| `test_plan_approved_never_applied_with_impl_commits` | issue has implementation commits but `status:plan-approved` was never applied | fixture: impl commits, no approval label, marker may or may not exist | non-compliant |
   227|| `test_marker_without_label_discrepancy` | `.planning/plan-approved/` marker exists but `status:plan-approved` label was never applied | fixture: marker file present, no label event | indeterminate with discrepancy flag |
   228|| `test_implementation_before_approval_commit_evidence` | commits touching implementation paths (not safe-paths) exist before earliest approval signal | fixture: commit to `scripts/enforcement/` at T1, approval at T2 > T1 | non-compliant (implementation before approval) |
   229|| `test_safe_path_commits_not_counted_as_implementation` | commits to `docs/plans/`, `scripts/review/results/`, `.planning/`, adapter configs are not classified as implementation | fixture: only plan/review/doc commits before approval | compliant (planning activity, not implementation) |
   230|| `test_issue_planning_mode_usage_evidence_tiers` | authoritative (session log) → compliant; secondary (plan + review artifacts) → compliant (inferred); fallback (issue comment only) → indeterminate; none → non-compliant | fixture set: one issue per tier | correct tier classification for each |
   231|| `test_template_conformance_for_discovered_plan_artifacts` | plan artifact contains all required template headings per `_template-issue-plan.md` | fixture: conformant plan; fixture: plan missing Acceptance Criteria heading | conformant → pass; missing heading → fail with specific heading named |
   232|| `test_review_artifact_matches_plan_revision` | review artifact date is on or after plan's last substantive edit | fixture: review dated after plan edit; fixture: plan edited after review (stale) | after → compliant; stale → indeterminate on review dimension |
   233|| `test_stale_review_after_plan_edit` | plan was substantively edited after review artifact was created | fixture: plan edited at T2, review at T1 < T2 | indeterminate; report flags stale review |
   234|| `test_retroactive_label_is_flagged` | `status:plan-approved` added >24h after the last review artifact date, suggesting retroactive labeling | fixture: review at T1, label at T1+48h | non-compliant or indeterminate with retroactive flag |
   235|| `test_malformed_review_artifact_is_not_treated_as_valid_review` | review artifact exists but is empty, has no verdict line, or is <100 bytes | fixture: empty file; fixture: file with "APPROVE" verdict | empty → non-compliant; valid → compliant |
   236|| `test_commits_without_issue_reference` | commits with no `#NNN` reference are excluded from issue evidence rather than forcing false negative | fixture: commits without issue refs | excluded from per-issue matrix; reported in audit summary as unattributed |
   237|| `test_conflicting_evidence_resolution` | GitHub timeline evidence beats local marker when they conflict | fixture: label says approved at T1, marker commit says T2 ≠ T1 | classification follows GitHub timeline (T1); conflict reported |
   238|| `test_report_emits_included_and_excluded_issue_lists` | report contains explicit `## Included Issues` and `## Excluded Issues` sections with issue numbers and reasons | fixture: mixed cohort | both sections present with ≥1 entry each |
   239|| `test_report_splits_by_cohort` | report has separate compliance counts for engineering-critical and non-engineering cohorts | fixture: 2 eng-critical + 2 non-eng issues | separate count rows in report |
   240|| `test_report_includes_decision_rubric_outcome` | report contains a `## Recommendation` section stating which rubric row was selected | fixture: 60% compliant, 15% indeterminate | "Tighten guidance" recommendation with rubric citation |
   241|
   242|---
   243|
   244|## Acceptance Criteria
   245|
   246|### Implementation completion (required to close #2046)
   247|
   248|- [ ] `scripts/enforcement/audit_planning_compliance.py` produces a per-issue evidence matrix with all fields from `test_evidence_matrix_records_all_required_signals`.
   249|- [ ] Audit verifies `status:plan-review` → `status:plan-approved` chronology and detects all six misuse patterns from the `status:plan-approved` usage checks table.
   250|- [ ] Audit detects implementation-before-approval using commit evidence against safe-path exclusion list per the definition above.
   251|- [ ] Audit classifies `issue-planning-mode` usage across all three evidence tiers (authoritative/secondary/fallback) with correct indeterminate handling.
   252|- [ ] Audit checks plan-revision matching: stale reviews (plan edited after review) are flagged as indeterminate.
   253|- [ ] Report output written to `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` (refresh, not duplicate) containing: included/excluded issue lists, per-issue evidence summary, cohort-split compliance counts, and a recommendation section citing the decision rubric.
   254|- [ ] All 21 TDD tests pass in `tests/enforcement/test_audit_planning_compliance.py` using fixtures in `tests/fixtures/planning-compliance/`.
   255|- [ ] Engineering-critical issues failing compliance at any rate trigger escalation recommendation regardless of overall rate.
   256|
   257|### Plan approval gate (required before implementation begins)
   258|
   259|- [ ] Adversarial review from Codex and Gemini returns APPROVE or MINOR.
   260|- [ ] Claude review artifact is generated or a documented two-provider exception is approved by user.
   261|
   262|---
   263|
   264|## Adversarial Review History
   265|
   266|| Date | Provider | Verdict | Status |
   267||---|---|---|---|
   268|| 2026-04-14 | Codex | MAJOR | Addressed: evidence model now has tiers with outcomes, chronology checks explicit, audit universe defined with exact query and rollout date |
   269|| 2026-04-14 | Gemini | MAJOR | Addressed: `status:plan-review` verification added, skill-usage evidence tiers concrete, cohort policy matrix with inclusion/exclusion rules |
   270|| — | Claude | **Missing** | No Claude review artifact exists. Required before `status:plan-approved` (see Acceptance Criteria) |
   271|
   272|Full review artifacts: `scripts/review/results/2026-04-14-plan-2046-codex.md`, `scripts/review/results/2026-04-14-plan-2046-gemini.md`
   273|
   274|**Current status:** Re-review required to confirm MAJOR findings are resolved. Claude review still needed.
   275|
   276|---
   277|
   278|## Risks and Open Questions
   279|
   280|- **Risk:** GitHub timeline/event history may be incomplete for some historical issues. Mitigation: incomplete timeline → `indeterminate` classification, never silently compliant.
   281|- **Risk:** commit timestamps alone can distort chronology if clock skew exists between local and GitHub. Mitigation: `test_commit_only_signal_is_low_confidence` ensures commit-only evidence is never treated as authoritative.
   282|- **Risk:** `status:plan-approved` has never been applied to any issue as of 2026-04-09. If this remains true at audit time, 100% of in-scope issues will be non-compliant on the approval dimension. The decision rubric handles this (escalation at <50%).
   283|- **Risk:** session transcript availability varies by provider. Mitigation: evidence model falls back to secondary/fallback tiers with indeterminate classification when transcripts are unavailable.
   284|- **Resolved:** evidence model concreteness — now has authoritative/secondary/fallback tiers with explicit outcomes.
   285|- **Resolved:** audit universe ambiguity — now has exact rollout boundary (2026-04-08 21:54 CST), in-scope query, and exclusion rules.
   286|- **Resolved:** decision rubric — now has three-tier recommendation with per-cohort override for engineering-critical issues.
   287|
   288|---
   289|
   290|## Complexity: T2
   291|
   292|**T2** — moderate audit/reporting implementation with timeline parsing, evidence classification, and fixture-backed verification.
   293|
```
