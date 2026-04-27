# Plan for #2503: Standardize canonical approval-request comments for plan-review issues

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-27
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2503
> **Review artifacts:** scripts/review/results/2026-04-26-plan-2503-codex.md | supplemental local: scripts/review/results/2026-04-26-plan-2503-hermes.md | required before posting: scripts/review/results/2026-04-26-plan-2503-claude.md and scripts/review/results/2026-04-26-plan-2503-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/ai/continuous-planning-pipeline.py` — `has_canonical_approval_comment()` currently requires comments to include the current plan filename, current plan SHA, review artifact wording, `approve`, `revise`, `hold`, `execution remains unauthorized`, and `approval marker` before Lane A can classify an issue as an approval candidate.
- Found: `scripts/ai/continuous-planning-pipeline.py` — live issue enrichment fetches comments and `closedByPullRequestsReferences`; #2503 must add GraphQL comment-window metadata without dropping the existing PR handoff evidence used by Lane E classification.
- Found: `scripts/ai/continuous-planning-pipeline.py:131-176` — `review_summary()` already returns `(clean, warnings, evidence)` with `evidence['plan_sha256']` plus per-provider data in `evidence['providers'][provider]`; #2503 should extend/consume this exact evidence shape when cross-checking comment `Review-Artifacts`/`Review-Verdicts`.
- Found: `docs/plans/README.md` — Step 5 only says to post the completed plan as a GitHub issue comment and apply `status:plan-review`; it does not define a canonical machine-readable approval-request shape.
- Found: `coordination/issue-planning-mode` and `coordination/continuous-planning-pipeline` skill guidance — both require explicit user approval and a local `.planning/plan-approved/<issue>.md` marker; approval comments must not create implementation authority.
- Gap: no durable template exists for approval-request comments, the current parser is token-based rather than schema-backed, and live issue enrichment does not carry enough comment-window metadata to distinguish no canonical request from an insufficient/truncated comment window.

### Standards
| Standard | Status | Source |
|---|---|---|
| Planning workflow approval gate | applicable | `docs/plans/README.md` Step 5/6 and Status Meanings |
| Hard-stop policy | context only | `docs/standards/HARD-STOP-POLICY.md` scope is engineering-critical issues; #2503 instead relies on AGENTS.md plus `docs/plans/README.md` all-issue gates for mandatory approval boundaries |
| Continuous planning Lane A/B semantics | applicable | `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` and `scripts/ai/continuous-planning-pipeline.py` |

### LLM Wiki pages consulted
- Not applicable; this is a workflow/harness issue and does not add domain wiki content.

### Documents consulted
- Issue #2503 — requires canonical approval-request comment template, parser fixtures, and safe repost/backfill guidance.
- Parent issue #2489 / plan `docs/plans/2026-04-26-issue-2489-continuous-planning-pipeline.md` — introduced Lane A approval candidates requiring clean review evidence and approval-request surfacing.
- `docs/reports/continuous-planning-pipeline.md` — current Lane A is empty, so standardizing comments directly improves approval-buffer recovery.
- `docs/plans/README.md` — existing posting instructions are too broad for machine-readable approval detection.

### Gaps identified
- No canonical approval-request comment template with fixed fields.
- No parser/validator fixtures for complete, ambiguous, stale, truncated, and comment-window-failed states.
- No safe backfill/repost operator guide using `gh --body-file`.
- No explicit comment-window contract: the parser needs fetched comment count/window metadata so incomplete GitHub comment evidence produces `comment_window_insufficient` rather than false Lane A readiness.
- No durable docs explicitly stating approval comments are decision requests only and never create Lane B authority without `status:plan-approved` plus `.planning/plan-approved/<issue>.md`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-27T01:30:07Z via `gh issue view`):
- `#2503` — OPEN — feat(ai-orchestration): standardize canonical approval-request comments for plan-review issues
- `#2489` — CLOSED — feat(ai-orchestration): continuous planning pipeline for AFK issue throughput

**File existence** (verified 2026-04-27T01:30:07Z):
- EXISTS: `scripts/ai/continuous-planning-pipeline.py`
- EXISTS: `docs/plans/README.md`
- EXISTS: `docs/standards/HARD-STOP-POLICY.md`
- EXISTS: `docs/reports/continuous-planning-pipeline.md`
- MISSING (new or updated by implementation): canonical approval-request comment template and validator/backfill tests.

