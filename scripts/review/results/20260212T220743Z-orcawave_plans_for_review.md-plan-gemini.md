### Verdict: APPROVE

### Summary
The proposed work items form a coherent package to mature the hydrodynamics capabilities. WRK-130 establishes the necessary visualization standard, WRK-131 migrates a critical legacy workflow (Passing Ship) into the modern stack with a robust validation strategy against historical data, and WRK-132 addresses known accuracy gaps in the core solver benchmarking. The reliance on existing architectural patterns (Specs, Runners, Report Generators) significantly reduces implementation risk.

### Issues Found
- [P2] Important: **WRK-131 Phase 1 (Excel Extraction)**: Reverse-engineering `.xlsm` files can be non-trivial if the core logic resides in complex VBA macros rather than cell formulas. The plan assumes relatively straightforward extraction.
- [P3] Minor: **WRK-132 Phase 2 (Fixes)**: The "Likely causes" are hypotheses. If the root cause for the Barge Roll/Sway mismatch turns out to be fundamental solver theory differences (e.g., potential theory implementation details) rather than input parameters, the "Fix" phase might stall without a contingency to "Document and Accept" differences.

### Suggestions
- **WRK-130**: Ensure the `DiffractionReportData` schema is versioned. If the reporting requirements evolve (e.g., adding a new solver like WAMIT later), older JSON archives should still be readable.
- **WRK-131**: For Phase 5 (Benchmarks), consider creating a "Gold Standard" test case that is synthetic (not based on a client project) to serve as the permanent regression test in the repo, ensuring tests can run in CI without relying on local archive drives or sanitization.
- **WRK-132**: Add a step to explicitly check the "Remote Interaction" or "Multibody" settings in both solvers if not already covered. Discrepancies often hide in how solvers handle interaction frequencies or near-field formulations.

### Questions for Author
- **WRK-131**: Does the current Python environment have libraries capable of parsing `.xlsm` macro code if the logic is hidden in VBA (e.g., `oletools`), or will this require manual inspection of the Excel file?
- **WRK-131**: For the OrcaFlex integration, do we already have the license and `OrcFxAPI` python bindings confirmed and available in the execution environment?
