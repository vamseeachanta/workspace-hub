# Plan for #2129: Automate Issue-State Drift and Redundancy Audit Across GitHub + Analysis Artifacts

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2129
> **Review artifacts:** pending — `scripts/review/results/2026-04-11-plan-2129-claude.md`, `scripts/review/results/2026-04-11-plan-2129-codex.md`, `scripts/review/results/2026-04-11-plan-2129-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/knowledge/review-open-issues.py` — currently fetches only open issue `number,title,labels`, groups by category/priority, and emits table/yaml/json summaries. It does not inspect issue state drift, issue relationships, artifact freshness, repo-reality contradictions, or duplicate structure.
- Found: `scripts/knowledge/tests/test_review_open_issues.py` — existing lightweight unit coverage for grouping/formatting can be extended for issue-hygiene audit logic.
- Found: `scripts/refresh-agent-work-queue.py` — deterministic GitHub queue summarizer with tested markdown/staleness/parity patterns, useful as an output-shaping reference but not a drift detector.
- Found: `tests/work-queue/test_queue_refresh.py` — demonstrates deterministic fixture-heavy testing patterns for GitHub-derived reports.
- Found: `docs/reports/issue-overlap-audit-2026-03-31.md` — already documents duplicate canonicalization patterns and explicitly flags #53 for re-evaluation, giving a seeded duplicate/stale-premise corpus.
- Found: `docs/plans/claude-ops-2026-04-10-052749/results/2050.md`, `2020.md`, `2027.md`, `1839.md`, `1899.md` — current analysis artifacts cited by issue #2129 comments as concrete stale/contradictory examples.
- Found: `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` — current weekly-review scope still says to open follow-on issues broadly and does not yet reference a dedicated hygiene audit.
- Gap: No current script produces deterministic `refresh / merge / close / verify` recommendations from live GitHub issue state plus local artifact evidence.
- Gap: No current artifact invalidation layer detects when a generated result becomes stale within hours because issue state changed.
- Gap: No current duplicate detector requires structural evidence beyond title similarity.
- Gap: No current repo-reality checker validates that cited paths/config claims inside generated analysis still match the repo.

### Standards
| Standard | Status | Source |
|---|---|---|
| GitHub issue-planning workflow in `docs/plans/README.md` | done | local repo workflow reference |
| Deterministic operator output (`refresh / merge / close / verify`) from issue #2129 comments | gap | GitHub issue #2129 comments dated 2026-04-10 and 2026-04-11 |
| Duplicate-anchor baseline for overlap handling | done | `docs/reports/issue-overlap-audit-2026-03-31.md` |

### LLM Wiki pages consulted
- None specific to this repo task; no relevant wiki page was required beyond local repo docs and issue history.

### Documents consulted
- `docs/plans/_template-issue-plan.md`
- `docs/plans/README.md`
- `docs/reports/issue-overlap-audit-2026-03-31.md`
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- `docs/plans/claude-ops-2026-04-10-052749/results/1839.md`
- `docs/plans/claude-ops-2026-04-10-052749/results/1899.md`
- `docs/plans/claude-ops-2026-04-10-052749/results/2050.md`
- `docs/plans/claude-ops-2026-04-10-052749/results/2020.md`
- `docs/plans/claude-ops-2026-04-10-052749/results/2027.md`
- GitHub issue #2129 body and three owner comments
- GitHub issue #53 live state (`OPEN`) versus overlap audit recommendation to close/defer because original premise no longer matches repo reality

