### Verdict: MAJOR

### Summary
The r2 direction is better on provenance and citation fail-closed behavior, but the shown implementation still has a blocking source-path correctness defect and enough unreviewable surface area in the truncated diff to avoid approval. The main issue is that the provenance README path appears to be resolved from the `digitalmodel` repo even though the staged artifacts and cited wiki path place the relevant concept/provenance material in sibling wiki repos.

### Issues Found
- [P1] `src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py`: `_repo_root()` returns `Path(__file__).resolve().parents[3]`, so `_resolve_ocimf_provenance_readme()` requires `digitalmodel/docs/data/OCIMF_CORPUS_README.md`. The review context says legal scans and artifacts span `digitalmodel`, `llm-wiki-acma`, and `llm-wiki`, and the citation sidecar points to `wikis/marine-engineering/...` / `wikis/acma-projects/...`; there is no evidence in the staged stat that `digitalmodel/docs/data/OCIMF_CORPUS_README.md` exists or is staged. This can make the calculation fail-closed in normal repo execution even when the licensed workbook is correctly supplied, or worse, validate against a stale local-only file not represented in the reviewed diff.
- [P2] `src/digitalmodel/naval_architecture/b1528_sirocco_current_heading_rudder_report.py`: the implementation imports `Citation` / `validate_citation` from `digitalmodel.citations.schema`, but the staged stat shows no schema file changes. If this module is new or changed outside the shown diff, the review payload does not include it; if it already exists, the tests should explicitly cover that `_citation_sidecar(result)` serializes citations without leaking the local workbook path. The shown preflight returns `Citation` objects and a raw `workbook_path`, so serialization boundaries matter.
- [P2] Review payload is truncated before the OCIMF workbook parsing/interpolation functions, `_citation_sidecar`, `_provenance`, HTML/PDF/DOCX generation, and the new tests. Those are the highest-risk parts for licensing leakage, coefficient provenance, and numeric correctness, so this cannot be approved from the supplied content even though 66 tests passed.

### Suggestions
- Resolve provenance through an explicit reviewed artifact path or configuration, and test the exact path. If the provenance README is intentionally in `digitalmodel`, include it in the diff/stat; if it belongs to a wiki repo, do not hardcode it under `digitalmodel` via `_repo_root()`.
- Add or verify tests that run `issue_2760_source_preflight()` with `OCIMF_WORKBOOK_PATH` set to a temp fixture and assert missing env, missing workbook, and missing provenance all fail with precise errors.
- Add a leakage test over all emitted JSON/MD/HTML/DOCX/PDF-manifest text artifacts asserting no absolute local workbook path and no coefficient corpus/table values are emitted beyond approved report-specific outputs.

### Questions for Author
- Where is `docs/data/OCIMF_CORPUS_README.md` expected to live at runtime: `digitalmodel`, `llm-wiki`, or another sibling repo?
- Can you provide the untruncated staged diff for `_provenance`, `_citation_sidecar`, workbook interpolation, and the new tests?
