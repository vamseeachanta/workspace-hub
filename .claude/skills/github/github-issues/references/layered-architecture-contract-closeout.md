# Layered Architecture Contract Closeout

Use for GitHub issue trees that split architecture into data, execution, and report layers and then implement machine-readable contracts/schemas.

## Durable lesson

Adversarial review can approve the broad architecture while still finding schema-level loopholes. Treat placeholder acceptance in machine-readable gates as a closeout blocker, not a cosmetic issue.

## Closeout checks before committing/closing

1. Re-run targeted tests for every changed contract/schema/fixture pair.
2. If a schema gate uses checksum fields to prove publication readiness, require real checksum shape, not just a non-empty string.
   - Good pattern: `^sha256:[a-fA-F0-9]{64}$`
   - Bad pattern: allowing placeholders such as `sha256:contract-checksum-required-at-publication`.
3. Replace fixture placeholder checksums with actual hashes from the current artifacts before claiming `report_eligible` or publication readiness.
4. Add at least one negative test proving placeholder checksum strings fail when the readiness flag is true.
5. Re-run the reviewer that found the blocker on the narrow patch before closeout when feasible.
6. Do not commit/close while any adversarial `MAJOR` remains unresolved, even when another provider returned `APPROVE`.

## Layer-specific routing reminder

- Data layer: distinguish raw data sources, private/local llm-wiki raw data, and public llm-wiki derivatives.
- Execution layer: bind input data, tools/code execution, compute/runtime evidence, and report handoff outputs.
- Report layer: output residency should mirror input/data residency unless an explicit promotion gate proves sanitization, legal/review approval, and evidence binding.
