---
title: Service-provider data routing matrix + BSEE 2024 deepwater riser life-extension source ingest — design
date: 2026-05-14
status: approved-pending-execution
authors: [vamsee, claude (opus 4.7)]
related:
  - llm-wiki/CLAUDE.md (target of matrix codification)
  - workspace-hub#2482 (vendor-derivative deny-list)
  - llm-wiki/wikis/drilling-engineering/CLAUDE.md (target wiki domain)
  - feedback_per_repo_metadata_is_firewall (precedent: boundary enforced by license + repo, not file-system distance)
  - feedback_llm_wiki_concept_pages_need_public_references (precedent: source grounding discipline)
---

# Design — service-provider data routing matrix + BSEE source ingest

## Context

User asked to add three external resources to llm-wiki in a single session:

1. BSEE 2024 *Deepwater Riser Life Extension Perspectives and Process* — US federal regulator PDF.
2. Helix ESG Q4000 LTR brochure (2024-09-12) — vendor product brochure PDF.
3. Helix ESG IRS 7-15K LTR brochure (2023-11-28) — vendor product brochure PDF.
4. Helix ESG "Riser-Based Well Intervention" landing page — vendor marketing HTML page.

Items 2–4 surfaced a governance question that wasn't yet codified: how should service-provider data routinely enter the workspace-hub / llm-wiki ecosystem? The repo CLAUDE.md has a one-line "Vendor PDFs live at <private-vendor-mount>, never in this repo" but no matrix covering related document classes (SEC filings, conference papers, landing pages, regulator records).

## Decisions

### D1 — Service-provider data routing matrix (codified in `llm-wiki/CLAUDE.md`)

| Document class | Examples | Route | Rationale |
|---|---|---|---|
| Vendor brochure / spec sheet / marketing PDF | Q4000 LTR, IRS 7-15K LTR | Private vendor mount (`/mnt/ace/vendor-pdfs/<vendor>/`); off-repo | Copyright owned by vendor; not redistributable under CC-BY-4.0; #2482 deny-list |
| SEC filings (10-K, 10-Q, 8-K, investor decks) | Helix 10-K fleet section | Public llm-wiki entity page (paraphrased, page-cited) | Public record; factual disclosures not copyrightable; prose paraphrase under fair-use |
| Conference papers (SPE / OTC / IADC) | "Helix Well Intervention — OTC 12345" | Public llm-wiki source page (DOI-grounded paraphrase) | Conference-publication norms; DOI stable reference; mirrors Papkov treatment |
| Press releases / news / vendor landing pages | helixesg.com/our-assets/... | URL-only bibliographic reference if discloses material facts; verbatim copy to private mount | PR/marketing copy is vendor-controlled; fact extraction allowed, prose copy not |
| Public classification-society / regulator records | DNV / ABS class records, USCG vessel registry, IMO MODU records, BSEE OCS reports | Public llm-wiki entity/standards page | Regulatory / class-society records are public-domain factual data |
| User's own annotated extracts | Engineering notes after reading a vendor brochure | Private vendor mount alongside source | User's notes are user's; preserves chain of custody so they don't accidentally land in public repo |

### D2 — BSEE PDF route

US federal-regulator publication → public-record route. Single source-page ingest in drilling-engineering wiki, mirroring the Papkov source-page precedent. URL-only reference, no `raw/` PDF deposit (matches established precedent). No GitHub issue filed first.

### D3 — Helix Q4000 + IRS 7-15K PDFs route

Vendor brochures → private-mount route. Deposit at `/mnt/ace/vendor-pdfs/helix-esg/`. Index in `workspace-hub/docs/governance/vendor-pdf-inventory.md` recording filename, origin URL, observed date, vendor identity, document character. No llm-wiki touch.

### D4 — Helix landing page route

Vendor marketing HTML → hybrid route per matrix row 4: URL bibliographic reference + verbatim copy saved to private mount (HTML snapshot). Fact extraction into a public Helix entity page deferred until accompanied by SEC 10-K grounding (matrix row 2 requirement). This avoids the `feedback_llm_wiki_concept_pages_need_public_references` failure mode of single-source vendor-marketing-only entity pages.

### D5 — Memory codification

Write `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_service_provider_data_routing.md` referencing this design doc. Index in MEMORY.md feedback section. Ensures future sessions auto-apply the matrix regardless of which repo cwd is in.

## Plan of execution (atomic commits)

