# Resource Pack

## Problem Context
- WRK-1380 is the manual-curation child of WRK-1339 for populating vessel dimensions from 110 SNAME ship-plan PDFs.
- The target output is a `ship-dimensions.yaml` template filled with LOA, beam, draft, depth, displacement, and speed, with Jane's cross-checks on a prioritized subset.
- The work is explicitly drawing-heavy and image-first, so the planning baseline should assume human review of plans rather than text-only extraction.

## Relevant Documents/Data
- `data/doc-intelligence/manifests/naval-architecture/` contains ship-plan manifests for hull-specific PDFs such as `bb34.manifest.yaml`, `cv7.manifest.yaml`, and `ca34.manifest.yaml`.
- `data/doc-intelligence/manifests/naval-architecture/Janes-Fighting-Ships-2009-2010.manifest.yaml` confirms the Jane's reference is locally indexed.
- `knowledge/seeds/naval-architecture-resources.yaml` points to the mounted canonical PDFs under `/mnt/ace/docs/_standards/SNAME/`.
- Mounted source documents confirmed present:
  - `/mnt/ace/docs/_standards/SNAME/textbooks/Janes-Fighting-Ships-2009-2010.pdf`
  - `/mnt/ace/docs/_standards/SNAME/textbooks/Principles-of-Naval-Architecture-Vol1-SNAME.pdf`

## Constraints
- Stage 2 requires `evidence/resource-intelligence.yaml` and the standard resource-pack companion files.
- Current workflow approval polling only succeeds when GitHub reads from the actual issue repo (`vamseeachanta/digitalmodel`) rather than the workspace repo default.
- OCR tooling is not reliable enough to replace manual reading for drawing-dominant ship plans.

## Assumptions
- Ship-plan manifests are the authoritative list of hull PDFs to process.
- Jane's 2009-2010 is the preferred verification source for a first verified subset.
- Route A/simple remains appropriate if no new execution blockers appear after planning.

## Open Questions
- Where is the expected `generate-ship-dimension-template.py` artifact located, or was it generated outside the current repo tree?
- What is the canonical in-repo destination path for the resulting `ship-dimensions.yaml` file?
- Should Stage 10 execution use a fixed pilot subset (capital ships first) before broader vessel coverage?

## Domain Notes
- This is document-intelligence work with a naval-architecture corpus and a manual-curation execution pattern.
- The useful source split is: local manifests for inventory, mounted SNAME/Jane's PDFs for content, and lightweight OCR-tool documentation to justify manual-first handling.
- Representative capital-ship manifests already exist (`bb34`, `bb35`, `bb42`, `bb45`, `bb48`, `bb49`, `bb62`, `bb63`, `bb64`, `ca34`, `cv7`), which is enough to draft a capital-ships-first execution plan.

## Source Paths
- `.claude/work-queue/pending/WRK-1380.md`
- `knowledge/seeds/naval-architecture-resources.yaml`
- `data/doc-intelligence/manifests/naval-architecture/Janes-Fighting-Ships-2009-2010.manifest.yaml`
- `data/doc-intelligence/manifests/naval-architecture/bb34.manifest.yaml`
- `/mnt/ace/docs/_standards/SNAME/textbooks/Janes-Fighting-Ships-2009-2010.pdf`
- `/mnt/ace/docs/_standards/SNAME/textbooks/Principles-of-Naval-Architecture-Vol1-SNAME.pdf`
