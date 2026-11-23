# Execution Manifest Schema

Human-readable companion to `execution-manifest.schema.yaml`.

An execution manifest is the reproducibility and evidence handoff record for E-L1 through E-L4. It links source IDs to commands, machines/providers, outputs, validation evidence, legal scan evidence, checksums, and review artifacts.

Minimum required fields are machine-tested in `tests/architecture/test_execution_layer_contract.py`.

## Fail-closed rules

- No inline raw data fields.
- Unknown source IDs require an explicit blocked registry kind tied to #2731/#2732.
- Report handoff requires tests, legal scan status, checksums, review artifacts, and `output_residency`.
- Public output residency requires promotion gates.