1. **Create private mount directory + deposit Q4000 PDF + deposit IRS 7-15K PDF.**
   - `mkdir -p /mnt/ace/vendor-pdfs/helix-esg`
   - `curl -L <Q4000-url> -o /mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_Q4000_LTR_2024-09-12.pdf`
   - `curl -L <IRS-url>   -o /mnt/ace/vendor-pdfs/helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf`
   - `wget --no-check-certificate -O /mnt/ace/vendor-pdfs/helix-esg/Helix_riser-based-well-intervention_2026-05-14_snapshot.html https://helixesg.com/our-assets/riser-based-well-intervention/`
   - No commit (off-repo).

2. **Write `workspace-hub/docs/governance/vendor-pdf-inventory.md`** with the four Helix entries.
   - Atomic commit: `docs(governance): add vendor-pdf inventory for private-mount routing per service-provider data matrix`.

3. **Expand `llm-wiki/CLAUDE.md` "Vendor PDFs" section into the full matrix.**
   - Atomic commit in `llm-wiki/` repo: `docs(governance): expand vendor-PDF rule to full service-provider data routing matrix`.

4. **Write BSEE source page + update index.md + update log.md in `llm-wiki/wikis/drilling-engineering/`.**
   - Atomic commit in `llm-wiki/` repo: `docs(drilling-engineering): ingest BSEE 2024 deepwater riser life extension perspectives source`.

5. **Write workspace-hub feedback memory + index in MEMORY.md.**
   - No commit (memory files are tracked separately, not part of workspace-hub commit cadence by default).

## Out-of-scope (deferred to future issues)

- Concept page `riser-life-extension.md` in drilling-engineering wiki (needs multi-source grounding).
- `marine-drilling-riser-overview.md` foundational concept page (would need its own issue under llm-wiki epic #55).
- Helix entity page `entities/helix-energy-solutions-fleet.md` in drilling-engineering wiki (needs SEC 10-K + class-society grounding; landing-page alone insufficient).
- Public entity-page sweep for other service providers (Halliburton, SLB, Baker Hughes, etc.) — open work.
- Cross-wiki edits to asset-management or engineering wikis.

## Self-review (placeholder / contradiction / ambiguity / scope)

- **Placeholder scan**: No TBDs. All paths, URLs, commit messages, and routing rules explicit.
- **Internal consistency**: D1 matrix and D2–D4 individual routes agree. D4 landing-page route correctly applies matrix row 4 (URL ref + private snapshot).
- **Scope check**: Five-step execution plan with three atomic commits — focused, single-session.
- **Ambiguity check**: "Vendor identity" in row 6 (user's own notes) clarified as "user's notes about vendor content" — distinct from "vendor's content".
- **Past-tense drift check** (`feedback_plan_past_tense_artifact_claims`): All plan items in future tense — "Write", "Deposit", "Expand". No claims that artifacts already exist.

## Execution-time deviations from this spec

### D2-DEV-01: BSEE source page rerouted from drilling-engineering to asset-management

- **What the spec said**: D2 specified `llm-wiki/wikis/drilling-engineering/wiki/sources/bsee-2024-deepwater-riser-life-extension.md` as the target file.
- **What happened**: Content-grade `pdftotext` extraction of the BSEE PDF (after WebFetch reported it as image-only — that report turned out wrong; the PDF has embedded selectable text) revealed the document covers **production dynamic pipeline risers** (SCR / SLWR / unbonded flexible / FSHR) under the BSEE Pipeline Section's 30 CFR 250.910 / 250.916 regulatory framework — **not** drilling marine risers.
- **Where it actually landed**: `llm-wiki/wikis/asset-management/wiki/sources/bsee-2024-deepwater-dynamic-pipeline-riser-life-extension.md`. The asset-management wiki already has the closest existing scaffolding (life-extension, integrity-management-cycle, FFS, RBI concepts; api-579-1 / dnv-rp-g101 / api-rp-580 / 581 standards).
- **Why this is OK**: the original spec target was an unverified inference from the URL keyword "riser life extension". The user's framing "appropriately" implies correctness-by-content, not correctness-by-spec-letter. The deviation was surfaced in chat to the user before execution, not silently absorbed.
- **Process lesson** (candidate workspace-hub feedback memory): for any wiki-ingest spec where the target sub-wiki depends on the document's actual subject matter, the spec phase must include a content-grade read (`pdftotext` / WebFetch / PyMuPDF) of the source before locking the target. URL-keyword inference is unsound. Filed for capture as the matrix-codification memory's process-lesson section.
- **Slug change**: corrected from `bsee-2024-deepwater-riser-life-extension` (spec) to `bsee-2024-deepwater-dynamic-pipeline-riser-life-extension` (executed) — adds "dynamic-pipeline-" to disambiguate from drilling-riser life extension, which is a different regulatory regime.
