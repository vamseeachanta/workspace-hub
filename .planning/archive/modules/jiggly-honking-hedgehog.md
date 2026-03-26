# WRK-1404: Organize /mnt/ace/docs/ subfolders and deduplicate engineering references

## Context

The local-analysis relocation (WRK-1384/1396) surfaced 9 subfolders in `/mnt/ace/docs/` that need review. Some contain misplaced code/repos, some have duplicates, and `rearrange-data/` is a 187MB dump of 60+ unsorted files. Goal: clean structure, remove duplicates, relocate misplaced content.

## Plan

### Step 1: Delete junk
- Remove `engineering-refs/rearrange-data/DELETE/` (one random JPG)
- Remove duplicate `engineering-refs/rearrange-data/OrcaFlexModelGen.xlsm` (parent has copy)
- Remove duplicate `engineering-refs/rearrange-data/The Selfish Gene - R. Dawkins (1976) WW.pdf` (keep the Richard_Dawkins version)
- Remove `sd-python-docs/~$*.docx` temp lock files

### Step 2: Sort rearrange-data/ personal/admin → admin/
Move these subdirs and files from `rearrange-data/` to `docs/admin/`:
- **Subdirs**: `2018IndiaTravel/`, `7202 San Ramon/`, `EyePrescription/`, `Invoices/`, `KM/`, `VisaExtension/`
- **Files**: `VA_BlankCheck.JPG`, `BudgetRevenueBalance.xlsx`, `Amazon.com - Online Return Center (Orimeter).pdf`, `2018-07-APIMertonScreenshot.PNG`, `Occidental_Climate Report_2018.pdf`

Merge with existing `admin-refs/` content (rename `admin-refs/` → `admin/`).

### Step 3: Sort rearrange-data/ books → books/
Move to `docs/books/`:
- `Richard_Dawkins_The_Selfish_Gene.pdf`
- `Petroleum_Production_Engineering,_Elsevier_(2007).pdf`
- `Introduction to Wellbore Positioning eBook.pdf`
- `Wellbore Ranging Technologies Intercept Applications and Best Practices.pdf`
- `Statistics-ESLII_print12.pdf`, `Statistics-ISLR Seventh Printing.pdf`
- `50YearsDataScience.pdf`, `MiningofDataSets.pdf`, `machine-learning-workflow-ebook.pdf`
- `MAN_WRT1900AC_8820-01897_RevA00_EN_FR-CA_Comprehensive.pdf` (router manual → admin/)

### Step 4: Sort rearrange-data/ engineering → engineering-refs/
Move remaining engineering PDFs/files to `docs/engineering-refs/`:
- DNV: `2015-05 DNVGL-OS-E101.pdf`, `2018-01 DNVGL-OS-E101.pdf`, `DNV RP-O501 (Erosion).pdf`, `n-004.pdf`
- API: `API_11BR_*.pdf`, `API RP 16Q*.pdf`, `API RP 16Q*.docx`, `TVO17-083*API579*.xlsx`
- O&G: `O&G Bolting.pdf`, `Subsea Bolting Technologies.pdf`, `Piping-Components-Ebook.pdf`, `How to Read P&ID.pdf`
- Drilling: `Drilling Diverter Control Procedures.pdf`, `HuisDrill-12000.pdf`, `Varco Coiled tubing handbook.pdf`
- Wellbore: `SPE-1014-0025-OGF (Sand Production).pdf`, `Remedial Cementing Practices Document-2.pdf`
- FEA/analysis: `Wood_Group_Kenny-*.pdf`, `bentley-sacs_brochure.pdf`, `SACS Training in Delhi.pdf`, `HHS Accu-TVD Tool Poster.pdf`
- Float/displacement: `RB122_Float_Equiment.pdf`, `RB130_Displacement.pdf`, `rb200_DimensionsandStrength.pdf`
- Models: `SCR Model.xlsm`, `SCR Model.xlsx`, `Frontier.xlsm`, `controlFileGML_Main.m`
- Project docs: `31420-PRP-0001-02 (Enbridge Stampede*).pdf`, `CVX JACK St MALO databook.pdf`, `2H Project Map Database*.xlsm` (x2), `0596_GC2010*.pdf`, `GP650601_COM.PDF`, `gp660601_com.doc`, `Skill_genie.pdf`
- Cheatsheets: `Docker_CheatSheet*.pdf`, `zt_docker_cheat_sheet.pdf`, `Jupyter_Notebook_Cheat_Sheet.pdf`, `weidadeyue_jupyter-notebook.bw.pdf`, `Chang_LaTeX_sheet.pdf`, `cheat-sheet-v2.pdf`, `ws-restwsdl-pdf.pdf`, `jsonpickle.pdf`

### Step 5: Archive misplaced folders
- `docker-examples/` → `_archive-docker-examples/`
- `github-references/` → `_archive-github-references/`
- `sd-python-docs/` → `_archive-sd-python-docs/`

### Step 6: Rename admin-refs → admin
- `mv docs/admin-refs docs/admin` (merge rearrange-data personal files here)

### Step 7: Remove empty rearrange-data/
- Verify `engineering-refs/rearrange-data/` is empty, then `rmdir`

### Step 8: Verify
- `ls` each reorganized folder to confirm structure
- Confirm no broken symlinks or orphaned files

## Execution order
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (sequential, each depends on prior)

## Files touched
All under `/mnt/ace/docs/`:
- `engineering-refs/rearrange-data/` — emptied and removed
- `admin-refs/` → renamed to `admin/`, receives personal files
- `books/` — receives book PDFs
- `engineering-refs/` — receives engineering PDFs
- `docker-examples/` → `_archive-docker-examples/`
- `github-references/` → `_archive-github-references/`
- `sd-python-docs/` → `_archive-sd-python-docs/`
