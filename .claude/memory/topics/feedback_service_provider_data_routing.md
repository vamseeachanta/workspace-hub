> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_service_provider_data_routing.md

---
name: feedback-service-provider-data-routing
description: "6-row matrix governing how service-provider/vendor data enters the workspace-hub + llm-wiki ecosystem; vendor brochures stay off-repo, public-record sources go to public wiki, applies across all repos"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3f825a3-b95b-4aef-823b-54cab637c9dd
---

Service-provider data flows through six distinct routes depending on document class and copyright surface. Apply this matrix before ingesting any vendor-adjacent material anywhere in the workspace-hub ecosystem.

**The matrix** (canonical authority: `llm-wiki/docs/governance/service-provider-data-routing.md` + summary in `llm-wiki/CLAUDE.md`):

| Document class | Route |
|---|---|
| Vendor brochure / spec sheet / marketing PDF (e.g. Helix Q4000 LTR, Halliburton equipment data sheets) | Off-repo at `/mnt/ace/vendor-pdfs/<vendor-slug>/`; index entry in `workspace-hub/docs/governance/vendor-pdf-inventory.md` |
| SEC filings (10-K, 10-Q, 8-K, investor decks) | Public llm-wiki entity page, paraphrased with page-citation |
| Conference papers (SPE / OTC / IADC / OMAE) with stable DOIs | Public llm-wiki source page, DOI-grounded paraphrase |
| Press releases / vendor marketing landing pages (HTML) | URL-only reference in public wiki for facts disclosed; verbatim HTML snapshot off-repo at private mount |
| Public class-society / regulator records (ABS / DNV / LR / BV / IACS; USCG; IMO; BSEE OCS) | Public llm-wiki entity/standards/source page directly (US federal under 17 U.S.C. § 105 is additionally public-domain) |
| User's own annotated extracts (engineering notes on a vendor brochure) | Off-repo alongside the source PDF at private mount |

**Why:** llm-wiki publishes under MIT (code) + CC-BY-4.0 (content). Vendor-derivative content (brochures, spec sheets, marketing prose) cannot be re-licensed under CC-BY-4.0 by us — we lack the upstream rights. "Publicly accessible URL" ≠ "permission to redistribute". The 2026-05-05 spinout governance + workspace-hub#2482 deny-list codified the off-repo rule for vendor PDFs specifically; the 2026-05-14 matrix expansion extends the same principle to the other five document classes that surfaced when a Helix Energy Solutions ingest request collided with a same-session BSEE federal-regulator ingest request. The two have OPPOSITE routing despite both being "PDFs from external sources" — the deciding axis is copyright + publisher class, not file format.

**How to apply:**

1. **Before** writing any vendor / regulator / publisher-adjacent content into any wiki, classify the source into one of the six rows. If it doesn't clearly fit, default to off-repo and surface the gap.
2. **Vendor identity is not the deciding axis** — `Helix` isn't the problem, Helix's *brochure* is. A Helix entity page in `wiki/entities/helix-energy-solutions-fleet.md` grounded in their SEC 10-K + class-society records is legitimate (row 2 / row 5). The same vendor's product brochure is row 1.
3. **Apply at content-grade, not URL-grade**. Don't infer document class from the URL filename or path keyword. `BSEE...Riser_Life_Extension.pdf` looked like drilling-engineering content but actually covered production pipeline risers under different regulatory subpart. **Read the source before locking ingest targets.** (This process-lesson is general: any wiki-ingest spec where the target sub-wiki depends on the document's actual subject matter must include a content-grade read — `pdftotext` / WebFetch / PyMuPDF — before the spec commits to a target. URL-keyword inference recurred 2026-05-14; surface the candidate-target deviation immediately if pdftotext reveals different subject matter.)
4. **Worked examples** (2026-05-14):
   - Helix ESG Q4000 LTR brochure → row 1 → `/mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_Q4000_LTR_2024-09-12.pdf` + workspace-hub commit a2103c70 inventory entry.
   - Helix ESG IRS 7-15k LTR brochure → row 1 → same.
   - Helix ESG riser-based-well-intervention service-line landing page → row 4 → URL noted in inventory + HTML snapshot at `/mnt/ace/vendor-pdfs/helix-esg/Helix_riser-based-well-intervention_2026-05-14_snapshot.html`.
   - BSEE 2024 Deepwater Dynamic Pipeline Riser Life Extension PDF → row 5 → public wiki at `llm-wiki/wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md` (commit a6b50d23).
5. **Don't double-cite**. If a fact is in both a vendor brochure and the same vendor's SEC 10-K, cite the 10-K (row 2) in the public wiki page; reference the brochure only in the off-repo inventory.
6. **Anti-patterns to refuse**:
   - "Just save it as a source page; the URL is public" — public accessibility doesn't transfer redistribution rights.
   - "Paraphrase the brochure heavily" — preserving the vendor's structuring (which dimensions to report, which order) is still derivative work; needs public-record source.
   - "Add the brochure URL to the wiki, no content" — for row 1 sources, even URL references shouldn't appear in the public wiki because they signal what to copy. Save URL references in the off-repo inventory instead.

**Related guidance:**
- [[feedback-llm-wiki-concept-pages-need-public-references]] — concept pages need textbook/DOI/multi-source grounding (single brochure as sole source fails day-one lint).
- [[feedback-per-repo-metadata-is-firewall]] — the boundary is enforced by license + repo + .gitignore + .git, not by file-system distance.
- workspace-hub#2482 (deny-list authority).
- Design doc + execution: `workspace-hub/docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md`.

**Promotion path** if violations recur:
- Level-1 micro-skill: auto-load on llm-wiki edit-session entry.
- Level-2 script: pre-commit hook scanning `wikis/**/sources/*.md` for known vendor-brochure-URL patterns.
- Level-3 hook: stop-hook in workspace-hub `.claude/settings.json` firing the same scan across all child repos before any push.

Currently Level-0 prose. Recurrence-trigger for promotion: any session where a vendor-brochure-URL is found landed in a public wiki source-page, or any session where the deny-list is questioned in chat for the same vendor more than once.
