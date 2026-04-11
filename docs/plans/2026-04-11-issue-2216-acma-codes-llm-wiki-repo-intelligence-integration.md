# Plan for #2216: Integrate /mnt/ace/acma-codes into LLM-Wiki and Repo Intelligence Ecosystem

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2216-claude.md | scripts/review/results/2026-04-11-plan-2216-final.md

---

## Resource Intelligence Summary

### Existing repo code / artifacts relevant to this source collection

| Artifact | Path | Relevance |
|---|---|---|
| Mounted source registry | `data/document-index/mounted-source-registry.yaml` | `/mnt/ace/acma-codes` is NOT registered — gap |
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | API RP 2SK (done), API RP 1111 (done, multiple editions) already tracked; OCIMF and CSA are NOT in the ledger |
| Design code registry | `data/design-codes/code-registry.yaml` | Contains API-RP-1111 and API-RP-2A-WSD; no OCIMF or CSA entries |
| Corpus index | `data/document-index/index.jsonl` | 1,033,933 records across 8 sources; acma-codes not indexed |
| 7-phase pipeline | `scripts/data/document-index/phase-a-index.py` through `phase-g-*.py` | Existing indexing infrastructure for new source onboarding |
| Provenance dedup | `scripts/data/document-index/provenance.py` | Content-hash-based dedup — will identify API overlaps automatically |
| Cross-drive dedup report | `data/document-index/cross-drive-dedup-report.json` | Existing dedup analysis — should be consulted for overlap detection |
| Phase B summarization | `scripts/data/document-index/phase-b-extract.py` | Text extraction + LLM summary generation for new documents |

### Standards / registries consulted

| Standard/Registry | Status | Source |
|---|---|---|
| API RP 2SK (2nd Ed, 1996) | `done` in standards-transfer-ledger | `API-RP-2SK-2ND-ED`, domain: marine |
| API RP 1111 (multiple editions) | `done` in standards-transfer-ledger | `API-RP-1111`, `API-RP-1111-3RD-ED`, `API-RP-1111-DRAFT`, `API-RP-1111-ERRATA`; doc_paths in `/mnt/ace/0000 O&G/` |
| OCIMF Mooring Equipment Guidelines | NOT in transfer ledger | Only wiki coverage at `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` |
| OCIMF Tandem Mooring Guidelines | NOT in transfer ledger | No wiki or registry coverage |
| CSA Z276.1-20 (marine structures for LNG) | NOT in any registry | Entirely new to ecosystem |
| CSA Z276.18 (LNG production/storage) | NOT in any registry | Entirely new to ecosystem |
| Mounted source registry | `/mnt/ace/acma-codes` NOT registered | 8 sources registered; acma-codes is absent |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` — covers OCIMF MEG4 (4th Ed, 2018); cross-references DNV-OS-E301, API RP 2SK (4th Ed, 2024)
- `knowledge/wikis/engineering/wiki/concepts/mooring-line-failure-physics.md` — mooring failure physics
- `knowledge/wikis/engineering/wiki/entities/hmpe-mooring-failures.md` — HMPE failure investigations
- `knowledge/wikis/engineering/wiki/entities/mooring-analysis-system.md` — mooring analysis capabilities
- `knowledge/wikis/engineering/wiki/entities/prelude-flng-mooring.md` — FLNG mooring case study
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` — DNV position mooring standard
- `knowledge/seeds/mooring-failures-lng-terminals.yaml` — 40-entry mooring failures knowledge seed

### Documents consulted

- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` — #2205 parent operating model (pyramid, layers, flows)
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` — #2207 provenance contract (doc_key, reuse rules)
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` — #2209 boundary policy
- `docs/document-intelligence/intelligence-accessibility-map.md` — #2096 accessibility inventory
- `docs/assessments/document-intelligence-audit.md` — pipeline infrastructure audit (7-phase, 1M docs)
- `docs/document-intelligence/holistic-resource-intelligence.md` — #1575 resource intelligence plan
- `docs/plans/README.md` — plan index and workflow reference
- `data/document-index/shards/ace-shard-*.json` — existing shard data referencing OCIMF and API RP 2SK content

### Gaps identified

1. **No mounted source registration** — `/mnt/ace/acma-codes` is not in `mounted-source-registry.yaml`; the pipeline cannot discover it
2. **OCIMF not in transfer ledger** — OCIMF standards exist only as wiki content (ocimf-meg4.md), with no L2 provenance records
3. **CSA entirely absent** — CSA Z276 series not in any registry, ledger, wiki, or code-registry; completely undiscovered by the ecosystem
4. **OCIMF Tandem Mooring not in wiki** — only MEG4 has a wiki page; tandem mooring guidelines are untracked
5. **API RP 2SK edition mismatch** — transfer ledger tracks 2nd Ed (1996) matching acma-codes; wiki references 4th Ed (2024)
6. **No doc_key hashing** — acma-codes files have never been hashed; dedup against existing corpus is unverified
7. **Non-document artifacts present** — `Thumbs.db`, possibly `.xlsx` data files and `.txt` notes mixed with standards PDFs

---

## Real Inventory and Classification of `/mnt/ace/acma-codes`

### Known contents (from live inspection prior to this session)

**Sandbox limitation:** Direct filesystem access to `/mnt/ace/acma-codes` was denied by the Claude Code sandbox during this session. The inventory below is based on contents observed during pre-session live inspection and recorded in the planning prompt. This is a **known limitation** — the inventory should be verified by a human or an unrestricted agent before implementation.

| Top-level folder | Standards family | Known files | File types | Domain |
|---|---|---|---|---|
| `OCIMF/` | Oil Companies International Marine Forum | `OCIMF - 2008 - Mooring Equipment Guidelines.pdf`, `OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf` | PDF | marine / mooring |
| `API/` | American Petroleum Institute | `1996 Dec RP 2SK Stationkeeping Systems for Floating Structures 2nd ed.pdf`, `1999 July RP 1111 Offshore Hydrocarbon Pipelines 3rd ed.pdf` | PDF | marine / pipeline |
| `CSA/` | Canadian Standards Association | `276.1-20 marine structures associated with LNG facilities.pdf`, `Z276.18 LNG Production, storage, and handling.pdf` | PDF | marine / LNG |
| *(root or other)* | Mixed / unknown | Thumbs.db, possibly other `.xlsx`, `.txt` files | Mixed | n/a |

### Classification

**The collection is a mixed staging area** that requires separation before integration:

| Category | Description | Action required |
|---|---|---|
| **Raw standards (PDFs)** | Genuine standards documents from OCIMF, API, CSA | Register, hash, dedup, summarize, classify |
| **Duplicate standards** | API RP 1111 and RP 2SK likely duplicate content already at `/mnt/ace/0000 O&G/` | Dedup via `doc_key` (SHA-256); link as aliases if identical |
| **New standards families** | OCIMF (partially new), CSA (entirely new) | Full pipeline ingestion (Phase A through E) |
| **Non-document artifacts** | `Thumbs.db`, any `.xlsx`/`.txt` files | Filter out Thumbs.db; classify spreadsheets and text files separately |

### Source characterization

- **Not** a source-of-truth collection — this is a **staging drop** of standards assembled from unknown provenance
- **Not** a fully normalized corpus — folder names follow org conventions but file naming is inconsistent
- **Partially overlaps** with existing mounted sources (`og_standards_local` at `/mnt/ace/0000 O&G/`)
- **Contains genuinely new content** — CSA Z276 series and OCIMF tandem mooring guidelines are net-new to the ecosystem

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` |
| Plan review — Claude | `scripts/review/results/2026-04-11-plan-2216-claude.md` |
| Plan review — Final synthesis | `scripts/review/results/2026-04-11-plan-2216-final.md` |
| Mounted source registry (to update) | `data/document-index/mounted-source-registry.yaml` |
| Standards transfer ledger (to update) | `data/document-index/standards-transfer-ledger.yaml` |
| Code registry (to update) | `data/design-codes/code-registry.yaml` |
| Wiki pages (to create) | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md`, `knowledge/wikis/marine-engineering/wiki/standards/csa-z276*.md` |
| Intelligence accessibility map (to update) | `docs/document-intelligence/intelligence-accessibility-map.md` |

---

## Deliverable

A registered, deduplicated, and classified integration of `/mnt/ace/acma-codes` into the intelligence ecosystem, with new standards families (OCIMF tandem mooring, CSA Z276) tracked in the transfer ledger, indexed by the pipeline, and promoted into LLM-wikis where appropriate.

---

## Pseudocode / Integration Logic Sketch

This is planning-level pseudocode. No implementation code should be written in this run.

### Source registration
```
1. Add source_id "acma_codes_local" to mounted-source-registry.yaml
   - mount_root: /mnt/ace/acma-codes
   - document_intelligence_bucket: acma_codes
   - provenance_rule: staging area; dedup against og_standards first
   - dedup_rule: prefer /mnt/ace/0000 O&G for overlapping content

2. Run phase-a-index.py with new source root
   - Scans /mnt/ace/acma-codes recursively
   - Hashes all files (SHA-256 → doc_key)
   - Writes records to index.jsonl
   - Filters Thumbs.db and non-document artifacts
```

### Dedup pass
```
3. Run provenance.py merge against existing index
   - For each doc_key from acma-codes:
     - If doc_key exists in og_standards or ace_standards → link as alias
     - If doc_key is new → mark as new_source for pipeline processing
   - Expected results:
     - API RP 1111: likely alias of existing /mnt/ace/0000 O&G/.../API RP 1111 (1999).pdf
     - API RP 2SK: likely alias of existing record if same edition
     - OCIMF PDFs: likely new doc_keys (different editions from MEG4)
     - CSA PDFs: certainly new doc_keys (no existing records)
