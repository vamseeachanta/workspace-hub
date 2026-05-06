---
name: Kaggle oil-and-gas dataset backlog for worldenergydata
description: Discovery surface and backlog for ~250+ Kaggle "oil and gas" datasets — full survey lives in repo, this is the pointer
type: project
originSessionId: 5f3bc58a-2c99-432c-bb4f-e70962bc3556
---
The Kaggle search `https://www.kaggle.com/datasets?search=oil+and+gas` returns ~250+ datasets (12+ pages of 20). On 2026-05-05 the first ingest wave landed 5 datasets (4 incident/safety, 1 API 579 toy corpus). The **remaining backlog** with relevance scoring lives at:

`/mnt/local-analysis/workspace-hub/worldenergydata/data/SOURCES_kaggle.md` → §"Discovery surface — Kaggle 'oil and gas' search backlog"

**Why:** the user surfaced the volume of Kaggle datasets on 2026-05-05 (linked page 9 of search) and asked it be noted, so future ingest passes can pick from a curated backlog rather than re-running the discovery search.

**How to apply:**
- Before ingesting another Kaggle oil-and-gas dataset, check `SOURCES_kaggle.md` first — it has slug, size, module-fit, and license rationale for the top ~12 candidates.
- Don't pre-ingest the backlog; gate each on a real downstream consumer (a planned analysis, a module need).
- The 1.8 GB `afrniomelo/3w-dataset` (Petrobras real well-event corpus) is the highest-leverage backlog item but needs `/mnt/ace` placement.
- Re-survey command (Kaggle CLI ≥2.0):
  `kaggle datasets list -s "oil and gas" --sort-by votes -p 1 --csv`

**Iron law from this discovery work:** relevance density on Kaggle search drops off fast after page 3. Sorting by votes/downloads is more efficient than paginating through the long tail.
