# Ecosystem workflow registry — discovery manifest (#3284)

`workflow-manifest.json` is a single, provenance-stamped, ecosystem-wide
enumeration of every callable workflow across the tier-1 repos. It aggregates
each repo's own `docs/registry/workflows.yaml` so a consumer (Deckhand, an agent,
a CI gate) can discover and resolve a workflow without reading four registries.

- **Generator:** `scripts/workflow/generate_workflow_manifest.py`
- **Schema:** `workflow-manifest.schema.json`
- **Reference resolver:** [`deckhand/src/deckhand/capability_smoke.py`](../../../deckhand/src/deckhand/capability_smoke.py) — the manifest's per-workflow field-set is chosen to be exactly what this resolver's `resolve_workflow()` consumes, so a manifest entry round-trips through it.
- **Source registries:** the four tier-1 repos in `config/tier1-python-repos.txt` (`assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`), resolved via `scripts/lib/tier1_repos.py` — never hardcoded paths.

## Usage

```bash
# Regenerate the committed manifest snapshot:
uv run python scripts/workflow/generate_workflow_manifest.py --write

# Stale-detection gate (exit 1 if any repo's live registry hash drifts from the
# committed manifest; generated_at is excluded from the comparison):
uv run python scripts/workflow/generate_workflow_manifest.py --check
```

## How consumers read it

1. Pick a `workflow_id` (`repo:id@version`) directly, OR resolve a `routing_id`
   (`repo:id`) to its latest-stable `workflow_id` via `latest_by_routing_id`.
2. Feed the resolved ref to `capability_smoke.resolve_workflow()`, which uses the
   manifest's per-row `input` and the **top-level** `invocation` template
   (`{input}`-only substitution) to render the run command.
3. Driving the actual run via `run_workflow()` is #3282 scope; this manifest
   supplies the resolver inputs.

## Field-set (per the schema)

| Field | Meaning |
|---|---|
| `workflow_id` | `repo:id@version` — disambiguates duplicate ids across versions (D4). |
| `routing_id` | `repo:id` — unversioned routing key; resolve via `latest_by_routing_id`. |
| `version` / `status` / `latest` | the deckhand routing triple (unversioned row == v1). |
| `input` | per-row input, **preserved** — the resolver fails closed without it (D4). |
| `runtime` | per-row runtime (`offline` / `requires-license` / `fast` / `uv-python` / ...). |
| `invocation` | **top-level** registry template, `{input}`-only (D1). Never a per-row `test:` nodeid. Null + warning for pre-#3295 registries. |
| `license_gated` | `runtime == 'requires-license'` (D4). `data_source.network_required` does NOT set it. |
| `request_schema` / `response_schema` / `result` | structured passthrough — null when absent, **no `str` coercion** (D1; #3282 owns the shape). |
| `determinism` | reserved-null (D3/D6); #3283 (Wave 2) populates via a key-allowlist, not a registry heuristic. |

## Provenance + staleness

- Each `repos[]` entry carries `registry_sha256` (SHA-256 of the raw registry
  text) + best-effort `git_sha` + declared `schema_version` (recorded, never
  assumed — target is the v2 additive superset).
- `--check` recomputes each repo's registry hash and **fails closed** (exit 1)
  when any differs from the committed manifest, so a stale manifest is never
  silently served. `generated_at` is excluded so a no-op regeneration is a no-op
  diff.

## Notes

- Duplicate ids across versions are real today (`digitalmodel:mooring-fatigue`
  v1 stable+latest / v2 experimental); both appear as distinct `workflow_id`s and
  `latest_by_routing_id["digitalmodel:mooring-fatigue"]` resolves to `@1`.
- As of 2026-06-28: 136 callable rows across the 4 repos; exactly the 2
  `digitalmodel` `requires-license` rows are `license_gated`; `assetutilities`
  and `assethold` are pre-#3295 (no top-level `invocation` yet → null + warning).
