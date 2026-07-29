> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_mnt_ace_corpus_claims_unreliable.md

---
name: mnt-ace-corpus-claims-unreliable
description: /mnt/ace corpus size/scope figures in issues & estimates are systematically wrong — always source-verify (catalog/pdfinfo/ls) before planning ingest
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

Issue-body and estimate figures about `/mnt/ace` corpora are **systematically unreliable**. In the 2026-05-26 llm-wiki ingest plan-drafting wave, Codex source-verification contradicted the stated scope in **every single case**:

- **O&G-Standards:** BOTH common figures are partly right at different scopes — `_catalog.json` = **27,343 docs / 26,982 PDFs** (organized dirs), but on-disk = 54,897 PDFs because the catalog OMITS `raw/` + uncataloged dirs (ABS/ASCE/ASME/AWS/HSE/IEC/NACE). **`raw/` (27,504 PDFs) is CONFIRMED 100% SHA-256-duplicate staging** (0 unique) → exclude. So true UNIQUE ingest scope ≈ organized dirs only (~27–28K), NOT 55K. Three different "true" numbers (catalog 27,343 / disk 54,897 / unique ~28K) — verify catalog AND disk AND dedup before trusting any (llm-wiki #134, 2026-05-27).
- **conferences:** "~19,797 PDFs" → catalog says **21,996 PDFs / 30 conferences / 38,526 files**.
- **literature:** "~4,095 docs" → catalog says **5,456 PDFs** (11,783 total files).
- **#108 electrical:** named standards (IEC 60079/61508/61511, IEEE 1580) **absent**; real corpus was IEC 60092-series + 61363-1 + IEEE 45.
- **#105 drilling:** "~46 pages" → actually 36; several pages had no backing local PDF (unverified revisions).
- **#106 production:** stated API-17 subsea family + 14E/16Q **not in the source dir**.
- **#104/#103:** encrypted/DRM files and an encoding-damaged GL PDF only surfaced on `pdfinfo`/extraction probe.

**Why:** these corpora were assembled/migrated over time; catalogs (`_catalog.json`, `*-catalog.yaml`, `conference-index.jsonl`) drift from disk, and issue bodies carry stale round-number estimates. Planning against the stated numbers produces wrong scope, wrong pages, and double-ingest.

**How to apply:**
- Before drafting/executing any `/mnt/ace` ingest, **source-verify**: `ls`/`find` counts, the corpus's own `_catalog.json`/`_inventory.db`, and `pdfinfo` for encryption/edition. Treat issue figures as claims to check, not facts.
- Make **catalog↔disk reconciliation** the first gate for large corpora; **block ingest of uncataloged dirs** until explained.
- Record verified counts + DRM/encryption status in the plan; route DRM-locked → metadata-only.

This is why dispatching Codex to *plan-with-source-inspection* (not trust the brief) paid off repeatedly. Related: [[feedback_codes_standards_data_in_private_wiki]], [[project_llm_wiki_canonical_clone_location]], [[feedback_mock_vs_live_invocation_divergence]].