### Gaps identified
- `review-open-issues.py` needs a new audit mode that joins live GitHub issue metadata with local result artifacts instead of only grouping labels.
- The repo lacks a parser/index for generated analysis artifacts under `docs/plans/**/results/*.md` and therefore cannot invalidate stale recommendations after issue closure or parent/child status changes.
- The repo lacks a contradiction check that compares artifact claims against current filesystem/config reality; live check confirms `.claude/skills/workspace-hub/session-start-routine` is missing, which matches one cited contradiction pattern in `results/1839.md` and should become a fixture rather than an ad hoc observation.
- The repo lacks a duplicate scoring pass that combines title/body similarity with at least one structural signal such as same parent cluster, same target paths, same label/category cluster, or prior overlap-audit membership.
- Weekly review documentation does not yet consume a dedicated hygiene audit, so the current flow can still spawn overlapping tickets rather than first surfacing drift.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2129-issue-state-drift-redundancy-audit.md` |
| Core implementation | `scripts/knowledge/review-open-issues.py` |
| Core tests | `scripts/knowledge/tests/test_review_open_issues.py` |
| Additional fixtures (expected) | `scripts/knowledge/tests/fixtures/issue_hygiene/` |
| Machine-readable audit output | `logs/quality/issue-hygiene-audit-latest.json` |
| Operator report output | `logs/quality/issue-hygiene-audit-latest.md` |
| Weekly-review doc update | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` |
| Duplicate baseline input | `docs/reports/issue-overlap-audit-2026-03-31.md` |
| Review artifact — Claude | `scripts/review/results/2026-04-11-plan-2129-claude.md` |
| Review artifact — Codex | `scripts/review/results/2026-04-11-plan-2129-codex.md` |
| Review artifact — Gemini | `scripts/review/results/2026-04-11-plan-2129-gemini.md` |

---

## Deliverable

An issue-hygiene audit mode in `scripts/knowledge/review-open-issues.py` that scans live GitHub issues plus local generated analysis artifacts, flags stale/redundant issue state in four bounded categories, and emits deterministic JSON and operator-readable `refresh / merge / close / verify` recommendations that the weekly-review flow can consume.

---

## Pseudocode

```text
function fetch_live_issue_snapshot(repo, limit):
    query open and recently-updated issues with labels, state, timestamps, body, comments
    normalize child/parent references and recent closure transitions

function scan_analysis_artifacts(root_glob):
    load docs/plans/**/results/*.md
    extract referenced issue numbers, verdict phrases, recommended actions, cited repo paths
    store artifact timestamp and evidence snippets

function classify_hygiene_findings(issue_snapshot, artifact_index, repo_state):
    flag stale artifacts when recommended action conflicts with live issue state
    flag parent/child drift when umbrellas still route through closed/subsumed children
    flag stale issue premises when repo paths/config reality contradict issue/artifact claims
    flag duplicates only when semantic similarity plus a structural signal both exist

function render_outputs(findings):
    emit stable JSON schema with category, evidence, recommendation, confidence
    emit concise markdown report grouped by refresh/merge/close/verify
    return non-zero only for schema/data errors, not for ordinary findings

function integrate_weekly_review():
    update weekly-review documentation/entrypoint to reference hygiene audit before opening more tickets
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/knowledge/review-open-issues.py` | Extend from label-grouping utility into bounded issue-hygiene audit mode |
| Modify | `scripts/knowledge/tests/test_review_open_issues.py` | Add regression coverage for stale artifacts, duplicates, premise contradictions, and output schema |
| Create | `scripts/knowledge/tests/fixtures/issue_hygiene/` | Hold deterministic fixture snapshots for issue/artifact drift cases |
| Update | `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md` | Reference the hygiene audit as the review gate before creating more overlapping tickets |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_flags_stale_artifact_when_issue_closed_after_generation` | Closed issues invalidate stale action artifacts | fixture modeled on `results/2050.md` or `results/2020.md` plus live issue state `CLOSED` | finding category=`stale-artifact`, recommendation=`refresh` or `close` with issue/artifact evidence |
| `test_flags_parent_child_drift_for_umbrella_with_closed_child` | Umbrella issue recommendations are invalidated by changed child state | fixture modeled on `results/1899.md` routing through child `#2056` now `CLOSED` | finding category=`parent-child-drift`, recommendation=`refresh` or `verify` |
| `test_flags_repo_reality_contradiction_for_cited_missing_or_changed_path` | Audit catches stale issue/artifact claims contradicted by repo reality | fixture modeled on `results/1839.md` plus current filesystem/config snapshot | finding category=`repo-reality-contradiction`, recommendation=`verify` |
| `test_flags_stale_issue_premise_when_original_issue_no_longer_matches_repo` | Open issue premise can be stale even without a result artifact | issue fixture modeled on live #53 plus overlap-audit evidence | finding category=`stale-premise`, recommendation=`verify` or `close` |
| `test_requires_structural_signal_for_duplicate_detection` | Title similarity alone does not produce duplicate verdicts | two issue fixtures with similar titles but no shared structural signal | no duplicate finding |
| `test_detects_duplicate_cluster_with_structural_evidence` | Duplicate detection works when overlap signals exist | fixture anchored to `docs/reports/issue-overlap-audit-2026-03-31.md` duplicate sets | finding category=`duplicate`, recommendation=`merge` |
| `test_emits_stable_machine_readable_schema` | JSON output shape is deterministic and machine-consumable | mixed finding fixture corpus | stable ordered JSON with category, recommendation, evidence, issue refs |
| `test_operator_report_groups_findings_by_action_bucket` | Human report is concise and action-oriented | mixed findings | markdown sections for `refresh`, `merge`, `close`, `verify` |
| `test_weekly_review_reference_points_to_hygiene_audit` | Weekly-review flow references hygiene audit instead of opening more overlap blindly | updated doc content | explicit hygiene-audit reference present |

