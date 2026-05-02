# Adversarial implementation review: workspace-hub #2452 inventory artifact

You are an adversarial reviewer. Do not praise. Find defects only.
Review the committed inventory artifact for whether it satisfies the approved #2452/#2468 slice.
Return APPROVE, MINOR, or MAJOR. MAJOR means must fix before treating this slice as complete.

## Expected contract
#2452 approved implementation slice:
- create durable checked-in inventory report before #2468 source-remediation edits
- file: worldenergydata/docs/ci/flake8-inventory-2026-04-23.md
- report must include exact command provenance, grouped rule-family counts, _cross_database_data.py outlier classification, representative non-outlier files, and note /tmp source was transient
- no source-code remediation in this slice


## Artifact under review
Path: worldenergydata/docs/ci/flake8-inventory-2026-04-23.md
Commit: 46061f36 docs(#2452): add durable flake8 inventory

```markdown
# Flake8 Inventory — worldenergydata main — 2026-04-23

## Provenance

- Parent issue: `workspace-hub#2452`
- Child owner for this durable inventory: `workspace-hub#2468`
- Generated: `2026-04-24T01:27:42Z`
- Repository root: `worldenergydata` nested repo
- Command: `uv run flake8 src/ --max-line-length=100 --extend-ignore=E203,W503 --exclude=__pycache__,*.egg-info,.git,.venv`
- Exit code: `1` (expected before remediation)
- Parsed flake8 findings: `4752`
- Raw transient source: `/tmp/2452-flake8-current.txt` in the execution session only; not a durable artifact

## Summary

- Total parsed findings: `4752`
- Unique files with findings: `280`
- Dominant outlier: `src/worldenergydata/marine_safety/_cross_database_data.py` with `4060` findings
- Purpose: durable grouped inventory before source-remediation edits, per #2452/#2468.

## Rule family counts

| Rule | Count |
|---|---:|
| `E231` | 3857 |
| `E501` | 421 |
| `F401` | 280 |
| `F841` | 44 |
| `E402` | 36 |
| `E722` | 26 |
| `F541` | 23 |
| `E741` | 19 |
| `E731` | 14 |
| `F402` | 9 |
| `E712` | 9 |
| `F601` | 8 |
| `F811` | 5 |
| `W291` | 1 |

## Pathological outlier

`src/worldenergydata/marine_safety/_cross_database_data.py` accounts for `4060` of `4752` parsed findings.

| Rule in outlier | Count |
|---|---:|
| `E231` | 3857 |
| `E501` | 203 |

This file is intentionally split to `workspace-hub#2467`. It should not be mixed into the first safe-rule cleanup wave.

## Non-outlier counts

| Rule outside outlier | Count |
|---|---:|
| `F401` | 280 |
| `E501` | 218 |
| `F841` | 44 |
| `E402` | 36 |
| `E722` | 26 |
| `F541` | 23 |
| `E741` | 19 |
| `E731` | 14 |
| `F402` | 9 |
| `E712` | 9 |
| `F601` | 8 |
| `F811` | 5 |
| `W291` | 1 |

## Top files by finding count

| Rank | File | Findings |
|---:|---|---:|
| 1 | `src/worldenergydata/marine_safety/_cross_database_data.py` | 4060 |
| 2 | `src/worldenergydata/bsee/reports/comprehensive/templates/economic_tables.py` | 26 |
| 3 | `src/worldenergydata/modules/well_production_dashboard/well_detail_views.py` | 19 |
| 4 | `src/worldenergydata/marine_safety/analysis/cause_report.py` | 15 |
| 5 | `src/worldenergydata/bsee/reports/comprehensive/hierarchical_aggregator.py` | 12 |
| 6 | `src/worldenergydata/canada/aer/api_client.py` | 11 |
| 7 | `src/worldenergydata/well_production_dashboard/well_production.py` | 11 |
| 8 | `src/worldenergydata/bsee/reports/comprehensive/templates/compliance_references.py` | 10 |
| 9 | `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 9 |
| 10 | `src/worldenergydata/marine_safety/analysis/correlation/deduplicator.py` | 9 |
| 11 | `src/worldenergydata/marine_safety/reports/quality_dashboard.py` | 9 |
| 12 | `src/worldenergydata/bsee/reports/comprehensive/visualizations/dashboard_builder.py` | 8 |
| 13 | `src/worldenergydata/cli/commands/landman.py` | 8 |
| 14 | `src/worldenergydata/well_production_dashboard/interactive_components.py` | 8 |
| 15 | `src/worldenergydata/bsee/data/_legacy/production_unclean_code.py` | 7 |
| 16 | `src/worldenergydata/bsee/data/_legacy/scrapy_production_data.py` | 7 |
| 17 | `src/worldenergydata/bsee/reports/comprehensive/exporters/excel_exporter.py` | 7 |
| 18 | `src/worldenergydata/common/legacy/ong_fd_components.py` | 7 |
| 19 | `src/worldenergydata/marine_safety/analysis/cause_statistics.py` | 7 |
| 20 | `src/worldenergydata/bsee/analysis/well_api12.py` | 6 |
| 21 | `src/worldenergydata/cli/commands/marine_safety.py` | 6 |
| 22 | `src/worldenergydata/common/legacy/wellpath3D.py` | 6 |
| 23 | `src/worldenergydata/marine_safety/scrapers/ntsb_scraper.py` | 6 |
| 24 | `src/worldenergydata/bsee/paleowells/cli.py` | 5 |
| 25 | `src/worldenergydata/bsee/reports/comprehensive/cli.py` | 5 |

## Top module areas

| Rank | Area | Findings |
|---:|---|---:|
| 1 | `src/worldenergydata/marine_safety/_cross_database_data.py` | 4060 |
| 2 | `src/worldenergydata/bsee/reports` | 99 |
| 3 | `src/worldenergydata/bsee/analysis` | 65 |
| 4 | `src/worldenergydata/bsee/data` | 45 |
| 5 | `src/worldenergydata/marine_safety/analysis` | 42 |
| 6 | `src/worldenergydata/cli/commands` | 33 |
| 7 | `src/worldenergydata/common/legacy` | 31 |
| 8 | `src/worldenergydata/modules/well_production_dashboard` | 31 |
| 9 | `src/worldenergydata/marine_safety/importers` | 17 |
| 10 | `src/worldenergydata/common/validation` | 13 |
| 11 | `src/worldenergydata/canada/aer` | 12 |
| 12 | `src/worldenergydata/well_production_dashboard/well_production.py` | 11 |
| 13 | `src/worldenergydata/marine_safety/reports` | 10 |
| 14 | `src/worldenergydata/marine_safety/scrapers` | 9 |
| 15 | `src/worldenergydata/metocean/clients` | 9 |
| 16 | `src/worldenergydata/testing/performance` | 9 |
| 17 | `src/worldenergydata/well_production_dashboard/interactive_components.py` | 8 |
| 18 | `src/worldenergydata/bsee/pipeline` | 6 |
| 19 | `src/worldenergydata/canada/common` | 6 |
| 20 | `src/worldenergydata/metocean/statistics` | 6 |
| 21 | `src/worldenergydata/bsee/paleowells` | 5 |
| 22 | `src/worldenergydata/canada/bcer` | 5 |
| 23 | `src/worldenergydata/hse/importers` | 5 |
| 24 | `src/worldenergydata/landman/providers` | 5 |
| 25 | `src/worldenergydata/marine_safety/cli_import.py` | 5 |

## First safe-rule cleanup guidance for #2468

- Start outside the pathological outlier file.
- Prefer mechanically safer first-pass families: `F401`, `E501`, and `E402`.
- Keep higher-risk semantic families such as `E722` and `F841` out of the first safe-rule wave unless independently planned and justified.
- Re-run the exact flake8 command after each cleanup slice and record residual counts for #2469.
- Final closure remains owned by #2469 and must include Black, isort, exact flake8, and GitHub Actions `Lint` green on `main`.

## Representative non-outlier findings

| File | Line | Col | Rule | Message |
|---|---:|---:|---|---|
| `src/validators/data_validator.py` | 205 | 23 | `F541` | f-string is missing placeholders |
| `src/validators/data_validator.py` | 210 | 27 | `F541` | f-string is missing placeholders |
| `src/worldenergydata/brazil_anp/production/well_production.py` | 15 | 1 | `F401` | 'typing.Optional' imported but unused |
| `src/worldenergydata/bsee/analysis/all_fields_runner.py` | 96 | 9 | `F841` | local variable 'days_col' is assigned to but never used |
| `src/worldenergydata/bsee/analysis/bsee_analysis.py` | 111 | 101 | `E501` | line too long (103 > 100 characters) |
| `src/worldenergydata/bsee/analysis/bsee_analysis.py` | 118 | 101 | `E501` | line too long (106 > 100 characters) |
| `src/worldenergydata/bsee/analysis/bsee_analysis.py` | 121 | 101 | `E501` | line too long (108 > 100 characters) |
| `src/worldenergydata/bsee/analysis/bsee_analysis.py` | 124 | 101 | `E501` | line too long (119 > 100 characters) |
| `src/worldenergydata/bsee/analysis/buckskin/buckskin_config.py` | 10 | 1 | `F401` | 'typing.List' imported but unused |
| `src/worldenergydata/bsee/analysis/buckskin/report.py` | 21 | 1 | `F401` | '.buckskin_config.BUCKSKIN' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/cost_calibration.py` | 34 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.classify_water_depth_band' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/cost_engine.py` | 21 | 1 | `F401` | 'typing.Optional' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/cost_engine.py` | 23 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.WaterDepthBand' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/cost_summary.py` | 26 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.ActivityType' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/cost_summary.py` | 26 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.ConfidenceLevel' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/regional_loader.py` | 22 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.ConfidenceLevel' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/report.py` | 24 | 1 | `F401` | 'typing.Optional' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/sanctioned_dataset.py` | 20 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.WaterDepthBand' imported but unused |
| `src/worldenergydata/bsee/analysis/cost/sanctioned_dataset.py` | 20 | 1 | `F401` | 'worldenergydata.bsee.analysis.cost.models.WellDepthBand' imported but unused |
| `src/worldenergydata/bsee/analysis/financial/analyzer.py` | 232 | 101 | `E501` | line too long (105 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/cash_flow_calculator.py` | 119 | 101 | `E501` | line too long (107 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/cli_interface.py` | 44 | 101 | `E501` | line too long (114 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 17 | 5 | `F401` | 'openpyxl.styles.Fill' imported but unused |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 17 | 5 | `F401` | 'openpyxl.styles.PatternFill' imported but unused |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 27 | 5 | `F401` | 'openpyxl.worksheet.table.Table' imported but unused |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 27 | 5 | `F401` | 'openpyxl.worksheet.table.TableStyleInfo' imported but unused |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 269 | 101 | `E501` | line too long (106 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 270 | 101 | `E501` | line too long (124 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 271 | 101 | `E501` | line too long (133 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 292 | 101 | `E501` | line too long (108 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/report_generator.py` | 302 | 101 | `E501` | line too long (104 > 100 characters) |
| `src/worldenergydata/bsee/analysis/financial/validators.py` | 169 | 9 | `E722` | do not use bare 'except' |
| `src/worldenergydata/bsee/analysis/forecasting/decline_analysis.py` | 9 | 1 | `F401` | 'dataclasses.field' imported but unused |
| `src/worldenergydata/bsee/analysis/forecasting/decline_cli.py` | 13 | 1 | `F401` | 'pandas as pd' imported but unused |
| `src/worldenergydata/bsee/analysis/forecasting/decline_cli.py` | 141 | 17 | `F541` | f-string is missing placeholders |
| `src/worldenergydata/bsee/analysis/forecasting/decline_plots.py` | 9 | 1 | `F401` | 'typing.Optional' imported but unused |
| `src/worldenergydata/bsee/analysis/forecasting/decline_plots.py` | 11 | 1 | `F401` | 'numpy as np' imported but unused |
| `src/worldenergydata/bsee/analysis/forecasting/decline_plots.py` | 174 | 31 | `F541` | f-string is missing placeholders |
| `src/worldenergydata/bsee/analysis/intervention/dashboard.py` | 793 | 101 | `E501` | line too long (105 > 100 characters) |
| `src/worldenergydata/bsee/analysis/intervention/drilling_report.py` | 13 | 1 | `F401` | 'numpy as np' imported but unused |
| `src/worldenergydata/bsee/analysis/intervention/drilling_report.py` | 17 | 1 | `F401` | 'worldenergydata.bsee.analysis.intervention.activity_aggregator.classify_activity' imported but unused |
| `src/worldenergydata/bsee/analysis/intervention/intervention_detail_report.py` | 12 | 1 | `F401` | 'numpy as np' imported but unused |
| `src/worldenergydata/bsee/analysis/intervention/well_design_analyzer.py` | 10 | 1 | `F401` | 'numpy as np' imported but unused |
| `src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` | 2 | 1 | `F401` | 'datetime' imported but unused |
| `src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` | 3 | 1 | `F401` | 'os' imported but unused |
| `src/worldenergydata/bsee/analysis/legacy/production_api12_original.py` | 210 | 9 | `F841` | local variable 'prod_cumulative_mmbbl_groups_by_field' is assigned to but never used |
| `src/worldenergydata/bsee/analysis/lower_tertiary/report_part1.py` | 18 | 1 | `F401` | 'pandas as pd' imported but unused |
| `src/worldenergydata/bsee/analysis/production_api12.py` | 166 | 9 | `F841` | local variable 'api12_df' is assigned to but never used |
| `src/worldenergydata/bsee/analysis/production_api12.py` | 185 | 9 | `F841` | local variable 'prod_cumulative_mmbbl_groups_by_field' is assigned to but never used |
| `src/worldenergydata/bsee/analysis/production_api12.py` | 385 | 101 | `E501` | line too long (128 > 100 characters) |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 381 | 9 | `E722` | do not use bare 'except' |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 586 | 13 | `E722` | do not use bare 'except' |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 783 | 101 | `E501` | line too long (123 > 100 characters) |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 784 | 101 | `E501` | line too long (116 > 100 characters) |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 806 | 21 | `E722` | do not use bare 'except' |
| `src/worldenergydata/bsee/analysis/well_api12.py` | 864 | 101 | `E501` | line too long (117 > 100 characters) |
| `src/worldenergydata/bsee/analysis/well_data_verification/audit/compliance.py` | 389 | 9 | `F841` | local variable 'validation_events' is assigned to but never used |
| `src/worldenergydata/bsee/analysis/well_data_verification/audit/compliance.py` | 506 | 101 | `E501` | line too long (106 > 100 characters) |
| `src/worldenergydata/bsee/analysis/well_data_verification/audit/compliance.py` | 684 | 21 | `E722` | do not use bare 'except' |
| `src/worldenergydata/bsee/analysis/well_data_verification/audit/database.py` | 440 | 9 | `E722` | do not use bare 'except' |

```

## Required output
Verdict: APPROVE | MINOR | MAJOR
Findings:
- [SEVERITY] finding with evidence
Checks performed:
- list concrete checks
