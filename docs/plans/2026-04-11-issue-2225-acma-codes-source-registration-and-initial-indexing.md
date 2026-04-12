# Plan for #2225: Register /mnt/ace/acma-codes as Mounted Source and Run Initial Indexing/Dedup

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2225
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2225-claude.md | scripts/review/results/2026-04-11-plan-2225-final.md

---

## Resource Intelligence Summary

### Existing repo code / artifacts relevant to this issue

| Artifact | Path | Relevance |
|---|---|---|
| Mounted source registry | `data/document-index/mounted-source-registry.yaml` | 12 sources registered; `/mnt/ace/acma-codes` is NOT present -- primary gap this issue closes |
| Pipeline config | `scripts/data/document-index/config.yaml` | 8 source entries in `sources:` block; `acma_codes` not present; defines `exclude_patterns`, `extensions`, `deduplication.source_priority` |
| Phase A indexer | `scripts/data/document-index/phase-a-index.py` | Multi-source filesystem scanner; computes SHA-256 hashes; calls `provenance.py` for merge; accepts `--source` flag for single-source runs |
| Provenance merger | `scripts/data/document-index/provenance.py` | Content-hash-based dedup; merges duplicate records into single entries with provenance arrays; supports source priority ordering |
| Corpus index | `data/document-index/index.jsonl` | 1,033,933 records across 8 sources; acma-codes not indexed (confirmed: no records with source=acma_codes) |
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 standards; `API-RP-2SK-2ND-ED` is `done` (no doc_paths); `API-RP-1111` is `done` with 3+ doc_paths in `/mnt/ace/0000 O&G/`; NO OCIMF entries; NO CSA entries |
| Parent plan #2216 | `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` | Approved integration plan; recommends 4-way follow-on split; this issue is follow-on #1 |
| Cross-drive dedup report | `data/document-index/cross-drive-dedup-report.json` | Existing dedup analysis across drives; should be consulted during dedup pass |

### Standards / registries consulted

| Standard/Registry | Status | Source |
|---|---|---|
| API RP 2SK (2nd Ed, 1996) | `done` in transfer ledger; no `doc_paths` populated | `data/document-index/standards-transfer-ledger.yaml` line 3047 |
| API RP 1111 (multiple editions) | `done` in transfer ledger; 3+ `doc_paths` in `/mnt/ace/0000 O&G/` | `data/document-index/standards-transfer-ledger.yaml` |
| OCIMF (any) | NOT in transfer ledger | Only wiki coverage at `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` (MEG4 4th Ed 2018) |
| CSA Z276 (any) | NOT in any registry | Entirely absent from ecosystem |
| Mounted source registry | `/mnt/ace/acma-codes` NOT registered | `data/document-index/mounted-source-registry.yaml` -- 12 sources, none matching |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` -- covers OCIMF MEG4 (4th Ed, 2018); distinct from acma-codes OCIMF MEG 2008 (3rd Ed predecessor)
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` -- DNV position mooring; cross-references API RP 2SK (4th Ed, 2024)

### Documents consulted

- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` -- #2205 parent operating model (pyramid, layers, flows)
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` -- #2207 provenance contract (`doc_key` = SHA-256, alias paths, reuse rules)
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` -- #2209 boundary policy (registries are durable L2; plans are transient L5)
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` -- parent plan with live inventory classification
- GitHub issue #2225 -- scope, acceptance criteria, deliverables
- GitHub issue #2216 -- parent umbrella; `status:plan-approved`

### Gaps identified

1. **No mounted source registration** -- `/mnt/ace/acma-codes` absent from `mounted-source-registry.yaml`; the pipeline cannot discover it
2. **No config.yaml source entry** -- `acma_codes` not in `sources:` block; `phase-a-index.py` will not scan it
3. **No dedup source priority** -- `acma_codes` not in `deduplication.source_priority` list
4. **Sandbox prevents live inventory verification** -- same limitation as parent plan; inventory is inherited from #2216 pre-session observation
5. **API RP 2SK 2nd Ed has no doc_paths in ledger** -- hash comparison is the only reliable dedup method
6. **OCIMF and CSA entirely absent** -- no ledger, no wiki (except MEG4 which is a different edition), no code-registry entries; these will be net-new doc_keys

