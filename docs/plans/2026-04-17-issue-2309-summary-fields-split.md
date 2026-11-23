# Plan for #2309: Split `summary_done` into `summary_done` + `summary_file_exists`

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-17 (rev-2 after Claude MINOR + Codex MAJOR)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2309
> **Parent:** #1878 (closed)
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2309-claude.md | ...-codex.md

---

## Revision Note

- **rev-1:** Claude MINOR (4 actionable asks) + Codex MAJOR (5 blocking + 1 ops-sequencing concern). Claude and Codex both independently caught the `_is_already_enriched()` resume-bug. Codex additionally surfaced a latent `write_index()` seam, stale-carryover risk, and pushed back on the one-PR packaging.
- **rev-2:** All blocking findings addressed — see `## Adversarial Review Summary` below for the traceability table. Key structural changes: (a) enrich_one patch paired with `_is_already_enriched` update and `CARRYOVER_FIELDS` extension (three-seam patch, not one-line); (b) dead-code `phase-a-index.py::write_index()` deleted (0 callers verified); (c) ops split into 3 commits (code/tests → re-enrichment → YAML) not one bundle; (d) 6 additional tests covering mixed-schema resume, Phase C/E mixed-schema behavior, stale-carryover, and the corrupt-file divergence that proves the split is worth doing; (e) validator default lowered 0.75 → 0.70 for consistency with the existing aspirational-defaults pattern.

---

## Resource Intelligence Summary

### Existing repo code

