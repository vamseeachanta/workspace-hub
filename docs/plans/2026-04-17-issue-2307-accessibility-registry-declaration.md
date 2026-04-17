# Plan for #2307: Declare content_type/summary_done in accessibility registry

> **Status:** adversarial-reviewed
> **Complexity:** T1
> **Date:** 2026-04-17 (rev-2 after 2 Claude MINOR nits)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2307
> **Parent:** #1878 (closed); **sibling:** #2136, #2205, #2306, #2309
> **Review artifacts:** scripts/review/results/2026-04-17-plan-2307-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `data/document-index/intelligence-accessibility-registry.yaml:144-160` — existing `registry-corpus-index` asset entry targeting `data/document-index/index.jsonl`. Fields: `asset_key, title, asset_type: registry, layer: L2, canonical_path, human_entry_point, agent_entry_point, query_command, machine_scope, source_of_truth_tier: git-tracked, durability: durable, freshness_source, freshness_cadence: monthly, record_count: 1033933, discoverability: partially-discoverable, gaps: null, owner_issue: null`.
- Found: `data/document-index/intelligence-accessibility-registry.yaml:1-18` — header block with `schema_version: '1.0.0'`, `asset_type enum`, `layer enum`, `source_of_truth_tier enum`, `durability enum`, `discoverability enum`. No existing enum for field-level declarations — this plan extends the schema.
- Found: `scripts/data/document-index/validate-index-metadata.py` (from #1878) — authoritative reachability check; exit-0 contract for field coverage.
- Gap: No field-level declaration for `content_type`, `summary_done` anywhere in the registry.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable.

### Documents consulted

| Source | Finding |
|---|---|
| Issue #2307 body | Requires: field name/type/derivation source; reachability path; freshness signal; known-consumer list. Pre-condition: bump schema version if needed. |
| #2136 (closed) | Parent owner issue for the registry. Registry structure: asset-granularity with enum-controlled metadata. |
| #2205 | Operating-model pyramid. `index.jsonl` fields are **structural/reachability (L2)** — not semantic (L3) — so inline field declarations in the L2 asset entry are the right home. |
| #2306 (closed, commit `a13da73df`) | Companion artifact: maturity YAML now holds the **numbers**. Accessibility registry holds the **reachability contract**. Cross-link both. |
| #2309 | Proposes `summary_file_exists` field split. Plan must document that `summary_done` today conflates existence+content-quality, and that #2309 will introduce a separate field — frame `summary_done` declaration with that caveat. |
| Issue #1878 closeout consumer list | Known consumers spot-checked against enriched index: `build-capability-map.py`, `assess-deep-extraction-yield.py`, `generate-coverage-report.py`, `ghost-audit.py`, `dde-migration-report.py`. |

### Gaps identified

- No `fields:` sub-block exists under any asset. Schema extension.
- The `gaps: null` marker on `registry-corpus-index` is outdated — previously no field-level reachability; this plan fills that gap.
- `record_count: 1033933` is the combined-scope figure. Adding `record_count_by_scope` is tempting but out of scope for #2307 — out-of-scope note captures it.

<!-- Source count: 7 distinct (issue body + 6 others). Contract requires ≥3. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-17-issue-2307-accessibility-registry-declaration.md` |
| Edit target | `data/document-index/intelligence-accessibility-registry.yaml` |
| Plan review — Claude | `scripts/review/results/2026-04-17-plan-2307-claude.md` |

---

## Deliverable

A `registry-corpus-index` asset entry augmented with an inline `fields:` sub-block declaring `content_type` and `summary_done` — including type, derivation, reachability path, freshness signal, known-consumer list, and cross-references to #1878/#2306/#2309 — plus schema version bumped to `1.1.0` and a dated comment in the header explaining the additive change.

---

## Pseudocode

T1 — trivial. Single YAML edit. No functions.

---

## Edit specifications

### Edit A (line 19): bump `schema_version`

Find: `schema_version: '1.0.0'`
Replace: `schema_version: '1.1.0'`

### Edit B (add schema note to header, after line 18)

Before the `generated:` line (line 17), append a comment block:

```yaml
# schema_version history:
#   1.0.0 (2026-04-11) — initial registry
#   1.1.0 (2026-04-17) — additive: per-asset `fields:` sub-block for structural field declarations (#2307)
```

### Edit C (extend `registry-corpus-index` entry at lines 144-160)

Find the block:

```yaml
  - asset_key: registry-corpus-index
    title: Document Corpus Index
    asset_type: registry
    layer: L2
    canonical_path: data/document-index/index.jsonl
    human_entry_point: data/document-index/registry.yaml
    agent_entry_point: data/document-index/index.jsonl
    query_command: "wc -l data/document-index/index.jsonl"
    machine_scope: [all-git-clones]
    source_of_truth_tier: git-tracked
    durability: durable
    freshness_source: "git log -1 --format=%ci data/document-index/index.jsonl"
    freshness_cadence: monthly
    record_count: 1033933
    discoverability: partially-discoverable
    gaps: null
    owner_issue: null
```

Replace with (keeping all existing keys unchanged, adding `fields:` sub-block and annotating `gaps`):

```yaml
  - asset_key: registry-corpus-index
    title: Document Corpus Index
    asset_type: registry
    layer: L2
    canonical_path: data/document-index/index.jsonl
    human_entry_point: data/document-index/registry.yaml
    agent_entry_point: data/document-index/index.jsonl
    query_command: "wc -l data/document-index/index.jsonl"
    machine_scope: [all-git-clones]
    source_of_truth_tier: git-tracked
    durability: durable
    freshness_source: "git log -1 --format=%ci data/document-index/index.jsonl"
    freshness_cadence: monthly
    record_count: 1033933  # Combined scope: index.jsonl (649,564) + conference-index-batch.jsonl
    discoverability: partially-discoverable
    gaps: "Conference-batch corpus not yet field-enriched (#2305)."
    validator: "scripts/data/document-index/validate-index-metadata.py"
    owner_issue: null
    # Fields populated by #1878 enrichment; reachability contract for agent queries.
    fields:
      - name: content_type
        type: string
        enum: [document, spreadsheet, presentation, cad, simulation-input, script, text, web, image, archive, other]
        enum_source_of_truth: "scripts/data/document-index/content_type_map.yaml"
        derivation: "scripts/data/document-index/enrich-summary-metadata.py (ext → content_type via content_type_map.yaml — canonical source for enum values)"
        query_example: 'jq -r "select(.content_type == \"cad\") | .path" data/document-index/index.jsonl'
        coverage_source: "data/document-index/resource-intelligence-maturity.yaml::status.index_jsonl_only.content_type_non_other_percent"
        provenance: "#1878; current coverage 99.9988% (see #2306 maturity YAML for live figure)"
      - name: summary_done
        type: boolean
        derivation: "scripts/data/document-index/enrich-summary-metadata.py (summary_done_from_file: True iff non-empty summary text on ace drive)"
        query_example: 'jq "select(.summary_done == true)" data/document-index/index.jsonl'
        coverage_source: "data/document-index/resource-intelligence-maturity.yaml::status.index_jsonl_only.summary_done_percent"
        provenance: "#1878; current coverage 16.1% (see #2306). NOTE: #2309 will split this into `summary_done` (content-quality) and `summary_file_exists` (existence, ~87.8%)."
        known_consumers:
          - scripts/data/document-index/build-capability-map.py
          - scripts/data/document-index/assess-deep-extraction-yield.py
          - scripts/data/document-index/generate-coverage-report.py
          - scripts/data/document-index/ghost-audit.py
          - scripts/data/document-index/dde-migration-report.py
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `data/document-index/intelligence-accessibility-registry.yaml` | Edits A, B, C |
| Update | `docs/plans/README.md` | Plan row |

No code, no tests.

---

## TDD Test List

Not applicable (T1 YAML edit). Verification is a parse check + grep:

| Check | Command |
|---|---|
| YAML parses | `python3 -c "import yaml; yaml.safe_load(open('data/document-index/intelligence-accessibility-registry.yaml'))"` → exit 0 |
| Schema version bumped | `grep "^schema_version:" ...` → `'1.1.0'` |
| Existing `registry-corpus-index` asset still present & path unchanged | `grep -A2 "asset_key: registry-corpus-index" ...` shows `canonical_path: data/document-index/index.jsonl` |
| New `fields:` block present with both fields | `python3 -c "import yaml; r=yaml.safe_load(open('...')); f=[a for a in r['assets'] if a['asset_key']=='registry-corpus-index'][0]['fields']; assert {f[0]['name'], f[1]['name']} == {'content_type', 'summary_done'}"` → exit 0 |
| Other asset entries untouched | `git diff --stat` shows only the registry YAML changed; line-count delta matches (schema bump + header comment + new fields block) |

---

## Acceptance Criteria

- [ ] YAML parses cleanly
- [ ] Schema version `1.1.0`
- [ ] Two field declarations present under `registry-corpus-index.fields[]` with `name ∈ {content_type, summary_done}`
- [ ] Each field has type, derivation, query_example, coverage_source pointing at #2306's maturity YAML, provenance
- [ ] `known_consumers` present on `summary_done` (5 entries from #1878 spot-check)
- [ ] `validator` key present pointing at validate-index-metadata.py
- [ ] Cross-references to #1878, #2306, #2309 present
- [ ] Existing 18 asset entries byte-identical except for the targeted `registry-corpus-index` mutation (git diff scoped)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE (2 MINOR nits → addressed in rev-2) | Schema bump 1.1.0 correct (matches #2306 precedent); registry has no consumer script that would reject unknown keys (`grep -rln` verified); all cross-refs accurate; content_type enum matches `content_type_map.yaml`; known_consumers list matches #1878 closeout. |

**Overall result:** Ready for approval — single-provider review sufficient, nits addressed.

Revisions made in rev-2:
- Moved `validator:` to sibling position near `gaps:` (consistent with asset-level metadata placement)
- Added `enum_source_of_truth: "scripts/data/document-index/content_type_map.yaml"` field to `content_type` entry; also referenced the map in `derivation:` as canonical source to reduce drift risk

---

## Risks and Open Questions

- **Risk:** The registry schema currently has no `fields:` key anywhere — this is a schema extension, not a conformant entry. If a validation script rejects unknown keys, this change would break tooling. Mitigation: `intelligence-accessibility-registry.yaml` has no schema-enforcement script in this repo (verified via `grep -rln "intelligence-accessibility-registry" scripts/`). Extension is safe.
- **Risk:** The `content_type` enum of 11 values is duplicated between `content_type_map.yaml` and the registry entry. If a new category is added to `content_type_map.yaml`, the registry drifts. Mitigation: accept drift as low-cost (new categories are rare), or add a note directing readers to `content_type_map.yaml` as source-of-truth (doing so in the `derivation` field).
- **Open:** Should the `record_count_by_scope:` split (1.03M combined vs 649,564 single-corpus) land here or in a separate issue? Recommendation: separate issue — this PR strictly declares the new fields.
- **Open:** The `known_consumers` list will rot as consumers are added/removed. Accept the rot risk (documented) or add a discovery mechanism? Recommendation: accept — the list is a pointer to check, not an authoritative manifest.

---

## Complexity: T1

Single YAML file, 3 edits (schema bump + header comment + asset extension). No code, no tests, single-provider adversarial review sufficient.