**Line excerpts** (`grep -n` verified 2026-04-27T01:30:07Z):
```
274:def has_canonical_approval_comment(issue: dict[str, Any], plan_path: Path | None, plan_sha: str | None) -> tuple[bool, list[str]]:
279:        return False, ["approval_comment_ambiguous"]
376:        ok_comment, comment_warnings = has_canonical_approval_comment(
```

**Gap proofs**:
- `docs/reports/continuous-planning-pipeline.md` generated 2026-04-26 shows Lane A: `0` and recommendation: `Recommend planning/QA only until approval candidates and review backlog recover.`
- `docs/plans/README.md` Step 5 currently says to post the completed plan as an issue comment but does not provide a fixed machine-readable schema.

<!-- Verification: count distinct sources above: issue #2503, parent #2489 plan, continuous-planning-pipeline.py, docs/plans/README.md, hard-stop policy, generated continuous planning report, skills/guidance. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-27-issue-2503-canonical-approval-request-comments.md` |
| Approval request template | `docs/standards/PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md` |
| Parser/validator implementation | `scripts/ai/continuous-planning-pipeline.py` |
| Tests | `tests/analysis/test_continuous_planning_pipeline.py` |
| Operator/backfill guide | `docs/governance/plan-review-approval-comment-backfill.md` |
| Plan review — Claude | `scripts/review/results/2026-04-26-plan-2503-claude.md` required for default pipeline readiness |
| Plan review — Codex | `scripts/review/results/2026-04-26-plan-2503-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-26-plan-2503-gemini.md` required for default pipeline readiness |
| Supplemental local review — Hermes | `scripts/review/results/2026-04-26-plan-2503-hermes.md` audit-only; not a substitute for default Claude/Codex/Gemini evidence |

---

## Deliverable

A documented and test-backed canonical approval-request comment schema plus parser/backfill guidance so Lane A can identify ready-for-user-decision issues without ever treating comments as implementation approval authority.

---

## Pseudocode

