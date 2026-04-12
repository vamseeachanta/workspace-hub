# Plan for #2226: Backfill OCIMF/CSA Ledger Entries and Provenance Aliases from Indexed Source

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2226
> **Parent:** https://github.com/vamseeachanta/workspace-hub/issues/2216
> **Upstream:** https://github.com/vamseeachanta/workspace-hub/issues/2225 (source registration + indexing)
> **Review artifacts:** scripts/review/results/2026-04-11-plan-2226-claude.md | scripts/review/results/2026-04-11-plan-2226-final.md

---

## Resource Intelligence Summary

### Existing repo code / artifacts relevant to this issue

| Artifact | Path | Relevance |
|---|---|---|
| Standards transfer ledger | `data/document-index/standards-transfer-ledger.yaml` | 425 standards; API-RP-1111 (5 entries, `done`); API-RP-2SK-2ND-ED (1 entry, `done`, no doc_paths); **NO OCIMF entries; NO CSA entries** |
| Design code registry | `data/design-codes/code-registry.yaml` | Contains API-RP-1111 (5th Ed), API-RP-2A-WSD; **NO OCIMF, NO CSA, NO API-RP-2SK entries** |
| Corpus index | `data/document-index/index.jsonl` | 2,521 acma_codes records now indexed (from completed #2225); OCIMF across 3 folders (182 records), CSA in 1 folder (10 records), API in 1 folder (53 records) |
| Provenance merger | `scripts/data/document-index/provenance.py` | Content-hash-based dedup; merges by `content_hash` into single records with provenance arrays |
| Provenance contract | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Defines `doc_key` = SHA-256 of file content; alias rules; edition/supersession treatment; required provenance fields |
| Parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Pyramid model; L2 owns provenance; L3 wiki inherits from L2 |
| Parent plan #2216 | `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` | Approved integration plan; recommended 4-way follow-on split; this issue is follow-on #2 |
| Upstream plan #2225 | `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` | Source registration and Phase A indexing; defines handoff boundary to this issue |
| Mounted source registry | `data/document-index/mounted-source-registry.yaml` | `acma_codes_local` now registered (from #2225) |

### Standards / registries consulted

| Standard/Registry | Ledger Status | Findings |
|---|---|---|
| API RP 1111 (multiple editions) | `done` (5 entries) | `doc_paths` populated from `/mnt/ace/0000 O&G/`; acma-codes has `1999 July RP 1111` with `doc_key: 23be68a8...` which is a different hash from existing records |
| API RP 2SK (2nd Ed, 1996) | `done` (1 entry: `API-RP-2SK-2ND-ED`) | **No `doc_paths` populated**; acma-codes has 2nd ed (`doc_key: dd7838f9...`), 3rd ed 2005 (`doc_key: 8117eb28...`), 3rd ed alt scan (`doc_key: d4062ff1...`), and 2008 addendum (`doc_key: 63ce67c3...`) |
| OCIMF MEG (any edition) | **NOT in ledger** | acma-codes has MEG 2008 (3rd Ed) at 2 paths with different doc_keys: `51de0e48...` (OCIMF/) and `58d0e4a9...` (OCIMF 3rd ed/); MEG4 (4th Ed, 2018) indexed at `b2627091...` |
| OCIMF Tandem Mooring | **NOT in ledger** | acma-codes has `OCIMF-Tandem Mooring...FPSO.pdf` with `doc_key: 5e5f61e7...`; entirely new |
| OCIMF OVID/OVPQ | **NOT in ledger** | acma-codes has `OCIMF OVID OVPQ-Master-Full.pdf` (`doc_key: 9ed18d9c...`) and `OVID_operator_application_ovpq.pdf` (`doc_key: 41e3d972...`); inspection/vetting documents, not standards |
| OCIMF MEG4 justification | **NOT in ledger** | `Mooring Equipment Guidelines (MEG4) justification.pdf` (`doc_key: 4d716398...`); supporting document |
| OCIMF Coefficient data | N/A | `OCIMF Coef.xlsx` (`doc_key: bb80d89d...`) and digitized figure PDFs (A5-A19); data artifacts, not standards |
| CSA Z276.1-20 | **NOT in any registry** | Marine structures for LNG facilities; `doc_key: b576ada3...` |
| CSA Z276.2-19 | **NOT in any registry** | Near-shoreline FLNG facilities; `doc_key: ea0777be...`; **not identified in parent #2216 plan** |
| CSA Z276.18 | **NOT in any registry** | LNG production/storage/handling; `doc_key: 3aa1fdc3...` |
| CSA B625-13 | **NOT in any registry** | Portable tanks for transport of dangerous goods; `doc_key: 4ab7bec3...`; **not identified in parent #2216 plan** |
| CSA 22.1-12 | **NOT in any registry** | Canadian Electrical Code; `doc_key: bcf8f523...`; **not identified in parent #2216 plan** |

### LLM Wiki pages consulted

- `knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md` -- covers OCIMF MEG4 (4th Ed, 2018); distinct from acma-codes MEG 2008 (3rd Ed predecessor)
- `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` -- DNV position mooring; cross-references API RP 2SK (4th Ed, 2024)

### Documents consulted

- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` -- #2207 provenance contract defining `doc_key`, alias rules, edition treatment
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` -- #2205 parent operating model
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md` -- parent plan with inventory classification
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md` -- upstream plan defining handoff boundary
- GitHub issue #2226 -- scope, acceptance criteria, deliverables
- GitHub issue #2216 -- parent umbrella; approved follow-on split

### Gaps identified

1. **OCIMF not in transfer ledger** -- No OCIMF entries exist despite 182+ indexed records across 3 edition folders
2. **CSA not in any registry** -- 5 distinct CSA standards discovered (3 more than the parent plan identified)
3. **API RP 2SK ledger entry has no `doc_paths`** -- Cannot verify dedup without adding acma-codes paths
4. **No `doc_key` fields in ledger** -- Ledger identifies standards by human-readable `id` only; #2207 contract recommends `doc_key` but field does not exist yet
5. **Hash format inconsistency** -- Existing non-acma sources use 32-character truncated hashes; acma_codes uses proper 64-character SHA-256; direct hash comparison for dedup WILL FAIL across sources
6. **OCIMF MEG 2008 exists as 2 different scans** -- `OCIMF/` and `OCIMF 3rd ed/` folders contain the same-named file with different doc_keys (different binary content)
7. **OCIMF supporting documents (OVID, coefficient data) need classification** -- Not standards per se, but related materials

<!-- Verification: 10+ distinct sources consulted across all sub-sections. Count: 12+ -->

---

## Real Indexed Findings from `acma_codes`

This section provides evidence-grounded analysis of the indexed records from the completed #2225 work.

### OCIMF Documents (182 records across 3 folders)

#### Standards-grade documents (ledger candidates)

| File | Folder | doc_key (SHA-256) | Size | Classification |
|---|---|---|---|---|
| OCIMF - 2008 - Mooring Equipment Guidelines.pdf | `OCIMF/` | `51de0e48fa14366a...` | PDF | **MEG 3rd Ed (2008)** -- historical predecessor of MEG4 |
| OCIMF - 2008 - Mooring Equipment Guidelines.pdf | `OCIMF 3rd ed/` | `58d0e4a955b70f45...` | PDF | **MEG 3rd Ed (2008) -- different scan** from `OCIMF/` copy |
| OCIMF - 2008 - Mooring Equipment Guidelines, CDs.pdf | `OCIMF/` and `OCIMF 3rd ed/` | `51faabf33fcec378...` | PDF | MEG 3rd Ed companion CDs document |
| OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf | `OCIMF/` | `5e5f61e785295f0a...` | PDF | **Net-new OCIMF guideline** -- not in any registry |
| Mooring Equipment Guidelines - MEG4.pdf | `OCIMF (MEG 4)/` | `b2627091310d4573...` | PDF | **MEG 4th Ed (2018)** -- matches wiki page edition |
| Mooring Equipment Guidelines (MEG4) justification.pdf | `OCIMF/` | `4d716398100129a9...` | PDF | Supporting justification document for MEG4 transition |

#### Inspection/operational documents (NOT ledger candidates)

| File | doc_key | Reason for exclusion |
|---|---|---|
| OCIMF OVID OVPQ-Master-Full.pdf | `9ed18d9cb21b661f...` | Vessel inspection questionnaire, not a standard |
| OVID_operator_application_ovpq.pdf | `41e3d9720f051c9c...` | OVID operator application form |
| Box Code.txt | `bb8a9c6c23a512ca...` | Metadata text file (0 MB) |

#### Data artifacts (NOT ledger candidates, but valuable for engineering)

| Item | doc_key | Description |
|---|---|---|
| OCIMF Coef.xlsx | `bb80d89d044cb49d...` | Coefficient spreadsheet (same file in `OCIMF/` and `OCIMF 3rd ed/`) |
| Figures A5-A19 PDFs | Various (10 unique doc_keys) | Digitized drag/wind coefficient figures from MEG 3rd Ed appendix |
| LNGC Coeficients.pdf/xlsx | In `OCIMF 3rd ed/old & other/` | LNG carrier coefficient data |
| OCIMF MEG4 Appendix A figures | In `OCIMF (MEG 4)/` | MEG4 edition coefficient figures (~9 PDFs) |
| OCIMF MEG4 MSMP pages | In `OCIMF (MEG 4)/` | Individual pages from MEG4 MSMP section (~12 PDFs) |

### CSA Documents (10 records, 5 unique standards)

| File | doc_key (SHA-256) | Domain | Classification |
|---|---|---|---|
| 276.1-20 marine structures associated with LNG facilities.pdf | `b576ada30e9ccea7...` | marine / LNG | **Net-new; marine structural standard for LNG** |
| 276.2-19 near-shoreline FLNG facilities.pdf | `ea0777be24937a34...` | marine / LNG | **Net-new; FLNG siting standard** -- not in parent #2216 plan |
| Z276.18 LNG Production, storage, and handling.pdf | `3aa1fdc3e2c73e1f...` | marine / LNG operations | **Net-new; LNG operations standard** |
| B625-13 Portable tanks for the transport of dangerous goods.pdf | `4ab7bec3ce7c4311...` | transport / hazmat | **Net-new; dangerous goods transport** -- not in parent plan |
| CSA 22.1-12.pdf | `bcf8f523ebb4445d...` | electrical | **Net-new; Canadian Electrical Code** -- not in parent plan |

### API Overlap Analysis (53 records)

The acma-codes API folder contains 28+ unique standards, far more than the 2 (RP 1111, RP 2SK) identified in the parent plan. Key overlaps with the existing ledger:

| acma-codes File | acma doc_key | Existing Ledger Entry | Existing Hash Format | Dedup Status |
|---|---|---|---|---|
| 1999 July RP 1111...3rd ed.pdf | `23be68a89a071831...` (64-char) | `API-RP-1111-3RD-ED` has no doc_paths, no doc_key | N/A | **Cannot hash-compare; same edition** -- should be alias |
| 1996 Dec RP 2SK...2nd ed.pdf | `dd7838f9f26ce212...` (64-char) | `API-RP-2SK-2ND-ED` has no doc_paths, no doc_key | N/A | **Cannot hash-compare; same edition** -- should be alias |
| 2005 Oct RP 2SK.pdf | `8117eb28e9c6f9af...` (64-char) | No 3rd Ed entry in ledger | N/A | **New edition; not tracked** |
| API 2SK 3rd edition.pdf | `d4062ff1a8df959d...` (64-char) | No 3rd Ed entry in ledger | N/A | **Different scan of 3rd Ed** |
| RP 2SK_Addendum 2008.pdf | `63ce67c3267a7d04...` (64-char) | No addendum entry | N/A | **New; addendum not tracked** |

**Critical finding:** Direct hash-comparison dedup between acma_codes and earlier sources is impossible because:
1. Earlier sources use 32-character truncated hashes (likely MD5 or SHA-256 first 16 bytes)
2. acma_codes uses proper 64-character SHA-256 hashes
3. The ledger entries for API RP 1111 and 2SK have no `doc_key` fields at all

**Implication:** Alias linkage in this issue must be based on **metadata matching** (standard ID + edition + year), not content-hash comparison. The #2207 provenance contract's `doc_key` comparison model cannot be fully applied until the hash format inconsistency is resolved (tracked by #2207 Section 10 open question #1).

---

## Candidate Ledger Entries / Updates

### New OCIMF Entries

| Proposed ID | Title | org | domain | doc_paths (from acma-codes) | status | notes |
|---|---|---|---|---|---|---|
| `OCIMF-MEG-3RD-ED-2008` | OCIMF Mooring Equipment Guidelines (3rd Ed, 2008) | OCIMF | marine | `OCIMF/OCIMF - 2008 - Mooring Equipment Guidelines.pdf`, `OCIMF 3rd ed/OCIMF - 2008 - Mooring Equipment Guidelines.pdf` | done | Historical predecessor of MEG4; 2 different scans (different doc_keys) |
| `OCIMF-MEG-3RD-ED-CDS` | OCIMF Mooring Equipment Guidelines CDs Companion (2008) | OCIMF | marine | `OCIMF/OCIMF - 2008 - Mooring Equipment Guidelines, CDs.pdf` | done | Companion to MEG 3rd Ed |
| `OCIMF-MEG4-2018` | OCIMF Mooring Equipment Guidelines (4th Ed, 2018) | OCIMF | marine | `OCIMF (MEG 4)/Mooring Equipment Guidelines - MEG4.pdf` | done | Current edition; has existing wiki page at `ocimf-meg4.md` |
| `OCIMF-TANDEM-MOORING` | OCIMF Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities | OCIMF | marine | `OCIMF/OCIMF-Tandem Mooring...FPSO Facilities.pdf` | done | Net-new guideline; no prior coverage |

### New CSA Entries

| Proposed ID | Title | org | domain | doc_paths | status | notes |
|---|---|---|---|---|---|---|
| `CSA-Z276.1-20` | CSA Z276.1-20 Marine Structures Associated with LNG Facilities | CSA | marine | `CSA/276.1-20 marine structures associated with LNG facilities.pdf` | done | Net-new; LNG marine structures |
| `CSA-Z276.2-19` | CSA Z276.2-19 Near-Shoreline FLNG Facilities | CSA | marine | `CSA/276.2-19 near-shoreline FLNG facilities.pdf` | done | Net-new; not in parent plan |
| `CSA-Z276.18` | CSA Z276.18 LNG Production, Storage, and Handling | CSA | marine | `CSA/Z276.18 LNG Production, storage, and handling.pdf` | done | Net-new; LNG operations |
| `CSA-B625-13` | CSA B625-13 Portable Tanks for Transport of Dangerous Goods | CSA | transport | `CSA/B625-13 Portable tanks for the transport of dangerous goods.pdf` | done | Net-new; not in parent plan |
| `CSA-22.1-12` | CSA C22.1-12 Canadian Electrical Code | CSA | electrical | `CSA/CSA 22.1-12.pdf` | done | Net-new; not in parent plan; domain: electrical, not marine |

### Existing API Entries to Update (alias paths only)

| Existing ID | Update | acma-codes path to add as alias |
|---|---|---|
| `API-RP-1111-3RD-ED` | Add acma-codes path to `doc_paths` | `/mnt/ace/acma-codes/API/1999 July RP 1111 Offshore Hydrocarbon Pipelines 3rd ed.pdf` |
| `API-RP-2SK-2ND-ED` | Add acma-codes path to `doc_paths` | `/mnt/ace/acma-codes/API/1996 Dec RP 2SK Stationkeeping Systems for Floating Structures 2nd ed.pdf` |

### New API Entries (editions not currently in ledger)

| Proposed ID | Title | acma-codes paths | notes |
|---|---|---|---|
| `API-RP-2SK-3RD-ED` | API RP 2SK Design and Analysis of Stationkeeping Systems (3rd Ed, 2005) | `API/2005 RP 2SK with 2008 Add/2005 Oct RP 2SK.pdf`, `API/2005 RP 2SK with 2008 Add/API 2SK 3rd edition.pdf` | New edition; 2 different PDF copies (different doc_keys confirm different scans) |
| `API-RP-2SK-3RD-ED-ADDENDUM` | API RP 2SK 3rd Ed Addendum (2008) | `API/2005 RP 2SK with 2008 Add/RP 2SK_Addendum 2008.pdf` | Addendum to 3rd Ed |

**Scope note:** The remaining ~25 API standards in acma-codes (RP 14J, RP 505, RP 500, 7K, BULL 2U, RP 2C, RP 2D, RP 2H, RP 2A-WSD, RP 14C, RP 14F, RP 14G, RP 54, RP 75, RP 95J, 4F, catalogues, INT-MET) are out of scope for this issue. They should be addressed in a separate follow-on issue that systematically resolves all API overlaps.

---

## Alias vs New-Entry Treatment for API Overlaps

### Decision framework

Per the #2207 provenance contract (Section 3.4):

| Scenario | Treatment | Rationale |
|---|---|---|
| Same standard, same edition, same binary content | **Alias** -- add path to existing entry's `doc_paths` | Same doc_key confirms byte-identical copy |
| Same standard, same edition, different binary content | **Alias with note** -- add path to existing entry's `doc_paths`; note different scan in `notes` | Different scan of same edition is still the same standard |
| Different edition of same standard | **New entry** -- create separate ledger entry with edition suffix | Different edition = different content = different identity |
| Addendum or errata | **New entry** -- create separate ledger entry with addendum/errata suffix | Addendums are distinct published documents |

### Application to this issue

| acma-codes document | Treatment | Reasoning |
|---|---|---|
| API RP 1111 (1999, 3rd Ed) | **Alias** of `API-RP-1111-3RD-ED` | Same edition identified by title; cannot hash-verify but metadata match is sufficient |
| API RP 2SK (1996, 2nd Ed) | **Alias** of `API-RP-2SK-2ND-ED` | Same edition identified by title; add as first `doc_paths` entry (currently empty) |
| API RP 2SK (2005, 3rd Ed) -- both scans | **New entries** (`API-RP-2SK-3RD-ED`) | 3rd Edition not tracked in ledger; two different scans = two doc_paths on one entry |
| API RP 2SK Addendum (2008) | **New entry** (`API-RP-2SK-3RD-ED-ADDENDUM`) | Published addendum is a distinct document |

### Why metadata matching instead of hash comparison

The ideal approach per #2207 would be to compare `doc_key` (SHA-256) values directly. This is not possible because:
1. The existing ledger entries have no `doc_key` field
2. Earlier indexed sources use 32-character truncated hashes, not 64-character SHA-256
3. Adding `doc_key` to all ledger entries requires a separate back-population task (#2207 Section 9.4)

**For this issue:** Use metadata matching (standard ID + edition year + edition number) to establish alias relationships. This is reliable for the specific API standards in scope because edition identification is unambiguous from filenames.

**For future issues:** The hash format inconsistency should be resolved before attempting automated alias detection across sources.

---

## Provenance / doc_key Linkage Expectations

### Consistent with #2207 contract

1. **Every new ledger entry** should include `doc_paths` populated from real indexed paths
2. **`doc_key` field** is NOT added to ledger entries in this issue (the field does not exist in the current schema; adding it is a schema change scoped to #2207 Section 9.4)
3. **Provenance array** in `index.jsonl` already tracks multi-source paths via `provenance.py` merge; this issue does not modify `index.jsonl`
4. **Alias paths** added to existing entries' `doc_paths` arrays preserve the existing ledger structure

### What this issue does for doc_key traceability

| Action | How it supports doc_key model |
|---|---|
| Populate `doc_paths` on new entries | Creates path-based traceability from ledger to indexed records |
| Populate `doc_paths` on `API-RP-2SK-2ND-ED` (currently empty) | Closes a provenance gap |
| Document doc_keys in plan notes | Records SHA-256 values for future `doc_key` back-population |
| **Does NOT add** `doc_key` field to YAML schema | Schema change deferred per #2207 implementation plan |

### How doc_key can be threaded in future

When #2207 implementation adds `doc_key` to ledger schema:
- New entries from this issue can be back-populated from `index.jsonl` by matching paths
- Entries with multiple scans (e.g., OCIMF MEG 2008 with 2 doc_keys) should pick the highest-priority-source scan as canonical doc_key and record the other as `alternate_doc_keys`
- This is explicitly out of scope for #2226

---

## Whether Design-Code Registry Updates Are In Scope

### Analysis

The `code-registry.yaml` tracks **design codes actively used in digitalmodel/doris repos** with edition currency. Currently contains 8 entries: DNV-ST-F101, DNV-RP-C203, DNV-RP-C205, DNV-RP-F105, API-RP-2A-WSD, API-RP-2RD, API-RP-1111, BS-7910, ASME-B31.4, ISO-13628-7.

| Candidate | Should it go in code-registry? | Reasoning |
|---|---|---|
| OCIMF MEG4 | **Deferred** | MEG4 provides mooring design guidelines used in analysis, but there is no current `digitalmodel` or `doris` module that directly implements MEG4 calculations. May be warranted after wiki promotion (#2227) if code modules are created. |
| OCIMF MEG 2008 | **No** | Historical predecessor; not actively used for design. |
| OCIMF Tandem Mooring | **No** | Operational guideline, not a design code. |
| CSA Z276.1-20 | **No** | LNG facility standard; no active design code implementation. |
| CSA Z276.2-19 | **No** | FLNG siting standard; no active design code implementation. |
| CSA Z276.18 | **No** | LNG operations standard; not a design code. |
| CSA B625-13 | **No** | Transport standard; not a design code. |
| CSA 22.1-12 | **No** | Electrical code; no active design code implementation. |
| API RP 2SK | **Maybe** | API RP 2SK is actively used in mooring analysis. However, the registered edition in acma-codes (2nd/3rd Ed) does not match the current edition (likely 4th Ed, 2024, per wiki). Adding it requires confirming which edition is actively used. **Deferred** to a separate review. |

**Decision:** No code-registry changes in this issue. OCIMF MEG4 and API RP 2SK are the strongest candidates but both require additional context (active module usage, current edition) that is outside this issue's scope.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-11-issue-2226-ocimf-csa-ledger-provenance-backfill.md` |
| Plan review -- Claude | `scripts/review/results/2026-04-11-plan-2226-claude.md` |
| Plan review -- Final synthesis | `scripts/review/results/2026-04-11-plan-2226-final.md` |
| Standards transfer ledger (to modify) | `data/document-index/standards-transfer-ledger.yaml` |
| Design code registry (NOT modified) | `data/design-codes/code-registry.yaml` |

---

## Deliverable

New OCIMF and CSA entries in `standards-transfer-ledger.yaml` with provenance-linked `doc_paths` from indexed acma-codes records, plus alias path updates for overlapping API RP 1111 and RP 2SK entries, with documented alias/edition treatment rationale.

---

## Pseudocode / Ledger-Backfill Logic Sketch

This is planning-level pseudocode. No implementation code should be written in this run.

### Ledger backfill (YAML edits)

```
1. Add 4 new OCIMF entries to standards-transfer-ledger.yaml:
   FOR EACH [OCIMF-MEG-3RD-ED-2008, OCIMF-MEG-3RD-ED-CDS, OCIMF-MEG4-2018, OCIMF-TANDEM-MOORING]:
     - id: <proposed_id>
     - title: <full_title>
     - org: OCIMF
     - domain: marine
     - doc_path: <primary acma-codes path>
     - doc_paths: [<all acma-codes paths for this standard>]
     - status: done
     - notes: <edition info, cross-references, scan differences>
     - exhausted: false
     - absorbed_into: []

2. Add 5 new CSA entries:
   FOR EACH [CSA-Z276.1-20, CSA-Z276.2-19, CSA-Z276.18, CSA-B625-13, CSA-22.1-12]:
     - org: CSA
     - domain: marine (for Z276 series), transport (B625-13), electrical (22.1-12)
     - Follow same field pattern as OCIMF entries

3. Update existing API RP 1111 entry:
   - Find API-RP-1111-3RD-ED entry
   - Append acma-codes path to doc_paths array

4. Update existing API RP 2SK entry:
   - Find API-RP-2SK-2ND-ED entry
   - Set doc_path to acma-codes path (currently empty)
   - Set doc_paths to [acma-codes path]

5. Add 2 new API RP 2SK edition entries:
   - API-RP-2SK-3RD-ED with both scan paths
   - API-RP-2SK-3RD-ED-ADDENDUM with addendum path

6. Update ledger header:
   - Increment total count by 11 (4 OCIMF + 5 CSA + 2 API 2SK)
   - Update done count accordingly
```

### Validation pass

```
7. After edits, verify:
   - No duplicate IDs introduced
   - All doc_paths point to real indexed paths in index.jsonl
   - All org values match existing taxonomy (API, OCIMF, CSA are new orgs)
   - All domain values match existing taxonomy
   - Ledger YAML is valid and parseable
   - Total/done counts are correct
```

---

## Files to Change (Planning Scope Only)

These are the files that will be modified during **future implementation**. This plan does NOT implement these changes.

| Action | Path | Reason |
|---|---|---|
| Modify | `data/document-index/standards-transfer-ledger.yaml` | Add 11 new entries (4 OCIMF + 5 CSA + 2 API RP 2SK editions); update 2 existing entries (API-RP-1111-3RD-ED, API-RP-2SK-2ND-ED) with alias paths; update header counts |
| NOT modified | `data/design-codes/code-registry.yaml` | Deferred -- no active design code modules for OCIMF/CSA |
| NOT modified | `data/document-index/index.jsonl` | Already contains acma_codes records from #2225; this issue does not reindex |
| NOT modified | `knowledge/wikis/**` | Wiki promotion is #2227 scope |
| Update | `docs/plans/README.md` | Add this plan to the index |

---

## Verification List for Future Implementation

| Test | What it verifies | Expected input | Expected output |
|---|---|---|---|
| verify_ocimf_entries_exist | 4 OCIMF entries in ledger | `standards-transfer-ledger.yaml` | Entries for OCIMF-MEG-3RD-ED-2008, OCIMF-MEG-3RD-ED-CDS, OCIMF-MEG4-2018, OCIMF-TANDEM-MOORING |
| verify_csa_entries_exist | 5 CSA entries in ledger | `standards-transfer-ledger.yaml` | Entries for CSA-Z276.1-20, CSA-Z276.2-19, CSA-Z276.18, CSA-B625-13, CSA-22.1-12 |
| verify_api_2sk_3rd_entries | 2 new API RP 2SK entries | `standards-transfer-ledger.yaml` | Entries for API-RP-2SK-3RD-ED, API-RP-2SK-3RD-ED-ADDENDUM |
| verify_api_1111_alias | acma-codes path added to API-RP-1111-3RD-ED | `standards-transfer-ledger.yaml` | `doc_paths` includes `/mnt/ace/acma-codes/API/1999 July RP 1111...` |
| verify_api_2sk_alias | acma-codes path added to API-RP-2SK-2ND-ED | `standards-transfer-ledger.yaml` | `doc_paths` includes `/mnt/ace/acma-codes/API/1996 Dec RP 2SK...` |
| verify_no_duplicate_ids | No duplicate ledger IDs | `standards-transfer-ledger.yaml` | All `id` values are unique |
| verify_doc_paths_indexed | All new doc_paths exist in index.jsonl | Cross-check ledger doc_paths against index | Every path in a ledger entry has a matching index record |
| verify_header_counts | Total and done counts updated | `standards-transfer-ledger.yaml` header | total: 436, done: 435 |
| verify_domain_taxonomy | Domain values follow existing taxonomy | Ledger entries | marine, transport, electrical, pipeline (existing domains) |
| verify_yaml_valid | Ledger YAML parses without errors | `standards-transfer-ledger.yaml` | No YAML parse errors |
| verify_no_ledger_conflicts | New entries don't conflict with existing | Ledger entries | No conflicting claims about same standard |

---

## Acceptance Criteria

- [ ] 4 OCIMF entries added to `standards-transfer-ledger.yaml` (MEG 3rd Ed, MEG CDs, MEG4, Tandem Mooring)
- [ ] 5 CSA entries added to `standards-transfer-ledger.yaml` (Z276.1-20, Z276.2-19, Z276.18, B625-13, 22.1-12)
- [ ] 2 new API RP 2SK edition entries added (3rd Ed, 3rd Ed Addendum)
- [ ] `API-RP-1111-3RD-ED` `doc_paths` updated with acma-codes alias path
- [ ] `API-RP-2SK-2ND-ED` `doc_paths` populated with acma-codes path (closing empty-paths gap)
- [ ] All `doc_paths` in new/updated entries correspond to real indexed records in `index.jsonl`
- [ ] Entries include provenance notes consistent with #2207 contract (edition, scan variation, supersession where applicable)
- [ ] Overlapping API documents are handled as aliases (same edition) or distinct entries (different edition) with documented rationale
- [ ] No duplicate or conflicting ledger truth is introduced
- [ ] Ledger header `total` and `done` counts updated correctly
- [ ] YAML remains valid and parseable
- [ ] Findings reported back to #2216 parent issue
- [ ] `code-registry.yaml` is NOT modified (deferred with documented rationale)

---

## Downstream Handoff to #2227 (Wiki Promotion)

This issue produces the following for downstream #2227:

| What #2226 produces | How #2227 uses it |
|---|---|
| OCIMF-MEG-3RD-ED-2008 ledger entry with doc_paths | Source for wiki page on MEG3 historical context |
| OCIMF-MEG4-2018 ledger entry with doc_paths | Source for updating existing `ocimf-meg4.md` wiki with provenance back-link |
| OCIMF-TANDEM-MOORING ledger entry with doc_paths | Source for new wiki page `ocimf-tandem-mooring.md` |
| CSA-Z276.1-20, Z276.2-19, Z276.18 ledger entries | Source for new wiki pages in `marine-engineering/wiki/standards/` |
| Documented alias/edition treatment | Ensures wiki pages reference correct edition identity |

**What #2226 does NOT do (reserved for #2227):**
- Create or modify any wiki pages
- Update `ocimf-meg4.md` with cross-references
- Create new CSA wiki pages
- Add `doc_key` back-links to wiki frontmatter

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (self-review) | MINOR | See `scripts/review/results/2026-04-11-plan-2226-claude.md` for full review |

**Overall result:** PASS with minor caveats

Revisions made based on review:
- Confirmed metadata matching workaround is already documented as temporary in Risks section
- Ledger `notes` fields should reference indexed records rather than enumerating data artifacts
- No structural plan changes required; all 3 minor findings are informational or already addressed

---

## Risks and Open Questions

### Risks

1. **Hash format inconsistency blocks hash-based dedup** -- Existing sources use 32-char hashes; acma_codes uses 64-char SHA-256. This means the #2207 provenance contract's preferred `doc_key` comparison model cannot be used for cross-source alias detection until hash formats are normalized. **Mitigation:** Use metadata matching (title, edition, year) for alias determination in this issue; document the hash inconsistency as an input to #2207 implementation.

2. **OCIMF MEG 2008 has 2 different scans** -- The `OCIMF/` and `OCIMF 3rd ed/` copies of the same-named file have different doc_keys (`51de0e48...` vs `58d0e4a9...`). Per #2207 Section 3.4, different binary = different doc_key. **Mitigation:** Create one ledger entry (`OCIMF-MEG-3RD-ED-2008`) with both paths in `doc_paths` and note the scan difference. When `doc_key` is added to ledger schema, pick the canonical scan.

3. **CSA scope larger than parent plan anticipated** -- 5 CSA standards instead of 2. Three additional standards (Z276.2-19, B625-13, 22.1-12) are outside the marine/LNG domain. **Mitigation:** Include all 5 with accurate domain classification (marine, transport, electrical). The ledger is a comprehensive registry, not domain-limited.

4. **Many more API standards need alias resolution** -- 25+ API standards in acma_codes beyond RP 1111 and RP 2SK are unresolved. **Mitigation:** Explicitly scope this issue to only RP 1111 and RP 2SK; recommend follow-on issue for remaining API aliases.

5. **No `doc_key` field in ledger schema** -- The #2207 contract recommends adding `doc_key` to the ledger but the field does not exist yet. Adding it for just these entries would create schema inconsistency. **Mitigation:** Defer `doc_key` addition to a coordinated schema migration; document SHA-256 values in plan notes for future back-population.

### Open Questions

1. **Should CSA 22.1-12 (Canadian Electrical Code) be included?** -- It's in the acma-codes/CSA folder but is a general electrical code, not marine/LNG-specific. The issue scope says "OCIMF and CSA standards from acma-codes" which arguably includes all CSA standards found. **Recommendation:** Include it with `domain: electrical` for completeness; it was part of the indexed source.

2. **Should OCIMF OVID/OVPQ documents get ledger entries?** -- These are inspection/vetting questionnaire documents, not engineering standards. **Recommendation:** Exclude from ledger; they are operational forms, not standards. If needed, they can be addressed in a separate operational-document registry.

3. **Should the ~25 remaining API standards in acma-codes get alias resolution in this issue?** -- The issue title says "OCIMF/CSA ledger entries" with API being secondary (alias handling only). **Recommendation:** Limit API scope to RP 1111 and RP 2SK (explicit in issue body); create a follow-on issue for remaining API standards.

4. **How should the OCIMF coefficient data (xlsx, digitized figures) be handled?** -- These are engineering data artifacts, not standards. They have value for mooring analysis but don't fit the standards-transfer-ledger model. **Recommendation:** Defer to a separate data-asset registry or note their existence in the MEG entry `notes` field. Not ledger entries.

---

## Complexity: T2

**T2** -- Multiple YAML entries across one file, with alias/edition analysis requiring cross-referencing indexed data against existing ledger state. Not T1 (involves 11+ new entries with non-trivial alias logic) but not T3 (no architecture changes, no new files created, builds on existing ledger structure). The main complexity is in the alias/edition decision-making, which this plan resolves.
