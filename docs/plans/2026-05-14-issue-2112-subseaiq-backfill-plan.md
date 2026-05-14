# Issue #2112 Plan — SubseaIQ Equipment Counts Backfill

## Metadata

- Issue: #2112 — `data(field-dev): backfill SubseaIQ equipment counts to unblock cost benchmarking`
- Repository: `vamseeachanta/workspace-hub`
- Plan file: `docs/plans/2026-05-14-issue-2112-subseaiq-backfill-plan.md`
- Date: 2026-05-14
- Status: plan-only draft for morning user review
- Complexity: T3
- Catalog match: /goal catalog #2695 Tier 1 #13, `schema migration safety review` `[planning-heavy]`
- Current run mode: PLAN ONLY. Do not implement this plan in the current session.
- Routing requested by user:
  - Planning brain: Hermes routing
  - Hands for later implementation: Hermes -> Claude Code
  - Review after this plan-only run: Codex T1 + Claude T2 in the morning

## Objective

Backfill the minimum public-source, provenance-backed GoM SubseaIQ equipment-count data required to unblock #2055 cost benchmarking, without silently accepting proxy, placeholder, or semantically inconsistent values.

The implementation that follows this plan must produce at least 10 Gulf of Mexico field/project records with substantive, reviewed values for:

- `num_trees`
- `num_manifolds`
- `tieback_distance_km`

and must retain source URLs, confidence, field-level basis notes, and conflict/normalization decisions.

## Hard Stop for This Session

This session stops after planning:

- Create this plan file.
- Add the plan to `docs/plans/README.md`.
- Post the planned approach on #2112.
- Do not edit data files, validators, benchmark code, labels, or approval markers.
- Do not flip or rely on self-created `status:plan-approved` state.

## Issue Relationships

- #2112 is the data gate: backfill equipment counts and tieback distance.
- #2055 is downstream: benchmark curves for cost-per-equipment-unit by water-depth band. It must remain blocked until #2112 proves the data gate.
- #2558 is a related source-pack issue: primary-source GoM equipment/cost evidence package for #2112/#2055. #2112 may consume or produce source-pack structure, but should not close #2558 unless explicitly scoped later.
- #2695 is the /goal catalog and routing source. This plan used Tier 1 #13 as the closest match because the task is a one-shot schema-aware data backfill/migration with high downstream correctness risk.

## Resource Intelligence Summary

### Sources Consumed

| Source | Finding |
|---|---|
| GitHub issue #2112 | Acceptance requires at least 10 GoM records with non-null `num_trees`, `num_manifolds`, and `tieback_distance_km`, plus provenance/confidence and a validation command/test. Current issue body states 0/10 current records have those fields. |
| GitHub issue #2055 | Downstream benchmark implementation depends on equipment counts for >=10 GoM fields and confirmed name-match mapping between SubseaIQ project names and cost datapoints. Cost-per-tree/manifold/km implementation must wait. |
| GitHub issue #2558 | Related primary-source source-pack issue remains open with `status:needs-data`; source-pack work should inform #2112 but not be conflated with #2112 closeout unless separately approved. |
| GitHub issue #2695 and `.claude/rules/goal-invocation.md` | /goal invocation requires catalog lookup and status/routing checks. #2112 is not in the weekly picklist but is not skipped; explicit user direction authorizes plan-only work. |
| `data/field-development/subseaiq-scan-latest.json` | Target SubseaIQ-derived scan has 10 GoM fields (`Perdido`, `Appomattox`, `Whale`, `Atlantis`, `Thunder Horse`, `Mars`, `Mad Dog`, `Stones`, `Lucius`, `Ursa`) with host/depth/capacity/year context but lacks the required equipment/tieback fields in the inspected records. |
| `data/field-development/gom-field-development-unblock-2112.json` | Prior candidate artifact is structurally complete but substantively blocked: `records_with_all_required_structural: 10`, `records_with_all_required_public_sourced_and_semantically_consistent: 0`, `status: blocked_adversarial_review_failed`, `unblock_status: not_unblocked`. Treat it as source leads, not accepted evidence. |
| `docs/reports/field-development-unblock-2112.md` | Prior report says no invented values are accepted; `status:needs-data` should remain until primary-source/semantically consistent evidence exists. It prioritizes Mad Dog Phase 2/Argos, Appomattox, Thunder Horse, Stones/Lucius/Perdido, then Atlantis/Na Kika/Mars. |
| `scripts/knowledge/tests/test_field_development_unblock_2112.py` | Current validator only asserts the provisional blocked status and structural completeness of the candidate artifact. It does not yet validate accepted final-unblock evidence. Implementation must upgrade/add tests so structural completeness alone cannot unblock #2055. |
| `scripts/dispatch/overnight-2026-05-13/H2-issue-2112.sh` and README snippets | Dispatch surface independently confirms no canonical plan existed, #2112 is plan-only for this session, and implementation must stop until morning review/approval. |
| `docs/plans/_template-issue-plan.md` and `docs/plans/README.md` | Canonical plan must live under `docs/plans/`, cite resource intelligence, define artifacts/tests/ACs/risks, and add a README index row. |

