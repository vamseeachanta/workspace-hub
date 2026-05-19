# Session note — public graph hardening RED test targets

Context: While hardening llm-wiki public graph manifests, a first RED test asserted an exact node count (`len(nodes) == 3`) for a fixture. That failed because the fixture legitimately created an additional eligible page (`overview.md`). The useful learning is not the specific count; it is that public graph tests should target contract violations directly.

## Durable pattern

When addressing adversarial findings on graph artifacts, write RED tests against public-safety and schema contracts, not incidental corpus shape.

Prefer tests that prove:

1. **No unresolved internal targets leak into public artifacts**
   - Create a markdown link or wikilink to a repo-relative path that is not part of the eligible tracked public corpus.
   - Assert generator output does not emit that unresolved value as `edges.target_node` and does not preserve it in summary unresolved-target lists unless the schema explicitly permits a sanitized aggregate count.
   - Assert validator rejects any edge whose `target_node` is not in `node_ids` for v1 public graphs.

2. **All output surfaces are scanned for private/source leakage**
   - Seed node fields, edge evidence, summary metadata, CSV mirrors, and Markdown report text with private-looking strings or forbidden source-scope markers.
   - Assert validator fails closed on every surface, not just JSONL.

3. **CSV mirrors are content-validated, not existence-checked**
   - Corrupt `nodes.csv` or `edges.csv` after generation.
   - Assert validator compares CSV headers/rows back to JSONL canonical output and fails on drift.

4. **Schema and generator stay aligned**
   - If `evidence_locator` / `derivation_rule` are required by the validator, tests should assert generator emits them and docs describe them.
   - If relation allowlists change, tests should cover both accepted and rejected relation names.

## Anti-pattern

Avoid RED assertions that encode fixture accidentals such as exact page count or edge count unless the test fixture is intentionally minimal and every created page is named in the assertion. Count-only failures obscure the real governance issue and can block legitimate corpus expansion.

## Closeout reminder

After implementing the fix, regenerate artifacts and rerun the validator against the current repo root. A test-only graph fixture passing is not enough; the checked-in artifacts must prove freshness and public-safety under the live corpus.
