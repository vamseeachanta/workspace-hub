# Session note — public graph review-major remediation

## Context

During llm-wiki issue work on public-safe graph manifests, adversarial review flagged MAJOR issues around provenance, source boundaries, backlinks, stale validator contracts, and freshness validation.

The useful durable lesson is not the specific issue number; it is the contract-sync pattern for public knowledge graph artifacts.

## Failure shape observed

Targeted tests showed most behavior passing, with remaining failures concentrated in schema/documentation/validator drift:

- Generator had added provenance/backlink fields.
- Validator CSV header contracts still expected the older field set.
- Schema documentation did not mention new fields such as `source_scope`.
- A provisional relation, `blocked-by-clearance`, remained in the v1 validator allowlist after review said to remove it.
- Freshness validation existed but needed to be default/fail-closed rather than easy to skip accidentally.

## Fix pattern

When remediating public graph review majors:

1. Compare generator CSV/JSONL fields to validator field tuples.
2. Update JSONL and CSV parity tests to cover any new fields.
3. Update schema docs in the same patch; tests should assert key terms appear.
4. Remove rejected provisional relation names from all v1 allowlists and docs.
5. Compute backlinks from edges deterministically, then validate mirrors against JSONL.
6. Make current-corpus freshness validation default behavior; provide only an explicit test-only skip if required.
7. Run targeted tests before broader validation.

## Commands from the observed workflow

Targeted test shape:

```bash
uv run pytest tests/test_public_graph_manifests.py -q
```

Representative validator/schema files:

- `scripts/generate_public_graph_manifests.py`
- `scripts/validate_public_graph_manifests.py`
- `docs/schemas/public-graph-v1.md`

## Anti-patterns

- Updating the generator but leaving validator CSV headers stale.
- Treating Markdown schema docs as optional when tests and downstream agents rely on them.
- Allowing private/raw corpus provenance to leak into public graph artifacts.
- Keeping workflow-control relations in public v1 graph schemas after review rejection.