### Retrieval Gaps and Follow-up Discovery Needed During Implementation

- Fully inventory any existing source-pack layout before introducing new files, especially if #2558 has partial artifacts not visible from the initial summary.
- Search sibling repos (`digitalmodel`, `worldenergydata`) before implementing if the final data surface moves there; this plan currently treats `workspace-hub/data/field-development/` as the #2112 authoritative artifact because the issue body names it directly.
- Public web/source research must be redone or refreshed during implementation; prior candidate data cannot be trusted as final values.
- Cost data may be useful context for #2055 but is not a required #2112 unblock field unless name-match/cost mapping is needed to verify downstream readiness.

## Current State / Problem Statement

The current repository has two competing truths:

1. `subseaiq-scan-latest.json` is the issue-named target dataset but lacks the three required fields.
2. `gom-field-development-unblock-2112.json` has 10 structurally complete records, but the repo itself marks that artifact as adversarially failed because values mix direct facts with proxy/placeholder/cost-class seeds.

The next implementation must not simply copy the failed candidate artifact into the target dataset or flip a gate based on structural non-null counts. It must create a field-level evidence model that distinguishes:

- accepted direct public facts,
- defensibly normalized facts,
- conflicting values retained for review,
- proxy leads rejected from unblock counts,
- unknown values that keep a record out of the accepted threshold.

## Deliverable

After approved implementation, the repository will contain a validated, provenance-backed GoM field-development equipment-count backfill where at least 10 accepted records satisfy the #2112 gate and the validation/report explicitly states whether #2055 may remove `status:needs-data`.

## Non-Goals

- Do not implement #2055 benchmark functions in this issue.
- Do not remove `status:needs-data` from #2055 unless the final validation report proves #2112's accepted-data gate and the user approves the label change.
- Do not fabricate missing values, infer final values from generic field class, or use zero as placeholder.
- Do not treat export pipeline length, host-to-host distance, or total flowline length as `tieback_distance_km` unless the report explicitly normalizes and justifies that definition for the field.
- Do not treat drill centres, riser bases, field centers, or gathering systems as `num_manifolds` unless the source equates them to subsea manifold structures and the basis note says so.
- Do not overwrite conflicting values; preserve alternatives in provenance/conflict notes.
- Do not commit secrets, paywalled raw PDFs, credentials, or private-source text.

## Schema / Data Contract

### Required accepted fields per record

Each accepted record must have:

```json
{
  "name": "Mad Dog Phase 2 / Argos",
  "region": "US Gulf of Mexico",
  "host": "Argos",
  "num_trees": 14,
  "num_trees_basis": "...",
  "num_manifolds": 2,
  "num_manifolds_basis": "...",
  "tieback_distance_km": 10.5,
  "tieback_distance_km_basis": "...",
  "source_urls": ["https://..."],
  "confidence": "high|medium|low",
  "field_status": "accepted|needs_review|rejected_proxy|insufficient_evidence"
}
```

The exact output file may retain the existing `gom_fields` envelope, but it must add machine-checkable gate metadata:

```json
{
  "issue": 2112,
  "schema_version": "field-development-unblock-v2",
  "required_gate": {
    "minimum_complete_records": 10,
    "records_with_all_required_structural": 10,
    "records_with_all_required_public_sourced_and_semantically_consistent": 10,
    "unblock_status": "unblocked|not_unblocked",
    "validation_status": "accepted|blocked"
  }
}
```

### Recommended companion structures

Use additive fields rather than lossy overwrite:

- `source_evidence[]`: per-field source snippets/URLs/title/accessed date/source type.
- `conflicts[]`: alternate values, source URL, reason not selected.
- `normalization_notes[]`: unit conversion, semantic mapping, and why the selected definition is acceptable.
- `rejected_proxy_notes[]`: explicit list of values not counted toward the gate.

If this grows too large for the scan file, keep `subseaiq-scan-latest.json` as the current operational scan and add a companion source-pack JSON/Markdown under `data/field-development/` or `docs/reports/`, but ensure the validator joins them deterministically.

