# Codex adversarial plan review — digitalmodel 716

Verdict: **REQUEST_CHANGES — 1 MAJOR**. Advisory plan review only; no implementation or native execution approval.

Reviewed revision 1 of `docs/plans/2026-09-11-digitalmodel-716-validator.html`, SHA256 `d9688a93b646de6f1e3d974d32fe8f792121965c0f21c0a77b583353d061df54`, against digitalmodel `a7fe3775717db3f67ff1e4d4e8733c5a9f285357` and the case-level validation triage.

## C1 — MAJOR: local final values/order cannot establish inherited state at assignment

**Location:** Proposed validation contract, items 1–2; TDD table, first two rows.

The plan will categorically error on reversed local ordering, an explicitly disabled mode, or an explicitly incompatible solution method. It also promises unresolved inherited context will warn and excludes an include-state resolver. These contracts conflict when a setting follows the maximum assignment rather than precedes it.

A General overlay containing `ImplicitVariableMaxTimeStep: 0.5` followed by `ImplicitUseVariableTimeStep: true` could inherit an already-enabled implicit mode. The reversed local ordering alone does not prove failure. Similarly, setting the maximum and then disabling variable stepping does not establish that the maximum assignment occurred while disabled. An incompatible solution method written later has the same ambiguity. These examples are logical counterexamples to the proposed unconditional diagnosis, not claims of native-tested acceptance.

An intervening unresolved `includefile` can also change a mode established earlier in the local mapping. A local-prefix checker must not carry certainty across that boundary without proving the include's effect.

The existing validator labels ERROR as “Will definitely fail to load” (`src/digitalmodel/solvers/orcaflex/yaml_validator.py:22`). Replacing an unconditional nonexistent-property error with another unjustified definite-failure error would preserve the defect class this repair targets. Orcina documents sequential processing: [Text data files](https://www.orcina.com/webhelp/OrcaFlex/Content/html/Textdatafiles.htm).

**Required bounded correction:** specify state at the maximum assignment, considering only preceding effective local setters. Relevant later setters will not establish that state. When inherited context or an intervening include leaves it unknown, emit the planned unresolved-context warning. Retain errors for a definitely incompatible preceding state, invalid values, or known wrong placement. A reversed-order negative test will establish the incompatible preceding state explicitly; a bare reversed-order overlay will warn. This does not require a new include resolver.

Add RED fixtures for maximum-before-enable, maximum-before-disable, maximum-before-incompatible-method, and known local mode followed by an unresolved include before the maximum. Keep the generator ordering regression unchanged: canonical ordering remains desirable without claiming all alternate overlay orderings are invalid.

Duplicate-key caution within the same defect: `yaml.safe_load` collapses duplicate mappings, so its final dictionary cannot reliably reconstruct assignment order. Repeated relevant General mode/maximum keys or repeated General mappings must be detected before collapsing them, or treated as ambiguous with an unresolved-context warning. Add a fixture with a mode setter on both sides of the maximum. A bounded YAML-node ambiguity check is sufficient; no native interpretation or full include resolver is required. Parent proposed this safeguard after the initial finding; its implementation is not claimed here.

## Checks and limits

- Read the actual plan and current validator parsing/API, invalid-property set, section allowlist, and error-severity contract.
- Read `GeneralBuilder.build`, `GenericModelBuilder.build`, and `TestImplicitVariableMaxTimeStep`: the base builder sets implicit mode with variable stepping disabled; the generic builder deliberately enables/reorders/preserves active maxima. The plan must continue to preserve these output bytes and settings.
- Compared the plan with the triage's six active maxima and six warning section families. Recognition of these section names is explicitly limited in the plan; no additional defect is asserted merely because nested schema and native qualification remain out of scope.
- The plan reserves RED tests before edits, separate artifact review, and user approval. Mooring mechanics, restart serialization, and native qualification remain separate; this review grants no approval for those operations.
- No tests or native solver were run during this review. No cross-provider consensus is asserted. A source reread was first attempted from the hub worktree and failed because that source belongs to digitalmodel; the successful source reads cited above used the digitalmodel worktree.

Cleanup: only this review artifact was added by this task. Existing audit scratch, hub artifacts owned by the parent, and pre-existing stashes remain preserved as expected residue. No source changes or commits.
