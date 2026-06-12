---
name: llm-wiki-table-fidelity-provisional-by-default
description: "Auto-parsed standard tables are structurally-consistent-but-often-value-wrong; corpus policy is parse_status provisional-by-default + verification queue (NORSOK canary, 2026-05-27)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

Established by the NORSOK canary for llm-wiki #124 (decided on #122, 2026-05-27).

**The hard lesson:** automated table extraction (pdfplumber/pdftotext) produces tables that are **structurally consistent but value-wrong** — e.g. NORSOK M-710 Table A.1/A.2/C.1/C.2 collapsed 3 condition rows (30/10/60 vol%) into one. These pass any structural heuristic; only **value-level comparison against the source PDF** (done by the adversarial review) catches them. So pure auto-parsing CANNOT reach a trustworthy-clean bar at 27K-doc scale.

**Policy (corpus-wide, all ingest epics):**
- Every table CSV carries `parse_status`: **`provisional-unverified`** (auto-parsed, default), `raw-unverified` (raw_layout capture), or `verified` (only after explicit source-check — vision/human).
- Default is provisional-unverified; never imply clean without verification.
- `datasets/_verification-queue.csv` lists provisional/raw tables awaiting verification.
- Trustworthy-NOW deliverables = **verbatim normative clauses + honestly-flagged table captures**; analysis-ready CSVs are a *verified subset* built over time.
- Raw vendor PDFs stay off-repo ([[feedback_codes_standards_data_in_private_wiki]]); the page holds derived data + `source_pdf` pointer.

**Canary process learnings (worth repeating for the other epics):**
- Run the canary review-fix-rereview loop against SOURCE, not just structure — it found defects 2 rounds deep.
- Negative-spec prompts ("here's what the last attempt got wrong, don't repeat") steer Codex off failure modes reliably.
- Selective normative verbatim (not full-document dump) keeps pages usable (NORSOK pages 6–82K vs a 2 MB raw dump).
- cd into the clone before write-dispatch ([[feedback_codex_exec_cwd_is_sandbox_root]]).

Related: [[project_llm_wiki_priority_and_resource_intelligence]], [[feedback_mnt_ace_corpus_claims_unreliable]].