## Field Normalization Rules

### `num_trees`

Accepted values:

- subsea production trees,
- subsea wells/trees where the source uses wells as tree count for a subsea project and the basis note says this is the source terminology,
- phased counts only when the record name includes the phase or the record explicitly scopes to that development phase.

Rejected/provisional values:

- total field well count that includes dry trees or platform wells unless separated,
- planned/future wells mixed with installed wells without date/status,
- generic “up to N wells” not tied to the project phase unless marked lower confidence and accepted by review.

### `num_manifolds`

Accepted values:

- subsea production/injection manifold structures,
- explicit “manifold centers” when source terminology confirms they are subsea manifolds.

Rejected/provisional values:

- drill centres if the source does not equate them to manifold structures,
- risers, pipeline end terminations, field centres, or templates unless specifically documented as manifolds,
- placeholder zeroes.

### `tieback_distance_km`

Preferred definition:

- maximum subsea production-system offset from receiving host, in kilometers.

Allowed normalized sources:

- source-reported host separation or subsea-to-host distance,
- source-reported miles converted to kilometers with explicit conversion note,
- project phase host offset if the record is phase-scoped.

Rejected/provisional values:

- export pipeline length,
- total flowline length,
- host-to-shore distance,
- field-to-field or host-to-host distances not representing subsea-to-host tieback,
- assumed 0 for host-adjacent fields.

## Target Field Priority

Use this priority order because existing report evidence already identified relative source strength:

1. Mad Dog Phase 2 / Argos — likely strongest public source set for wells/trees, drill centres/manifolds, cost, and host separation.
2. Appomattox — strong tree/manifold source leads; needs semantically correct tieback metric.
3. Thunder Horse — strong trees/tieback expansion data; needs careful base/project scoping.
4. Stones, Lucius, Perdido — use operator fact sheets, OTC/SPE papers, BOEM/BSEE where available; watch manifold/tieback definitions.
5. Atlantis, Mars, Ursa, Whale — fill only if direct/defensible evidence exists; otherwise add alternate GoM records from source research rather than forcing weak records into the 10-record threshold.

The implementation is allowed to replace the accepted 10-record set with better-supported GoM fields/projects if the target `subseaiq-scan-latest.json` names are not sourceable enough. If replacing, preserve a mapping from original scan record to accepted record and explain exclusions.

## Source Strategy

Preferred source classes, in order:

1. Operator fact sheets and project pages: BP, Shell, Chevron, Anadarko/Oxy, LLOG, etc.
2. Offshore Technology / SubseaIQ / Subsea7 / TechnipFMC / OneSubsea / SLB / Wood / Subsea Integration Alliance public project pages.
3. OTC/SPE abstracts and public papers where factual equipment summaries are visible.
4. BOEM/BSEE/public regulatory records only if they identify project equipment or distances clearly.
5. Reputable industry news articles as secondary corroboration.

Implementation must record:

- URL,
- source title or organization,
- accessed date,
- field(s) supported,
- quoted or paraphrased basis note short enough to avoid copyright/raw-paste risk,
- confidence and reason.

If a public source is unavailable or blocked, record a lead but do not count it as accepted evidence.

## Implementation Plan

### Phase 0 — Preflight and state verification

- Re-check #2112/#2055/#2558 labels and comments.
- Confirm no newer plan supersedes this file.
- Confirm target artifacts and current data-gate counts.
- Do not alter labels unless explicitly approved.

Commands:

```bash
gh issue view 2112 --repo vamseeachanta/workspace-hub --json number,title,state,labels,url,comments
gh issue view 2055 --repo vamseeachanta/workspace-hub --json number,title,state,labels,url
gh issue view 2558 --repo vamseeachanta/workspace-hub --json number,title,state,labels,url
uv run python - <<'PY'
import json
from pathlib import Path
p = Path('data/field-development/subseaiq-scan-latest.json')
data = json.loads(p.read_text())
records = data.get('gom_fields') or data.get('records') or data.get('projects') or []
req = ['num_trees', 'num_manifolds', 'tieback_distance_km']
print(len(records), sum(all(r.get(k) is not None for k in req) for r in records))
PY
```

### Phase 1 — Test-first gate redesign

Add or update tests before data edits so the failed candidate cannot pass as final evidence.

Tests should cover:

- target scan or accepted companion dataset has >=10 accepted GoM records,
- accepted count uses `field_status == accepted` or equivalent substantive status, not just non-null numerics,
- each accepted field has field-level basis notes and at least one source supporting it,
- rejected proxies do not count toward the accepted threshold,
- report states whether #2055 remains blocked or can proceed,
- prior failed candidate status remains historically truthful or is superseded explicitly.

