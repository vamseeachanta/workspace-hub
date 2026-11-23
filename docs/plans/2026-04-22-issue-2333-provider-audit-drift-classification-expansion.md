# Plan for #2333: Provider-audit drift classification expansion

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2333
> **Review artifacts:** `scripts/review/results/2026-04-22-plan-2333-codex.md`, `scripts/review/results/2026-04-22-plan-2333-gemini.md`

---

## Resource Intelligence Summary

### Attested repo evidence
- `scripts/analysis/provider_session_ecosystem_audit.py` exists and is the owning classifier/output generator for this issue.
- `analysis/provider-session-ecosystem-audit.json` exists and already shows Codex generated-site/adjacent-project examples currently counted under actionable repo-local drift.
- `docs/reports/provider-session-ecosystem-audit.md` exists and already distinguishes recent event-time activity from corpus-change interpretation.
- `docs/reports/2026-04-20-provider-audit-followup-bundle.md` exists and already groups the concrete non-actionable families relevant to this issue: generated-site/adjacent-project paths, `github://...` symbolic URIs, and cross-repo paths such as `digitalmodel/specs/module-registry.yaml`.
- Existing code-level behavior to preserve in this issue:
  - symbolic targets stay separate from repo drift
  - sibling-repo targets stay separate from repo drift
  - external/transient worktree and scratch-path reads stay separate from repo drift

### Concrete scope alignment with Issue #2333
The issue title and body require transient worktree and scratch-path reads to remain separate from actionable repo drift. This plan therefore has two explicit responsibilities:
1. Preserve and test the existing non-actionable separation for transient/worktree/external reads.
2. Add one new non-actionable repo-relative bucket (`non_repo_artifact`) for generated-site/adjacent-project artifact families that are currently being miscounted as actionable repo drift.

This is an expansion of the same anti-noise objective, not a scope pivot away from transient/scratch-path handling.

