# Codex adversarial code review — digitalmodel 716

Verdict: **REQUEST_CHANGES — 1 MAJOR**. Review of the uncommitted candidate in the isolated validator worktree against approved revision 3. No native acceptance or deployment approval.

## C1 — MAJOR: sequence traversal fabricates proven General mapping context

`src/digitalmodel/solvers/orcaflex/yaml_timestep_validation.py`, `_inventory` and `inspect_source`, erase sequence edges from the path. A mapping inside the General value's sequence therefore receives the same `("General",)` path as a direct General mapping. `inspect_source` grants it known General placement. The existing validator skips its General-specific checks because the actual General value is a list.

Exact offline reproduction input:

```yaml
General:
 - DynamicsSolutionMethod: Implicit time domain
   ImplicitUseVariableTimeStep: true
   ImplicitVariableMaxTimeStep: 0.1
```

Observed through `validate_orcaflex_yaml(path)` on the candidate:

```text
general_sequence True []
```

That is `valid=True` with no diagnostics. The approved contract permits positive recognition in a General mapping; it does not grant list items inherited General scope. This also weakens the old unconditional rejection into a clean result for an unsupported placement. No native assertion about how OrcaFlex handles this malformed shape is needed to establish the unsupported static-certainty claim.

Required repair: preserve container-edge identity or otherwise prove that the mapping is the direct General value before granting known placement. A sequence-wrapped General mapping must yield an explicit unsupported/placement diagnostic, rather than clean recognition. Add a RED test for this exact shape and a nested sequence variant; retain ordinary direct-General acceptance and conservative bare-fragment handling. This is a bounded context-provenance correction, not a request for general nested-schema validation.

## Other checks and limits

- Read the complete new helper and validator diff, current General dispatch, recursive forbidden-property checks, and focused test file.
- Ran four temporary-file probes without native/API calls. The sequence case above was clean; splitting its setters across separate list items warned. An unknown solution-method string warned. A maximum scalar shared through an alias warned. These latter observations do not establish general alias correctness.
- Source inventory contains cycle detection and limits expanded visits/depth before dictionary loading. No unbounded cycle was reproduced in this review. Native/schema acceptance is not inferred from those guards.
- Reviewed scope retains generator bytes/settings, source-order ambiguity handling, unknown-section warnings and independent native/engineering gates. The reported 96 focused and 199 broader tests were parent-run evidence; this reviewer did not rerun or independently claim those totals.
- `git diff --check` passed. No source/test changes, commits or native executions were performed by this review. The owned temporary directory was removed by `TemporaryDirectory`; this report and parent-owned implementation files are expected residue.

This is one provider's verdict, not cross-provider consensus. Correction and a targeted verification of C1 are required before advisory code approval.