Likely file:

- `scripts/knowledge/tests/test_field_development_unblock_2112.py`

### Phase 2 — Source-pack extraction and candidate table

Create a working source table from public sources. Recommended durable artifact:

- `data/field-development/gom-field-development-unblock-2112.json` upgraded to `field-development-unblock-v2`, or
- new sidecar `data/field-development/gom-field-development-source-pack-2112.json` if preserving v1 history is cleaner.

For each candidate record, capture field-level source evidence and conflicts before final normalization.

### Phase 3 — Normalize and select accepted records

Apply the field normalization rules above.

For each accepted record:

- select one canonical value per required field,
- retain alternates/conflicts,
- set confidence,
- write concise basis notes,
- mark `field_status: accepted` only if all three required values are public-sourced and semantically consistent.

For records that do not qualify:

- keep them as `needs_review`, `rejected_proxy`, or `insufficient_evidence`,
- explain why they do not count.

### Phase 4 — Update target dataset/read surface

The issue names `data/field-development/subseaiq-scan-latest.json` as the target. Implementation must either:

- backfill accepted fields directly into that file with provenance pointers, or
- keep the raw scan immutable-ish and add a deterministic enriched companion that the validator/report uses.

If choosing a companion, add a clear README/report note so future #2055 work knows which file is authoritative for benchmark input.

### Phase 5 — Report and downstream gate statement

Update:

- `docs/reports/field-development-unblock-2112.md`

The report must include:

- accepted count,
- rejected/proxy count,
- list of accepted records and selected values,
- source/provenance summary,
- conflict summary,
- exact validator command and result,
- explicit #2055 gate statement: `#2055 may remove status:needs-data` or `#2055 remains blocked`.

### Phase 6 — Review and closeout after implementation

Before closing #2112:

- run tests,
- run a data sanity script/report,
- run Codex T1 + Claude T2 review or equivalent approved review route,
- post evidence comment on #2112,
- only then request or perform label changes per user-approved workflow.

## Pseudocode

```text
load target scan and prior candidate data
load or create source-pack working structure
for each candidate GoM field/project:
    collect public sources for trees, manifolds, tieback distance
    extract candidate values with source URL, field name, unit, basis note
    normalize values by field-specific semantic rules
    classify each candidate field value as accepted, conflict, rejected_proxy, or insufficient
    if all three required fields have accepted values:
        mark record accepted and include in gate count
    else:
        preserve record but exclude from gate count
compute structural_count and substantive_accepted_count
write enriched dataset/source pack atomically
write report summarizing accepted, rejected, conflicts, and downstream #2055 gate
run validator that fails if accepted_count < 10 or source/basis fields are missing
```

## Files to Change During Approved Implementation

| Action | Path | Reason |
|---|---|---|
| Modify or supersede | `data/field-development/gom-field-development-unblock-2112.json` | Upgrade from blocked v1 candidate to provenance-backed v2 accepted/blocked dataset, preserving the v1 failure history or superseding it explicitly. |
| Modify or enrich | `data/field-development/subseaiq-scan-latest.json` | Issue-named target dataset must expose or point to accepted equipment/tieback fields. |
| Modify | `docs/reports/field-development-unblock-2112.md` | Human-readable evidence report and #2055 gate statement. |
| Modify | `scripts/knowledge/tests/test_field_development_unblock_2112.py` | Convert structural-only blocked-state tests into final substantive gate tests. |
| Optional add | `data/field-development/gom-field-development-source-pack-2112.json` | If source-pack detail is too large/noisy for the operational scan. |
| Optional add | `data/field-development/README.md` | Explain authoritative dataset vs raw scan vs source-pack if more than one data artifact is used. |
| No change in this issue | `digitalmodel/src/digitalmodel/field_development/benchmarks.py` | Downstream #2055 implementation surface; must wait. |
| No change in this issue | `worldenergydata/subseaiq/analytics/cost_correlation.py` | Downstream #2055 helper surface; must wait. |

## TDD Test List

