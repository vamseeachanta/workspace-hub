> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-21
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_codes_standards_data_in_private_wiki.md

---
name: codes-standards-data-in-private-wiki
description: "Vendor-licensed codes/standards data (OCIMF, API, DNV, ABS, IACS UR, ASCE, ASME) belongs in private vamseeachanta/llm-wiki — verbatim text, digitized tables, figure extracts all permitted in repo"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 301086a5-63fe-4d73-a934-dd43ff2f9c0d
---

Vendor-licensed engineering codes and standards data lives in the **private** `vamseeachanta/llm-wiki` repo. Verbatim clause/convention text, digitized coefficient tables (re-emitted as CSV), figure captions, and per-figure descriptions are all permitted in the repo. The raw vendor PDF itself stays at `/mnt/ace/acma-codes/<code>/` as the canonical source of truth; the wiki holds the digitized derivation.

**Why:** the 2026-05-20 user directive collapsed the licensing window for codes-and-standards content by flipping `vamseeachanta/llm-wiki` from public to private. Previously the public posture required `extraction_policy: metadata-only` + `raw_copy_allowed: false` + `## Boundary` sections on every standards page — high friction for ingest and per-page-design overhead. Privacy removes the public-redistribution risk; engineering content can land at full fidelity. Forks/stars on llm-wiki were 0 at flip time so no external dependents to coordinate. User framing: "OCIMF is codes and standards and is public knowledge. Let us land it in llm-wiki public repo" → escalated to "let us get clients and go with full flow" → llm-wiki visibility-flipped to private.

**How to apply:**
- Confirm `gh repo view vamseeachanta/llm-wiki --json visibility` returns `PRIVATE` before committing codes/standards content
- Frontmatter: drop legacy `extraction_policy` and `raw_copy_allowed`; add `visibility: private-llm-wiki`; cite `sources:` with the off-repo `/mnt/ace/` PDF path
- Body: verbatim quote + digitized tables fine; raw vendor PDF stays off-repo at `/mnt/ace/`
- Cross-repo references from public workspace-hub/digitalmodel use bare path form (`wikis/<domain>/...`), not https URLs that would 404 for external readers
- Calc-citation contract unchanged; resolver fails closed for unauthenticated `pip install digitalmodel` users by design
- Public-domain codes (US CFR, NOAA, NIST, IMO post-release circulars) may stay public if a public sibling wiki exists — verify public-domain status; when in doubt, route private
- Methodology/convention/interpretive content (not directly reproducing standard text) can live in public surfaces if a public sibling exists; currently inside private llm-wiki under `methodology/`

Pilot: OCIMF MEG3/MEG4 Annex A landed 2026-05-20 under `wikis/marine-engineering/wiki/datasets/ocimf-meg4-annex-a/` (3 CSVs covering Annex A figures A5-A19) + verbatim §A1/§A2 convention text in the standards pages. Rule codified at [[codes-standards-data-routing-rule]] in `.claude/rules/codes-standards-data-routing.md`.

**Supersedes / amends:**
- [[offrepo_intel_routing]] — partial supersede: `/mnt/ace/` still holds the source PDFs; derived data now in private wiki rather than off-repo only
- [[service_provider_data_routing]] — partial supersede on the codes/standards row
- [[project_llm_wiki_spunout]] — full supersede: llm-wiki is private again as of 2026-05-20 21:30 CT
