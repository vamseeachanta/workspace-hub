# Public graph unresolved-target and agent-surface leakage hardening

## Trigger

Use this note when an llm-wiki-style public graph generator/validator is being closed after adversarial review, especially when schema text says unresolved/private/agent targets are excluded but generated edge artifacts still contain them.

## Durable lesson

Public-safe source-scope filtering is not enough if only nodes are filtered. Edge fields can still leak excluded surfaces through `target_ref`, `evidence_path`, `evidence_locator`, report summaries, or CSV mirrors.

The validator must scan every emitted artifact surface, not just node paths:

- JSONL node fields
- JSONL edge fields
- CSV mirrors
- summary JSON
- dated Markdown report

## Fail-closed rules

1. If the public schema says unresolved targets are dropped, `target_layer == "unresolved"` must be invalid in generated artifacts and validator allowlists.
2. Do not keep `unresolved` as an accepted target layer merely because it is useful during generator development. Development warnings belong in logs/summary diagnostics, not public v1 edge rows.
3. Agent instruction surfaces must be rejected anywhere in public artifacts, not merely excluded from node discovery:
   - `CLAUDE.md`
   - `AGENTS.md`
   - provider/runtime instruction files if the repo has equivalents
4. High-risk implementation/result relations must come only from emitted public curated link-map nodes. Basename checks are insufficient.
5. Curated high-risk parsing needs negative tests for zero URLs and multiple URLs, not only the successful exactly-one-URL case.

## Patch shape

Typical code changes:

- Generator: drop unresolved edges before dedupe/serialization.
- Validator: remove `unresolved` from allowed target layers and add an unconditional failure if encountered.
- Validator safety regex: reject `CLAUDE.md` / `AGENTS.md` literals across artifact strings.
- Tests: assert no unresolved target layers are emitted, assert agent-surface strings fail validation, and add direct regression for multiple-URL high-risk curated lines.
- Schema/report: keep wording aligned with the actual validator behavior.

## Validation order

After patching, rerun in order:

```bash
uv run pytest -q tests/test_public_graph_manifests.py
uv run python scripts/generate_public_graph_manifests.py --root . --date <YYYY-MM-DD>
uv run python scripts/validate_public_graph_manifests.py --root .
uv run pytest -q
bash /mnt/local-analysis/workspace-hub/scripts/legal/legal-sanity-scan.sh --repo=llm-wiki --diff-only
git diff --check
```

Then rerun adversarial review before issue closeout.
