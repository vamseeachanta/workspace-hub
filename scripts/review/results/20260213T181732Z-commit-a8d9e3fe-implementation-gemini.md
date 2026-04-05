I will begin by examining the existing OrcaFlex templates and the `modular_generator` to understand the project's conventions and validation requirements.
I will now read the `spec.yml` for the newly added `drilling_riser` and compare its structure and metadata with an existing template like `riser_catenary` to ensure stylistic consistency and verify the `modular_generator` integration.
I will read `docs/modules/orcaflex/library/templates/riser_lazy_wave/spec.yml` to further investigate the template styles and determine which one is the current standard.
I will search for the `modular_generator` code in `src/digitalmodel/solvers/orcaflex/modular_generator.py` to understand how it processes the `generic:` and higher-level abstraction sections.
I will search for the term `modular_generator` across the entire project to locate its definition and implementation.
I will now examine the `ProjectInputSpec` definition in `src/digitalmodel/solvers/orcaflex/modular_generator/schema/root.py` to understand how it handles different models.
I will examine `src/digitalmodel/solvers/orcaflex/modular_generator/schema/generic.py` to understand the `GenericModel` schema and compare it with the `drilling_riser/spec.yml` file.
I will check `docs/modules/orcaflex/library/templates/audit_results.yaml` to confirm that the quality scores and metadata align with the newly added specifications.
I will check the `docs/modules/orcaflex/library/templates/wind_turbine_fixed/spec.yml` file on disk to verify the `line_count` and investigate the discrepancy with `audit_results.yaml`.
I will read the `docs/modules/orcaflex/library/templates/wind_turbine_fixed/spec.yml` file to examine its contents and understand why the line count is significantly higher than expected.
I will examine the end of the file to determine if the length is due to the inclusion of `WingTypes`.
I will check the `git log` to determine if there have been any commits more recent than the one on Friday, February 13, 2026.
I will examine the `src/digitalmodel/solvers/orcaflex/modular_generator/builders/generic_builder.py` file to understand how `GenericVariableData` is utilized in `GenericModelBuilder`.
I will read `docs/modules/orcaflex/library/templates/installation_pull_in/spec.yml` to examine how it handles connections and compare it with the `jumper_rigid_subsea` template.
I will read `docs/modules/orcaflex/library/templates/installation_subsea/spec.yml` to further investigate the connection handling and determine if the discrepancy in the number of values is a consistent pattern.
I will examine `src/digitalmodel/solvers/orcaflex/modular_generator/extractor.py` to investigate whether the `MonolithicExtractor` has a bug that causes the discrepancy between the number of headers and values in the connection tables.
I will search for `ConnectionzRelativeTo` throughout the codebase to determine if the "off-by-one" error is a widespread issue in other template files.
I will read `docs/modules/orcaflex/library/templates/drilling_riser/spec.yml` around line 277 to examine the `ConnectionDeclination`, `ConnectionGamma`, `ConnectionReleaseStage`, and `ConnectionzRelativeTo` headers and their corresponding values.
I will examine `src/digitalmodel/solvers/orcaflex/modular_generator/builders/lines_builder.py` to see if the 8-value rows for 9-column headers are intentional and how the generator handles them.
I will check `docs/modules/orcaflex/examples/yml/C06/C06 CALM buoy.yml` to see the number of values in the rows corresponding to the 9-column connection header.
I will examine `scripts/audit_spec_library.py` to understand the logic behind the quality score calculations.
I will verify the existence of the source files listed in `catalog.yaml`: `jumper/plet_to_plem/monolithic/SZ.yml`, `examples/raw/B01/B01 Drilling riser.dat`, and `examples/raw/K02/K02 10MW fixed-bottom OWT.dat`.
I will read `docs/modules/orcaflex/library/templates/drilling_riser/spec.yml` around line 100 to examine the `MomentOfInertiaTensor` header and its associated values.
### Verdict: APPROVE

### Summary
The commit adds three comprehensive OrcaFlex templates (Subsea Jumper, Drilling Riser, and Fixed-bottom Wind Turbine), significantly expanding the library's reach into complex offshore structures. The templates follow the project's established `generic` model schema and include high-fidelity hydrodynamic and structural data derived from established OrcaFlex examples. While the wind turbine template was initially missing required aerofoil data, this was addressed in a subsequent fix.

### Issues Found
- [P2] Important: [docs/modules/orcaflex/library/templates/wind_turbine_fixed/spec.yml:1385] In this specific commit, the `WingTypes` AF01-AF30 are referenced by the turbine blades but omitted "for brevity" from the file. This makes the template unusable for model generation in its current state. (Note: Resolved in commit `318fa23`).
- [P3] Minor: [docs/modules/orcaflex/library/templates/audit_results.yaml:1, 155] The audit report renumbered/shuffled several `&id` tags for existing specs, creating unnecessary noise in the diff.

### Suggestions
- **Template Completeness**: For complex templates like the wind turbine, avoid omitting data "for brevity" in the primary spec file, as it breaks the self-contained nature of the library. If file size is a concern, consider a referenced data structure if supported by the generator.
- **Audit Stability**: Modify the audit script (`scripts/audit_spec_library.py`) to use stable identifiers (e.g., based on path hash) for YAML anchors rather than sequential IDs to reduce diff noise in future updates.

### Test Coverage Assessment
- **Manual Validation**: Verified that all source files referenced in `catalog.yaml` exist in the repository.
- **Schema Validation**: The templates were successfully validated against the `ProjectInputSpec` schema (reported as `schema_valid: true` in audit results).
- **OrcaFlex Convention**: Confirmed that the "8-value row for 9-header" connection format is a standard OrcaFlex YAML export convention and is handled correctly by the target software.
