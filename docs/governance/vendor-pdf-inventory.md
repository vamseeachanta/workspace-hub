---
title: Vendor PDF / vendor marketing-asset inventory (private mount index)
date: 2026-05-14
purpose: Index of vendor-derivative assets deposited at /mnt/ace/vendor-pdfs/ off the public llm-wiki repo
governance: workspace-hub#2482 (vendor-derivative deny-list); llm-wiki/CLAUDE.md service-provider data routing matrix
related_design: docs/governance/2026-05-14-service-provider-data-routing-and-bsee-ingest-design.md
---

# Vendor PDF / vendor marketing-asset inventory

This file is the workspace-hub-side index of vendor-derivative assets routed to the private mount per the service-provider data routing matrix in `llm-wiki/CLAUDE.md`. The assets themselves are NOT in any git repo — they live at `/mnt/ace/vendor-pdfs/<vendor>/` and are deliberately off-repo per the 2026-05-05 spinout governance.

This index IS in workspace-hub git history because the index itself contains no copyrighted vendor content — only filenames, origin URLs, observed dates, and document character.

## Schema

Each entry records:
- **Vendor** — issuing entity (parent company / brand).
- **Local path** — `/mnt/ace/vendor-pdfs/<vendor-slug>/<filename>`.
- **Origin URL** — where the asset was downloaded from (for re-fetching if local copy is lost).
- **Observed date** — date the local copy was acquired (ISO YYYY-MM-DD).
- **Document character** — one of: brochure, spec-sheet, marketing-landing-page, press-release, white-paper, technical-manual.
- **Asset category** (per matrix) — `vendor-brochure`, `vendor-marketing-html`, etc.
- **Public-record cross-reference** — if the same facts are disclosed in an SEC filing or class-society record, note the citation so future entity-page work in llm-wiki has a public-domain anchor.

## Helix Energy Solutions Group (helixesg.com)

| Local filename | Origin URL | Observed | Character | Category | Public-record anchor |
|---|---|---|---|---|---|
| `helix-esg/Helix_Well_Ops_Q4000_LTR_2024-09-12.pdf` | `https://helixesg.com/downloads/Helix_Well_Ops_-_Q4000_-_LTR_09-12-2024_FINAL.pdf` | 2026-05-14 | Q4000 vessel light-intervention technical-reference brochure (4 pages, PDF v1.4, 3.2MB) | vendor-brochure | Helix Energy Solutions 10-K fleet section (Q4000 listed under Well Intervention segment); USCG vessel registry; ABS class record |
| `helix-esg/Helix_Well_Ops_IRS-7-15k_LTR_2023-11-28.pdf` | `https://helixesg.com/downloads/Helix_Well_Ops-_IRS_7_15k-_LTR_11-28-23_FINAL.pdf` | 2026-05-14 | Intervention Riser System (7" 15,000 psi) technical-reference brochure (4 pages, PDF v1.4, 4.0MB) | vendor-brochure | Helix Energy Solutions 10-K Well Intervention segment; SPE / OTC conference papers on 15k psi IRS deployments (if surfaced separately) |
| `helix-esg/Helix_riser-based-well-intervention_2026-05-14_snapshot.html` | `https://helixesg.com/our-assets/riser-based-well-intervention/` | 2026-05-14 | Service-line marketing landing page (70KB HTML) | vendor-marketing-html | Helix Energy Solutions 10-K (Well Intervention segment description); investor-presentation deck |

## How to use this inventory

- **Future Helix entity page in llm-wiki**: when sufficient public-record grounding accumulates (10-K fleet section + class-society records + at least one OTC/SPE conference paper), build `llm-wiki/wikis/drilling-engineering/wiki/entities/helix-energy-solutions-fleet.md` modeled on the existing 6 drilling-contractor entity stubs (transocean-fleet.md, valaris-fleet.md, etc.). Cite this inventory's "Public-record anchor" column entries — NEVER cite the local PDF files.
- **Personal reference**: open the local files via `xdg-open /mnt/ace/vendor-pdfs/helix-esg/<filename>` for engineering review. Engineering notes generated while reading these belong alongside them at `/mnt/ace/vendor-pdfs/helix-esg/notes-*.md` (private mount discipline preserves chain of custody).
- **Adding new vendors**: create `/mnt/ace/vendor-pdfs/<new-vendor-slug>/`, deposit assets, then append a new section to this file following the schema above.

## Excluded from this inventory (route differently per matrix)

- US federal regulator PDFs (BSEE, EPA, USCG technical guidance) — public-domain under 17 U.S.C. § 105; route to public llm-wiki source pages directly.
- Conference papers with stable DOIs (SPE, OTC, IADC, ASME-OMAE) — route to public llm-wiki source pages with DOI grounding.
- Classification-society public records (ABS, DNV, LR, BV) — route to public llm-wiki entity pages with class-record citation.
