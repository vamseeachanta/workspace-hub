# 5 Terminal Prompts — Ready to Paste
> 2026-03-26 | Best run during 2x window (after 1 PM CDT)
> Can run in 5 parallel terminals OR sequentially in 1 terminal

---

## Terminal 1 — #1360: Extract algorithms from riser-eng-job

```
GitHub issue #1360. Extract reusable engineering algorithms and methods from riser-eng-job archives at /mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/. There are 6,695 code and calculation files: 3,550 .xls, 3,064 .dat, 43 .xlsx, 29 .inp, 8 .m, 1 .vbs spread across 4 project subfolders (2100-blk31-slor-design, 3824-containment-riser, 3836-hp1-riser, 3837-cdp2-fsr).

Do the following:
1. Sample 20 .dat files across subfolders to categorize them (OrcaFlex sim files, ABAQUS input, raw data, etc.)
2. For .xls/.xlsx files: use Python (openpyxl for xlsx, xlrd for xls) to extract sheet names and detect calc spreadsheets vs plain data tables. Flag sheets with formulas.
3. For .m files: extract function signatures and header comments describing purpose
4. For .inp files: identify FEA software (ABAQUS, ANSYS, OrcaFlex) and analysis type from file headers
5. Build an algorithm catalog at /mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/algorithms.yaml with: file_path, software, analysis_type, description, reusability_score (high/medium/low)
6. Identify high-value reusable items (validated analysis templates, engineering calcs) and flag for promotion to digitalmodel source modules
7. Write summary with recommendations to /mnt/local-analysis/workspace-hub/.planning/algorithm-extraction.md
8. Update GitHub issue #1360 with findings: gh issue comment 1360 -b "summary here"
```

---

## Terminal 2 — #1397: Open-source engineering software catalog

```
GitHub issue #1397. Survey, catalog, and index all open-source engineering software relevant to the workspace-hub ecosystem.

Cover these domains:
- FEA: CalculiX, Code_Aster, FEniCS, OpenSees, Elmer, MOOSE, deal.II
- CFD: OpenFOAM, SU2, Palabos, Nektar++
- O&G/subsea/marine: OpenDrift, OpenFAST, MoorDyn, MAP++, OrcaFlex (commercial but catalog it), Ashes
- CAD/CAE: FreeCAD, OpenSCAD, BRL-CAD, Salome-Meca
- GIS: QGIS plugins, GRASS GIS, PostGIS
- Doc intelligence: marker, docling, surya, nougat, unstructured
- Data/workflow: Apache Airflow, Prefect, DVC, MLflow

For each library collect via web search and GitHub API: name, repo URL, license, latest version, Python API availability, maturity (active/maintained/stale based on last commit), stars, contributors, download size estimate, and integration fit with digitalmodel.

Deliverables:
1. Master catalog: /mnt/local-analysis/workspace-hub/data/oss-engineering-catalog.yaml
2. Top 10 for immediate digitalmodel integration with rationale
3. Check which are already cloned to /mnt/ace/ — note gaps
4. Summary: /mnt/local-analysis/workspace-hub/.planning/oss-catalog.md
5. Update GitHub issue: gh issue comment 1397 -b "summary here"
```

---

## Terminal 3 — #1438: Bridge 1,987 extraction tables into federated index

```
GitHub issue #1438. Deep extraction produced 1,987 CSV tables from naval architecture textbooks, stored in extraction-report YAMLs under data/doc-intelligence/extraction-reports/. These tables are invisible to the query tool because index_builder.py only reads *.manifest.yaml files.

Steps:
1. Find and sample extraction reports: ls data/doc-intelligence/extraction-reports/*.yaml | head -20, then read 2-3 to understand the table metadata schema
2. Read the current index builder: scripts/data/doc-intelligence/index_builder.py (or find it via: find . -name "index_builder.py" -path "*/doc-intelligence/*")
3. Read the target index: data/doc-intelligence/tables/index.jsonl — understand the schema
4. Write a bridge script at scripts/data/doc-intelligence/bridge-extraction-tables.py that:
   - Scans all extraction-report YAMLs for table entries
   - Extracts: CSV file_path, parent document, page number, caption, column names, row count
   - Converts to the tables/index.jsonl schema
   - Appends to tables/index.jsonl with dedup by file_path
5. Run the bridge script
6. Verify the 1,987 tables are now queryable (test with the query tool if it exists)
7. Update GitHub issue: gh issue comment 1438 -b "summary here"
```

---

## Terminal 4 — #1406 + #1407 + #1415 + #1416: Infrastructure + docs cleanup (4 light items)

```
Execute these 4 light GitHub issues in sequence:

ISSUE #1406 — Create centralized machine registry:
Create /mnt/local-analysis/workspace-hub/config/machines/registry.yaml with entries for the 4 known machines: dev-primary (this machine, ace-linux-1), dev-secondary (dde storage), licensed-win-1, licensed-win-2. Per machine: hostname, IP/mount path, role, available software, storage paths. Check /mnt/remote/ for mount evidence and /mnt/ace/ structure for storage layout. Close issue when done.

ISSUE #1407 — Fix skills-curation cron:
Find the skills-curation cron script (check crontab -l, /etc/cron.d/, and .claude/ for cron configs). The issue is an invalid Claude CLI invocation. Fix the command syntax to use the correct claude CLI format. Test that it runs without error. Close issue when done.

ISSUE #1415 — Organize engineering-refs/ into subdirectories:
Sort /mnt/ace/docs/engineering-refs/ (currently flat with mixed PDFs, spreadsheets, misc) into subdirectories: dnv/, api/, drilling/, fea/, general/. Move files by matching filename patterns (DNV*, API*, ANSYS*, etc.). Leave ambiguous files in place. Close issue when done.

ISSUE #1416 — Review _archive- folders for permanent deletion:
Review /mnt/ace/docs/_archive-docker-examples/, _archive-github-references/, _archive-sd-python-docs/. For each: check file count, last modified date, whether contents are available elsewhere (e.g., on GitHub). Recommend keep or delete. If clearly safe to delete, do it. If uncertain, add a note and skip. Close issue when done.

For each issue: do the work, then close with gh issue close NUMBER -c "completion summary"
```

---

## Terminal 5 — #1419-1423: Fix 5 missing back-links (batch)

```
Fix 5 missing back-link issues. These are cross-reference links between skill/workflow files that were detected by a validation script.

ISSUE #1419 — Missing back-link: workspace-hub/workflow-gatepass should reference workspace-hub/
ISSUE #1420 — Missing back-link: workspace-hub/wrk-lifecycle-testpack should reference workspace-hub/
ISSUE #1421 — Missing back-link: workspace-hub/work-queue-workflow should reference data/
ISSUE #1422 — Missing back-link: data/research-literature should reference data/dark-intel
ISSUE #1423 — Missing back-link: data/calculation-report should reference data/dark-intel

For each issue:
1. Find the source file (search for workflow-gatepass, wrk-lifecycle-testpack, etc. in specs/, .claude/skills/, or docs/)
2. Understand what back-link is expected (a "Related" or "See also" reference to the target)
3. Add the missing cross-reference in the appropriate section of the source file
4. Close the issue: gh issue close NUMBER -c "Added back-link from X to Y"

Work through all 5 sequentially. If a source file cannot be found (specs/ was partially migrated), note it and close as won't-fix.
```
