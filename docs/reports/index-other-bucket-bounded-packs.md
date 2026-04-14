# Index-Level `other` Bucket — Bounded Context Packs

Generated: 2026-04-14T22:49:40.578217+00:00

## Scope

This report packages bounded candidate packs for issue #2247 using exact file-path allowlists.
The approved execution input for #2249 was `data/document-index/index.jsonl`, but that artifact is absent in this checkout.
To keep the issue moving without writing outside the owned paths, this run used the mounted fallback index at `/mnt/ace/docs/master-index.jsonl` and treated the output as a candidate-pack handoff rather than a fully reconciled authoritative writeback list.

## Input Reconciliation

- `registry.yaml` index-level `other` count: `44705`
- `data-audit-report.md` index-level `other` count: `44705`
- Repo-local `data/document-index/index.jsonl` present: `False`
- Execution surface used for this run: `mounted-master-index` at `/mnt/ace/docs/master-index.jsonl`
- Result: the authoritative 44,705-count baseline is corroborated by the repo audit artifacts but could not be re-counted locally because the repo-local live index file is missing.

## Immediate Execution Packs

| Priority | Pack ID | Action | Proposed Domain | Candidate Count | Selection Boundary |
|---|---|---|---|---:|---|
| 1 | `ace-project-pipeline-9427-itt-reclassify` | `reclassify_now` | `pipeline` | 681 | `disciplines/production/projects/9427_2pipeline_engg/05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001` |
| 2 | `ace-project-drilling-3824-calculation-allowlist` | `reclassify_now` | `drilling` | 266 | `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL` |
| 3 | `ace-project-drilling-31057-calculation-allowlist` | `reclassify_now` | `drilling` | 179 | `disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL` |
| 4 | `ace-project-misc-614-sewol-calculation-allowlist` | `reclassify_now` | `naval-architecture` | 274 | `disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL` |
| 5 | `ace-project-misc-614-sewol-report-allowlist` | `reclassify_now` | `naval-architecture` | 23 | `disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP` |
| 6 | `ace-project-misc-2100-package-engineering-calcs` | `reclassify_now` | `installation` | 103 | `disciplines/misc/projects/2100_blk31_slor_design/00_inbox/2100 BLK31 SLOR Design/300 Package Engineering` |
| 7 | `ace-project-drilling-3824-component-data-summarize-first` | `summarize_first` | `drilling` | 504 | `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data` |
| 8 | `ace-project-misc-2100-bp-documents-summarize-first` | `summarize_first` | `installation` | 720 | `disciplines/misc/projects/2100_blk31_slor_design/05_reports/2100 BLK31 SLOR Design/BP Documents` |

## Pack Details

### `ace-project-pipeline-9427-itt-reclassify`

- Action: `reclassify_now`
- Proposed domain: `pipeline`
- Candidate count: `681`
- Selection rule: `disciplines/production/projects/9427_2pipeline_engg/05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001` with doc classes `pdf-doc, specification, word-doc, procedure, report`
- #2247 writeback target: `#2247`
- Rationale: ITT, FEED, EPC, and deliverable-list documents are already grouped under a single pipeline-engg subtree and can be written back as a bounded pipeline reference pack.
- Example records:
  - `disciplines/production/projects/9427_2pipeline_engg/05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001/1. ITT/EPC - ANNEXURE 3 (Scope of Work).pdf`
  - `disciplines/production/projects/9427_2pipeline_engg/05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001/1. ITT/EPC - ANNEXURE 4 (Completion Schedule).pdf`
  - `disciplines/production/projects/9427_2pipeline_engg/05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001/1. ITT/EPC SOW-Appendices/Appendix 01-Study Reports/Buckling/AD41-2721626-G-24778_0.pdf`

### `ace-project-drilling-3824-calculation-allowlist`

- Action: `reclassify_now`
- Proposed domain: `drilling`
- Candidate count: `266`
- Selection rule: `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL` with doc classes `calculation, spreadsheet`
- #2247 writeback target: `#2247`
- Rationale: Macondo containment riser calculation workbooks are tightly clustered under the CAL subtree and represent a clean drilling-domain allowlist.
- Example records:
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL/1000 Mad Dog Riser/3824-CAL-1001-1 (Mad Dog Hang Off Model).xls`
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL/1000 Mad Dog Riser/3824-CAL-1002-1 (Current Profiles).xls`
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL/1000 Mad Dog Riser/3824-CAL-1002-2 (Return Period Current Profiles).xls`

### `ace-project-drilling-31057-calculation-allowlist`

- Action: `reclassify_now`
- Proposed domain: `drilling`
- Candidate count: `179`
- Selection rule: `disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL` with doc classes `calculation, spreadsheet`
- #2247 writeback target: `#2247`
- Rationale: The ENI riser calculation subtree contains explicit CAL-coded workbooks and is small enough for exact allowlist writeback in #2247.
- Example records:
  - `disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL/0000 - Phase 1/31057-CAL-0001-7 Remaining Fatigue Life Calculation (DRAFT).xlsx`
  - `disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL/0000 - Phase 1/31057-CAL-0002-1 Analysis vs. Metocean Data (CHECKED).xlsx`
  - `disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL/0000 - Phase 1/31057-CAL-0003-2 NOAA Current Data (CHECKED).xlsb`

### `ace-project-misc-614-sewol-calculation-allowlist`

