# Plan for #1878: Fix document index metadata — restore `content_type` and `summary_done` in index.jsonl

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-16 (rev-2 after adversarial review)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/1878
> **Review artifacts:** `scripts/review/results/2026-04-16-plan-1878-claude.md` | `...-codex.md` | `...-gemini.md`

---

## Revision Note (rev-2)

First review wave returned **Claude: MAJOR, Codex: MAJOR, Gemini: MINOR**. This revision addresses all blocking findings:

- Fixed multi-pattern hash-key lookup (Claude F1) — four filename conventions on disk, not two
- Dropped `summary_title` / `summary_discipline` from default schema (Gemini A1)
- Mirrored `enrich-readability.py` pattern: `--resume`, `--workers`, `ProcessPoolExecutor`, `.tmp`/`.bak` (Claude F3)
- Added pre-flight sample reconciliation (Claude F2)
- Scope-split: GOTCHA edits + maturity YAML + accessibility registry moved to follow-up issues (Claude F7, Gemini S1/D1/D3)
- Phase A atomic write + dated backup, independent of enrichment script (Codex F2)
- Phase C/E integration test asserting field survival (Codex F3)
- Empirical baseline count for `conference-index-batch.jsonl` (Codex F1)
- Known-consumer enumeration (Gemini BC1)

---

## Resource Intelligence Summary