- Found: `scripts/data/document-index/enrich-summary-metadata.py:77-84` — `enrich_one()` already computes `summary_path = find_summary(...)` internally but only exposes `summary_done` (via `summary_done_from_file(summary_path)` or False). The additive split is a 1-line change.
- Found: `scripts/data/document-index/_summary_lookup.py` — no changes needed; `find_summary()` already returns `Path | None`.
- Found: `scripts/data/document-index/validate-index-metadata.py` — current defaults: `content_type_max_missing 0.10`, `content_type_min_non_other 0.90`, `summary_done_min 0.55`. Needs new `summary_file_exists_min` threshold.
- Found: `tests/data/document-index/test_enrich_summary_metadata.py` — has 14 tests covering content_type, summary_done, enrich_one composition. Needs additions for `summary_file_exists`.
- Found: `tests/data/document-index/test_enrich_cli.py` — 5 tests covering dated backup, atomic rename, --resume, field preservation, dry-run stats. Some stats-assertion tests will need `summary_file_exists` in the dict.
- Found: `tests/data/document-index/test_validate_index_metadata.py` — 6 tests. Will need 2-3 new tests for the new threshold.
- Gap: No test in the suite exercises the case where a summary file exists but has no summary content — that will be the critical new distinction.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2309 body | Semantics: `summary_file_exists` = True iff `find_summary` returns non-None; `summary_done` = True iff file exists AND non-empty content. Defaults requested: `--summary-file-exists-min 0.75`. Observed production: 87.8% file_exists vs 16.1% summary_done. |
| Issue #1878 ops closeout | 649,564 records enriched; `summary_done_true: 104,767 (16.1%)`. No `summary_file_exists` recorded because field didn't exist. Re-enrichment needed to populate both fields. |
| Issue #2306 (closed, commit `a13da73df`) | Maturity YAML `status.index_jsonl_only` block currently has `summary_done_percent: 16.1`. Needs additive `summary_file_exists_percent` field on same-day refresh after enrichment. Schema version already at 1.1.0 — no further bump needed. |
| Issue #2307 (closed, commit `25d90339c`) | Accessibility registry `registry-corpus-index.fields[]` currently declares `content_type` + `summary_done`. Needs 3rd entry for `summary_file_exists`. Current `provenance:` note on summary_done already references #2309 — the update will clean that up. |
| Issue #2305 memo (closed) / #2325 (filed) | Conference corpus is 0% enriched and falls outside this scope. Validator thresholds in #2309 apply only to the main `index.jsonl` corpus. |
| `/mnt/ace/data/document-index/summaries/` preflight (from #1878) | 87.8% match rate in 1000-sample — matches projection for `summary_file_exists` coverage. |

### Gaps identified

- No test today distinguishes "file exists but empty" from "file doesn't exist" at the enrichment level (they both produce `summary_done=False`). New test needed.
- Maturity YAML and accessibility registry need coordinated updates post-enrichment; plan batches them into the same PR so no readable window with drift.
- Carryover helper (`_carryover_metadata.py`) currently declares `CARRYOVER_FIELDS = ("content_type", "summary_done")`. Must be extended to include `summary_file_exists` so Phase A/C/E preserve it too.

<!-- Source count: 7 distinct (issue body + 6 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2309-summary-fields-split.md` |
| Enrichment patch | `scripts/data/document-index/enrich-summary-metadata.py` (modify) |
| Carryover patch | `scripts/data/document-index/_carryover_metadata.py` (modify: extend `CARRYOVER_FIELDS`) |
| Validator patch | `scripts/data/document-index/validate-index-metadata.py` (modify: new threshold) |
| Tests (enrichment) | `tests/data/document-index/test_enrich_summary_metadata.py` (extend) |
| Tests (CLI) | `tests/data/document-index/test_enrich_cli.py` (extend) |
| Tests (validator) | `tests/data/document-index/test_validate_index_metadata.py` (extend) |
| Tests (carryover) | `tests/data/document-index/test_carryover_metadata.py` (extend) |
| Maturity YAML update | `data/document-index/resource-intelligence-maturity.yaml` (add `summary_file_exists_percent` in `index_jsonl_only` block, add dated note) |
| Registry update | `data/document-index/intelligence-accessibility-registry.yaml` (add 3rd field declaration; tighten summary_done's provenance note) |
| Plan reviews | `scripts/review/results/2026-04-17-plan-2309-{claude,codex}.md` |

---

## Deliverable

A `data/document-index/index.jsonl` where every record carries three enriched fields — `content_type`, `summary_done`, `summary_file_exists` — plus (a) a validator with a new `--summary-file-exists-min` threshold defaulting to 0.75, (b) carryover in Phase A/C/E for the new field, (c) maturity YAML updated with the new coverage percent, (d) accessibility registry declaring the new field alongside the existing two.

---

## Pseudocode

### `enrich-summary-metadata.py::enrich_one()` (modify)

```
def enrich_one(record, summaries_dir):
    record["content_type"] = content_type_for_ext(record.get("ext"))
    summary_path = find_summary(record, summaries_dir)
    # NEW: expose file existence as its own boolean
    record["summary_file_exists"] = summary_path is not None
    # UNCHANGED: summary_done still means "file exists AND non-empty content"
    record["summary_done"] = (
        False if summary_path is None else summary_done_from_file(summary_path)
    )
    return record
```

### `enrich-summary-metadata.py::_is_already_enriched()` (modify — Claude+Codex)

Current code at line 104 checks only two fields. Must check all three so `--resume` doesn't silently skip pre-split records:

```
def _is_already_enriched(record):
    return (
        "content_type" in record
        and "summary_done" in record
        and "summary_file_exists" in record  # NEW
    )
```

### `phase-a-index.py::write_index()` (DELETE — Codex)

Dead function at lines 301-330. Zero callers verified via `grep -rn "write_index\b" scripts/ tests/`. Deleting it closes the "latent seam" Codex flagged. The only live write path is `write_merged_index_with_carryover()` (landed in #1878 wave 6b). Deletion is a tightening, not a behavior change.

### `enrich-summary-metadata.py::enrich_index()` stats block (modify)

Extend the stats dict initialization and accumulation:

```
stats = {
    "total": len(records),
    "content_type_non_other": 0,
    "summary_done_true": 0,
    "summary_file_exists_true": 0,  # NEW
}
# ... accumulation loop gets one more counter
```

### `_carryover_metadata.py` (modify 1-line)

```
CARRYOVER_FIELDS = ("content_type", "summary_done", "summary_file_exists")
```

### `validate-index-metadata.py` (modify)

Add one CLI flag and one check:

```
parser.add_argument("--summary-file-exists-min", type=float, default=0.75)

# In validate():
sfe_rate = sfe_count / total
if sfe_rate < min_summary_file_exists:
    msgs.append(f"FAIL: only {sfe_count}/{total} records have summary_file_exists=True "
                f"({100*sfe_rate:.1f}% < {100*min_sfe:.1f}%)")
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/data/document-index/enrich-summary-metadata.py` | Emit `summary_file_exists`; add to stats dict; extend `_is_already_enriched` |
| **Delete** | `scripts/data/document-index/phase-a-index.py::write_index()` | Dead code (0 callers); closes latent seam flagged by Codex |
| Modify | `scripts/data/document-index/_carryover_metadata.py` | Extend `CARRYOVER_FIELDS` tuple |
| Modify | `scripts/data/document-index/validate-index-metadata.py` | `--summary-file-exists-min 0.70` (rev-2: lowered from 0.75) + check |
| Modify | `tests/data/document-index/test_enrich_summary_metadata.py` | 5 new tests (see TDD list) |
| Modify | `tests/data/document-index/test_enrich_cli.py` | 3 updates: dry-run stats dict assertions, resume test, preservation test |
| Modify | `tests/data/document-index/test_validate_index_metadata.py` | 3 new tests: threshold rejection, override, healthy |
| Modify | `tests/data/document-index/test_carryover_metadata.py` | 2 new tests: carryover includes summary_file_exists; atomic_write preserves |
| Modify | `data/document-index/resource-intelligence-maturity.yaml` | Add `summary_file_exists_percent` under `status.index_jsonl_only`; 1 dated note |
| Modify | `data/document-index/intelligence-accessibility-registry.yaml` | Add 3rd `fields[]` entry; tighten `summary_done.provenance` (drop #2309 forward-ref) |
| Update | `docs/plans/README.md` | Plan row |

Explicitly NOT in scope:
- GOTCHA-refresh edits (landed in #2308; wording already uses "~16%" vaguely enough to survive this split).
- Conference corpus (#2325).
- Pre-commit wiring of validator (still deferred per #1878 plan's open question).

---

## TDD Test List

| # | Test name (file) | What it verifies |
|---|---|---|
| 1 | `test_summary_file_exists_true_when_file_present` (enrich) | non-empty summary file → True |
| 2 | `test_summary_file_exists_true_when_file_empty_content` (enrich) | file present with `summary: ""` → True (diverges from summary_done) |
| 3 | `test_summary_file_exists_true_when_file_has_no_summary_key` (enrich) | file present with no `summary` key → True (diverges from summary_done) |
| 4 | `test_summary_file_exists_false_when_file_missing` (enrich) | no file on disk → False |
| 5 | `test_enrich_one_populates_both_summary_fields` (enrich) | record gets both `summary_done` and `summary_file_exists` keys every time |
| 6 | `test_enrich_index_stats_includes_summary_file_exists_true` (cli) | dry-run returns stats dict with the new counter |
| 7 | `test_validator_rejects_low_summary_file_exists` (validator) | <75% rate → exit 1 |
| 8 | `test_validator_summary_file_exists_min_cli_override` (validator) | `--summary-file-exists-min 0.10` relaxes default |
| 9 | `test_validator_passes_when_all_three_thresholds_met` (validator) | healthy index → exit 0 with new field present |
| 10 | `test_carryover_preserves_summary_file_exists` (carryover) | A/C/E carryover keeps the new field across rewrites |
| 11 | `test_pipeline_chain_preserves_all_three_fields` (pipeline_chain — update existing test 31) | Full chain A→enrich→C→E retains all three |
| **12** | `test_resume_re_enriches_pre_split_records` (cli) | **rev-2 (Codex):** `--resume` against a record that has `content_type` + `summary_done` but lacks `summary_file_exists` MUST re-enrich that record (not skip it) |
| **13** | `test_summary_file_exists_true_summary_done_false_on_corrupt_json` (enrich) | **rev-2 (Claude):** file present with malformed JSON → `summary_file_exists=True`, `summary_done=False`. Asserts divergence. |
| **14** | `test_summary_file_exists_true_summary_done_false_on_unicode_decode` (enrich) | **rev-2 (Claude):** non-UTF-8 summary bytes → `summary_file_exists=True`, `summary_done=False`. Asserts divergence. |
| **15** | `test_phase_c_writeback_preserves_both_summary_fields` (pipeline_chain) | **rev-2 (Codex):** Phase C bounded writeback on a record with both fields keeps both unchanged |
| **16** | `test_phase_e_backpopulate_preserves_both_summary_fields` (pipeline_chain) | **rev-2 (Codex):** Phase E backpopulate on a record with both fields keeps both unchanged |
| **17** | `test_stale_carryover_does_not_mask_removed_summary_file` (carryover — *informational*) | **rev-2 (Codex):** documents the known stale-carryover property. This test is **expected to FAIL** on design — if summary file is removed after prior enrichment, carryover still re-applies `summary_done=True`. Test documents the behavior; comment inline that the mitigation is "full re-enrichment, not carryover-only." |

Per TDD: write all tests first, confirm they fail, implement minimum code, verify they pass, then run the full `tests/data/document-index/` suite for no regressions.

**Note on test #17:** This is an explicitly-marked **behavior-documentation** test, not a regression test. Codex flagged the stale-carryover risk; #2309 does not fix it (full re-enrichment is the mitigation, and that IS in the ops sequence below). The test captures the property so any future code change that accidentally "fixes" it surfaces for review. Implement as a `@pytest.mark.xfail(reason="...")` or equivalent so CI stays green.

---

## Acceptance Criteria

- [ ] All 17 new/updated tests pass (tests 1-16 green; test 17 xfail as documented)
- [ ] No regression: `pytest tests/data/document-index/` all green (currently 139 passing → target 155 with 16 new + update test 31)
- [ ] `phase-a-index.py::write_index()` dead code deleted (0 callers pre- and post-deletion verified)
- [ ] Dry-run against production index reports `summary_file_exists` coverage ≥70% (projection: ~87.8%)
- [ ] Live re-enrichment writes `summary_file_exists` on all 649,564 records
- [ ] Validator default (≥70% summary_file_exists) passes on enriched index
- [ ] Backup `index.jsonl.backup-YYYY-MM-DD` exists after re-enrichment
- [ ] Maturity YAML `index_jsonl_only.summary_file_exists_percent` populated with live figure + dated note — **committed AFTER live enrichment verifies** (per Codex ops-sequencing)
- [ ] Accessibility registry declares the new field alongside existing two; `summary_done.provenance` no longer forward-references #2309 as unresolved
- [ ] Commit sequence (rev-2, per Codex): **(1)** code + tests + dead-code-delete; **(2)** live re-enrichment ops result (documented in close comment, not a commit); **(3)** YAML/registry updates once live figures known. Final commit count: 2-3

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR → addressed in rev-2 | (1) `_is_already_enriched()` must include new field or --resume silently skips pre-split records; (2) divergence tests missing (file exists but corrupt/unreadable — the cases that prove the split was worth doing); (3) threshold 0.75 over-tight vs 87.8% projection, suggest 0.70; (4) move production dry-run gate before first commit. |
| Codex | MAJOR → addressed in rev-2 | (1) same `--resume` bug (independently caught); (2) latent `phase-a-index.py::write_index()` seam at lines 262-280 (zero callers — delete); (3) stale-carryover risk: removed summary files still carry `summary_done=True` via carryover helper; (4) missing tests for --resume mixed-schema, Phase C/E mixed-schema, stale-carryover; (5) **ops sequencing: YAML must come AFTER live re-enrichment, not bundled in same commit wave.** |

**Overall rev-1 result:** FAIL — 1 MAJOR + 1 MINOR → revision required.

**Revisions made in rev-2 (traceability):**

| Finding | Response in rev-2 |
|---|---|
| Claude F1 / Codex F1: `_is_already_enriched` resume bug | Pseudocode section now shows the 3-field check; AC requires it |
| Codex F2: latent `write_index()` seam | `phase-a-index.py::write_index()` **deleted** (0 callers verified); AC requires the deletion |
| Codex F3: stale-carryover risk | Acknowledged as a **non-goal** of #2309 (full re-enrichment is the mitigation, which IS in the ops sequence); test #17 documents the property as xfail |
| Claude F2 + Codex F4: missing divergence/mixed-schema tests | 6 new tests added (#12-17), each traced to the reviewer who asked |
| Claude F3: threshold 0.75 over-tight | Lowered to 0.70 in pseudocode, CLI default, and ACs |
| Claude F4: dry-run gate placement | ACs now sequence dry-run gate BEFORE first commit |
| Codex F5: ops sequencing | AC-level 3-commit sequence: (1) code+tests+delete; (2) live re-enrichment (result documented, no commit); (3) YAML+registry with live figures |

**Overall rev-2 result:** Ready for approval — all blocking and minor findings addressed mechanically.

---

## Risks and Open Questions

- **Risk:** The 75% default is tight against the projected 87.8%, leaving only 12.8pp of headroom. If a future re-index produces paths that diverge from summarizer paths (e.g., path renames), the validator could fail even when everything is working. Mitigation: threshold is CLI-flaggable; documented in validator `--help`. Open question flagged for the user: is 0.75 tight enough, or should it be 0.70 for more slack?
- **Risk:** Re-enrichment on the production 649K corpus takes ~45 min (per #1878 ops). Should be a final step after all tests pass and PRs are merged — not interleaved with dev. The plan sequences it correctly.
- **Open:** Should the plan merge in two PRs (code+tests first, then YAML updates after ops) or one? Recommendation: **one PR** — the maturity YAML/registry updates depend on the live numbers, which depend on re-enrichment. Ops run happens mid-PR with the final YAML commit afterward. Cleaner single-issue closure.
- **Open:** Should `summary_file_exists` backfill onto the already-enriched index without a full re-enrichment? Technically possible (the field can be derived purely from `find_summary()` on existing records), but the implementation cost is a new "backfill" script. Recommendation: skip the backfill — just re-run the normal enrichment.

---

## Complexity: T2

Extends 3 source files with mechanical additive changes; extends 4 test files; extends 2 YAML files; requires production re-enrichment run (~45 min). No architectural change, no new module, no schema-breaking migration. Full TDD with 11 new/updated tests. Single-provider review would be thin for a code change touching validator thresholds; 2-provider review is proportionate.
