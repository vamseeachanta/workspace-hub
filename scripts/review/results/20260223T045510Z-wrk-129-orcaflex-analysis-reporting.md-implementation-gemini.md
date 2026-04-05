I will begin by exploring the directory structure to identify the correct location for the new OrcaFlex reporting module.
I will list the contents of the `src` directory to find the appropriate location for the OrcaFlex reporting module.
I will check the `src/solvers` directory to see if there are any existing solver implementations.
I will list the contents of the `src/models` directory to understand how models are structured in the project.
I will search for "digitalmodel" in the codebase to find its location and understand the project structure.
I will list the contents of the `src` directory again to see if `digitalmodel` is a subdirectory within it.
I will list the contents of `src/workspace_hub` to see if the `digitalmodel` or `solvers` are located there.
I will read the `src/solvers/base.py` file to understand the base class for solvers and follow the project's conventions.
I will read the `src/config/__init__.py` file to see how it handles different patterns and if it gives any clues about the `digitalmodel` location.
I will list the contents of the `src/utilities` directory to look for any clues or utilities related to `digitalmodel`.
I will read the `src/models/data_models.py` file to understand the existing data model structure and ensure consistency.
I will list the contents of the `digitalmodel` directory to confirm its existence and explore its structure.
I will list the contents of `digitalmodel/src/digitalmodel` to verify the internal package structure and find the solvers directory.
I will list the contents of `digitalmodel/src/digitalmodel/solvers` to find the orcaflex directory or where it should be created.
I will list the contents of `digitalmodel/src/digitalmodel/solvers/orcaflex` to see if the reporting directory already exists or if I need to create it.
I will list the contents of `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting` to see if there's any existing implementation that I should build upon or if it's empty.
I will read the `__init__.py` file in the reporting directory to understand what's currently exported.
I will read the `models/report.py` file to see the current state of the OrcaFlexAnalysisReport data model.
I will read `models/geometry.py` to verify if it aligns with the requirements for `GeometryData`, `LineProfileData`, and `KeyPointData`.
I will read `models/materials.py` to check the `MaterialData`, `LineTypeData`, and `CoatingData` models.
I will read `models/boundary_conditions.py` to verify the `BCData`, `SeabedModelData`, and `ConstraintData` models.
I will read `models/mesh.py` to confirm the `MeshData`, `SegmentData`, and `MeshQualityData` models.
I will read `models/other_structures.py` to check the `OtherStructuresData` and `AttachedStructureData` models.
I will read `models/loads.py` to verify the `EnvironmentData`, `LoadCaseData`, and `HydroCoeffData` models.
I will read `models/analysis.py` to check the `AnalysisSetupData` and `SolverSettingsData` models.
I will read `models/results.py` to confirm the `StaticResultsData`, `DynamicResultsData`, and `ExtremeResultsData` models.
I will read `models/design_checks.py` to verify the `DesignCheckData` and `UtilizationData` models, ensuring they follow the required pass/fail logic.
I will read `models/fatigue.py` to confirm the `FatigueResultsData` model.
I will read `css.py` to see the shared stylesheet and ensure it matches the specified design (dark header, white section cards, etc.).
I will list the contents of the `section_builders` directory to see which section builders have already been implemented.
I will read `section_builders/header.py` to see if it's a complete implementation or just a stub.
I will read `section_builders/executive_summary.py` to check the implementation of the executive summary, including the UC bar chart.
I will read `report_generator.py` to understand the main entry point and how the different sections are sequenced and rendered.
I will read `renderers/riser.py` to see how the riser-specific report is rendered and if it includes the mandatory sections and plots.
I will read `renderers/base.py` to understand the base renderer's logic and how it uses the section config to build the report.
I will list the contents of the `digitalmodel/tests/solvers/orcaflex/reporting` directory to see if the tests have been implemented and are passing.
I will run the tests in `digitalmodel/tests/solvers/orcaflex/reporting` to check the current status of the implementation and identify any failures.
I will run the tests using `uv run pytest` to ensure that the correct environment and dependencies are used.
I will read `tests/solvers/orcaflex/reporting/test_report_generator.py` to understand the current test coverage for report generation and see if more tests are needed.
I will read `tests/solvers/orcaflex/reporting/test_conflicts.py` to see how conflict detection between UC and pass/fail is tested.
I will list the contents of the `extractors` directory to see if the OrcFxAPI bridges have been implemented.
I will read `extractors/geometry_extractor.py` to see how it extracts data from OrcaFlex models and if it uses vectorised API calls as recommended.
I will read `results_extractor.py` to see if it follows the vectorised API calls for time histories and envelopes.
I will create `tests/solvers/orcaflex/reporting/test_models.py` to thoroughly test the Pydantic data models, ensuring they correctly validate data and handle default values as specified.
I will create `tests/solvers/orcaflex/reporting/test_section_builders.py` to verify that each section builder generates HTML with the correct anchors and structure, ensuring the report's navigation and layout are robust.
I will create `tests/solvers/orcaflex/reporting/test_renderers.py` to ensure that each structure-specific renderer correctly sequences and includes the necessary sections, confirming that the reports are tailored to each structure type.
I will read `renderers/pipeline.py` to see if it includes pipeline-specific sections like the KP chainage table and upheaval buckling check, ensuring the renderer meets the requirements.
I will run all the tests in `digitalmodel/tests/solvers/orcaflex/reporting`, including the newly created ones, to ensure that everything is working as expected.
I will read `section_builders/geometry.py` to understand its HTML structure and fix the assertion in `test_section_builders.py`.
I will update `tests/solvers/orcaflex/reporting/test_section_builders.py` to use `plotly-graph-div` instead of `plotly-chart` for asserting the presence of Plotly charts, ensuring the tests accurately reflect the generated HTML.
I will run the reporting tests again to verify that the fix for `test_geometry_builder_with_data` is working as expected.
I will read `renderers/jumper.py` to ensure that the jumper-specific sections are correctly implemented and included in the report.
I will read `renderers/mooring.py` to check the implementation of mooring-specific report sections.
I will read `renderers/installation.py` to verify the implementation of installation-specific report sections.
I will read `section_builders/utils.py` to see how `wrap_section` is implemented and if it handles mandatory vs. conditional sections correctly.
I will read `section_builders/design_checks.py` to verify the implementation of the UC heatmap and the pass/fail governing logic.
I will read `section_builders/results_dynamic.py` to check the implementation of dynamic result plots and envelopes.
I will read `section_builders/results_static.py` to ensure it includes the tension and bending moment profiles as required.
I will refactor `_build_design_checks_html` to include a Plotly heatmap when multiple check types and arc length positions are provided, fulfilling the requirement for a detailed utilization ratio visualization.
I will add a test case to `tests/solvers/orcaflex/reporting/test_section_builders.py` to verify that the design checks section correctly renders a heatmap when provided with multi-location data, ensuring the new logic is functional.
I will run the reporting tests again to confirm that all 20 tests, including the new design checks heatmap test, pass.
I will read `section_builders/materials.py` to ensure it includes the line type properties table and plots for section properties and submerged weight.
I will read `section_builders/boundary_conditions.py` to ensure it includes the BC annotation overlay and seabed reaction profile.
I will read `section_builders/mesh.py` to ensure it includes the segment length profile and adjacent ratio profile as required.
I will read `section_builders/loads.py` to ensure it includes the current profile and wave scatter diagram as required.
I will read `section_builders/analysis_setup.py` to ensure it includes the solver settings as required.
I will read `section_builders/results_extreme.py` to ensure it includes the MPM comparison chart as required.
I will read `section_builders/fatigue.py` to ensure it includes the fatigue damage and life profiles, and the rainflow matrix as required.
I will read `section_builders/summary.py` to ensure it includes the recommendations and summary notes as required.
I will read `section_builders/appendices.py` to ensure it includes the notation, design code formulas, and solver settings as required.
I will read `tests/solvers/orcaflex/reporting/test_renderers.py` and enhance it to verify that all mandatory anchors are present in the rendered HTML for different structure types.
I will run the reporting tests one last time to ensure that all 20 tests pass after the recent additions and changes.
I will update `GEMINI.md` to reflect that the design checks heatmap has been implemented and all tests are passing, marking the task as complete.
I will update `.gemini/GEMINI.md` to reflect the completion of all phases of WRK-129, including data models, section builders, renderers, and pipeline integration.
I will read `.gemini/GEMINI.md` to ensure I have the exact content for the replacement, avoiding any errors with whitespace or indentation.
I will read `digitalmodel/CLAUDE.md` to see if it contains the task list or any other information related to the project's progress.
I will read `digitalmodel/AGENTS.md` to see if it contains the canonical contract and task mappings.
I will list the contents of `digitalmodel/specs/wrk/WRK-129` to find the specification for WRK-129.
I will list the contents of `digitalmodel/docs/modules/orcaflex/reporting` to see if there are any example reports or additional documentation.
I will list the contents of `digitalmodel/docs` to see if I can find the orcaflex reporting documentation.
I will list the contents of `digitalmodel/docs/modules` to look for the orcaflex documentation.
I will list the contents of `digitalmodel/docs/modules/orcaflex` to see if there's a reporting subdirectory.
I will read `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/models/__init__.py` to verify that all the required data models are correctly exported.
I will read `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting/section_builders/__init__.py` to ensure all section builder functions are properly exported.
The OrcaFlex Analysis Report Standardization (WRK-129) has been completed and verified. 

Key implementations include:
- **Data Models**: Pydantic v2 models for all report sections, including unified pass/fail logic and conflict detection for design checks.
- **Section Builders**: Pure functions generating HTML for all 17 canonical sections, featuring Plotly-based visualizations (3D/2D profiles, histograms, envelopes, and a dynamic UC heatmap).
- **Renderers**: Strategy-based renderers for Riser, Pipeline, Jumper, Mooring, and Installation structure types, ensuring tailored report content.
- **Extractors**: Optimized OrcFxAPI bridges utilizing vectorised calls for high-performance data extraction.
- **Verification**: 21 new and existing tests cover model validation, HTML structure, anchor contracts, and structure-specific rendering.

The framework produces single-file HTML reports with sticky navigation, executive summaries with worst-case utilization highlighting, and detailed FEA setup and results documentation following the analyst's causal chain.

```bash
# Run verified tests
uv run pytest tests/solvers/orcaflex/reporting -v
```
All tests passed (21 passed).