```

### Standards ledger update
```
4. Add new entries to standards-transfer-ledger.yaml:
   - OCIMF-MEG-2008 (Mooring Equipment Guidelines, 3rd Ed predecessor)
   - OCIMF-TANDEM-MOORING (Tandem Mooring and Offloading Guidelines)
   - CSA-Z276.1-20 (Marine structures for LNG facilities)
   - CSA-Z276.18 (LNG production, storage, and handling)
   - Verify API RP 2SK entry has acma-codes path as alias
   - Verify API RP 1111 entry has acma-codes path as alias
```

### Pipeline processing
```
5. Run Phase B (summarize) for new doc_keys only
6. Run Phase C (classify) → assign domains (marine, LNG, pipeline)
7. Run Phase E (registry) → update aggregate stats
```

### Wiki promotion
```
8. Evaluate promotion candidates:
   - OCIMF Tandem Mooring → new wiki page (sufficient for mooring domain)
   - CSA Z276.1-20 → new wiki page (LNG marine structures — new domain area)
   - CSA Z276.18 → new wiki page (LNG operations — new domain area)
   - OCIMF MEG 2008 → update existing ocimf-meg4.md with historical context
   - API RP 2SK / 1111 → no new wiki pages needed (already covered)
```

---

## Files to Change (Planning Scope)

These are the files that will be modified during **future implementation**. This plan does NOT implement these changes.

| Action | Path | Reason |
|---|---|---|
| Modify | `data/document-index/mounted-source-registry.yaml` | Add `acma_codes_local` source entry |
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add OCIMF and CSA entries; add alias paths for API entries |
| Modify | `data/design-codes/code-registry.yaml` | Add OCIMF and CSA code-family entries if warranted |
| Run | `scripts/data/document-index/phase-a-index.py` | Index new source |
| Run | `scripts/data/document-index/provenance.py` | Dedup against existing corpus |
| Run | `scripts/data/document-index/phase-b-extract.py` | Summarize new documents |
| Run | `scripts/data/document-index/phase-c-classify.py` | Classify new documents |
| Run | `scripts/data/document-index/phase-e-registry.py` | Update registry stats |
| Create | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | New wiki page for tandem mooring guidelines |
| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-1.md` | New wiki page for CSA Z276.1 (LNG marine structures) |
| Create | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-18.md` | New wiki page for CSA Z276.18 (LNG operations) |
| Modify | `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` | Add historical MEG3/2008 edition context and acma-codes source reference |
| Modify | `docs/document-intelligence/intelligence-accessibility-map.md` | Add acma-codes source to accessibility inventory |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## TDD / Verification List for Future Implementation

| Test | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_acma_source_registered | mounted-source-registry includes acma_codes_local | `mounted-source-registry.yaml` | Entry with mount_root `/mnt/ace/acma-codes` |
| verify_index_includes_acma | Phase A indexed acma-codes files | `index.jsonl` filtered by source=acma_codes | Records for OCIMF, API, CSA PDFs |
| verify_thumbsdb_excluded | Non-document artifacts filtered | `index.jsonl` filtered by source=acma_codes | No Thumbs.db records |
| verify_api_dedup | API RP 1111 and 2SK deduplicated against existing | `provenance.py` merge output | Existing doc_keys with new alias paths |
| verify_ocimf_new_dockeys | OCIMF PDFs have unique doc_keys | `index.jsonl` for OCIMF source | New doc_keys not matching existing records |
| verify_csa_new_dockeys | CSA PDFs have unique doc_keys | `index.jsonl` for CSA source | New doc_keys not matching existing records |
| verify_ledger_entries | OCIMF and CSA added to transfer ledger | `standards-transfer-ledger.yaml` | Entries for OCIMF-MEG-2008, OCIMF-TANDEM, CSA-Z276.1, CSA-Z276.18 |
| verify_summaries_generated | Phase B produced summaries for new doc_keys | `summaries/<doc_key>.json` | Non-empty summary files for each new document |
| verify_wiki_ocimf_tandem | Wiki page created for tandem mooring | `knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md` | Page with frontmatter including doc_key |
| verify_wiki_csa | Wiki pages created for CSA Z276 | `knowledge/wikis/marine-engineering/wiki/standards/csa-z276-*.md` | Pages with frontmatter including doc_key and domain |

---

## Acceptance Criteria

- [ ] `/mnt/ace/acma-codes` is registered as a mounted source in `mounted-source-registry.yaml`
- [ ] Phase A index includes all valid documents from `/mnt/ace/acma-codes` (Thumbs.db excluded)
- [ ] Dedup pass confirms API RP 1111 and RP 2SK are aliases of existing records (or documents them as distinct editions)
- [ ] OCIMF and CSA standards families are added to `standards-transfer-ledger.yaml`
- [ ] Phase B summaries exist for all new (non-duplicate) doc_keys
- [ ] Wiki pages created for: OCIMF Tandem Mooring, CSA Z276.1, CSA Z276.18
- [ ] Existing `ocimf-meg4.md` wiki page updated with historical edition context
- [ ] Intelligence accessibility map updated to include acma-codes source
- [ ] No regression in existing registries or pipeline outputs
- [ ] All new wiki pages include `doc_key` back-link in frontmatter per #2207 contract

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | MINOR | 3 findings: sandbox limitation on live inventory, edition-matching ambiguity for API RP 2SK, CSA domain assignment (marine vs LNG) needs clarification |

**Overall result:** PASS with minor caveats

Revisions made based on review:
- Added explicit sandbox limitation callout in inventory section
- Added edition-matching note for API RP 2SK (2nd vs 4th edition)
- Clarified CSA domain should be `marine` per existing taxonomy (LNG is not a separate domain; the closest is `marine`)
- Recommended follow-on issue split to manage scope

---

## Risks and Open Questions

### Risks

1. **Sandbox access limitation** — This plan's inventory is based on pre-session observation, not live filesystem traversal during planning. The full file listing and exact file count are unverified. **Mitigation:** Verify inventory during implementation with unrestricted access.

2. **Edition mismatch for API RP 2SK** — The acma-codes copy is "2nd ed (1996)". The transfer ledger tracks `API-RP-2SK-2ND-ED` as `done`. These may be the same file (same doc_key) or different scans. **Mitigation:** Hash comparison during dedup pass will resolve.

3. **Unknown additional content** — The inventory only covers known sample files. The actual `/mnt/ace/acma-codes` directory may contain additional folders or files (e.g., ABS, BV, Lloyd's, NORSOK standards). **Mitigation:** Phase A indexing will discover all files; plan should be updated if materially more content exists.

4. **OCIMF 2008 vs MEG4 (2018) relationship** — The acma-codes OCIMF MEG is 2008 edition (likely 3rd Ed). The wiki covers MEG4 (2018, 4th Ed). These are distinct editions, not duplicates. **Mitigation:** Link via `superseded_by` provenance rather than dedup.

5. **CSA Z276 domain assignment** — CSA Z276 covers LNG marine structures and operations. Current taxonomy has 12 domains but no dedicated `LNG` domain. **Mitigation:** Classify under `marine` domain; consider whether a future taxonomy expansion is warranted.

### Open Questions

1. **Should `/mnt/ace/acma-codes` remain a permanent mounted source or be absorbed into `/mnt/ace/0000 O&G/`?** — If the content is eventually moved into the org-structured O&G standards tree, the mounted source entry should be updated to reflect the new location. Recommend: register as-is now, decide on physical reorganization separately.

2. **Are there more folders beyond OCIMF/, API/, CSA/?** — The sandbox prevented full enumeration. If additional standards families exist (e.g., ABS, BV, IMO), the scope of follow-on work increases significantly.

3. **Should XLSX files be processed through the document intelligence pipeline?** — The pipeline is primarily PDF-oriented. Spreadsheet processing may require additional extraction logic. Recommend: index but defer deep extraction of non-PDF content.

4. **Should this issue remain one implementation issue or split?** — See recommendation below.

---

## Recommended Follow-On Issue Split

This issue should **split into 4 follow-on implementation issues** after plan approval:

| # | Follow-on title | Scope | Depends on |
|---|---|---|---|
| 1 | Register `/mnt/ace/acma-codes` as mounted source and run Phase A indexing | Source registration + initial indexing + dedup pass | Nothing (entry point) |
| 2 | Add OCIMF and CSA to standards-transfer-ledger with provenance backfill | Ledger entries + doc_key hashing + path alias linking for API overlaps | Follow-on #1 |
| 3 | Promote OCIMF Tandem Mooring and CSA Z276 into LLM-wikis | Wiki page creation + existing page updates + frontmatter back-links | Follow-on #2 |
| 4 | Update accessibility entry points and intelligence map | Accessibility map update + entry-point additions per #2096/#2104 | Follow-on #3 |

**Rationale for split:** Each follow-on has a clean dependency chain and can be independently planned, reviewed, and implemented. Combining them into one issue would create a T3-complexity implementation with mixed concerns (registry, pipeline, wiki, docs).

---

## Complexity: T2

**T2** — Multi-file planning with registry, pipeline, and wiki implications. Not trivially T1 (involves multiple registries and a dedup pass) but not architecture-level T3 (builds on existing pipeline infrastructure and established operating model). The follow-on implementation issues individually range from T1 (source registration) to T2 (wiki promotion).