- Action: `reclassify_now`
- Proposed domain: `naval-architecture`
- Candidate count: `274`
- Selection rule: `disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL` with doc classes `calculation, spreadsheet`
- #2247 writeback target: `#2247`
- Rationale: Sewol CAL workbooks are strongly engineering-specific and bounded to a single salvage-analysis subtree suitable for targeted reclassification.
- Example records:
  - `disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL/2000 ANSYS/614-CAL-0001-12 SewolWeightsV12 Full (FEA Weights Resolved).xlsx`
  - `disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL/2000 ANSYS/614-CAL-2001-10 (ANSYS FE Weights Calculations) - Verification.xlsx`
  - `disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL/2000 ANSYS/614-CAL-2005-03 (ANSYS SideLift BCs).xlsm`

### `ace-project-misc-614-sewol-report-allowlist`

- Action: `reclassify_now`
- Proposed domain: `naval-architecture`
- Candidate count: `23`
- Selection rule: `disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP` with doc classes `report`
- #2247 writeback target: `#2247`
- Rationale: The Sewol REP subtree is a small set of report-coded deliverables and is the cleanest report-only pack in the salvage archive.
- Example records:
  - `disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP/614-REP-0004-01 Sewol Salvage FEA Model Verification.pdf`
  - `disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP/614-REP-0004-02 Sewol Salvage FEA Model Verification.pdf`
  - `disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP/614-REP-0004-03 Sewol Salvage FEA Model Verification.pdf`

### `ace-project-misc-2100-package-engineering-calcs`

- Action: `reclassify_now`
- Proposed domain: `installation`
- Candidate count: `103`
- Selection rule: `disciplines/misc/projects/2100_blk31_slor_design/00_inbox/2100 BLK31 SLOR Design/300 Package Engineering` with doc classes `calculation, spreadsheet, report`
- #2247 writeback target: `#2247`
- Rationale: The 2100 package-engineering inbox subtree is a bounded calculation-heavy installation pack rather than a mixed correspondence archive.
- Example records:
  - `disciplines/misc/projects/2100_blk31_slor_design/00_inbox/2100 BLK31 SLOR Design/300 Package Engineering/312 Flexible Riser Jumper Pre-installation/ACL Frame and Clamp Designs (Internal).xls`
  - `disciplines/misc/projects/2100_blk31_slor_design/00_inbox/2100 BLK31 SLOR Design/300 Package Engineering/312 Flexible Riser Jumper Pre-installation/CTR Flexible Pre-Installation rev1 TdB.xls`
  - `disciplines/misc/projects/2100_blk31_slor_design/00_inbox/2100 BLK31 SLOR Design/300 Package Engineering/312 Flexible Riser Jumper Pre-installation/Calculations/2100-204-CAL-0001-1 Riser Designation (For Report & Drawings).xls`

### `ace-project-drilling-3824-component-data-summarize-first`

- Action: `summarize_first`
- Proposed domain: `drilling`
- Candidate count: `504`
- Selection rule: `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data` with doc classes `pdf-doc, word-doc, presentation, procedure, calculation, specification`
- #2247 writeback target: `#2247`
- Rationale: Component-data files are engineering-relevant but mixed enough that #2247 should summarize and normalize them before committing authoritative domain/path writeback.
- Example records:
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data/PIP/1 - Flexibles Jumpers/1 - General/Bend Stiffener Adapter/BS Adapter -Updated.doc`
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data/PIP/1 - Flexibles Jumpers/1 - General/Bend Stiffener/60D Material Data (Raw) @ 10 & 30 deg C.pdf`
  - `disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data/PIP/1 - Flexibles Jumpers/1 - General/Bend Stiffener/H70218-DT-001 - Bend Stiffener Design Package -  Document Transmittal.pdf`

### `ace-project-misc-2100-bp-documents-summarize-first`

- Action: `summarize_first`
- Proposed domain: `installation`
- Candidate count: `720`
- Selection rule: `disciplines/misc/projects/2100_blk31_slor_design/05_reports/2100 BLK31 SLOR Design/BP Documents` with doc classes `pdf-doc, specification, report, word-doc, plan`
- #2247 writeback target: `#2247`
- Rationale: BP document drops are bounded but mixed vendor/client material. They are good candidates for summary-first normalization before domain writeback.
- Example records:
  - `disciplines/misc/projects/2100_blk31_slor_design/05_reports/2100 BLK31 SLOR Design/BP Documents/Angola Block 31NE (PSVM) water chemistry modelling_Vs 2 0 (sent by BP embedded in DBA comments).doc`
  - `disciplines/misc/projects/2100_blk31_slor_design/05_reports/2100 BLK31 SLOR Design/BP Documents/BP Reliability/GP 78-03.pdf`
  - `disciplines/misc/projects/2100_blk31_slor_design/05_reports/2100 BLK31 SLOR Design/BP Documents/BP Reliability/GP 78-04.pdf`

## Remain Miscellaneous For Now

| Selection Rule | Candidate Count | Reason |
|---|---:|---|
| `path_prefix=disciplines/knowledge_skills/projects/ri/00_inbox/ri AND doc_class=email` | 31156 | Legacy RI inbox email pool is extremely large, mixed, and operationally expensive to normalize. Keep miscellaneous until a dedicated email/thread normalization issue exists. |
| `path_prefix=disciplines/knowledge_skills/projects/ri/05_reports/ri AND doc_class=pdf-doc` | 90798 | The RI report/pdf archive is a legacy bulk dump with mixed provenance and insufficient project boundaries for #2247-style bounded writeback. |

## #2247 Handoff Contract

- Consume `data/document-index/index-other-bucket-pack-manifest.yaml` as the canonical allowlist artifact.
- Resolve each `record_keys` file-path allowlist against the authoritative index on the #2247 execution machine.
- Write back only the allowlisted records for each pack.
- Preserve `provenance_note` so the fallback execution surface used here is visible in downstream review.

Expected authoritative writeback fields for each allowlisted record:

- `domain`
- `path_category`
- `path_subcategory`
- `review_note`
- `provenance_note`