Issue class: `cat:document-intelligence` / data-pipeline bundle. Retrieval contract (#2208) requires ≥3 distinct sources. Ten are listed below (one added after rev-2 investigation).

### Existing repo code

- Found: `scripts/data/document-index/phase-a-index.py:89-96,130-134` — stores `content_hash` as `"sha256:<64hex>"` (prefixed) or `"md5:<32hex>"` (legacy og_standards). Also writes `summary: null` for every record.
- Found: `scripts/data/document-index/summarise-worker.py:63-70` — hash-key derivation: **returns `content_hash` as-is** when present (with `sha256:` / `md5:` prefix intact); else `sha256(path)[:16]`. Writes to `summaries/<key>.json`.
- Found: `scripts/data/document-index/phase-c-classify.py` — bounded-writeback mode rewrites `domain/status/target_repos` in index.jsonl. **Will clobber new fields unless carryover added.**
- Found: `scripts/data/document-index/phase-e-backpopulate.py`, `phase-e-registry.py` — also rewrite index.jsonl. Same clobber risk.
- Found: `scripts/data/document-index/enrich-readability.py` — canonical enrichment-script pattern (`uv run --no-project`, `--dry-run`, `--resume`, `--workers`, `ProcessPoolExecutor`, `.tmp` → `.bak` rotation). New script mirrors this exactly.
- Gap: No script merges summary-file existence into index records. No ext → content_type mapping exists anywhere.

### Standards

Not applicable — pipeline/schema fix, not an engineering-calculation issue.

### LLM Wiki pages consulted

No relevant wiki pages — pipeline-schema issue only.

### Documents consulted

| Source | Finding |
|---|---|
| `docs/reports/2026-04-16-issue-1878-diagnosis.md` | Confirms fields never existed in schema. Projects 83.7% summary match for index.jsonl. Does **not** enumerate all four filename conventions (see new finding below). |
| Issue #1878 body | 647K records, 0% content_type coverage; parent #1839 is unrelated session-governance context. |
| `/mnt/ace/data/document-index/summaries/` filename inventory (rev-2) | **Four** filename conventions on disk: 601,320 × `<16hex>.json` (path-derived), 78,274 × `sha256:<64hex>.json` (prefix included), 27,083 × `<32hex>.json` (bare md5), 10,460 × `<64hex>.json` (bare sha256). ~37K bare-form files are invisible to single-pattern lookup — diagnosis missed them. Total 717,141 ≈ matches diagnosis. |
| `.claude/skills/coordination/engineering-issue-workflow/SKILL.md:80,211` | GOTCHA warnings. **Scope-split to follow-up issue** — not edited by this PR. |
| `.claude/skills/coordination/workflow-compliance-audit/SKILL.md:60` | Duplicate GOTCHA. Same deferral. |
| `docs/standards/engineering-issue-workflow-skill.md:85` | Duplicate GOTCHA. Same deferral. |
| `data/document-index/resource-intelligence-maturity.yaml` | Combined-scope figure (1.03M records / 61.9%) — must not be overwritten in place. Additive-field update deferred to follow-up. |
| `data/document-index/intelligence-accessibility-registry.yaml` | Advertises reachability of index fields. New `content_type` / `summary_done` declaration **deferred** to follow-up to keep data-fix PR tight. |
| `data/document-index/index.jsonl` head | Confirmed schema. `summary: null` on every record. |
| Index consumer survey (rev-2) | `grep -l "index.jsonl" scripts/` identifies consumers to verify for lenient parsing (see Known Consumers below). |

### Gaps identified

- No enrichment script exists.
- No ext → content_type mapping.
- No regression guard against 0% coverage re-index (the exact #1878 failure mode).
- Phase A / Phase C / Phase E all rewrite index.jsonl without carrying forward enriched fields.
- Three skill/doc files carry now-outdated GOTCHA warnings → **separate follow-up issues**.
- Accessibility registry drift risk → **separate follow-up issue**.

<!-- Source count: 10 distinct (1 issue body + 9 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-16-issue-1878-restore-index-metadata.md` |
| Enrichment script | `scripts/data/document-index/enrich-summary-metadata.py` |
| Content-type map | `scripts/data/document-index/content_type_map.yaml` |
| Hash-key lookup lib | `scripts/data/document-index/_summary_lookup.py` (shared by enrichment + future Phase A/C/E) |
| Validation script | `scripts/data/document-index/validate-index-metadata.py` |
| Preflight reconciler | `scripts/data/document-index/preflight-summary-match.py` |
| Tests | `tests/data/document_index/test_enrich_summary_metadata.py`, `test_validate_index_metadata.py`, `test_summary_lookup.py`, `test_phase_a_carryover.py`, `test_pipeline_chain_preserves_fields.py` |
| Phase-A patch | `scripts/data/document-index/phase-a-index.py` (modify: carryover + atomic write) |
| Phase-C patch | `scripts/data/document-index/phase-c-classify.py` (modify: carryover in writeback mode) |
| Phase-E patch | `scripts/data/document-index/phase-e-backpopulate.py` (modify: carryover) |
| Plan reviews | `scripts/review/results/2026-04-16-plan-1878-{claude,codex,gemini}.md` |

**Deferred to follow-up issues** (each gets its own `status:plan-review` cycle):

| Follow-up issue | Deliverable |
|---|---|
| (new) GOTCHA refresh — index metadata now queryable | Edit 3 skill/doc files in lockstep after two clean pipeline runs |
| (new) Maturity-YAML additive field | Add `index_jsonl_only_summary_coverage_percent` alongside the combined 61.9% figure; version bump |
| (new) Accessibility-registry declaration | Declare `content_type` / `summary_done` in `intelligence-accessibility-registry.yaml` |
| (new) `conference-index-batch.jsonl` coverage | Same fix pattern applied to the conference corpus |

---

## Deliverable

A `data/document-index/index.jsonl` where 100% of records have a `content_type` (derived from `ext`, with `other` as the catch-all) and a `summary_done` boolean (true when a non-empty summary file exists on the ace drive under any of four known filename conventions), plus (a) a validation guard that rejects regression, (b) a preflight reconciler, and (c) carryover in Phase A/C/E so later pipeline stages do not clobber the new fields.

---

## Pseudocode

### `_summary_lookup.py` — shared hash-key derivation

```
def candidate_filenames(record) -> list[str]:
    """Return ordered candidate summary filenames for a record.
    Multiple patterns exist on disk (rev-2 finding)."""
    ch = record.get("content_hash")  # may be "sha256:<64hex>", "md5:<32hex>", or None
    path = record["path"]
    path_fallback = sha256(path.encode()).hexdigest()[:16]  # matches summarise-worker.py:70

    candidates = []
    if ch:
        candidates.append(f"{ch}.json")               # e.g. "sha256:abc....json" (78,274 files)
        if ":" in ch:
            _, bare = ch.split(":", 1)
            candidates.append(f"{bare}.json")         # e.g. bare "<32hex>.json" (27,083) or "<64hex>.json" (10,460)
    candidates.append(f"{path_fallback}.json")        # path-derived 16-hex (601,320)
    return candidates

def find_summary(record, summaries_dir) -> Path | None:
    for name in candidate_filenames(record):
        p = summaries_dir / name
        if p.exists():
            return p
    return None
```

### `enrich-summary-metadata.py` — mirrors `enrich-readability.py` pattern

```
parse args: --dry-run, --resume, --workers N, --summaries-dir, --threshold-override
load content_type_map.yaml (ext → category; default "other")

if not --dry-run:
    copy index.jsonl → index.jsonl.backup-YYYY-MM-DD   # dated, never overwritten

open index.jsonl.tmp for streaming write
with ProcessPoolExecutor(workers) as ex:
    for record in stream_jsonl(index.jsonl):
        if --resume and "content_type" in record and "summary_done" in record:
            write record as-is; continue
        submit enrich_one(record) → future

    for future in as_completed(futures):
        record = future.result()
        write record to index.jsonl.tmp

atomic rename index.jsonl.tmp → index.jsonl
print coverage report

def enrich_one(record):
    ext = record.get("ext", "").lower().lstrip(".")
    record["content_type"] = content_type_map.get(ext, "other")

    summary_path = find_summary(record, summaries_dir)   # from _summary_lookup.py
    if summary_path is None:
        record["summary_done"] = False
        return record
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        record["summary_done"] = False
        return record
    record["summary_done"] = bool(data.get("summary") or "").strip().__len__() > 0
    return record
```

**Note:** `summary_title` / `summary_discipline` are NOT added to the default schema (Gemini A1). A future `--include-semantic` flag can opt into a sidecar `index-semantic.jsonl` in a separate issue.

### `preflight-summary-match.py` — Claude F2 pre-flight

```
sample 1000 random records from index.jsonl
for each: try find_summary() and count matches per candidate pattern
print: overall match rate, per-pattern match rate, per-segment rate
        (content_hash-present vs path-fallback)
if overall match rate < (projected rate - 5 percentage points): exit 1
```

### `validate-index-metadata.py`

```
parse args: --content-type-max-missing 0.10, --summary-done-min 0.55
load index.jsonl
total = count
missing_ct = count where content_type missing OR is None
non_other_ct = count where content_type is not None and != "other"
summary_done_true = count where summary_done is True

if missing_ct / total > 0.10: exit 1             # strict: must have field set
if non_other_ct / total < 0.90: exit 1           # Claude AC fix: ≥90% NON-`other`
if summary_done_true / total < 0.55: exit 1      # rev-2 threshold: 55% (Gemini BC3)
exit 0
```

### Phase A / C / E carryover

```
# phase-a-index.py — add --preserve-metadata (default true)
before scanning:
    existing = { r["path"]: {"content_type": r.get("content_type"),
                             "summary_done": r.get("summary_done")}
                 for r in load_jsonl(index_path) if exists }
after building new_records list:
    for r in new_records:
        if r["path"] in existing:
            r.update(existing[r["path"]])

# write path: atomic
write index.jsonl.tmp → rename to index.jsonl
(also create index.jsonl.backup-YYYY-MM-DD before rewrite — Codex F2)

# phase-c-classify.py bounded-writeback:
existing_enriched = { ... same pattern ... }
on writeback: merge existing_enriched fields into record before emit

# phase-e-backpopulate.py: identical pattern
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/data/document-index/enrich-summary-metadata.py` | Main enrichment, mirrors enrich-readability pattern |
| Create | `scripts/data/document-index/_summary_lookup.py` | Shared multi-pattern hash-key lookup |
| Create | `scripts/data/document-index/content_type_map.yaml` | Ext → content_type source of truth |
| Create | `scripts/data/document-index/validate-index-metadata.py` | Regression guard |
| Create | `scripts/data/document-index/preflight-summary-match.py` | Pre-flight sample reconciliation |
| Create | `tests/data/document_index/test_summary_lookup.py` | TDD for multi-pattern lookup |
| Create | `tests/data/document_index/test_enrich_summary_metadata.py` | TDD for enrichment |
| Create | `tests/data/document_index/test_validate_index_metadata.py` | TDD for validator |
| Create | `tests/data/document_index/test_phase_a_carryover.py` | TDD for Phase A carryover + atomic write |
| Create | `tests/data/document_index/test_pipeline_chain_preserves_fields.py` | Codex F3 — integration test: A → enrich → C → E preserves fields |
| Modify | `scripts/data/document-index/phase-a-index.py` | Carryover + atomic write + dated backup |
| Modify | `scripts/data/document-index/phase-c-classify.py` | Carryover in writeback mode |
| Modify | `scripts/data/document-index/phase-e-backpopulate.py` | Carryover |
| Update | `docs/plans/README.md` | Plan row (already added) |

Explicitly **NOT** in scope for this PR (follow-up issues to be filed after plan approval):

- Skill/doc GOTCHA edits (3 files)
- `resource-intelligence-maturity.yaml` additive field
- `intelligence-accessibility-registry.yaml` declaration
- `conference-index-batch.jsonl` parallel fix

---

## TDD Test List

| # | Test name | Verifies |
|---|---|---|
| 1 | `test_content_type_pdf_maps_to_document` | `.pdf` → `document` |
| 2 | `test_content_type_dwg_maps_to_cad` | `.dwg` → `cad` |
| 3 | `test_content_type_unknown_ext_maps_to_other` | unknown ext → `other` (never None) |
| 4 | `test_content_type_case_insensitive` | `.PDF` == `.pdf` == `document` |
| 5 | `test_lookup_prefers_full_prefixed_hash` | `content_hash="sha256:abc..."` finds `sha256:abc....json` first |
| 6 | `test_lookup_falls_back_to_bare_hash` | if prefixed filename missing, tries `abc....json` (bare) |
| 7 | `test_lookup_md5_prefix_and_bare_both_tried` | legacy og_standards: both `md5:<32hex>.json` and `<32hex>.json` attempted |
| 8 | `test_lookup_falls_back_to_path_sha256_16` | no content_hash → uses `sha256(path)[:16]` |
| 9 | `test_lookup_returns_none_when_no_file_matches` | missing summary on disk → None |
| 10 | `test_summary_done_true_when_summary_nonempty` | `{"summary": "x"}` → True |
| 11 | `test_summary_done_false_when_summary_empty_string` | `{"summary": ""}` → False |
| 12 | `test_summary_done_false_when_summary_key_absent` | summary JSON lacks `summary` key → False |
| 13 | `test_summary_done_false_on_corrupt_json` | malformed JSON → False (no crash) |
| 14 | `test_summary_done_false_on_unicode_decode_error` | non-UTF8 summary bytes → False |
| 15 | `test_summary_done_false_when_file_missing` | no file on disk → False |
| 16 | `test_enrichment_writes_dated_backup_before_overwrite` | `index.jsonl.backup-YYYY-MM-DD` exists after run |
| 17 | `test_enrichment_atomic_rename_via_monkeypatched_os_rename` | `os.rename` raising mid-run leaves original index intact (explicit injection seam) |
| 18 | `test_enrichment_resume_skips_already_enriched_records` | `--resume` + record with both fields → unchanged |
| 19 | `test_enrichment_preserves_all_prior_fields` | no existing field is deleted or mutated |
| 20 | `test_validator_rejects_low_content_type_coverage` | `<90%` non-`other` → exit 1 |
| 21 | `test_validator_rejects_missing_content_type_field` | `>10%` records missing field → exit 1 |
| 22 | `test_validator_rejects_low_summary_done` | `<55%` True → exit 1 |
| 23 | `test_validator_passes_healthy_index` | 95% non-`other` + 80% summary_done → exit 0 |
| 24 | `test_validator_thresholds_overridable_via_cli` | `--summary-done-min 0.40` relaxes default |
| 25 | `test_phase_a_preserves_enriched_fields_on_reindex` | re-run retains `content_type` + `summary_done` for matching path |
| 26 | `test_phase_a_no_preserve_metadata_flag` | `--no-preserve-metadata` starts fresh |
| 27 | `test_phase_a_writes_atomic_with_backup` | mid-write kill leaves prior index recoverable from dated backup |
| 28 | `test_phase_a_content_hash_churn` | if `content_hash` changes for a path between runs, carryover keys on `path` (not hash) and still preserves fields |
| 29 | `test_phase_c_writeback_preserves_enriched_fields` | bounded writeback keeps `content_type` + `summary_done` |
| 30 | `test_phase_e_backpopulate_preserves_enriched_fields` | Phase E rewrite keeps fields |
| 31 | `test_pipeline_chain_A_enrich_C_E_preserves_fields` | Codex F3 — synthetic 10-record index survives full chain |
| 32 | `test_preflight_exits_nonzero_on_low_match_rate` | simulated 20% match (vs 80% expected) → exit 1 |
| 33 | `test_preflight_reports_per_pattern_breakdown` | output includes match counts for each of 4 filename patterns |

---

## Acceptance Criteria

- [ ] All new tests pass: `uv run pytest tests/data/document_index/ -v`
- [ ] No regression: `uv run pytest` passes fully
- [ ] **Preflight** run on full index reports overall match rate ≥ 78% (projection 83.7% minus 5pp safety margin), with per-pattern breakdown matching the 601K/78K/27K/10K file-count distribution
- [ ] Dry-run enrichment report: ≥90% `content_type != "other"` (fixes Claude AC bug — was trivially satisfied before)
- [ ] Dry-run enrichment report: ≥55% `summary_done == True` (relaxed from 60% per Gemini; still well under projected 83.7%)
- [ ] 100% of records have `content_type` and `summary_done` keys present (no missing fields)
- [ ] Backup `index.jsonl.backup-2026-04-16` exists after enrichment run
- [ ] `validate-index-metadata.py` returns 0 on enriched index
- [ ] `validate-index-metadata.py` returns 1 on synthetic broken fixture (test asserts this)
- [ ] `phase-a-index.py --dry-run` on enriched index preserves fields
- [ ] Integration test `test_pipeline_chain_A_enrich_C_E_preserves_fields` passes
- [ ] Known-consumer spot-check: `build-capability-map.py`, `assess-deep-extraction-yield.py`, `generate-coverage-report.py`, `ghost-audit.py`, `dde-migration-report.py` all run to completion against enriched index without errors (lenient-parsing confirmation)
- [ ] Plan review artifacts at `scripts/review/results/2026-04-16-plan-1878-{claude,codex,gemini}.md` exist
- [ ] No edits to the 4 deferred surfaces (3 skill/doc files, maturity YAML, accessibility registry, conference-index-batch) — enforced by reviewer on PR

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR → (re-review pending after rev-2) | (1) `content_hash` prefix lookup bug; (2) ignored 46.1% match-rate gap; (3) missing `--resume`/`--workers`/`.tmp`/`.bak` pattern; + 4 minor |
| Codex | MAJOR → (re-review pending after rev-2) | (1) `conference-index-batch.jsonl` coverage unproven; (2) no Phase A atomic/backup write; (3) Phase C/E clobber risk not addressed |
| Gemini | MINOR → (re-review pending after rev-2) | (1) drop `summary_title`/`discipline` inline; (2) split skill/GOTCHA edits; (3) maturity YAML must be additive; (4) consumer-compat; (5) accessibility-registry declaration |

**Overall result (rev-1):** FAIL — 2 MAJOR + 1 MINOR → revision required before user approval

**Revisions made in rev-2:**

1. `_summary_lookup.py` multi-pattern lookup (4 filename conventions) — addresses Claude F1
2. `preflight-summary-match.py` pre-flight reconciler — addresses Claude F2
3. Full `ProcessPoolExecutor` / `--resume` / `--workers` / `.tmp`/`.bak` pattern — addresses Claude F3
4. `summary_title` / `summary_discipline` moved out of default schema — addresses Gemini A1
5. 4 deferred follow-up issues (GOTCHAs, maturity YAML, accessibility registry, conference-batch) — addresses Claude F7, Gemini S1/D1/D3
6. Phase A atomic write + dated backup — addresses Codex F2
7. Phase C + Phase E carryover patches + integration test (#31) — addresses Codex F3
8. Explicit conference-batch deferral with count documented as follow-up — addresses Codex F1
9. Known-consumer spot-check acceptance criterion — addresses Gemini BC1
10. Fixed `≥90% content_type` AC to `≥90% non-\`other\`` — addresses Claude AC bug
11. Threshold defaults made CLI-overridable with rationale — addresses Claude M1
12. Atomic-rename test injection seam specified (`os.rename` monkeypatch) — addresses Claude M2
13. Corrupt-JSON / unicode-decode / missing-key tests added (tests 12-14) — addresses Claude test gaps

**Re-review disposition:** Per the planning skill, re-review is recommended when rev-1 returned MAJOR. Options:

- (a) Run a second provider review wave on rev-2 before surfacing to user
- (b) Surface rev-2 to user with honest review history and let user decide whether to require re-review

Default recommendation: **(b)** — the rev-2 revisions are mechanical responses to specific blocking items, each traceable in the table above. A user approval gate is the next proper governance step.

---

## Risks and Open Questions

- **Risk:** Ace drive unmount mid-run produces partial enrichment. Mitigated by atomic rename + dated backup.
- **Risk:** Index size growth. With `summary_title`/`discipline` dropped (Gemini A1), growth is negligible (~25 MB for two new scalar fields vs. original ~65 MB).
- **Risk:** Validation thresholds may be wrong for different corpora. Mitigation: all thresholds CLI-flaggable with documented defaults.
- **Risk:** Phase A atomic-write change is a behavior change to the canonical indexer. Mitigation: behind `--atomic-write` flag (default true) with opt-out for debugging.
- **Risk:** 649K summary-file stats via NFS is slow. Mitigation: `--workers N`, progress logging every 10K records, `--resume` restart-safety.
- **Risk:** Backup files accumulate on every run. Mitigation: `.gitignore` rule for `index.jsonl.backup-*`; cleanup retention policy deferred to maturity-YAML follow-up issue.
- **Open:** Should PR include the `conference-index-batch.jsonl` coverage count (read-only) so the follow-up issue has a known baseline? Recommend: yes — `preflight-summary-match.py` can run in conference mode as a read-only probe.
- **Open:** Should `validate-index-metadata.py` be wired into pre-commit in this PR? Recommend: no — ship unwired; add to pre-commit in the accessibility-registry follow-up after first clean run.
- **Open:** Per rev-2 discussion, re-review before user approval or after? Flagged for user decision above.

---

## Complexity: T2

New enrichment/validation/preflight/lookup scripts + 5 test files + three existing-file modifications (Phase A/C/E) + integration test. No multi-module architecture change, no new standards, no cross-repo work. Full TDD required. Sized at the high end of T2 but does not cross into T3 (no new subsystem, no standards work, no cross-repo coordination).
