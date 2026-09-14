# Digitalmodel716 — Claude plan review

Model: haiku; effort low; existing auth; empty setting sources; no session persistence; tools disabled; packet-only prompt.
Deadline120s. Exit: 0. Elapsed: 82.37s. Timed out: False.
Private temporary directory removed: True.
Raw stdout SHA256: 0f9c942bee775ae8a8f66b6f399a3c0a366154c3bf1c80e3f8eff4fa75d6a1cb
Pinned source: a7fe3775717db3f67ff1e4d4e8733c5a9f285357; full yaml_validator, generic builder lines131–285, generic timestep tests439–503, validator tests101–200.
Private context redacted if present; otherwise exact output.

## Reviewed file hashes

{
  "docs/reports/2026-09-11-orcaflex-validation-triage.json": "b900d5b3477263cfe385f6c6fa33a38a71266fb0e7f531dc0f78adb89dd99c09",
  "docs/plans/2026-09-11-digitalmodel-716-validator.html": "d9688a93b646de6f1e3d974d32fe8f792121965c0f21c0a77b583353d061df54",
  "docs/reports/2026-09-11-orcaflex-mooring-readiness.html": "339d5c59d486f7d797c87305fa717b8451beb431db05993f2a15a8aad9d71332"
}

## Actual stdout

**VERDICT: MINOR**

---

**Plan strengths:**
- Bounded scope: validator only; no generator/model-file changes
- Baseline evidence is thorough (441 YAML files, 6-error/19-warning inventory, reproduction command provided)
- Generator already preserves the property correctly (confirmed in baseline `generic_builder.py:252` and `test_generic_builder.py:443`)
- Physics isolation confirmed: validator accepts/rejects YAML; does not generate or serialize models
- Approval gates explicit and non-negotiable
- Acknowledged limitations (incomplete nested validation, mooring/native gaps delegated to #718)

---

**Material defects and required fixes:**

**1. Existing test incompatibility (TDD setup missing)**
The baseline test `test_implicit_variable_max_time_step` in `test_yaml_validator.py` currently expects `ImplicitVariableMaxTimeStep` to be invalid (ERROR). After the plan, this fixture becomes valid when variable stepping is enabled (the condition). The plan mentions "RED tests before implementation" but does not explicitly state this existing test must be **rewritten or replaced**.

*Fix:* Add to the plan: "The existing test `TestInvalidProperties.test_implicit_variable_max_time_step` will be removed and replaced by new conditional-property fixtures in the validator test suite that validate: (a) acceptance when `ImplicitUseVariableTimeStep=True` precedes the max value; (b) rejection when mode is False/absent or out of order."

**2. Property order enforcement unspecified**
The plan states validator will check "explicit mode and local order," but does not define the error for reversed order: if YAML has `ImplicitVariableMaxTimeStep: 0.5` **before** `ImplicitUseVariableTimeStep: true` in the same General section, should the validator error or warn? The generator baseline test (`test_use_flag_precedes_max_step`) enforces generator order, but the validator acceptance contract must match.

*Fix:* Add to the TDD table: "Reversed order (max before mode) in same General section: explicit ERROR 'ImplicitVariableMaxTimeStep must appear after ImplicitUseVariableTimeStep in the same General section.'"

**3. Re-audit execution and enforcement mechanism not specified**
The plan states "The 94-path re-audit will report elapsed time, every remaining finding and unchanged generated hashes," and later "any remaining context warning will stay unresolved instead of forcing a green total." This implies CI must actively enforce "warnings do not block merge" (distinct from errors). The plan does not specify: (a) which CI stage runs the 94-path audit, (b) how "unchanged hashes" are verified, or (c) what the rule-set is for warning-vs.-error exit codes.

*Fix:* Add to the plan: "Post-implementation, the 94-path re-audit will execute in the required CI check `cfd/yaml-validator-audit` using `pytest … tests/solvers/orcaflex/test_yaml_validator.py` with all 441 original YAML files. Exit code will be 0 if all errors are resolved and all generated hashes match `docs/reports/2026-09-11-orcaflex-local-example-inventory.json`. Warnings will not block merge; the audit report will be published as a PR artifact."

---

**Non-defects (adversarial check):**
- Six section names recognized but not fully validated: acknowledged and scoped ("Recognizing a top-level section does not validate nested data")
- Boolean parsing explicit-mode enforcement: deferred to TDD tests (acceptable, explicit in plan)
- Mooring pretension physics risk: correctly delegated to #718 and gated from native execution
- No model bytes changed: validator only; generator already correct

---

**Recommendation:** Approve after the three targeted clarifications above are inserted into "Artifact map" and "TDD, verification and acceptance" sections. All other elements (scope, evidence, gates, risk management) are sound.


## Actual stderr