| Test | Verification | Expected Result |
|---|---|---|
| `test_2112_final_dataset_has_ten_accepted_gom_records` | Counts accepted records with all required fields. | `>= 10` accepted records. |
| `test_2112_acceptance_requires_substantive_status_not_structural_only` | Ensures non-null proxy records do not satisfy the gate. | Records with `field_status != accepted` are excluded. |
| `test_2112_accepted_records_have_field_level_basis_and_sources` | Checks basis/source fields for each required value. | No accepted required field lacks provenance. |
| `test_2112_rejected_proxy_values_are_preserved_but_not_counted` | Confirms proxy/placeholder leads are retained as evidence trail only. | Rejected values exist if encountered but do not count. |
| `test_2112_tieback_definition_excludes_export_pipeline_lengths` | Detects basis notes/normalization flags for disallowed distance semantics. | Export/shore/total-flowline values are not accepted as tieback without explicit normalization. |
| `test_2112_report_states_downstream_2055_gate` | Reads report and checks gate wording. | Report explicitly says #2055 unblocked or still blocked. |
| `test_2112_source_urls_are_public_http_urls` | Validates source URL fields. | Accepted records have non-empty public `http(s)` URLs. |
| `test_2112_confidence_enum_and_conflict_notes` | Checks confidence and conflict shape. | Confidence is controlled enum; conflicts retained if present. |

Expected command:

```bash
uv run pytest scripts/knowledge/tests/test_field_development_unblock_2112.py -q
```

## Acceptance Criteria

- [ ] At least 10 GoM records have accepted, non-null `num_trees`, `num_manifolds`, and `tieback_distance_km`.
- [ ] Accepted records are public-source-backed and semantically consistent under this plan's normalization rules.
- [ ] Provenance/confidence/basis notes exist at field level or record level with field-specific mapping.
- [ ] Proxy, placeholder, generic, or conflicting values are preserved but do not count toward the gate.
- [ ] Validator command proves the accepted threshold, not merely structural non-null completeness.
- [ ] Report states the exact downstream #2055 gate result.
- [ ] #2055 benchmark code remains untouched in #2112 implementation.
- [ ] Codex T1 + Claude T2 review, or user-approved equivalent, finds no unresolved MAJOR before closeout.

## Adversarial Review Summary

Review is intentionally deferred by user direction for this overnight plan-only session.

| Provider | Role | Status | Notes |
|---|---|---|---|
| Codex | T1 review | Deferred to morning | Should focus on data-gate correctness, schema/test adequacy, and proxy leakage. |
| Claude | T2 review | Deferred to morning | Should focus on source strategy, semantic normalization, and implementation handoff clarity. |
| Hermes | Planning/routing | Complete for draft | Performed issue/artifact intake and wrote this canonical plan. |

This plan should not be treated as implementation-approved solely because #2112 currently has `status:plan-approved`; the user explicitly requested morning review before implementation.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Public sources do not support 10 records under strict semantics. | Do not force weak records. Keep #2112 blocked, report fewer accepted records, and route #2558/source-pack follow-up. |
| Candidate artifact v1 proxy values leak into final dataset. | Tests must count only accepted substantive records and exclude `blocked_adversarial_review_failed`/proxy statuses. |
| Tieback distance semantics vary by source. | Preserve source wording and classify export/flowline/shore lengths separately unless explicitly normalized. |
| Manifold vs drill-centre terminology is ambiguous. | Require basis notes and confidence downgrade or exclusion when source wording is not equivalent. |
| Downstream #2055 starts too early. | Keep non-goals explicit and avoid benchmark-code edits. Final report controls #2055 gate. |
| Web sources change or disappear. | Record accessed dates and source metadata; consider archived/permalink references where allowed. |
| Copyright/raw-source overcapture. | Store concise factual basis notes and URLs, not large copied passages. |
| Dirty worktree causes accidental inclusion of unrelated edits. | Stage only #2112 files during implementation; verify `git diff --cached --name-status` before commit. |

## Open Questions for Morning Review

1. Should accepted #2112 data be written directly into `subseaiq-scan-latest.json`, or should the raw scan remain separate with an enriched authoritative companion?
2. Should #2558 be promoted to the formal source-pack owner before implementation, with #2112 consuming it, or should #2112 create the minimal source-pack itself?
3. Is it acceptable to replace weak original 10 scan fields with stronger GoM projects if public evidence for the original set is insufficient?
4. What confidence threshold should unblock #2055: all accepted records `high|medium`, or can a bounded number of `low` records count if evidence is direct but incomplete?

## Complexity Justification

T3.

Reasoning:

- Multi-artifact data migration/backfill with schema and validation changes.
- Engineering-domain semantic ambiguity across equipment, manifold, and tieback definitions.
- Downstream benchmark work (#2055) can be materially wrong if proxy data passes.
- Requires provenance retention, conflict handling, and adversarial review.
- Existing candidate artifact is intentionally marked failed, so implementation must avoid a tempting but invalid structural pass.

## Stop Condition

For this plan-only session, stop after posting the planned approach comment on #2112. Implementation must happen in a separate approved session after morning review.
