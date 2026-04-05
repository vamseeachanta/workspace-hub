I will start by exploring the codebase to verify the existing assets mentioned in the work items, specifically checking the hull library structure, benchmark scripts, and spec files, to ensure the feasibility and accuracy of the proposed plans.

I will locate the diffraction specification code, examine the hull panel catalog schema and the benchmark library script, and list the OrcaFlex library directory to assess the project's current state and identify any missing files or discrepancies.

I will list the contents of the `solvers` directory to confirm the presence or absence of the diffraction specification module, ensuring I have the complete context before finalizing my review.

### Verdict: REQUEST_CHANGES

### Summary
The proposed roadmap for expanding the hull library and standardizing benchmarks is generally well-structured, particularly the logic for hull cataloging (WRK-110) and RAO linking (WRK-115). However, a critical dependency failure exists: multiple plans rely on a `diffraction_spec` module and `mesh_converter.py` file that do not exist in the codebase. This invalidates the "Existing Assets" assumptions for the hull manipulation tasks.

### Issues Found
- **[P1] Critical**: **Missing Asset Dependency in WRK-110, WRK-116, WRK-117.** These plans list `src/.../diffraction_spec/mesh_converter.py` as an existing asset for reuse. My investigation of `src/digitalmodel/solvers/` shows only `orcawave`, `gmsh_meshing`, `orcaflex`, etc. The `diffraction_spec` directory and `mesh_converter.py` file are missing. The plans must be updated to either include the creation of these tools or reference the correct existing modules (likely within `orcawave` or `gmsh_meshing`).
- **[P2] Important**: **Potential Logic Duplication in WRK-128.** The "Property Routing" plan risks overlapping with the existing `GenericModelBuilder` and `ProjectInputSpec` logic in `src/.../modular_generator/`. The plan should explicitly define how the new "routers" interact with existing builders to avoid maintaining two parallel pipelines for transforming specs into OrcaFlex objects.
- **[P3] Minor**: **Ambiguous Asset Lifecycle in WRK-127.** The plan to "sanitize" templates in `docs/modules/orcaflex/library/tier2_fast` does not specify if the new templates will replace the existing raw examples or live in a new canonical location. This creates a risk of having "good" and "bad" specs co-existing without clear distinction for users.

### Suggestions
- **Correct the Asset Paths**: Update WRK-110, 116, and 117 to reflect reality. If `mesh_converter.py` needs to be built, move it to the "Scope" section. If it exists elsewhere (e.g., `solvers/orcawave`), correct the path.
- **Clarify RAO-Draft Sensitivity**: For WRK-115 (RAO Linking), ensure the schema explicitly handles draft matching. A hull can have multiple RAO sets for different drafts; the lookup logic must prevent using "Ballast" RAOs for a "Loaded" simulation.
- **Define Seed Strategy**: For WRK-126 (Benchmarking), add a check for models with fixed seeds in their input files, which would trivially pass "equivalence" but fail to test statistical variation.

### Questions for Author
- Is `diffraction_spec` intended to be a new module that abstracts over `orcawave` and `aqwa`, or should these tasks use the existing `solvers/orcawave` module?
- For WRK-128, should the "Property Router" be a standalone component or a refactoring of the existing `modular_generator` builders?