```
def render_approval_request(issue, plan_path, plan_sha, review_artifacts, verdicts):
    emit stable header: Plan Review Approval Request
    emit exact schema marker fields at top: Approval-Request-Schema: workspace-hub/plan-review-approval-request and Approval-Request-Version: 1
    emit exact field labels: Issue, Plan-Path, Plan-SHA256, Reviewed-Revision, Review-Artifacts, Review-Verdicts, Requested-Decision, Approval-Options, Authority-Warning, Requested-At-UTC
    encode Review-Artifacts and Review-Verdicts as order-independent provider-key maps with one line per required provider: `- claude: scripts/review/results/YYYY-MM-DD-plan-NNN-claude.md`, `- codex: ...`, `- gemini: ...` and `- claude: APPROVE|MINOR`; duplicate/missing provider keys or verdicts outside APPROVE/MINOR are `approval_comment_review_mismatch`
    emit issue, plan path, Plan-SHA256 (mandatory), optional reviewed commit/revision for audit only
    emit provider artifact table and verdicts
    emit explicit choices: Approve / Revise / Hold
    emit authority warning: execution unauthorized until status:plan-approved plus .planning marker
    emit backfill marker/version, timestamp


def parse_approval_request_comments(comments, comment_window, expected_plan_path, expected_plan_sha, review_evidence):
    if comments unavailable: return comment_check_failed
    preserve existing `closedByPullRequestsReferences`/PR handoff enrichment while adding comment_window metadata from GraphQL `issue.comments(last: 100) { totalCount nodes { body createdAt author { login } authorAssociation url } }`
    normalize nodes to newest-first and attach issue['comment_window'] = {'source': 'graphql', 'total_count': totalCount, 'fetched_count': len(nodes), 'exhaustive': len(nodes) >= totalCount, 'newest_first': True, 'fetch_limit': 100, 'fetch_failed': False}; each comment keeps `author_login`, `author_association`, and `url`
    scan canonical schema comments newest-first but separate trusted from untrusted
    collect untrusted canonical comments as `approval_comment_untrusted_author` warnings; they cannot supersede or block trusted canonical requests
    choose the newest trusted canonical schema comment (author_association OWNER/MEMBER/COLLABORATOR) as the authoritative request for freshness
    cross-check that trusted comment's Review-Artifacts and Review-Verdicts against explicit `review_evidence` from current `review_summary()` (`evidence['plan_sha256']`, `evidence['providers'][provider]['verdict']`, provider path/source fields when available); mismatch/missing provider evidence returns approval_comment_review_mismatch
    if the newest trusted canonical schema comment matches Plan-Path, Plan-SHA256, and current clean provider-review evidence: return ready_for_user_decision even when total_count > fetched_count
    if trusted canonical comments exist but the newest trusted one is stale/conflicting: return approval_comment_stale because `comments(last: 100)` contains the newest comments and older out-of-window comments cannot supersede it
    if no canonical schema comment is found and total_count > fetched_count: return comment_window_insufficient before considering ambiguous comments
    if GraphQL/window metadata is unavailable in live mode while comments were expected: return comment_check_failed
    require schema/version marker and all fixed fields
    reject stale comments deterministically as approval_comment_stale whenever the newest canonical schema comment exists but plan path or mandatory Plan-SHA256 does not match current plan; optional reviewed revision never substitutes for Plan-SHA256 freshness
    reject ambiguous free-text comments as approval_comment_ambiguous even if they contain approve/revise words
    warning precedence: comments API unavailable -> comment_check_failed; newest trusted canonical review-artifact/verdict mismatch -> approval_comment_review_mismatch; newest trusted canonical match -> ready_for_user_decision (with untrusted-author warning if untrusted schema comments also exist); newest trusted canonical stale/conflicting -> approval_comment_stale; no trusted canonical in truncated window -> comment_window_insufficient even if untrusted canonical comments are present; only untrusted canonical comments in an exhaustive window -> approval_comment_untrusted_author; exhaustive empty/fuzzy window -> approval_comment_ambiguous
    return ready_for_user_decision or deterministic warning code


def backfill_operator_guide(issue):
    require current clean provider review evidence first
    write body to temp file
    post with gh issue comment --body-file
    do not create approval marker or status:plan-approved label
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `docs/plans/README.md` | Add Step 5 pointer to the canonical template and keep this plan indexed in one edit |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | Collapse/redirect duplicated workflow/status authority text to a single canonical post/approval authority section; target line/heading families include `### Step 4: Post and Label`, duplicated `### Step 5/6: User Approval`, `### Status authority and surfacing rule`, `### Status precedence and stale-state handling`, `### Status precedence and surfacing rules`, `## Batch / Overnight Sessions`, and repeated `### Step 6: Implement (TDD)` sections |
| Modify | `.claude/skills/coordination/continuous-planning-pipeline/SKILL.md` | Update Lane A guidance to require a current canonical approval-request comment in addition to plan-review label and clean review evidence |
| Create | `docs/standards/PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md` | Durable schema/template, fixed fields, examples, and authority-boundary language |
| Create | `docs/governance/plan-review-approval-comment-backfill.md` | Operator guide for safe repost/backfill using `gh issue comment --body-file` |
| Modify | `scripts/ai/continuous-planning-pipeline.py` | Replace token-only comment heuristic with schema/version-aware parsing, GraphQL comment-window metadata, and deterministic warnings while preserving existing `closedByPullRequestsReferences`/Lane E PR evidence enrichment |
| Modify | `tests/analysis/test_continuous_planning_pipeline.py` | TDD fixtures for complete, ambiguous, stale, truncated/window-insufficient, missing-comment, and comment authority cases |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_canonical_approval_comment_unlocks_lane_a` | complete current comment enables Lane A | status:plan-review issue, clean reviews, current template comment | Lane A / `request_approval` |
| `test_free_text_approval_comment_is_ambiguous` | fuzzy comments do not count | comment says “please approve” without schema | `approval_comment_ambiguous`, not Lane A |
| `test_fixed_fields_without_schema_version_marker_are_ambiguous` | token-complete comments cannot bypass schema gate | comment includes issue/path/SHA/artifacts/choices/warning but lacks exact schema/version marker | `approval_comment_ambiguous`, not Lane A |
| `test_stale_approval_comment_plan_sha_blocks_lane_a` | old comment cannot approve new revision | comment has old mandatory Plan-SHA256 or plan path | `approval_comment_stale`, not Lane A |
| `test_missing_comments_returns_comment_check_failed` | API failure/unavailable comments are explicit | issue JSON lacks `comments` | `comment_check_failed`, not Lane A |
| `test_current_template_in_newest_window_unlocks_even_when_total_count_exceeds_100` | a matching newest trusted canonical approval request in the newest fetched GraphQL window is sufficient evidence | GraphQL `totalCount` > 100 and newest canonical node includes trusted authorAssociation, matching Plan-SHA256, and matching review artifacts/verdicts | Lane A / `request_approval` |
| `test_insufficient_comment_window_blocks_lane_a` | bounded/truncated comment evidence does not unlock approval when no current canonical request is seen | GraphQL `totalCount` exceeds fetched newest 100 comments and nodes omit current canonical request | `comment_window_insufficient`, not Lane A |
| `test_exhaustive_comment_window_without_template_is_ambiguous` | complete comment evidence with no schema is not approval-ready | exhaustive comments omit canonical request but contain fuzzy approval words | `approval_comment_ambiguous`, not Lane A |
| `test_live_issue_enrichment_fetches_comment_window_metadata` | live mode passes GraphQL comment-window metadata into parser | mocked `gh api graphql` response with `totalCount` and comment nodes including `authorAssociation` | issue dict has `comments` and `comment_window` keys: `source`, `total_count`, `fetched_count`, `exhaustive`, `newest_first`, `fetch_limit`, `fetch_failed`; comments retain author login/association/url |
| `test_comment_window_enrichment_preserves_pr_handoff_references` | Lane A comment hardening does not regress Lane E | mocked issue with `closedByPullRequestsReferences` plus GraphQL comments | issue retains PR handoff evidence and existing Lane E classifier fixtures still pass |
| `test_live_graphql_comment_fetch_failure_returns_comment_check_failed` | live failures never silently downgrade to ambiguous or ready | mocked `gh api graphql` nonzero exit/timeout/malformed JSON/GraphQL errors/missing `totalCount`/missing `nodes` | issue has `comment_window.fetch_failed=True` and parser returns `comment_check_failed` |
| `test_comments_present_without_comment_window_is_not_ready` | old-style fixtures/live enrichment cannot bypass the new window contract | issue has `comments` list but lacks `comment_window` metadata | `comment_check_failed` (or explicit non-ready warning), never Lane A |
| `test_comment_warning_precedence_is_deterministic` | unavailable/stale/truncated/ambiguous states do not collapse together | fixture matrix | exact warning precedence from pseudocode |
| `test_newer_conflicting_canonical_comment_blocks_older_matching_comment` | superseded approval requests cannot unlock Lane A | newest canonical schema comment has stale SHA, older canonical comment matches current SHA | `approval_comment_stale`; never Lane A |
| `test_untrusted_author_canonical_comment_does_not_unlock_lane_a` | arbitrary commenters cannot manufacture approval-buffer work | canonical comment has matching SHA but authorAssociation is NONE/FIRST_TIMER/CONTRIBUTOR | `approval_comment_untrusted_author`, not Lane A |
| `test_untrusted_canonical_comment_does_not_block_trusted_match` | untrusted schema comments cannot denial-of-service trusted requests | newest canonical comment untrusted, older trusted canonical comment matches current plan/reviews | Lane A / `request_approval` plus `approval_comment_untrusted_author` audit warning |
| `test_only_untrusted_comments_in_truncated_window_is_insufficient` | untrusted comments do not mask possible trusted comments outside fetched window | truncated window contains only untrusted canonical comments | `comment_window_insufficient`, not `approval_comment_untrusted_author`, not Lane A |
| `test_canonical_comment_review_artifacts_must_match_current_review_summary` | displayed review evidence cannot drift from actual provider evidence | parser receives explicit `review_evidence`; canonical comment has current SHA but missing/stale/MAJOR/unavailable provider-key map compared with `review_summary()` | `approval_comment_review_mismatch`, not Lane A |
| `test_review_artifact_and_verdict_maps_are_order_independent_and_complete` | machine grammar is fixed enough to parse reliably | `Review-Artifacts`/`Review-Verdicts` provider maps with reordered providers, duplicate keys, missing keys, bad verdicts | reordered valid maps pass; duplicate/missing/bad verdicts return `approval_comment_review_mismatch` |
| `test_parser_signature_requires_review_evidence_argument` | parser remains deterministic and fixture-driven | direct parser call without review evidence / with explicit review evidence | no implicit filesystem/global recomputation; exact `review_evidence` controls artifact/verdict matching |
| `test_comment_never_unlocks_lane_b_without_marker` | approval-request comment is not execution authority | status:plan-review or no marker | not Lane B |
| `test_backfill_template_contains_body_file_guidance` | docs prevent shell quoting/comment mutation mistakes | template/backfill doc | mentions `gh issue comment --body-file` and marker boundary |
| `test_backfill_guide_requires_clean_default_provider_reviews` | repost/backfill cannot manufacture approval readiness | backfill guide/template | requires current clean Claude/Codex/Gemini review evidence and warns against reposting when evidence is missing/stale/unavailable/MAJOR |
| `test_template_contains_required_fields` | docs stay machine-parseable | template markdown | fields include exact `Approval-Request-Schema: workspace-hub/plan-review-approval-request`, `Approval-Request-Version: 1`, issue, plan path, mandatory Plan-SHA256, review artifacts/verdicts, timestamp, choices, marker warning |
| `test_requested_at_utc_must_be_parseable_zulu_timestamp` | timestamp field is machine-validated, not mere prose | canonical comments with valid `YYYY-MM-DDTHH:MM:SSZ` and malformed timestamps | valid parses; malformed returns `approval_comment_ambiguous`/metadata warning and not Lane A |
| `test_template_example_round_trips_through_parser` | published docs and parser cannot drift | canonical example/body from `PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md` rendered with current plan path/SHA/reviews | parser returns ready-for-user-decision/Lane A inputs accepted |
| `test_planning_skills_reference_canonical_approval_request_template` | executable agent guidance does not drift from docs | `.claude/skills/coordination/issue-planning-mode/SKILL.md` and `continuous-planning-pipeline/SKILL.md` | both reference the template and Lane A approval-comment requirement |
| `test_issue_planning_mode_duplicate_sections_all_reference_canonical_request` | duplicated workflow/status sections cannot retain old fuzzy-post guidance | issue-planning-mode headings for Step 4, Step 5/6 approval, status authority/precedence/surfacing, Batch/Overnight Sessions, repeated implementation sections | every relevant section either references the canonical template or defers to a single canonical Step 4 authority block |

---

## Acceptance Criteria

- [ ] Canonical approval-request comment template exists at `docs/standards/PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md` with fixed fields: exact `Approval-Request-Schema: workspace-hub/plan-review-approval-request`, exact `Approval-Request-Version: 1`, issue, plan path, mandatory Plan-SHA256, optional reviewed revision for audit only, order-independent `Review-Artifacts` and `Review-Verdicts` provider maps for claude/codex/gemini, Approve / Revise / Hold choices, parseable `Requested-At-UTC` in `YYYY-MM-DDTHH:MM:SSZ`, and marker/authority warning.
- [ ] Planning workflow docs and executable planning skills reference the template before applying `status:plan-review`; duplicated workflow/status sections in `issue-planning-mode`, including Batch/Overnight Sessions, are structurally collapsed or redirected to one canonical post/approval authority section rather than retaining parallel authority prose; continuous-planning skill Lane A guidance requires current canonical approval-request evidence.
- [ ] Parser/validator distinguishes complete current comments from ambiguous, stale, untrusted-author, review-mismatch, missing-comment/API-failed, and `comment_window_insufficient` states using the explicit `comment_window` issue-data contract (`source`, `total_count`, `fetched_count`, `exhaustive`, `newest_first`, `fetch_limit`, `fetch_failed`) plus comment `author_association`/URL metadata and explicit `review_evidence` argument; GraphQL failures, malformed JSON, GraphQL error payloads, missing `totalCount`, missing `nodes`, malformed `Requested-At-UTC`, or old-style `comments` without `comment_window` return `comment_check_failed`/non-ready; comments lacking the exact schema/version marker are ambiguous even if all human-readable tokens are present; only the newest trusted canonical schema comment can unlock readiness, untrusted canonical comments are audit warnings rather than denial-of-service blockers when trusted evidence exists, truncated windows with only untrusted canonical comments remain `comment_window_insufficient`, and trusted comments must match current Plan-SHA256 plus current clean provider review artifact/verdict maps.
- [ ] Approval-request comments never create implementation authority without `status:plan-approved` and `.planning/plan-approved/<issue>.md`.
- [ ] Backfill guidance uses `gh issue comment --body-file`, requires current clean default-provider review evidence before reposting, and explicitly preserves approval-drift semantics; this is justified by #2489 Lane A’s clean-review evidence requirement, `docs/plans/README.md` all-issue planning gates, and AGENTS.md approval gates. Legacy clean-looking review artifacts that lack `Plan-SHA256`/current revision binding are not sufficient for backfill; operators must refresh provider review evidence rather than override.
- [ ] Targeted tests pass for the new parser/docs contract plus existing continuous-planning-pipeline tests, including existing Lane E PR handoff fixtures that depend on `closedByPullRequestsReferences`.
- [ ] No approval markers are created and no issues are moved to `status:plan-approved` by this implementation.
- [ ] Adversarial plan review artifacts are posted under `scripts/review/results/` and committed with the plan before moving this issue to `status:plan-review`; header/Artifact Map paths may refer to local uncommitted draft artifacts during review, but the GitHub status label/comment step is blocked until those same paths are retrievable from `main` after push.
- [ ] `docs/plans/README.md` contains the #2503 index row and the Step 5 template link in the same committed planning update.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Required default-provider artifact before `status:plan-review`; not replaced by Hermes. |
| Codex | MAJOR → addressed in r14 | r1 required explicit `comment_window_insufficient` contract, live evidence metadata, deterministic stale warning, and locked template path; r2 required planning-skill updates, continuous-planning skill Lane A update, exact GraphQL retrieval, mandatory Plan-SHA256 freshness, and canonical artifact paths; r3 required newest-window success semantics, live-enrichment TDD, warning precedence, and review-provider clarity; r4 required default provider evidence clarity, truncated-window precedence fix, backfill safety test, and timestamp test coverage; r5 required draft-artifact/main retrieval clarity, full duplicated-skill update scope, newest-canonical precedence, explicit `comment_window` keys, and README index acceptance; r6 required newest-stale precedence and schema/version marker acceptance/tests; r7 required removing contradictory exhaustive-window stale wording, enumerating issue-planning-mode duplicate section targets, and justifying clean-review backfill prerequisite; r8 required exact schema/version strings, GraphQL failure/malformed tests, corrected policy citation, and legacy no-SHA review handling for backfill; r9 required template/parser round-trip test and old-style comments-without-window regression; r10 required trusted-author validation, review-artifact/verdict cross-checking, and clearer local-vs-committed artifact status; r11 required exact `review_summary()` evidence shape, newest-untrusted-over-older-trusted test, and structural skill duplicate cleanup; r12 required untrusted-comments-as-warning semantics, Batch/Overnight guidance coverage, and parser signature accepting explicit `review_evidence`; r13 required truncated-window precedence for untrusted-only windows and exact machine grammar for review artifact/verdict provider maps; r14 required preserving Lane E `closedByPullRequestsReferences` enrichment and parseable UTC timestamp validation. |
| Gemini | PENDING | Required default-provider artifact before `status:plan-review`; not replaced by Hermes. |
| Hermes | PENDING | Supplemental local review may be recorded, but is audit-only and not a substitute for default Claude/Codex/Gemini evidence. |

**Overall result:** PENDING — Codex findings addressed locally; keep local status `draft` until fresh review finds no MAJOR blockers and required Claude/Codex/Gemini artifacts exist. Hermes review evidence is supplemental only.

Revisions made based on review:
- r1: locked template path to `docs/standards/PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md`; added explicit `comment_window_insufficient` data-model/test contract; made stale comments deterministically `approval_comment_stale`; created a separate governance backfill guide; consolidated duplicate README file-change rows.
- r2: added `.claude/skills/coordination/issue-planning-mode/SKILL.md` and `.claude/skills/coordination/continuous-planning-pipeline/SKILL.md` as implementation surfaces; specified GraphQL `comments(last: 100)` retrieval with `totalCount`; made Plan-SHA256 mandatory and reviewed revision audit-only; canonicalized artifact map to local 2026-04-26 artifacts.
- r3: clarified that a current canonical request found in the newest fetched comments unlocks Lane A even when total comments exceed the fetch window; added live-enrichment and warning-precedence tests; documented Codex + Hermes as local review evidence while Claude/Gemini remain pending/recommended.
- r4: made Claude/Codex/Gemini artifacts required for default pipeline readiness; moved truncated-window warning ahead of stale when the fetched window is incomplete; added clean-review prerequisite to backfill tests; added timestamp to required template-field test.
- r5: clarified that local draft artifacts are committed before they are expected on `main`; expanded `issue-planning-mode` scope to all duplicate/conflicting workflow sections; made newest canonical schema comment authoritative; defined exact `comment_window` issue-data keys; added README index acceptance.
- r6: fixed newest-stale precedence for `comments(last: 100)`; added schema/version marker to required fields and acceptance criteria; added a token-complete-but-marker-missing negative parser test.
- r7: removed contradictory exhaustive-window stale wording; enumerated exact `issue-planning-mode` duplicate heading families that must be updated; justified backfill clean-review prerequisite using #2489 Lane A and hard-stop policy.
- r8: specified exact schema/version marker strings and field labels; added GraphQL failure/malformed-response tests; corrected backfill prerequisite citation to #2489 Lane A, README, and AGENTS all-issue gates; defined legacy no-SHA reviews as insufficient for backfill.
- r9: added template-example/parser round-trip test; added regression for `comments` present without `comment_window` metadata; demoted hard-stop policy to context-only because #2503 is a harness/workflow issue, not engineering-critical.
- r10: added authorAssociation trust check, current review-summary artifact/verdict cross-check, warning codes for untrusted author/review mismatch, and explicit statement that local artifact paths block status promotion until committed/pushed and retrievable.
- r11: cited current `review_summary()` location/evidence shape; added newest-untrusted-over-older-trusted precedence test; changed skill update from editing duplicate prose to structurally collapsing/redirecting duplicate authority sections.
- r12: changed untrusted canonical comments from denial-of-service blockers to audit warnings when trusted canonical evidence exists; added Batch/Overnight Sessions to skill scope/tests; changed parser interface to accept `comment_window` and explicit `review_evidence`.
- r13: made truncated windows with only untrusted canonical comments return `comment_window_insufficient`; specified exact order-independent provider-key map grammar for `Review-Artifacts` and `Review-Verdicts` plus duplicate/missing/bad-verdict behavior.
- r14: added requirement/tests to preserve existing `closedByPullRequestsReferences` Lane E enrichment while adding GraphQL comments; made `Requested-At-UTC` parseable Zulu timestamp a machine-validated field.

---

## Risks and Open Questions

- **Risk:** Overly strict parsing could keep valid historical plan-review issues out of Lane A. Mitigation: expose deterministic warnings and provide safe backfill instructions rather than silently accepting fuzzy comments.
- **Risk:** Comment windows from GitHub API can be incomplete. Mitigation: use GraphQL `comments.totalCount` and fetched-node count; classify unavailable or truncated evidence as `comment_window_insufficient`/`comment_check_failed` rather than approval-ready.
- **Risk:** Operators may confuse “approval request” with “approval granted.” Mitigation: every template/backfill path must state execution remains unauthorized until `status:plan-approved` and a committed local marker exist.
- **Decision:** the durable template lives at `docs/standards/PLAN_REVIEW_APPROVAL_REQUEST_TEMPLATE.md`; `docs/plans/README.md` Step 5 links to it instead of duplicating the full schema.

---

## Complexity: T2

**T2** — bounded workflow/harness hardening across one report script, planning docs/template, and tests. It is not T3 because it does not change dispatch scheduling, approval markers, or implementation gates.
