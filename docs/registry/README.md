# Ecosystem workflow registry — discovery manifest (#3284)

`workflow-manifest.json` is a single, provenance-stamped, ecosystem-wide
enumeration of every callable workflow across the tier-1 repos. It aggregates
each repo's own `docs/registry/workflows.yaml` so a consumer (Deckhand, an agent,
a CI gate) can discover and resolve a workflow without reading four registries.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial history entry | 2026-10-22 | Separate repository discovery and registry failures from content drift; document linked-worktree resolution and structured check output. |

- **Generator:** `scripts/workflow/generate_workflow_manifest.py`
- **Schema:** `workflow-manifest.schema.json`
- **Reference resolver:** [`deckhand/src/deckhand/capability_smoke.py`](../../../deckhand/src/deckhand/capability_smoke.py) — the manifest's per-workflow field-set is chosen to be exactly what this resolver's `resolve_workflow()` consumes, so a manifest entry round-trips through it.
- **Source registries:** the four tier-1 repos in `config/tier1-python-repos.txt` (`assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`), resolved via `scripts/lib/tier1_repos.py` — never hardcoded paths.

## Usage

```bash
# Regenerate the committed manifest snapshot:
uv run python scripts/workflow/generate_workflow_manifest.py --write

# Stale-detection gate (fails on drift or unavailable comparisons;
# generated_at is excluded from the comparison):
uv run python scripts/workflow/generate_workflow_manifest.py --check

# Machine-readable classification for every compared repository:
uv run python scripts/workflow/generate_workflow_manifest.py --check --json
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
- `--check` recomputes each repo's registry hash and **fails closed** on content
  drift or an unavailable comparison. Exit zero requires every observation to
  be unchanged. Only valid hashes from successful saved and live observations
  are compared; equal null hashes cannot establish freshness. `generated_at`
  is excluded from comparison.

## Repository resolution and comparison states

The Python resolver tries an explicit base (argument or `TIER1_REPOS_BASE`),
then repositories nested in and beside the current checkout. It then uses
Git's common directory to try repositories nested in and beside the canonical
checkout. This works regardless of the linked worktree's nesting depth, without
guessing ancestor names. Linked checkouts with a `.git` file are accepted, as
are the existing `.git` directory and `pyproject.toml` markers. Existing
candidate precedence is preserved; duplicate physical locations are counted
once. Git child processes discard inherited Git bindings so a caller's
repository cannot redirect discovery or provenance.

The metadata basis is Git's [repository layout documentation](https://git-scm.com/docs/gitrepository-layout),
especially `commondir` and `worktrees` (consulted 2026-10-22). Bare repositories
and separate Git directories do not supply an inferred canonical checkout;
use `TIER1_REPOS_BASE` when metadata cannot establish the layout. This extends
the Python helper; the shell helper retains its existing discovery behavior.

Generation records `ok`, `missing-repository`, `missing-registry`, or
`invalid-registry`. Invalid covers unreadable or non-UTF-8 files, invalid YAML,
non-mapping registries, and malformed workflow lists or workflow IDs. This is
an aggregation structure check, not full validation of every descriptor field.
Malformed registries contribute no workflows and no usable hash.

The stale report gives exactly one classification per repository:

| Status | Evidence |
|---|---|
| `unchanged` | Successful saved and live observations with equal valid hashes. |
| `drifted` | Successful saved and live observations with unequal valid hashes. |
| `missing-repository` | Resolution fails or the resolved directory is absent. |
| `missing-registry` | The repository exists but its registry is absent. |
| `invalid-registry` | The live registry is unreadable or structurally invalid, or saved provenance cannot establish a valid comparison. |

JSON reports contain `ok` and `repos`, with `repo`, `status`,
`saved_registry_sha256`, and `registry_sha256` on each observation. A readable
live registry with missing, null, malformed, or unsuccessful saved provenance
has reason `invalid-saved-observation`; regenerate only after checking coverage.
A saved repository absent from the requested set is `missing-repository` with
reason `not-visited`, rather than an assertion that its bytes changed. Human
output lists actual drift separately from `UNAVAILABLE` observations and lists
unchanged repositories explicitly. Historical `unparseable-registry` saved
entries cannot establish a valid comparison either.

## Worked example

Inputs: five synthetic repositories initially contain identical valid registry
text. Keep `unchanged` intact, append a YAML comment to `drifted`, make `absent`
unresolvable, omit the registry in `no-registry`, and replace the registry of
`invalid` with a scalar. These are controlled inputs, not measured ecosystem
coverage.

Method: resolve each repository, read and parse its registry, validate the
aggregation structure, then compare a successful live hash with a successful
saved hash. A comment changes the hashed text even though it leaves the parsed
workflows unchanged. Missing or invalid evidence prevents comparison.

Answer: `unchanged` is unchanged; `drifted` is drifted; `absent` is a missing
repository; `no-registry` is a missing registry; `invalid` is an invalid registry.
The independent truth table partitions the five inputs into one unchanged,
one drifted and three unavailable observations. The check fails closed. No
engineering equation, coefficient or numerical acceptance limit applies.

The executable example is `test_worked_example_partitions_observations` in
`scripts/workflow/tests/test_generate_workflow_manifest.py`; its docstring
derives the expected partition directly from the inputs. Resolver tests in
`tests/quality/test_tier1_repo_path_resolver_py.py` create disposable linked
worktrees to compare canonical and nested discovery. No live manifest is
regenerated by these tests.

## Notes

- Duplicate ids across versions are real today (`digitalmodel:mooring-fatigue`
  v1 stable+latest / v2 experimental); both appear as distinct `workflow_id`s and
  `latest_by_routing_id["digitalmodel:mooring-fatigue"]` resolves to `@1`.
- As of 2026-06-28: 136 callable rows across the 4 repos; exactly the 2
  `digitalmodel` `requires-license` rows are `license_gated`; `assetutilities`
  and `assethold` are pre-#3295 (no top-level `invocation` yet → null + warning).
