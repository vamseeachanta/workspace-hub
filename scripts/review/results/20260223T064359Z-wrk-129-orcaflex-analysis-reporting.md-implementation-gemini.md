I will start by exploring the codebase to understand the existing patterns and locate the appropriate directories for the new OrcaFlex reporting module.
I will list the contents of the `src/digitalmodel` directory to understand its structure and find the correct location for the OrcaFlex solvers.
I will list the contents of the `src` directory to locate the relevant modules for the OrcaFlex analysis report framework.
I will list the contents of the `src/solvers` directory to find the OrcaFlex solver and any related reporting modules.
I will search for "orcaflex" throughout the codebase to identify its current location and any existing implementations.
I will list the contents of the `src/workspace_hub` directory to determine if it contains the OrcaFlex solvers.
I will search for the file `universal_runner.py` to gain more context about the analysis pipeline and its integration with OrcaFlex.
I will list the root directory once more to ensure I have a complete view of the project structure, specifically looking for the `digitalmodel` directory.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers/orcaflex` directory to understand the existing OrcaFlex implementation and identify where to integrate the reporting framework.
I will list the contents of the `digitalmodel/src/digitalmodel/solvers/orcaflex/reporting` directory to see if any reporting infrastructure already exists.
I will list the contents of the `models` and `section_builders` subdirectories within the OrcaFlex reporting module to determine the current state of implementation.
I will read the `report.py` and `geometry.py` model files to verify if they align with the specifications for WRK-129 and determine what work remains.
I will read the `geometry.py` file to confirm its implementation status and ensure it meets the requirements for the standardized report framework.
I will list the contents of the `section_builders` directory to assess the progress of Phase 2 and identify which sections still need to be implemented.
I will read the `header.py` section builder file to determine if it is a complete implementation or just a skeleton that needs further work.
I will read the `utils.py` file in the `section_builders` directory to check for the existence of an `_escape()` helper and see how it's implemented.
I will read the `report_generator.py` file to understand how it currently manages report generation and identify any necessary updates for mandatory/conditional sections and Plotly integration.
I will read the `css.py` file to verify its content and ensure it includes the necessary styles for the report, such as the dark header and responsive grid mentioned in the spec.
I will add the `_escape()` helper function to the `utils.py` file to centralize HTML escaping and ensure security across all section builders.
I will update the `header.py` file to use the newly created `_escape()` helper function from `utils.py`, ensuring consistent and secure HTML escaping.
I will read the `executive_summary.py` file to identify areas where `html.escape` is used and replace it with the `_escape()` helper function.
I will read the `design_checks.py` model file to verify how the `UtilizationData` and `DesignCheckData` classes are implemented, specifically checking the `pass_fail` logic and conflict detection.
I will search for all occurrences of `html.escape` within the `section_builders` directory to systematically replace them with the `_escape()` helper function.
I will update the `executive_summary.py` file to replace `html.escape` with the shared `_escape()` helper, ensuring consistent and secure HTML escaping.
I will update the `model_overview.py` file to replace `html.escape` with the `_escape()` helper function, ensuring consistent HTML escaping for the model overview section.
I will read the `model_overview.py` file to precisely identify the content and ensure an accurate replacement of `html.escape` with the `_escape()` helper.
I will now attempt to replace `html.escape` with the `_escape()` helper in `model_overview.py` using the correct file content as context.
I will read the `design_checks.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `design_checks.py` file to replace `html.escape` with `_escape()`, ensuring consistent HTML escaping while preserving intentional HTML badges in the summary table.
I will read the `geometry.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `geometry.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the geometry section.
I will read the `materials.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `materials.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the materials section.
I will read the `boundary_conditions.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `boundary_conditions.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the boundary conditions section.
I will read the `fatigue.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `fatigue.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the fatigue section.
I will read the `loads.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `loads.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the loads and environment section.
I will read the `other_structures.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `other_structures.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the other structures section.
I will read the `results_dynamic.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `results_dynamic.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the dynamic results section.
I will read the `results_extreme.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `results_extreme.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the extreme results section.
I will read the `results_static.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will read the `summary.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will now update the `summary.py` file to replace `html.escape` with the `_escape()` helper, ensuring consistent HTML escaping for the summary and recommendations section.
I will read the `appendices.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will read the `mesh.py` and `analysis_setup.py` section builder files to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will read the `analysis_setup.py` section builder file to identify and replace all instances of `html.escape` with the `_escape()` helper.
I will re-read `summary.py` to confirm that all `html.escape` calls have been successfully replaced with the `_escape()` helper.
I will read the `report_generator.py` file to identify any remaining `html.escape` calls and replace them with the `_escape()` helper for consistency.
I will check the installed version of `plotly` to ensure `PLOTLY_JS_VERSION` in `report_generator.py` is accurate and up-to-date.
I will search the codebase for "plotly-6.2.0.min.js" to see if its SRI hash is already documented or used elsewhere.
I will search for any occurrences of "plotly-" to identify the Plotly versions currently used in the project and their corresponding SRI hashes.
