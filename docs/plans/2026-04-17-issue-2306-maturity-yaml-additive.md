# Plan for #2306: Additive maturity-YAML field for index.jsonl-only coverage

> **Status:** adversarial-reviewed
> **Complexity:** T1
> **Date:** 2026-04-17 (rev-2 after Claude MINOR nit)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2306
> **Parent:** #1878 (closed)
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2306-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `data/document-index/resource-intelligence-maturity.yaml` — lines 1-3 define `version: "1.1.0"` and `schema_version: "1.0.0"`. Line 31-33 carries the combined-scope figures: `index_summary_coverage_percent: 61.9`, `total_index_records: 1033933`, `total_index_summaries: 639585`. Line 37 marks "YAML is the source of truth."
- Found: `data/document-index/resource-intelligence-maturity.md` — human-readable mirror of the YAML (per the `canonical_markdown_ref` field).
- Found: `scripts/data/document-index/validate-index-metadata.py` (from #1878) — authoritative source for the new numbers; produced PASS report against enriched index on 2026-04-16.
- Gap: No existing `index_jsonl_only:` sub-block to carry the single-corpus figures produced by #1878.

### Standards
Not applicable — YAML bookkeeping only.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2306 body | Scope: additive block with `total_records`, `summary_done_percent`, `content_type_non_other_percent`, `measurement_date`, `source`. Schema bump required. Preserve 61.9% combined figure unchanged. |
| Issue #1878 closeout ([comment-4263745741](https://github.com/vamseeachanta/workspace-hub/issues/1878#issuecomment-4263745741)) | Live-run numbers: 649,564 records; 649,556 non-other content_type (99.999% → document 100% per report); 104,767 summary_done=True (16.1%); validator PASS; run completed 2026-04-16. |
| Issue #2309 | Proposes splitting `summary_done` into `summary_done` + `summary_file_exists`. This plan must frame the 16.1% figure as "content-quality signal" so future readers understand it will not change meaning when #2309 lands. |
| Issue #2205 | Operating-model parent. The maturity YAML feeds #2205 dashboards; schema bump preserves their current denominator. |

### Gaps identified

- No `index_jsonl_only` block — to be created.
- Existing schema at `1.0.0` doesn't document any `index_jsonl_only` shape; schema bump to `1.1.0` needed.
- `notes:` array needs a dated entry explaining the additive change.

<!-- Source count: 6 distinct (issue body + 5 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2306-maturity-yaml-additive.md` |
| Edit target | `data/document-index/resource-intelligence-maturity.yaml` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2306-claude.md` |

---

## Deliverable

A `resource-intelligence-maturity.yaml` with a new `index_jsonl_only:` block carrying the 2026-04-16 post-enrichment numbers, `schema_version` bumped to `1.1.0`, and a `notes:` entry explaining the additive change. The combined-scope `index_summary_coverage_percent: 61.9` line is preserved byte-for-byte.

---

## Pseudocode

T1 — trivial. Single-file YAML edit. No functions.

---

## Edit specification

**File:** `data/document-index/resource-intelligence-maturity.yaml`

**Edit A (line 3): bump schema_version**

Find: `schema_version: "1.0.0"`
Replace: `schema_version: "1.1.0"`

**Edit B (after line 36): add `index_jsonl_only` block**

Insert after the existing `wrk_captured_standards: 23` line (i.e., inside the `status:` block) a new sub-key:

```yaml
  # Post-#1878 single-corpus figures (additive to the combined-scope values above).
  # These measure index.jsonl alone (649K records), not the 1.03M combined scope.
  # Run evidence: see issue #1878 close comment 2026-04-16.
  index_jsonl_only:
    total_records: 649564
    content_type_non_other_percent: 99.9988  # 649,556 / 649,564 — 8 records hit "other" fallback
    summary_done_percent: 16.1               # 104,767 / 649,564 — content-quality signal (#2309 will split)
    measurement_date: "2026-04-16"
    source: "scripts/data/document-index/validate-index-metadata.py"
    notes:
      - "summary_done=True is dominated by non-CAD records; 72% of the corpus is CAD with no extractable text."
      - "See #2309 for planned summary_file_exists field split (file-existence vs content-quality decoupling)."
```

**Edit C (append to top-level `notes:` array, after the last entry on line 42):**

Add two new bullet items:

```yaml
  - "2026-04-17: schema_version bumped 1.0.0 → 1.1.0 to accommodate additive index_jsonl_only block (#2306)."
  - "2026-04-17: Combined-scope index_summary_coverage_percent:61.9 preserved unchanged; single-corpus numbers captured under status.index_jsonl_only."
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `data/document-index/resource-intelligence-maturity.yaml` | Edits A, B, C |
| Update | `docs/plans/README.md` | Plan row |

No code changes. No tests required — YAML bookkeeping only.

---

## TDD Test List

Not applicable for T1 YAML edits. Verification is a parse check + grep:

| Check | Command |
|---|---|
| YAML still parses | `python3 -c "import yaml; yaml.safe_load(open('data/document-index/resource-intelligence-maturity.yaml'))"` → exit 0 |
| Combined figure preserved | `grep -c "index_summary_coverage_percent: 61.9" ...` → 1 |
| New block present | `grep -c "index_jsonl_only:" ...` → 1 |
| Schema version bumped | `grep "^schema_version:" ...` → `"1.1.0"` |

---

## Acceptance Criteria

- [ ] YAML parses cleanly (Python `yaml.safe_load` exits 0)
- [ ] Line 31 (`index_summary_coverage_percent: 61.9`) is unchanged
- [ ] `schema_version` is `"1.1.0"`
- [ ] `status.index_jsonl_only` block present with all five required keys + notes
- [ ] Top-level `notes:` array gains two new dated entries
- [ ] No other lines modified (git diff limited to schema bump, new block, notes append)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE (1 MINOR nit → addressed in rev-2) | Numbers accurate (16.1% and preserved 61.9% verified). Schema bump 1.0.0→1.1.0 appropriate for additive block. Placement under `status:` sound. #2205 dashboards unaffected. MINOR: `99.999` overclaimed precision — changed to `99.9988`. |

**Overall result:** Ready for approval — single-provider review sufficient per T1 guidance, nit addressed.

Revisions made in rev-2:
- `content_type_non_other_percent`: `99.999` → `99.9988` (accurate to 4 decimals)

---

## Risks and Open Questions

- **Risk:** Markdown mirror `resource-intelligence-maturity.md` may drift if not updated in the same PR. The YAML note says "Markdown summary must link here and must not diverge." Recommendation: update the markdown in a tightly-coupled follow-up (out of scope for #2306 to keep it T1).
- **Resolved in rev-2 (Claude MINOR):** `content_type_non_other_percent` is `99.9988` (accurate to 4 decimals) rather than `99.999` (which overclaimed precision — true ratio is `649556/649564 = 99.998769...`).
- **Open:** Should the `index_jsonl_only.notes` array reference specific commits from #1878 (e.g., `8c9d73690` for the enrichment run)? Recommendation: no — commits rot; issue numbers don't.

---

## Complexity: T1

Single YAML file, 3 edits (schema bump + insert block + append notes). No code, no tests, no architecture change. Single-provider adversarial review sufficient.
