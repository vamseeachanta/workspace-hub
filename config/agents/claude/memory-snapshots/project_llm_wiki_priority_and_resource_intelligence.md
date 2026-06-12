---
name: llm-wiki-priority-spine-resource-intelligence-component-extraction
description: Generic llm-wiki is the
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

User directives 2026-05-27 governing the whole /mnt/ace → llm-wiki program (recorded on llm-wiki #122):

**Priority spine.** Feeding the **generic `llm-wiki` is the #1 objective.** `llm-wiki-<client>` is a good **INTERMEDIATE staging step**, not the goal: raw client data → client wiki (unbridled, miss-nothing reference) → generic component/technology knowledge extracted → generic `llm-wiki`. **Only `acma` is an active client today**; other client wikis are built thoroughly only when needed.

**Resource-intelligence component extraction ("a component is a component").** Vendor/contractor/client component knowledge is generic engineering knowledge. Split:
- Generic `llm-wiki` ← the component's generic knowledge **where partial PUBLIC info exists** (standards, papers, public datasheets, regulator/class records). Ground on the public info; name the vendor as existence-proof/supplier, NOT as the technical authority (NOV vendor-product-family precedent). Needs per-component judgment incl. online research.
- Client wiki ← client-confidential project specifics only.
- Resource-intelligence (online research) also UPKEEPS references when problems arise (e.g. the OpenFAST/WEC-Sim "National Laboratory of the Rockies" attribution anomaly — maintain the canonical NREL/Sandia reference, fix as needed; don't block).

**One-canonical-source rule** (resolves the recurring double/triple-ingest risk): same content reachable from multiple roots (acma-codes vs O&G-Standards; `/mnt/ace/<client>` vs `client_projects` vs `docs/disciplines/<proj#>`) → pick ONE canonical source per spec/component by quality (unencrypted, newest, most complete). Decision 2a: **O&G-Standards is canonical for ASTM** (#124); #109 = SAE/ANSI + ASTM-absent-from-O&G.

**All data is important** — nothing dropped. Catalog/disk gaps (e.g. O&G-Standards `_catalog.json` omitting ABS/ASCE/ASME/AWS/NACE) get their own tracking issue (llm-wiki #134) and are tackled via reconciliation + dedup, not ignored.

Related: [[feedback_codes_standards_data_in_private_wiki]], [[feedback_mnt_ace_corpus_claims_unreliable]], [[feedback_porting_issues_private_not_public_hub]], [[project_llm_wiki_external_post_ingest_workflow]] (NOV precedent).