<!-- Verification: 8+ distinct sources consulted (issue body, mounted-source-registry.yaml, config.yaml, phase-a-index.py, provenance.py, standards-transfer-ledger.yaml, parent plan #2216, operating model #2205, provenance contract #2207, boundary policy #2209). Count: 10+ -->

---

## Live Inventory Findings for `/mnt/ace/acma-codes`

### Sandbox limitation

Direct filesystem access to `/mnt/ace/acma-codes` was denied by the Claude Code sandbox during this session (and during the parent #2216 planning session). The inventory below is **inherited from the approved parent plan #2216**, which recorded contents from pre-session live inspection.

**This is a known limitation.** The inventory must be re-verified by the implementer during execution when mount access is available.

### Inherited inventory (from #2216 approved plan)

| Top-level folder | Standards family | Known files | File types | Domain |
|---|---|---|---|---|
| `OCIMF/` | Oil Companies International Marine Forum | `OCIMF - 2008 - Mooring Equipment Guidelines.pdf`, `OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf` | PDF | marine / mooring |
| `API/` | American Petroleum Institute | `1996 Dec RP 2SK Stationkeeping Systems for Floating Structures 2nd ed.pdf`, `1999 July RP 1111 Offshore Hydrocarbon Pipelines 3rd ed.pdf` | PDF | marine / pipeline |
| `CSA/` | Canadian Standards Association | `276.1-20 marine structures associated with LNG facilities.pdf`, `Z276.18 LNG Production, storage, and handling.pdf` | PDF | marine / LNG |
| *(root or other)* | Mixed / unknown | `Thumbs.db`, possibly `.xlsx`, `.txt` files | Mixed | n/a |

### Source characterization

- **Staging area** -- not a normalized corpus; folder names follow org conventions but file naming is inconsistent
- **Small collection** -- estimated 6-10 PDF documents plus junk artifacts
- **Partially overlaps** with existing `og_standards_local` source at `/mnt/ace/0000 O&G/`
- **Contains net-new content** -- CSA Z276 series (entirely new) and OCIMF tandem mooring guidelines (not in any registry)

### Implementation-time verification requirements

The implementer MUST verify during execution:
1. Exact file count and total size of `/mnt/ace/acma-codes`
2. Whether additional folders exist beyond OCIMF/, API/, CSA/
3. Whether non-PDF files exist that need separate handling
4. Exact filenames for accurate SHA-256 hashing

---

## Proposed Source-Registration Model

### 1. Mounted source registry entry

Add to `data/document-index/mounted-source-registry.yaml`:

```yaml
- source_id: acma_codes_local
  document_intelligence_bucket: acma_codes
  mount_root: /mnt/ace/acma-codes
  local_or_remote: local
  index_artifact_ref: data/document-index/index.jsonl
  registry_ref: data/document-index/registry.yaml
  canonical_storage_policy: mixed staging area of standards assembled from unknown provenance
  provenance_rule: staging source; dedup against og_standards and ace_standards first
  dedup_rule: prefer /mnt/ace/0000 O&G for overlapping content (API duplicates); acma-codes is authoritative only for content not found in higher-priority sources
  availability_check_ref: scripts/readiness/check-network-mounts.sh
```

**Rationale:**
- `source_id: acma_codes_local` follows the `<collection>_<locality>` naming convention used by existing entries (e.g., `og_standards_local`, `ace_project_local`)
- `document_intelligence_bucket: acma_codes` creates a distinct bucket for provenance tracking
- `dedup_rule` explicitly states that overlapping API content should prefer the O&G standards source, consistent with the existing priority model
- `provenance_rule` marks this as a staging source, not a source of truth

### 2. Pipeline config entry

Add to `scripts/data/document-index/config.yaml` under `sources:`:

```yaml
  acma_codes:
    enabled: true
    paths:
      - /mnt/ace/acma-codes
    host: dev-primary
    source_type: acma_codes
    extensions: [.pdf, .docx, .xlsx, .pptx, .txt]
```

Add `acma_codes` to `deduplication.source_priority` list (lowest priority, after `workspace_spec` but before `api_metadata`):

```yaml
deduplication:
  source_priority:
    - og_standards
    - ace_standards
    - ace_conferences
    - ace_project
    - dde_project
    - va_hdd_2
    - workspace_spec
    - acma_codes        # NEW — lowest filesystem priority; staging area
    - api_metadata
```

**Rationale:**
- `acma_codes` gets lowest filesystem priority because it is a staging drop, not an organized standards library
- API documents that exist in both acma-codes and og_standards will keep the og_standards record as canonical, with acma-codes paths added as provenance aliases
- Extensions match the `ace_standards` pattern (PDF-primary with office doc support)

---

## Proposed Phase A Indexing Scope

### What Phase A does for acma-codes

1. **Recursive scan** of `/mnt/ace/acma-codes` via `phase-a-index.py --source acma_codes`
2. **SHA-256 hashing** of all non-excluded files to produce `doc_key` (content_hash) values
3. **Junk exclusion** via `exclude_patterns` in config.yaml
4. **Index record creation** -- one JSONL record per file with path, host, source, ext, size_mb, mtime, content_hash
5. **Provenance merge** -- `provenance.py` automatically merges records sharing the same content_hash with existing corpus, creating alias entries

### Expected index output

| Category | Expected count | Expected behavior |
|---|---|---|
| OCIMF PDFs | ~2 | New doc_keys (no existing records for OCIMF MEG 2008 or tandem mooring) |
| API PDFs | ~2 | Likely duplicate doc_keys of existing og_standards records; merged as provenance aliases |
| CSA PDFs | ~2 | New doc_keys (CSA entirely absent from corpus) |
| Non-PDF documents | 0-3 | Indexed if extension matches; classified separately |
| Junk artifacts | 0 (filtered) | Thumbs.db excluded by pattern match |

### Total expected new unique doc_keys: ~4-6

The API PDFs may or may not produce matching hashes depending on whether they are byte-identical to the copies in `/mnt/ace/0000 O&G/`. If different scans or editions, they will create new doc_keys linked via provenance as edition variants.

---

## Junk/Non-Document Exclusion Policy

### Existing exclusion patterns that already cover common junk

From `config.yaml`:
- `*/$RECYCLE.BIN/*`
- `*/.git/*`
- `*/__pycache__/*`
- `*/System Volume Information/*`
- `*.pyc`, `*.tmp`

### Additional exclusion needed for acma-codes

| Pattern | Target | Action |
|---|---|---|
| `Thumbs.db` | Windows thumbnail cache | Add to `exclude_patterns` if not already matched |
| `*.db` | SQLite/binary database files in non-standard locations | Evaluate case-by-case; Thumbs.db is always junk |
| `desktop.ini` | Windows folder metadata | Add to exclude patterns |

**Recommended additions to `config.yaml` `exclude_patterns`:**

```yaml
  - "Thumbs.db"
  - "desktop.ini"
  - "*.DS_Store"
```

**Rationale:** These are Windows/macOS system artifacts that appear in mounted directories. They have no document-intelligence value and should be globally excluded (benefits all sources, not just acma-codes).

### Non-PDF handling

If `.xlsx` or `.txt` files are found in `/mnt/ace/acma-codes`:
- They should be **indexed** (Phase A includes them via the extension filter)
- They should be **flagged for manual review** before Phase B summarization (spreadsheets may contain data tables, not narrative content)
- The `is_cad: false` flag applies; they receive normal SHA-256 hashing

---

## Initial Dedup Assessment Design

### Dedup method: Content-hash comparison

The existing `provenance.py` merge logic is the correct tool. It:
1. Groups all index records by `content_hash` (SHA-256)
2. Picks the primary record from the highest-priority source
3. Creates a `provenance` array with all known paths
4. Merges enrichment fields from secondary records

### Dedup execution plan

```
1. Run phase-a-index.py --source acma_codes
   - Scans /mnt/ace/acma-codes recursively
   - Computes SHA-256 for each file
   - Calls apply_provenance_to_pipeline() which automatically
     merges with existing index records by content_hash

2. After indexing, query the merged index:
   FOR EACH record WHERE source = "acma_codes":
     IF provenance array has entries from other sources:
       → DUPLICATE: this doc_key exists elsewhere
       → Report: which source has the primary copy
       → The acma-codes path becomes an alias
     ELSE:
       → NEW: this doc_key is unique to acma-codes
       → Report: new document for downstream processing

3. Generate dedup summary report:
   - Count of total files scanned
   - Count of excluded junk files
   - Count of duplicate doc_keys (alias of existing)
   - Count of new doc_keys (net-new to corpus)
   - Per-file: doc_key, primary source, alias sources, file path
```

### Expected dedup outcomes

| Document | Expected dedup result | Rationale |
|---|---|---|
| API RP 2SK (1996, 2nd Ed) | Possibly duplicate of `API-RP-2SK-2ND-ED` in og_standards | Same edition/year; hash comparison determines byte-identity |
| API RP 1111 (1999, 3rd Ed) | Possibly duplicate of `API-RP-1111` in og_standards | Multiple copies already tracked with doc_paths; hash determines match |
| OCIMF MEG 2008 | Likely NEW doc_key | 2008 edition (3rd Ed) is distinct from MEG4 (2018, 4th Ed) which exists only as wiki content, not as an indexed source document |
| OCIMF Tandem Mooring | Certainly NEW doc_key | No existing record in any registry |
| CSA Z276.1-20 | Certainly NEW doc_key | CSA entirely absent from ecosystem |
| CSA Z276.18 | Certainly NEW doc_key | CSA entirely absent from ecosystem |

### Dedup caveats

1. **Hash sensitivity**: Even the same standard title with different PDF scans will produce different hashes. Two copies of "API RP 2SK 2nd Ed" from different download sources may not be byte-identical.
2. **No fuzzy matching**: Phase A dedup is exact-hash-only. Title/metadata fuzzy matching (e.g., recognizing two different scans of the same standard) is a Phase B+ concern, not Phase A.
3. **Edition linking**: If API copies in acma-codes are different scans/editions, they become new doc_keys. Linking them as edition variants (via `superseded_by` or `absorbed_into`) is a ledger concern for downstream issue #2226, not this issue.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` |
| Plan review -- Claude | `scripts/review/results/2026-04-11-plan-2225-claude.md` |
| Plan review -- Final synthesis | `scripts/review/results/2026-04-11-plan-2225-final.md` |
| Mounted source registry (to modify) | `data/document-index/mounted-source-registry.yaml` |
| Pipeline config (to modify) | `scripts/data/document-index/config.yaml` |
| Corpus index (output) | `data/document-index/index.jsonl` |

---

## Deliverable

A registered `/mnt/ace/acma-codes` mounted source with Phase A indexing results in `index.jsonl` and an initial dedup assessment identifying which documents are net-new versus aliases of existing corpus content.

---

## Pseudocode / Indexing-Dedup Logic Sketch

This is planning-level pseudocode. No implementation code should be written in this run.

### Source registration (manual YAML edits)

```
1. Add acma_codes_local entry to mounted-source-registry.yaml
   - source_id, mount_root, dedup_rule as specified above

2. Add acma_codes source to config.yaml
   - paths: [/mnt/ace/acma-codes]
   - extensions: [.pdf, .docx, .xlsx, .pptx, .txt]

3. Add acma_codes to deduplication.source_priority
   - Position: after workspace_spec, before api_metadata

4. Add junk exclusion patterns to config.yaml
   - Thumbs.db, desktop.ini, .DS_Store
```

### Phase A indexing

```
5. Run: python phase-a-index.py --source acma_codes
   - Scanner walks /mnt/ace/acma-codes recursively
   - For each file matching extensions:
     - Skip if matches exclude_patterns
     - Compute SHA-256 hash -> content_hash
     - Create index record {path, host, source, ext, size_mb, mtime, content_hash}
   - apply_provenance_to_pipeline() merges with existing index:
     - If content_hash matches existing record -> add acma-codes path as alias
     - If content_hash is new -> create new canonical record
   - Write merged index.jsonl
```

### Dedup assessment (post-indexing query)

```
6. Query index.jsonl for records where source=acma_codes or provenance includes acma_codes
   - For each record:
     - Count provenance entries
     - If >1 provenance entry: mark as DUPLICATE, note primary source
     - If 1 provenance entry (acma_codes only): mark as NEW
   - Output summary:
     - Total scanned, excluded, duplicates, new
     - Per-document: doc_key, dedup_status, primary_source, file_path
```

---

## Files to Change (Planning Scope Only)

These are the files that will be modified during **future implementation**. This plan does NOT implement these changes.

| Action | Path | Reason |
|---|---|---|
| Modify | `data/document-index/mounted-source-registry.yaml` | Add `acma_codes_local` source entry |
| Modify | `scripts/data/document-index/config.yaml` | Add `acma_codes` source + junk exclusion patterns + priority entry |
| Run | `scripts/data/document-index/phase-a-index.py --source acma_codes` | Index new source |
| Output | `data/document-index/index.jsonl` | Will contain new/merged acma-codes records |
| Update | `docs/plans/README.md` | Add this plan to the index |

**NOT in scope for this issue** (delegated to downstream issues):
| Delegated to | What |
|---|---|
| #2226 | Add OCIMF and CSA to `standards-transfer-ledger.yaml`; provenance backfill with doc_key |
| #2227 | Promote OCIMF Tandem Mooring and CSA Z276 into LLM-wikis |
| #2228 | Update accessibility entry points and intelligence map |

---

## Verification List for Future Implementation

| Test | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_acma_source_registered | `mounted-source-registry.yaml` includes `acma_codes_local` | `mounted-source-registry.yaml` | Entry with `mount_root: /mnt/ace/acma-codes` and `source_id: acma_codes_local` |
| verify_config_has_acma_source | `config.yaml` has `acma_codes` source entry | `config.yaml` sources block | Entry with `paths: [/mnt/ace/acma-codes]` and `enabled: true` |
| verify_config_priority | `acma_codes` in dedup priority list at correct position | `config.yaml` dedup block | `acma_codes` present, after `workspace_spec`, before `api_metadata` |
| verify_junk_excluded | `Thumbs.db` is excluded from index | `index.jsonl` filtered by source=acma_codes | No records with path containing `Thumbs.db` |
| verify_index_includes_acma_pdfs | Phase A indexed PDF documents from acma-codes | `index.jsonl` filtered by source=acma_codes | Records for OCIMF, API, CSA PDFs |
| verify_api_dedup_or_new | API RP 1111/2SK either merge as aliases or register as new keys | `index.jsonl` provenance for matching content_hash | Either provenance array includes og_standards + acma_codes paths, or new doc_key with acma_codes-only provenance |
| verify_ocimf_new_dockeys | OCIMF PDFs produce unique doc_keys | `index.jsonl` for OCIMF files | New doc_keys not matching any existing records |
| verify_csa_new_dockeys | CSA PDFs produce unique doc_keys | `index.jsonl` for CSA files | New doc_keys not matching any existing records |
| verify_dedup_summary_produced | Implementation outputs a dedup assessment | Post-indexing analysis | Summary with counts: total, excluded, duplicate, new |
| verify_inventory_matches_plan | Actual file count matches or documents deviation from plan | Compare scan results to this plan's inventory | If materially different, document in implementation comment |

---

## Acceptance Criteria

- [ ] `mounted-source-registry.yaml` contains `acma_codes_local` entry with correct `mount_root`, `dedup_rule`, and `provenance_rule`
- [ ] `config.yaml` contains `acma_codes` source entry with correct paths, extensions, and host
- [ ] `config.yaml` dedup priority list includes `acma_codes` at lowest filesystem priority
- [ ] Junk exclusion patterns (`Thumbs.db`, `desktop.ini`, `.DS_Store`) are in `config.yaml`
- [ ] Phase A indexing completed: `index.jsonl` contains records from `source: acma_codes`
- [ ] All valid documents from `/mnt/ace/acma-codes` are indexed (Thumbs.db and system files excluded)
- [ ] Dedup assessment completed: each acma-codes doc_key is classified as DUPLICATE (alias) or NEW
- [ ] API RP 1111 and RP 2SK dedup status resolved (either confirmed as aliases of existing records or documented as distinct editions)
- [ ] OCIMF and CSA documents confirmed as new doc_keys
- [ ] Implementation summary comment posted on parent issue #2216
- [ ] Actual inventory verified against this plan's inherited inventory; deviations documented
- [ ] No changes made to standards-transfer-ledger, wikis, or accessibility map (those are downstream issues)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | MINOR | 3 findings: (1) inventory inherited not live-verified, (2) global exclude pattern scope exceeds strict #2225 boundary but is net-positive, (3) dedup output format not specified. 5 APPROVE findings: source priority, #2205/#2207 consistency, downstream handoff, retrieval adequacy. |

**Overall result:** PASS with minor caveats

Revisions made based on review:
- Confirmed inventory chain-of-inheritance is documented and acceptable
- Confirmed global exclude patterns are a net-positive collateral improvement
- Dedup output format left to implementer discretion (report in PR comment and/or issue comment)

---

## Risks and Open Questions

### Risks

1. **Sandbox access limitation** -- This plan's inventory is inherited from the approved parent plan #2216, which was itself limited by sandbox access. The implementer must verify the actual directory contents before executing. **Mitigation:** Verification requirement is explicit in the plan; deviations must be documented.

2. **Hash non-match for API copies** -- API RP 2SK 2nd Ed in acma-codes may be a different PDF scan than the copy in `/mnt/ace/0000 O&G/`, producing a different `doc_key` despite being the same standard edition. **Mitigation:** This is expected behavior per the #2207 provenance contract (different binary = different doc_key). Link via ledger provenance in downstream #2226.

3. **Unknown additional content** -- The inventory only covers known sample files. Additional folders, files, or standards families may exist. **Mitigation:** Phase A indexing will discover all files regardless; plan should be updated post-execution if materially more content exists.

4. **Mount unavailability** -- `/mnt/ace/acma-codes` may not be mounted at implementation time. **Mitigation:** `check-network-mounts.sh` readiness check; implementation should abort cleanly if mount is unavailable.

5. **Index corruption risk** -- Writing to the 1M-record `index.jsonl` could corrupt existing data if interrupted. **Mitigation:** The `--source acma_codes` flag limits scanning to the new source only; `provenance.py` uses atomic rename (`os.replace`) for safe writes.

### Open Questions

1. **Should `acma_codes` be a permanent source or eventually absorbed into `og_standards`?** -- The parent plan #2216 recommends registering as-is now and deciding on physical reorganization separately. This plan follows that recommendation.

2. **Are there more folders beyond OCIMF/, API/, CSA/?** -- Cannot verify from sandbox. Implementation must discover and document.

3. **Should the dedup assessment be a separate script or an inline query?** -- Recommend: implement as a post-indexing query script (or inline in the implementation PR) that reads `index.jsonl` and filters by source. Not a permanent tool unless the pattern recurs.

---

## Downstream Handoff to #2226

This plan explicitly defines the handoff boundary to downstream issue #2226 (standards-transfer-ledger + provenance backfill):

**What #2225 produces for #2226:**
- `acma_codes_local` registered in `mounted-source-registry.yaml`
- All acma-codes documents indexed in `index.jsonl` with `content_hash` (doc_key) values
- Dedup assessment identifying which doc_keys are new vs. aliases
- Verified inventory of actual directory contents

**What #2225 does NOT do (reserved for #2226):**
- Add OCIMF or CSA entries to `standards-transfer-ledger.yaml`
- Populate `doc_key` fields in existing ledger entries
- Link acma-codes API copies as ledger path aliases
- Any wiki, accessibility, or entry-point updates

---

## Complexity: T2

**T2** -- Multiple file modifications (registry YAML, config YAML, index output), pipeline execution (Phase A), and post-indexing analysis (dedup assessment). Not T1 (involves more than config changes) but not T3 (builds entirely on existing pipeline infrastructure with no architecture changes). Well-bounded scope with clear acceptance criteria.