### Scope boundary
- In scope: classifier taxonomy/precedence, audit JSON shape needed to expose the new bucket, generated markdown rendering updates produced by rerunning the audit script, and deterministic tests with fixed fixtures/assertions.
- Out of scope: changing legacy redirect policy docs, adding downstream playbooks, or manually editing generated report prose outside the audit generator.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2333-provider-audit-drift-classification-expansion.md` |
| Audit engine | `scripts/analysis/provider_session_ecosystem_audit.py` |
| Audit tests | `tests/analysis/test_provider_session_ecosystem_audit.py` |
| Generated audit JSON | `analysis/provider-session-ecosystem-audit.json` |
| Generated audit markdown | `docs/reports/provider-session-ecosystem-audit.md` |
| Prior follow-up bundle | `docs/reports/2026-04-20-provider-audit-followup-bundle.md` |
| Codex review | `scripts/review/results/2026-04-22-plan-2333-codex.md` |
| Gemini review | `scripts/review/results/2026-04-22-plan-2333-gemini.md` |

---

## Deliverable

A draft-ready implementation plan that introduces one new non-actionable drift bucket for generated-site/adjacent-project repo-relative paths, preserves existing sibling-repo/symbolic/external separation, and hardens the audit’s event-time-versus-corpus-change contract with concrete JSON/markdown assertions and fixed fixtures.

---

## Canonical Taxonomy and Precedence

Decision: generated-site paths will not be a top-level peer bucket. They will be a subtype inside a broader non-actionable repo-relative class named `non_repo_artifact`.

Rationale:
- The current code only has one actionable repo-relative lane (`repo`) plus non-repo lanes (`sibling_repo`, `symbolic`, `external`), so a broader “repo-relative but non-workspace-hub artifact” class fits the existing classifier shape better than a one-off `generated_site` bucket.
- The concrete path family under review (`content/demos/*.html`, `build.js`, `vercel.json`, `examples/demos/gtm/output/*.html`) is important, but the approval concern is to keep it out of actionable stale-path debt. A broader class prevents repeated taxonomy churn when the next adjacent-project family appears.
- The subtype still needs to be preserved in output so reviewers can see why a path was excluded from actionable repo drift.

Precedence order for `classify_read_target` and downstream counting:
1. `blank` — empty or null target.
2. `symbolic` — skill names, `github://...`, and slash-delimited symbolic identifiers that do not map to a repo path.
3. `external` — absolute or tilde-expanded paths outside the repo root.
4. `sibling_repo` — repo-relative paths whose first path component is a known repo name other than the current repo.
5. `non_repo_artifact` — repo-relative paths that syntactically look local but match the explicit generated-site/adjacent-project fixture rules below.
6. `repo` — everything else under the repo-relative lane.

Initial `non_repo_artifact` matcher contract for this issue:
- Exact files: `build.js`, `vercel.json`, `package.json`
- Prefixes: `content/demos/`, `content/partials/`, `examples/demos/gtm/output/`
- Purpose note in code/tests: these are recurring generated-site/adjacent-project artifacts observed in Codex audit output and should not inflate actionable workspace-hub stale-path counts.

Output contract for the new class:
- Add per-provider `top_non_repo_artifact_reads` and `non_repo_artifact_read_total` to the audit JSON summary.
- Exclude `non_repo_artifact` rows from `top_missing_repo_reads`, `missing_repo_reads`, and legacy remediation hints.
- Render a separate markdown section named `top non-repo artifact reads` for each provider.

---

## Concrete anomaly/event-time separation contract

The implementation will keep the existing reconciliation model and make it explicit in tests/docs rather than redefining it.

Required logic:
1. `recent_activity_since_previous_audit` remains event-time-only and is derived from raw post-hook log timestamps strictly greater than the previous audit timestamp.
2. `corpus_change_since_previous_audit` remains snapshot-to-snapshot and compares current provider summary totals against the previous audit snapshot.
3. Provider anomaly status is computed exactly as:
   - `post_record_delta = current_post_records - previous_post_records`
   - `event_time_post_records_since_previous_audit = recent_activity.providers[provider].post_records`
   - `reconciliation_gap_post_records = post_record_delta - event_time_post_records_since_previous_audit`
   - status `aligned` iff gap `== 0`
   - status `positive_corpus_growth_beyond_recent_activity` iff gap `> 0`
   - status `corpus_pruned_or_rebuilt` iff gap `< 0`
4. The report/output surface that tests must assert is:
   - JSON: `executive_summary.recent_activity_since_previous_audit.scope_note`
   - JSON: `executive_summary.corpus_change_since_previous_audit.scope_note`
   - JSON: per-provider `event_time_post_records_since_previous_audit`, `reconciliation_gap_post_records`, `status`, `interpretation`
   - Markdown: the provider corpus-change block lines for event-time post records, reconciliation gap, status, and interpretation
5. Classification expansion must not mutate this anomaly logic except insofar as path re-bucketing changes provider `missing_repo_reads`; the event-time/corpus separation remains post-record based and independently testable.
6. Existing transient/worktree/scratch-path handling must remain separate from actionable repo drift after the new `non_repo_artifact` bucket is added; tests must prove that `/mnt/local-analysis/worktrees/...` and `/tmp/...` examples still land in the non-actionable external/transient lane rather than being swallowed by `repo` or `non_repo_artifact`.

---

## Implementation Plan

1. Extend `classify_read_target` support in `scripts/analysis/provider_session_ecosystem_audit.py` with a deterministic `non_repo_artifact` decision point that runs after `sibling_repo` detection and before defaulting to `repo`.
2. Update provider summarization counters so `non_repo_artifact` reads accumulate in their own totals/top lists and no longer flow into actionable missing repo read counts or remediation-hint generation.
3. Update JSON summary assembly and markdown rendering so the new bucket is visible as a first-class reported output alongside symbolic/sibling/external surfaces.
4. Keep the existing corpus reconciliation algorithm, but tighten its contract in tests by asserting the exact JSON fields and markdown lines described above.
5. Regenerate `analysis/provider-session-ecosystem-audit.json` and `docs/reports/provider-session-ecosystem-audit.md` via the audit script so the checked-in generated artifacts reflect the new classification output.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/analysis/provider_session_ecosystem_audit.py` | add `non_repo_artifact` classification/counters/rendering and keep corpus reconciliation output explicit |
| Modify | `tests/analysis/test_provider_session_ecosystem_audit.py` | add fixed-fixture tests for bucket routing and exact anomaly/report output surfaces |
| Regenerate | `analysis/provider-session-ecosystem-audit.json` | generated audit JSON must reflect the new bucket totals/output fields |
| Regenerate | `docs/reports/provider-session-ecosystem-audit.md` | generated markdown must reflect the new bucket totals/output sections |

---

## TDD Test List

| Test name | What it verifies | Fixed fixture/input | Expected output/assertion |
|---|---|---|---|
| `test_classify_read_target_marks_generated_site_examples_as_non_repo_artifact` | Codex-style generated-site paths stop falling into `repo` | call `classify_read_target` with `content/demos/index.html`, `build.js`, `vercel.json`, and `examples/demos/gtm/output/demo_02_wall_thickness_report.html` against a tmp repo that does not contain them | each call returns scope `non_repo_artifact` and `exists is False` |
| `test_classify_read_target_keeps_transient_worktree_and_tmp_paths_in_external_lane` | existing transient/scratch-path separation is preserved | call `classify_read_target` with `/mnt/local-analysis/worktrees/workspace-hub-2151/docs/modules/ai/readiness-evidence-bundle.schema.yaml` and `/tmp/pending-queue-snapshot.txt` | each call returns scope `external` and does not contribute to repo-local missing drift |
| `test_summarize_raw_provider_excludes_non_repo_artifact_reads_from_missing_repo_counts` | summarization keeps non-actionable repo-relative artifacts out of actionable drift | one synthetic Codex/Hermes log file containing reads for `content/demos/index.html` (2), `build.js` (1), `docs/missing.md` (3), `github://vamseeachanta/workspace-hub/issues/2249` (1), and `digitalmodel/specs/module-registry.yaml` (1) | `missing_repo_read_total == 3`; `top_missing_repo_reads == [{"path": "docs/missing.md", "count": 3}]`; `non_repo_artifact_read_total == 3`; `top_non_repo_artifact_reads` contains the exact generated-site paths/counts; symbolic and sibling-repo lists remain separate |
| `test_build_corpus_change_summary_reports_positive_growth_gap_against_event_time_counts` | anomaly logic is concrete and independent from path bucketing | previous audit provider snapshot `post_records=10`; current provider snapshot `post_records=18`; recent activity provider `post_records=3` | JSON row has `post_record_delta == 8`, `event_time_post_records_since_previous_audit == 3`, `reconciliation_gap_post_records == 5`, `status == "positive_corpus_growth_beyond_recent_activity"`, and interpretation string starting `Snapshot grew more than recent event-time activity` |
| `test_build_corpus_change_summary_reports_zero_gap_as_aligned` | zero-gap reconciliation case is explicitly locked | previous audit provider snapshot `post_records=10`; current provider snapshot `post_records=13`; recent activity provider `post_records=3` | JSON row has `reconciliation_gap_post_records == 0` and `status == "aligned"` |
| `test_build_corpus_change_summary_reports_pruned_or_rebuilt_when_gap_is_negative` | negative reconciliation gap contract is equally concrete | previous snapshot `post_records=10`; current snapshot `post_records=12`; recent activity provider `post_records=5` | JSON row has `reconciliation_gap_post_records == -3` and `status == "corpus_pruned_or_rebuilt"` |
| `test_json_summary_exposes_recent_and_corpus_scope_notes` | JSON output keeps both scope-note contracts explicit | synthetic executive summary dict | JSON contains `executive_summary.recent_activity_since_previous_audit.scope_note` and `executive_summary.corpus_change_since_previous_audit.scope_note` exactly |
| `test_render_markdown_separates_recent_event_time_scope_from_corpus_change_scope` | markdown output keeps event-time and corpus-change sections distinct and assertable | minimal synthetic audit dict with `recent_activity_since_previous_audit.scope_note`, `corpus_change_since_previous_audit.scope_note`, one provider row containing `event_time_post_records_since_previous_audit`, `reconciliation_gap_post_records`, `status`, and `interpretation` | rendered markdown contains the exact headings `## Recent activity since previous audit` and `## Corpus change since previous audit`, both scope notes, and provider lines for event-time post records, reconciliation gap, status, and interpretation |
| `test_render_markdown_includes_top_non_repo_artifact_reads_section` | generated markdown exposes the new bucket distinctly | minimal synthetic audit dict with one provider and `top_non_repo_artifact_reads` rows for `content/demos/index.html` and `build.js` | markdown contains heading `### <provider> top non-repo artifact reads` and bullet rows for those exact paths/counts |

---

## Acceptance Criteria

- [ ] The plan fixes the taxonomy decision by defining `non_repo_artifact` as the canonical bucket for generated-site/adjacent-project repo-relative paths, with explicit precedence relative to `symbolic`, `external`, `sibling_repo`, and `repo`.
- [ ] `scripts/analysis/provider_session_ecosystem_audit.py` exposes `top_non_repo_artifact_reads` and `non_repo_artifact_read_total`, and those reads no longer contribute to `missing_repo_reads` or `top_missing_repo_reads`.
- [ ] Tests use fixed fixture paths/counts rather than placeholders and assert exact JSON or markdown output surfaces.
- [ ] The anomaly contract is approval-testable: tests assert `event_time_post_records_since_previous_audit`, `reconciliation_gap_post_records`, `status`, and `interpretation` for positive, zero, and negative reconciliation cases.
- [ ] Existing transient/worktree/scratch-path separation remains protected by explicit classifier tests alongside the new `non_repo_artifact` bucket.
- [ ] Generated artifacts are updated by rerunning the audit script, not by hand-editing report prose.
- [ ] After fresh external re-review, the plan can advance toward `status:plan-review`; remaining in `draft` is not itself a success criterion.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings addressed in this revision |
|---|---|---|
| Claude | PENDING | no review artifact yet |
| Codex | MAJOR on prior draft | this revision removes speculative scope, resolves taxonomy, adds zero-gap + JSON-scope-note tests, and restores explicit transient/worktree protection |
| Gemini | MAJOR on prior draft | this revision aligns the plan back to the issue scope by preserving transient/scratch-path separation while adding the bounded `non_repo_artifact` bucket |

**Overall result:** REVISED DRAFT — prior major findings have been patched in-plan; fresh external re-review is required before approval.

Revisions made based on review:
- removed unsupported line-number/attestation wording and kept evidence claims at the file-and-behavior level
- clarified that transient/worktree/scratch-path separation remains in scope and must stay protected
- replaced speculative review-artifact claims with a plain statement that fresh external re-review is still required
- added zero-gap and JSON-scope-note tests plus explicit transient-path classifier tests
- removed the approval-state contradiction (`remain in draft`) from acceptance criteria

---

## Risks and Open Questions

- **Risk:** An over-broad `non_repo_artifact` matcher could hide true workspace-hub stale-path debt; keep the initial matcher limited to the attested examples/prefixes above and expand only with new evidence.
- **Risk:** Re-bucketing can change provider `missing_repo_reads` enough to reshuffle urgency rankings; reviewers should expect regenerated JSON/markdown diffs in both provider summaries and executive interpretation sections.
- **Open:** None blocking for plan approval. Any future expansion beyond the attested generated-site/adjacent-project fixture list should happen in follow-up issues after observing new concrete path families.

---

## Complexity: T2

**T2** — bounded classifier/report/test work within one audit script and one existing test file, with generated artifact refresh but no architecture redesign.