---

## Acceptance Criteria

- [ ] `scripts/knowledge/review-open-issues.py` gains a bounded issue-hygiene audit mode without regressing existing grouping output.
- [ ] Audit surfaces at least one current-repo example for each required category: stale artifact, duplicate/near-duplicate, stale issue premise/repo contradiction, and parent/child drift.
- [ ] Duplicate detection requires at least one structural signal beyond title similarity.
- [ ] Audit emits stable machine-readable JSON plus a concise markdown/operator summary using only deterministic actions: `refresh / merge / close / verify`.
- [ ] Weekly-review flow documentation references this hygiene audit before opening more overlapping tickets.
- [ ] Unit tests cover the anchored examples from #2129 comments and prevent the known false-positive patterns.
- [ ] Review artifacts are posted to `scripts/review/results/` before the plan status advances beyond `draft`.

---

## Adversarial Review Summary

Pre-review findings captured from live repo evidence and issue comments; formal multi-provider plan review is still pending.

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Live repo review confirms the current script gap: `review-open-issues.py` only groups labels, while stale examples already exist (`#2050`, `#2020`, `#2027`, `#2056` closed after analysis generation; `#1899` still open as an umbrella; `#53` remains open despite overlap audit recommending re-evaluation). |
| Codex | PENDING | Not yet run; review artifact not collected. Planned focus: schema stability, fixture strategy, and false-positive guards for duplicate detection. |
| Gemini | PENDING | Not yet run; review artifact not collected. Planned focus: breadth of artifact scanning and weekly-review integration risks. |

**Overall result:** PENDING — keep status `draft` until formal adversarial review artifacts are collected.

Revisions made based on review:
- Added explicit four-category P0 boundary from issue comments: stale artifacts, duplicates, repo-reality contradictions/stale premises, and parent/child drift.
- Added false-positive guard that duplicate detection must require structural evidence beyond title similarity.
- Added explicit live anchors for current stale-state examples (`#2050`, `#2020`, `#2027`, `#2056`, `#1899`, `#53`).

---

## Risks and Open Questions

- **Risk:** Over-expanding `review-open-issues.py` could turn a simple grouping script into an unbounded portfolio-analysis tool; scope must stay on the four P0 detection categories called out in #2129 comments.
- **Risk:** Artifact parsing may be brittle if result docs vary in format; plan should treat evidence extraction as bounded heuristics with deterministic fallbacks.
- **Risk:** Repo-reality contradiction checks can create false positives if they rely on one file path only; the audit should preserve `verify` as the default recommendation when evidence is incomplete.
- **Risk:** Duplicate detection is especially easy to overfire in a repo with many related governance tickets; structural-signal requirements are mandatory.
- **Open:** Should stale artifacts with already-closed target issues recommend `refresh` (artifact refresh) or `close` (operator close-out of the stale task record) when both are plausible?
- **Open:** Which recently closed issues should remain in the live query window so same-day stale artifacts are still caught reliably?
- **Open:** Should umbrella/meta issues default to `verify` unless they contain direct executable scope, matching the issue comments’ false-positive guard?

---

## Complexity: T3

**T3** — this is a multi-signal audit spanning GitHub issue state, local artifact parsing, repo-reality checks, deterministic report generation, fixture-heavy regression tests, and weekly-review workflow integration.