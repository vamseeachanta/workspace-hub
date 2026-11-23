# Adversarial Re-Review Request: Issue #2046

You are an independent adversarial reviewer. This plan was revised after prior MAJOR findings. Evaluate the current plan text only. Find any remaining gaps, unresolved decisions, weak retrieval, non-falsifiable tests/acceptance criteria, or workflow/governance violations. Do NOT rubber-stamp.

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

Context:
- Repository: workspace-hub
- Review type: plan-stage adversarial re-review
- Focus on whether the revised plan is now actually approval-ready.

GitHub issue metadata:
- Issue: #2046
- Title: Audit compliance of strict issue planning workflow after rollout

Plan under review (2026-04-09-issue-2046-planning-compliance-audit.md):

```markdown
     1|# Plan for #2046: Audit Compliance of Strict Issue Planning Workflow After Rollout
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
    24|- `docs/plans/_template-issue-plan.md` — canonical section contract for discovered plan artifacts.
    25|- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — canonical workflow skill named by the repo hard gate.
    26|- `docs/standards/HARD-STOP-POLICY.md` — engineering-critical enforcement policy.
    27|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md` — adversarial review expectations.
    28|
    29|### Documents consulted
    30|- GitHub issue #2045 — onboarding baseline / rollout origin
    31|- GitHub issue #2047 — likely escalation path if audit fails
    32|- `docs/plans/README.md`
    33|- `docs/plans/_template-issue-plan.md`
    34|- `.claude/skills/coordination/issue-planning-mode/SKILL.md`
    35|- `docs/standards/HARD-STOP-POLICY.md`
    36|- `docs/standards/AI_REVIEW_ROUTING_POLICY.md`
    37|- `docs/governance/TRUST-ARCHITECTURE.md`
    38|- `docs/reports/2026-04-09-planning-workflow-compliance-audit.md`
    39|- `.claude/skills/coordination/workflow-compliance-audit/SKILL.md`
    40|- `.claude/hooks/plan-approval-gate.sh`
    41|- `scripts/enforcement/require-plan-approval.sh`
    42|- `gh issue view <issue> --json timelineItems` equivalent timeline/event retrieval path (must be implemented concretely in the audit script, not approximated by label snapshots alone)
    43|
    44|### Gaps identified
    45|- Current plan logic still over-relies on artifact presence and commit timestamps instead of chronology and evidence confidence.
    46|- No authoritative policy matrix is yet defined for engineering-critical, non-engineering, mixed, and legacy issue cohorts.
    47|- No fixture corpus yet covers retroactive labels, malformed review artifacts, marker/label mismatches, or commits without issue references.
    48|
    49|### Cohort policy matrix
    50|| Cohort | Inclusion rule | Compliance rule |
    51||---|---|---|
    52|| Engineering-critical | Issue has engineering-critical labels and entered planning workflow after #2045 rollout | Must prove plan artifact, adversarial review, `status:plan-review`, `status:plan-approved`, approval marker, and no implementation evidence before approval |
    53|| Non-engineering | Non-engineering issue entered planning workflow after #2045 rollout | Must prove same planning/review/approval sequence, but report separately from engineering-critical cohort |
    54|| Legacy / pre-rollout | Issue activity predates rollout or cannot be shown to have entered planning after rollout | Excluded from primary denominator; report separately |
    55|| Mixed / ambiguous | Conflicting evidence on cohort or sequencing | Included only as `indeterminate` unless stronger evidence resolves classification |
    56|
    57|### Evidence model for `issue-planning-mode` usage
    58|
    59|| Tier | Source | What it proves | Outcome if present | Outcome if absent |
    60||---|---|---|---|---|
    61|| **Authoritative** | Session transcript or hook log showing `/skill issue-planning-mode` or `.claude/skills/coordination/issue-planning-mode/SKILL.md` load event | Skill was invoked in the session | **compliant** for skill-usage dimension | Fall to secondary |
    62|| **Secondary** | Plan artifact in `docs/plans/` matching `*-issue-NNNN-*.md` that contains all required template sections (status header, Resource Intelligence, Artifact Map, TDD Test List, Acceptance Criteria, Adversarial Review) AND correctly sequenced review/approval artifacts exist | Workflow was followed even if skill invocation cannot be directly proven | **compliant** (inferred) for skill-usage dimension | Fall to fallback |
    63|| **Fallback** | GitHub issue comment or audit report text describing workflow steps performed, with timestamps consistent with plan/review/approval order | Workflow intent was present but artifacts are incomplete | **indeterminate** — count separately, do not count as compliant or non-compliant | **non-compliant** for skill-usage dimension |
    64|
    65|**Rule:** an issue classified as `indeterminate` on skill-usage is still evaluated on all other compliance dimensions (chronology, approval, review). Indeterminate on one dimension does not exempt the issue from the audit.
    66|
    67|### Audited population definition
    68|
    69|**Rollout boundary:** 2026-04-08 21:54 CST — commit `2bc0f4673` (full onboarding per #2045). This is the canonical cutoff; issues with implementation activity before this timestamp are pre-rollout.
    70|
    71|**Trigger threshold:** run the audit once at least 10 issues have received implementation commits post-rollout, OR 14 calendar days after rollout, whichever comes first. Per the existing audit report, 10 issues were already identified by 2026-04-09.
    72|
    73|**In-scope query:**
    74|```bash
    75|# All issues with implementation commits after rollout
    76|git log --oneline --after="2026-04-08T21:54:00" --no-merges --format="%s" \
    77|  | grep -oP '#\d+' | sort -u
    78|# Cross-reference with GitHub issue state
    79|gh issue list --state all --limit 500 --json number,labels,createdAt
    80|```
    81|
    82|**Inclusion rule:** an issue is in-scope if it has at least one implementation commit (non-docs, non-plan, non-config-only) after the rollout boundary.
    83|
    84|**Exclusion rules:**
    85|- Issues with only documentation or plan-file commits (no implementation code) — excluded as non-implementation.
    86|- Issues created and closed entirely before the rollout boundary — excluded as pre-rollout.
    87|- Issues with mixed pre/post-rollout activity: include only post-rollout commits in the chronology check. If all implementation commits are pre-rollout, exclude.
    88|
    89|**Minimum issue-count rule:** if fewer than 10 issues are in-scope at audit time, the audit still runs but the report must note the low sample size and flag that statistical conclusions are unreliable.
    90|
    91|### Approval signal precedence
    92|
    93|### User-approval evidence rule table
    94|
    95|| Rank | Evidence source | What qualifies | Use in audit |
    96||---|---|---|---|
    97|| 1 | GitHub timeline event by human actor | issue comment or label-change event attributable to repository owner/collaborator that explicitly approves the plan or applies `status:plan-approved` after review | authoritative |
    98|| 2 | `.planning/plan-approved/<issue>.md` marker committed after the human approval event | local corroboration only; never sufficient by itself | corroborating |
    99|| 3 | Issue comment quoting explicit user approval but lacking label change | acceptable only if actor is human and timestamps are consistent with later approval label or marker | fallback / may become indeterminate |
   100|| 4 | Agent-authored marker or label change with no human event | does not qualify as user approval evidence | non-compliant |
   101|
   102|**Actor classification rule:** treat `github-actions`, known bot accounts, and agent-owned service identities as non-human actors. Treat repository owner/collaborator/member accounts as human unless the event text itself states it was automated; ambiguous actors must be reported as `indeterminate`, not silently human.
   103|
   104|### Approval signal precedence
   105|1. GitHub timeline evidence showing `status:plan-approved` added after review/user-approval event by a human actor.
   106|2. Local `.planning/plan-approved/<issue>.md` marker as corroborating local evidence only.
   107|3. If GitHub and local signals disagree, classify by the stronger timeline evidence and report the conflict explicitly.
   108|
   109|### `status:plan-approved` usage and misuse checks
   110|
   111|The label `status:plan-approved` has specific semantics defined in `docs/plans/README.md`. The audit must check:
   112|
   113|| Check | What it detects | Classification if failed |
   114||---|---|---|
   115|| `status:plan-approved` applied without prior `status:plan-review` | Approval without review phase | **non-compliant** |
   116|| `status:plan-approved` applied by an agent (not the user) | Self-approval / no human gate | **non-compliant** |
   117|| `status:plan-approved` applied but no review artifacts exist in `scripts/review/results/` | Approval without adversarial review evidence | **non-compliant** |
   118|| `status:plan-approved` applied retroactively after implementation commits already exist | Post-hoc approval (label applied to legitimize already-done work) | **non-compliant** |
   119|| `status:plan-approved` never applied to an issue that has implementation commits | Missing approval entirely | **non-compliant** |
   120|| `.planning/plan-approved/<issue>.md` marker exists but `status:plan-approved` label was never applied | Local-only approval, not visible on GitHub | **indeterminate** — report the discrepancy |
   121|
   122|**Note from existing audit:** as of 2026-04-09, `status:plan-approved` has never been applied to any issue in the repository. The audit must verify whether this has changed at audit execution time.
   123|
   124|### Definition: "agent began coding before approval"
   125|
   126|An issue is classified as having **implementation before approval** if any of the following are true:
   127|
   128|1. **Commit evidence:** a commit referencing `#NNNN` touches files outside the safe-path list (not `docs/plans/`, not `scripts/review/results/`, not `.planning/`, not `CLAUDE.md`/`GEMINI.md`/`AGENTS.md`) AND the commit timestamp is earlier than the earliest approval evidence (either `status:plan-approved` label event or `.planning/plan-approved/<issue>.md` marker commit).
   129|2. **File-change evidence:** files in `src/`, `scripts/enforcement/`, `.claude/hooks/`, `tests/` (implementation paths) were modified in commits referencing the issue before any approval signal.
   130|3. **Session evidence (when available):** agent session transcript shows code generation or file writes for the issue before plan approval was granted.
   131|
   132|**Safe-path exclusion:** changes to plan files, review artifacts, documentation, and adapter configs (`CLAUDE.md`, `GEMINI.md`, `.codex/CODEX.md`) are not implementation — they are planning activity and do not trigger implementation-before-approval classification.
   133|
   134|### Plan-revision matching rules
   135|
   136|Review artifacts must correspond to the plan revision that was actually approved. The audit must check:
   137|
   138|1. **Revision date match:** the review artifact filename contains a date (`YYYY-MM-DD`) that is on or after the plan file's most recent substantive edit (determined by `git log -1 --format="%ai" -- docs/plans/*-issue-NNNN-*.md`).
   139|2. **Content hash match (when available):** if the review artifact references a plan hash or revision identifier, it must match the approved plan's content at the time of review.
   140|3. **Falsifiable stale-review heuristic:** if any diff after the review timestamp touches the headings `## Acceptance Criteria`, `## TDD Test List`, `## Files to Change`, or `## Risks and Open Questions`, the prior review is stale and the issue is classified as **indeterminate** on the review dimension until re-reviewed.
   141|4. **No review artifact at all:** if no review artifact exists for the issue, the review dimension is **non-compliant** regardless of other evidence.
   142|
   143|### Decision rubric
   144|
   145|After the audit completes, the report must include an explicit recommendation using this rubric:
   146|
   147|| Compliance rate | Indeterminate rate | Recommendation |
   148||---|---|---|
   149|| ≥80% compliant AND <10% indeterminate | Low | **Keep current approach** — workflow is adopted and enforcement is working |
   150|| 50–79% compliant OR 10–25% indeterminate | Moderate | **Tighten guidance** — update onboarding surfaces, add enforcement logging, re-audit in 2 weeks |
   151|| <50% compliant OR >25% indeterminate | High | **Escalate enforcement** — trigger #2047 escalation, consider promoting `compliance-dashboard` from advisory to blocking, add CI-level hard gates |
   152|
   153|The rubric applies per-cohort. Engineering-critical issues failing at any level trigger escalation regardless of the overall rate. The report must state which rubric row was selected and why.
   154|
   155|---
   156|
   157|## Artifact Map
   158|
   159|| Artifact | Path |
   160||---|---|
   161|| This plan | `docs/plans/2026-04-09-issue-2046-planning-compliance-audit.md` |
   162|| Audit script | `scripts/enforcement/audit_planning_compliance.py` |
   163|| Fixture corpus | `tests/fixtures/planning-compliance/` |
   164|| Script tests | `tests/enforcement/test_audit_planning_compliance.py` |
   165|| Canonical report | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` |
   166|| Workflow audit reference | `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` |
   167|| Review artifacts | `scripts/review/results/2026-04-14-plan-2046-codex.md` and `scripts/review/results/2026-04-14-plan-2046-gemini.md` |
   168|
   169|---
   170|
   171|## Deliverable
   172|
   173|A reproducible compliance-audit plan that defines a per-issue evidence matrix, verifies timeline sequencing for plan-review/review/approval/implementation, and produces a canonical report with explicit included/excluded issue lists and compliant/non-compliant/indeterminate outcomes by cohort.
   174|
   175|---
   176|
   177|## Pseudocode
   178|
   179|```text
   180|load all candidate issues and classify them by cohort policy matrix:
   181|    engineering-critical
   182|    non-engineering
   183|    mixed / legacy
   184|for each in-scope issue:
   185|    retrieve issue timeline/events
   186|    retrieve plan artifact and status
   187|    retrieve review artifacts and parse verdict/date
   188|    retrieve approval marker state
   189|    retrieve implementation evidence:
   190|        commits
   191|        session evidence when available
   192|        bypass evidence when available
   193|    build per-issue evidence matrix including skill-usage confidence
   194|    verify chronology:
   195|        status:plan-review before approval
   196|        status:plan-approved applied only after user approval evidence
   197|        adversarial review before approval
   198|        approval before implementation evidence
   199|    classify result as:
   200|        compliant
   201|        non-compliant
   202|        indeterminate
   203|generate canonical report with:
   204|    included issue list
   205|    excluded issue list with reasons
   206|    per-issue evidence summary
   207|    cohort counts for compliant/non-compliant/indeterminate
   208|    final decision: keep current approach or escalate enforcement
   209|    gaps, failure modes, and recommendations section
   210|```
   211|
   212|---
   213|
   214|## Files to Change
   215|
   216|### Implementation scope
   217|
   218|| Action | Path | Reason |
   219||---|---|---|
   220|| Create | `scripts/enforcement/audit_planning_compliance.py` | Audit script: evidence matrix builder, chronology checker, cohort classifier, report generator |
   221|| Create | `tests/fixtures/planning-compliance/` | Frozen fixtures: compliant issue, non-compliant issue (each misuse pattern), indeterminate issue, mixed cohort set, stale review, malformed artifact |
   222|| Create | `tests/enforcement/test_audit_planning_compliance.py` | 21 TDD tests per test list above |
   223|| Refresh | `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` | Overwrite with new audit output; preserve report path (no new file) |
   224|
   225|### Out of implementation scope
   226|
   227|| Path | Reason for exclusion |
   228||---|---|
   229|| This plan file | Plan revision is not an implementation deliverable |
   230|| `.claude/skills/coordination/workflow-compliance-audit/SKILL.md` | Reference only; no changes planned unless skill conflicts with audit logic |
   231|
   232|---
   233|
   234|## TDD Test List
   235|
   236|| Test name | What it verifies | Expected input | Expected output |
   237||---|---|---|---|
   238|| `test_evidence_matrix_records_all_required_signals` | each issue record contains: plan artifact path, review artifact paths, `status:plan-review` timestamp, `status:plan-approved` timestamp, approval marker path, implementation commit list, skill-usage tier | fixture: issue with all signals present | all fields populated; no `None` for required fields |
   239|| `test_status_plan_review_precedes_approval` | `status:plan-review` label event timestamp < `status:plan-approved` label event timestamp | fixture: timeline with both labels in correct order; fixture: reversed order | correct → compliant; reversed → non-compliant |
   240|| `test_review_precedes_approval` | review artifact file modification date < `status:plan-approved` timestamp | fixture: review dated before approval; fixture: review dated after | before → compliant; after → non-compliant |
   241|| `test_status_plan_approved_applied_after_user_approval` | `status:plan-approved` was applied by a human (not an agent) and after user approval evidence | fixture: label applied by user after review; fixture: label applied by agent | user → compliant; agent → non-compliant |
   242|| `test_plan_approved_without_prior_plan_review` | `status:plan-approved` applied but `status:plan-review` was never applied | fixture: issue with only `plan-approved` label | non-compliant |
   243|| `test_plan_approved_retroactive_after_implementation` | `status:plan-approved` applied after implementation commits already exist | fixture: impl commit at T1, label at T2 where T2 > T1 | non-compliant (post-hoc approval) |
   244|| `test_plan_approved_never_applied_with_impl_commits` | issue has implementation commits but `status:plan-approved` was never applied | fixture: impl commits, no approval label, marker may or may not exist | non-compliant |
   245|| `test_marker_without_label_discrepancy` | `.planning/plan-approved/` marker exists but `status:plan-approved` label was never applied | fixture: marker file present, no label event | indeterminate with discrepancy flag |
   246|| `test_implementation_before_approval_commit_evidence` | commits touching implementation paths (not safe-paths) exist before earliest approval signal | fixture: commit to `scripts/enforcement/` at T1, approval at T2 > T1 | non-compliant (implementation before approval) |
   247|| `test_safe_path_commits_not_counted_as_implementation` | commits to `docs/plans/`, `scripts/review/results/`, `.planning/`, adapter configs are not classified as implementation | fixture: only plan/review/doc commits before approval | compliant (planning activity, not implementation) |
   248|| `test_issue_planning_mode_usage_evidence_tiers` | authoritative (session log) → compliant; secondary (plan + review artifacts) → compliant (inferred); fallback (issue comment only) → indeterminate; none → non-compliant | fixture set: one issue per tier | correct tier classification for each |
   249|| `test_template_conformance_for_discovered_plan_artifacts` | plan artifact contains all required template headings per `_template-issue-plan.md` | fixture: conformant plan; fixture: plan missing Acceptance Criteria heading | conformant → pass; missing heading → fail with specific heading named |
   250|| `test_review_artifact_matches_plan_revision` | review artifact date is on or after plan's last substantive edit | fixture: review dated after plan edit; fixture: plan edited after review (stale) | after → compliant; stale → indeterminate on review dimension |
   251|| `test_stale_review_after_plan_edit` | plan was substantively edited after review artifact was created | fixture: plan edited at T2, review at T1 < T2 | indeterminate; report flags stale review via changed-headings heuristic |
   252|| `test_commit_only_signal_is_low_confidence` | commit timestamps without timeline or approval evidence are treated as suggestive only, never as sole proof of compliant approval order | fixture: commit history present but no timeline events | indeterminate / low-confidence flag, not compliant |
   253|| `test_retroactive_label_is_flagged` | `status:plan-approved` added >24h after the last review artifact date, suggesting retroactive labeling | fixture: review at T1, label at T1+48h | non-compliant or indeterminate with retroactive flag |
   254|| `test_malformed_review_artifact_is_not_treated_as_valid_review` | review artifact exists but is empty, has no verdict line, or is <100 bytes | fixture: empty file; fixture: file with "APPROVE" verdict | empty → non-compliant; valid → compliant |
   255|| `test_commits_without_issue_reference` | commits with no `#NNN` reference are excluded from issue evidence rather than forcing false negative | fixture: commits without issue refs | excluded from per-issue matrix; reported in audit summary as unattributed |
   256|| `test_conflicting_evidence_resolution` | GitHub timeline evidence beats local marker when they conflict | fixture: label says approved at T1, marker commit says T2 ≠ T1 | classification follows GitHub timeline (T1); conflict reported |
   257|| `test_report_emits_included_and_excluded_issue_lists` | report contains explicit `## Included Issues` and `## Excluded Issues` sections with issue numbers and reasons | fixture: mixed cohort | both sections present with ≥1 entry each |
   258|| `test_report_splits_by_cohort` | report has separate compliance counts for engineering-critical and non-engineering cohorts | fixture: 2 eng-critical + 2 non-eng issues | separate count rows in report |
   259|| `test_engineering_critical_override_triggers_escalation` | any engineering-critical non-compliance forces escalation recommendation regardless of aggregate rate | fixture: high overall compliance but one engineering-critical failure | recommendation = `Escalate enforcement` with override rationale |
   260|| `test_report_includes_decision_rubric_outcome` | report contains a `## Recommendation` section stating which rubric row was selected | fixture: 60% compliant, 15% indeterminate | `Tighten guidance` recommendation with rubric citation |
   261|
   262|---
   263|
   264|## Acceptance Criteria
   265|
   266|### Implementation completion (required to close #2046)
   267|
   268|- [ ] `scripts/enforcement/audit_planning_compliance.py` produces a per-issue evidence matrix with all fields from `test_evidence_matrix_records_all_required_signals`.
   269|- [ ] Audit verifies `status:plan-review` → `status:plan-approved` chronology and detects all six misuse patterns from the `status:plan-approved` usage checks table.
   270|- [ ] Audit detects implementation-before-approval using commit evidence against safe-path exclusion list per the definition above.
   271|- [ ] Audit classifies `issue-planning-mode` usage across all three evidence tiers (authoritative/secondary/fallback) with correct indeterminate handling.
   272|- [ ] Audit checks plan-revision matching: stale reviews (plan edited after review) are flagged as indeterminate using the changed-headings heuristic.
   273|- [ ] Report output written to `docs/reports/2026-04-09-planning-workflow-compliance-audit.md` (refresh, not duplicate) containing: included/excluded issue lists, per-issue evidence summary, cohort-split compliance counts, and a recommendation section citing the decision rubric.
   274|- [ ] Commit-only chronology signals without timeline evidence are treated as low-confidence only (`test_commit_only_signal_is_low_confidence`).
   275|- [ ] Engineering-critical issues failing compliance at any rate trigger escalation recommendation regardless of overall rate (`test_engineering_critical_override_triggers_escalation`).
   276|- [ ] All TDD tests pass in `tests/enforcement/test_audit_planning_compliance.py` using fixtures in `tests/fixtures/planning-compliance/`.
   277|
   278|### Plan approval gate (required before implementation begins)
   279|
   280|- [ ] Adversarial review from Codex and Gemini returns APPROVE or MINOR.
   281|- [ ] Claude review artifact is generated or a documented two-provider exception is approved by user.
   282|
   283|---
   284|
   285|## Adversarial Review History
   286|
   287|| Date | Provider | Verdict | Status |
   288||---|---|---|---|
   289|| 2026-04-14 | Codex | MAJOR | Addressed: evidence model now has tiers with outcomes, chronology checks explicit, audit universe defined with exact query and rollout date |
   290|| 2026-04-14 | Gemini | MAJOR | Addressed: `status:plan-review` verification added, skill-usage evidence tiers concrete, cohort policy matrix with inclusion/exclusion rules |
   291|| — | Claude | **Missing** | No Claude review artifact exists. Required before `status:plan-approved` (see Acceptance Criteria) |
   292|
   293|Full review artifacts: `scripts/review/results/2026-04-14-plan-2046-codex.md`, `scripts/review/results/2026-04-14-plan-2046-gemini.md`
   294|
   295|**Current status:** Re-review required to confirm MAJOR findings are resolved. Claude review still needed.
   296|
   297|---
   298|
   299|## Risks and Open Questions
   300|
   301|- **Risk:** GitHub timeline/event history may be incomplete for some historical issues. Mitigation: incomplete timeline → `indeterminate` classification, never silently compliant.
   302|- **Risk:** commit timestamps alone can distort chronology if clock skew exists between local and GitHub. Mitigation: `test_commit_only_signal_is_low_confidence` ensures commit-only evidence is never treated as authoritative.
   303|- **Risk:** `status:plan-approved` has never been applied to any issue as of 2026-04-09. If this remains true at audit time, 100% of in-scope issues will be non-compliant on the approval dimension. The decision rubric handles this (escalation at <50%).
   304|- **Risk:** session transcript availability varies by provider. Mitigation: evidence model falls back to secondary/fallback tiers with indeterminate classification when transcripts are unavailable.
   305|- **Resolved:** evidence model concreteness — now has authoritative/secondary/fallback tiers with explicit outcomes.
   306|- **Resolved:** audit universe ambiguity — now has exact rollout boundary (2026-04-08 21:54 CST), in-scope query, and exclusion rules.
   307|- **Resolved:** decision rubric — now has three-tier recommendation with per-cohort override for engineering-critical issues.
   308|
   309|---
   310|
   311|## Complexity: T2
   312|
   313|**T2** — moderate audit/reporting implementation with timeline parsing, evidence classification, and fixture-backed verification.
   314|
```
