I will start by locating the relevant files and examining their content to confirm the current implementation and line numbers for the planned changes.
I will expand the search to locate the files across the entire workspace, as they may be within one of the many top-level directories.
I will examine `report_generator.py` to identify the specific locations for fixing the `headings_deg` bug and adding the new title and subtitle fields.
I will now examine `benchmark_runner.py` to pinpoint the locations for adding the new configuration fields and threading them through the `BenchmarkRunner`.
I will now examine `validate_owd_vs_spec.py` to identify the appropriate locations for cleaning up stale flat reports and implementing the navigation links for multi-body reports.
I will now examine the `_generate_benchmark_report` method in `benchmark_runner.py` to determine the best approach for threading the new configuration fields into the report generation process.
I will begin by updating `report_generator.py` to fix the `headings_deg` bug, add the new `report_title` and `report_subtitle` fields to the `DiffractionReportData` class, and modify `_build_header_html` to incorporate these custom titles.
I will re-examine the `report_generator.py` file to verify the exact structure and content, ensuring I have the correct context for the replacement.
I'll search for the `report_date` definition within the `DiffractionReportData` class to ensure I have the correct context for adding the new fields.
I'll insert `report_title` and `report_subtitle` fields immediately following `report_date` within the `DiffractionReportData` class.
I will now modify `_build_header_html` in `report_generator.py` to incorporate the `report_title` and `report_subtitle` fields.
I'll examine `generate_diffraction_report` to locate the CSS definitions and add a style for the subtitle.
I will now add the CSS for `.report-header .subtitle`.
I'll correct the `old_string` by using double curly braces to match the f-string formatting in the file, and then I'll proceed with adding the CSS for `.report-header .subtitle` and `.nav-bar`.
I'll now address Step 1 and fix the `headings_deg` bug in `report_generator.py`.
I'm transitioning to `benchmark_runner.py` to begin Step 4, which involves adding the `report_title`, `report_subtitle`, and `navigation_html` fields to the `BenchmarkConfig`.
I will now proceed with Step 5, threading the new fields into the `report_data` within the `_generate_html_report` method.
I'll return to `validate_owd_vs_spec.py` to address Step 6, cleaning up stale reports, and Step 7, building the navigation HTML, after I've pinpointed the correct location for the latter.
I'll re-examine the start of the `run_comparison` function to find where the body loop is initiated.
I'll refine `run_comparison` to construct the `nav_html` and include it in `BenchmarkConfig`, and I'll ensure stale reports are cleaned up after the multi-body loop. I also need to verify the master summary's location to correctly set its relative path in the navigation. I'll check the `main` function in `scripts/benchmark/validate_owd_vs_spec.py` to see how the summary is generated.
`out_dir` in `run_comparison` is `OUTPUT_DIR / case_id / "benchmark"`. In `_run_case_pipeline`, the `run_comparison` function is called with various result and path arguments. I'll now examine `main` to locate the master summary.
I'll search `validate_owd_vs_spec.py` for `validation_summary.html` or any related summary generation terms.
Line 1662. Checking context.
`OUTPUT_DIR` is likely the parent of the case directories, and `validation_summary.html` resides there. Case reports are located in `OUTPUT_DIR / case_id / benchmark / body_n / benchmark_report.html`, making the relative path to the summary `../../validation_summary.html`. I've noted a discrepancy between `validation_report.html` and `benchmark_report.html` and will re-examine `BenchmarkRunner._generate_html_report` to confirm the default filename and whether it sets `result.report_html_path`.
Show me the conclusion of `_generate_html_report`.
I need to find the `generate_diffraction_report` call and the `html_path` return, so I'll check around line 620.
`BenchmarkRunner.run_from_results` calls `_generate_html_report`, assigning the returned `html_path` to `result.report_html_path`. I'll verify this in `benchmark_runner.py`.
`result.report_html_path` is confirmed. Moving to `validate_owd_vs_spec.py` for Steps 6 and 7. I'll construct a `nav_html` for multi-body cases, including active and inactive body links. Regarding coupling, since `coupling_report.json` isn't ideal for HTML linking, I'll investigate `BenchmarkPlotter.build_coupling_heatmap_html` in `benchmark_plotter.py` to see if I can link to the generated heatmap HTML, noting it might be per-pair.
Reading `benchmark_plotter.py`.
