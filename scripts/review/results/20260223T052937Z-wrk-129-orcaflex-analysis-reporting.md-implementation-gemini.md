I will begin by listing the contents of the `src` directory to locate the `digitalmodel` package and understand its structure.
I will check the `src/solvers` directory to see if the `orcaflex` module exists.
I will search for the string `digitalmodel` in the entire project to find its location.
I will check if the `src/digitalmodel` directory exists.
I will check if the `src/solvers/orcaflex` directory exists.
I will list the contents of the `digitalmodel` directory.
I will list the contents of the `digitalmodel/src` directory.
I will list the contents of the `digitalmodel/src/digitalmodel` directory.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers` directory.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers/orcaflex` directory.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting` directory.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models` directory.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/report.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/design_checks.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/geometry.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/report_generator.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/riser.py`.
I will list the contents of the `digitalmodel/tests/solvers/orcaflex/reporting` directory.
I will run the tests in the `digitalmodel/tests/solvers/orcaflex/reporting` directory using `pytest`.
I will try running the tests using `uv run pytest` from within the `digitalmodel` directory.
I will read the content of `digitalmodel/tests/solvers/orcaflex/reporting/test_report_generator.py` to see if the HTML injection security tests are present.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/base.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/__init__.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/header.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/model_overview.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/utils.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/results.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/design_checks.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/summary.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/css.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_dynamic.py`.
I will read the content of `digitalmodel/tests/solvers/orcaflex/reporting/test_section_builders.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/header.py` to include all required fields and ensure they are properly escaped.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/css.py` to include styles for the new header structure.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/model_overview.py` to ensure all user-supplied fields are HTML-escaped.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/summary.py` to escape `summary_notes` and `recommendations`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_dynamic.py` to ensure all labels and IDs used in HTML attributes and content are escaped.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/loads.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/materials.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/boundary_conditions.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/mesh.py`.
I will create a new test file `digitalmodel/tests/solvers/orcaflex/reporting/test_html_injection.py` to verify HTML injection security for all required fields.
I will run the newly created HTML injection tests using `uv run pytest`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/loads.py` to ensure all user-supplied fields are HTML-escaped.
I will update `digitalmodel/tests/solvers/orcaflex/reporting/test_html_injection.py` to use a simpler injection string and verify the expected escaped output.
I will run the updated HTML injection tests using `uv run pytest`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/base.py` to include section titles in the configuration and handle placeholder injection for mandatory sections.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/executive_summary.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/executive_summary.py` to return an empty string when no design checks are available, delegating placeholder responsibility to the renderer.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/geometry.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/geometry.py` to return an empty string when geometry data is missing.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/materials.py` to be "dumb".
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/boundary_conditions.py` to be "dumb".
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/mesh.py` to be "dumb".
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/loads.py` to be "dumb".
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/analysis_setup.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/analysis_setup.py` to be "dumb".
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_static.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_static.py` to be "dumb".
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/design_checks.py` to be "dumb".
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/appendices.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/other_structures.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/other_structures.py` to ensure all user-supplied fields are HTML-escaped.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_extreme.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/results_extreme.py` to ensure all user-supplied fields are HTML-escaped.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/fatigue.py`.
I will update `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/fatigue.py` to ensure all user-supplied fields are HTML-escaped.
I will run all tests in the `digitalmodel/tests/solvers/orcaflex/reporting` directory to ensure that my changes haven't introduced any regressions and that the mandatory section placeholders are working as expected.
I will update `digitalmodel/tests/solvers/orcaflex/reporting/test_section_builders.py` to reflect that section builders now return an empty string when data is missing, as per the new "dumb" builder specification.
I will run all tests in the `digitalmodel/tests/solvers/orcaflex/reporting` directory using `uv run pytest`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/pipeline.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/mooring.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/jumper.py`.
I will read the content of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/renderers/installation.py`.
I will check the installed version of Plotly using `uv run pip show plotly`.
I will use Google Web Search to find the SRI hash for Plotly version 6.2.0.
I will search for `orcawave` and `plotly` in the codebase to see how it's handled in existing reports.
