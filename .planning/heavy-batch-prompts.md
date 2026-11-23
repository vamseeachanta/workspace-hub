# Heavy Batch — 5 Terminals for 2x Window (after 1 PM CDT)
> Prepared 2026-03-26. Launch all 5 simultaneously after 1 PM CDT.

## Terminal 1: #1436 — Fix + restart ace_project batch (29.7% error rate)
```
The ace_project Phase B batch is running 10 shards but has a 29.7% error rate. The JSON parse fix was deployed but errors persist.

1. Check current shard status: grep "progress:" data/document-index/logs/claude-shard-*-20260326*.log | tail -10
2. Analyze error patterns beyond the JSON parse fix — sample 20 error lines from logs to categorize failure modes
3. Fix ALL identified issues in scripts/data/document-index/phase-b-claude-worker.py
4. Kill the 10 running shards (they're wasting API budget at 30% error rate): pkill -f phase-b-claude-worker
5. Verify shards stopped: ps aux | grep phase-b-claude-worker
6. Re-launch: bash scripts/data/document-index/launch-batch.sh 10 ace_project
7. Monitor first 5 minutes to confirm error rate drops below 5%
8. Close GitHub issue #1436 with results
```

## Terminal 2: #1360 — Extract algorithms from riser-eng-job (6,695 files)
```
Extract reusable engineering algorithms and methods from riser-eng-job archives.
Source: /mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/
File breakdown: 3,550 .xls, 3,064 .dat, 43 .xlsx, 29 .inp, 8 .m, 1 .vbs

1. Categorize the .dat files — are they FEA input/output (OrcaFlex, ABAQUS)? Sample 20 across subfolders
2. For .xls/.xlsx: extract sheet names and any named ranges/formulas using openpyxl/xlrd. Identify calc spreadsheets vs plain data
3. For .m files: extract function signatures, comments describing purpose
4. For .inp files: identify FEA software (ABAQUS, ANSYS) and analysis type
5. Build an algorithm catalog at /mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/algorithms.yaml:
   - file_path, software, analysis_type, description, reusability_score
6. For high-value items (reusable calcs, validated analysis templates): flag for migration to digitalmodel source
7. Write summary to .planning/ with recommendations on what to promote to reusable tools
8. Update GitHub issue #1360 with findings
```

## Terminal 3: #1397 — Open-source engineering software catalog
```
Survey, catalog, and index all open-source engineering software relevant to the workspace-hub ecosystem.

Domains: FEA (CalculiX, Code_Aster, FEniCS, OpenSees), CFD (OpenFOAM, SU2, Palabos), O&G/subsea/marine (OpenDrift, OpenFAST, MoorDyn, MAP++), CAD (FreeCAD, OpenSCAD, BRL-CAD), GIS (QGIS, GRASS, PostGIS), data science (pandas, scipy, scikit-learn), doc intelligence (marker, docling, surya), simulation (Elmer, MOOSE).

Per library collect: name, repo URL, license, latest version, Python API (y/n), maturity (active/maintained/stale), integration fit with digitalmodel, community size (stars/contributors), download size.

1. Web search for each domain to find comprehensive lists
2. For each library: check GitHub API for stars, last commit, license
3. Build master catalog at /mnt/local-analysis/workspace-hub/data/oss-engineering-catalog.yaml
4. Identify top 10 libraries for immediate integration with digitalmodel
5. For top 10: check if already cloned to /mnt/ace/, if not, clone them
6. Write summary + recommendations to .planning/
7. Update GitHub issue #1397
```

## Terminal 4: #1438 — Bridge 1,987 extraction tables into federated index
```
Deep extraction produced 1,987 CSV tables from naval architecture textbooks stored in extraction-report YAMLs. They're invisible to the query tool because index_builder.py only reads *.manifest.yaml files.

1. Find extraction reports: ls data/doc-intelligence/extraction-reports/*.yaml | head -20
2. Read a sample report to understand the table metadata schema
3. Read the current index_builder.py to understand manifest.yaml parsing
4. Read data/doc-intelligence/tables/index.jsonl to understand target schema
5. Write a bridge script (scripts/data/doc-intelligence/bridge-extraction-tables.py) that:
   - Scans all extraction-report YAMLs
   - Extracts table entries (file_path to CSV, parent doc, page, caption, columns, row_count)
   - Converts to index.jsonl format
   - Appends to tables/index.jsonl (dedup by file_path)
6. Run the bridge script
7. Verify: query.py --content-type tables should now find the new tables
8. Update GitHub issue #1438
```

## Terminal 5: #1363 — LLM domain-tag riser-eng-job literature (9,461 PDFs)
```
Apply LLM-based domain tagging to the riser-eng-job document catalog for digitalmodel cross-reference.

The catalog already exists: /mnt/ace/digitalmodel/docs/domain/subsea-risers/riser-eng-job/index.jsonl (9,461 records with doc_type, title, revision).

1. Read the existing index.jsonl to understand current fields
2. Read digitalmodel's domain taxonomy (check docs/domain/ directory structure for domain categories)
3. Design the tagging prompt: given title + doc_type + path, classify into domains (risers, moorings, VIV, fatigue, materials, installation, structural, flow-assurance, etc.)
4. For efficiency, use filename/title-based heuristic classification first (pattern matching) to handle the obvious 70%
5. For the remaining 30% ambiguous docs, use Claude batch classification (group by 50, single API call each)
6. Add domain_tags field to each record in index.jsonl
7. Create a domain-index.yaml mapping each domain to its document count and representative docs
8. Build cross-reference symlinks from digitalmodel/docs/domain/{domain}/ to tagged riser-eng-job docs
9. Update GitHub issue #1363
```

---

## Execution checklist
- [ ] Session reset (10 AM CDT) — fresh limits
- [ ] 10 AM–1 PM: close done issues, run Sonnet light batch
- [ ] 1 PM: open 5 terminals, paste prompts, launch simultaneously
- [ ] Monitor: check back at 2 PM, 3 PM for completion/errors
