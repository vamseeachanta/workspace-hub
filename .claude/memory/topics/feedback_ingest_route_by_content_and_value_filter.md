> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_ingest_route_by_content_and_value_filter.md

---
name: ingest-route-by-content-content-value-filter
description: "O&G-Standards publisher dirs are misfiled grab-bags → route by actual topic not folder label; image-only/low-text PDFs are noise → filter, don't one-page-per-PDF"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

Two ingest policies from the 2026-05-27 scale-3 batch (NEMA/MIL/SNAME → llm-wiki #124; decided on #122):

**1. Route by CONTENT, not folder label.** The O&G-Standards publisher dirs are misfiled grab-bags:
- the `NEMA` dir held wave-kinematics papers (Gudmestad, Pawsey) + material-damping-of-pipes — hydrodynamics/structural, not NEMA.
- the `SNAME` dir held US-Navy ship plans + a UK-MCA regulatory doc, not just SNAME.
So every doc must route to the domain its ACTUAL topic belongs to. Add a content-classification step to ingest prompts; re-home misfiled outputs (deduped vs existing coverage), fixing both the source and target domain `index.md` + `_verification-queue.csv`.

**2. Content-value filter.** PDFs with negligible extractable text (image-only scans, drawings, ship plans) must NOT become individual pages — the SNAME ingest produced ~73 near-empty pages with useless one-word titles (`Bb62`, `Cv2`). Skip them or log to the #135 vision-verification queue; never one-noise-page-per-image-PDF. A single catalog/index entry is acceptable if the collection has reference value.

**How to apply (bake into every ingest prompt going forward):**
- Pre-classify each PDF by extracted topic → target domain; don't trust the dir name.
- Gate page creation on a minimum extractable-text threshold; route image-only PDFs to the vision queue (#135).
- After a batch, audit page titles for one-word/garbage titles (noise signal) and off-domain topics (misfile signal) before committing.

This compounds the broader theme: [[feedback_mnt_ace_corpus_claims_unreliable]] — /mnt/ace counts, catalogs, AND folder taxonomy are all unreliable; verify content empirically. Related: [[project_llm_wiki_table_fidelity_provisional]], [[project_llm_wiki_priority_and_resource_intelligence]].
