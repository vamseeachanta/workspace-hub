# Workflow manifest freshness

The discovery freshness check compares a saved manifest with current registry
content. Matching source hashes alone do not establish that the saved workflows
and routing selections still describe those sources.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Document content comparison and a reproducible example to expose altered discovery data. |

## Scope and method

This contribution to initiative #3606 extends the existing discovery generator
from #3284 under #3281. It covers three slices:

1. Compare complete discovery content, including workflow payloads, routing,
   counts, warnings and format metadata, rather than registry hashes alone.
2. Reject missing or invalid saved evidence and unavailable source registries.
   Diagnostic snapshots remain writable, but cannot pass the freshness check.
3. Sort repository identities during generation and compare collections
   independently of ordering. Repeated repository selections are deduplicated.

The comparison removes only top-level `generated_at` and each repository's
best-effort `git_sha`, then sorts repository, workflow and warning collections.
It compares JSON representations to preserve scalar types: a boolean cannot
substitute for an integer. Duplicate JSON keys, duplicate collection identities
and non-finite JSON values are rejected. Diagnostics describe the failure class
without echoing manifest contents or filesystem locations.

The source contract is [the manifest schema](../registry/workflow-manifest.schema.json)
and [registry guidance](../registry/README.md). Format versions and default row
versions follow that existing contract. No engineering equations, empirical
coefficients or numerical acceptance tolerances apply.

## Worked example: inputs, method and answer

Run the following Python block from the repository root in an environment with
PyYAML. `TMPDIR` must name a writable scratch directory outside the checkout.
The example creates synthetic files there; it imports no workflow engine.

The input registry has two declared versions of `alpha`: version 1 is stable and
marked latest; version 2 is experimental. By the existing latest-stable rule,
the independent expected answer is `repoA:alpha@1`. There are two workflow rows
by direct enumeration. A new timestamp or unrelated commit leaves discovery
unchanged; replacing the selected input file changes it.

```python
import importlib.util
import json
import os
from pathlib import Path

module_path = Path("scripts/workflow/generate_workflow_manifest.py")
spec = importlib.util.spec_from_file_location("manifest_generator", module_path)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

scratch = Path(os.environ["TMPDIR"]) / "manifest-example"
registry_dir = scratch / "repoA" / "docs" / "registry"
registry_dir.mkdir(parents=True, exist_ok=True)
registry = registry_dir / "workflows.yaml"
# Version values and selection rule: workflow-manifest.schema.json, routing triple.
registry.write_text("""schema_version: 2
invocation: 'uv run python -m example {input}'
workflows:
  - id: alpha
    version: 1
    status: stable
    latest: true
    input: examples/alpha/input.yml
    runtime: offline
  - id: alpha
    version: 2
    status: experimental
    input: examples/alpha/experimental.yml
    runtime: offline
""", encoding="utf-8")


def resolve(slug):
    return scratch / slug


manifest = scratch / "manifest.json"
generator.write_manifest(manifest, slugs=["repoA"], resolve=resolve)
saved = json.loads(manifest.read_text(encoding="utf-8"))
# Independent enumeration: the input contains two rows.
assert saved["workflow_count"] == 2
assert saved["latest_by_routing_id"] == {"repoA:alpha": "repoA:alpha@1"}
clean = generator.check_stale(manifest, slugs=["repoA"], resolve=resolve)
assert clean == 0

# Keep the source registry and saved registry hash unchanged.
saved["workflows"][0]["input"] = "examples/alpha/replaced.yml"
manifest.write_text(json.dumps(saved), encoding="utf-8")
altered = generator.check_stale(manifest, slugs=["repoA"], resolve=resolve)
assert altered == 1
print(f"selected=repoA:alpha@1; rows=2; clean={clean}; altered={altered}")
```

Expected stdout:

```text
selected=repoA:alpha@1; rows=2; clean=0; altered=1
```

The altered case also reports a `STALE` diagnostic on stderr. Exit conventions
follow the generator's existing command contract: zero means agreement; one
means changed, invalid or unavailable evidence.

## Verification and limits

The generator test suite executes this example and covers altered workflow
fields, metadata, source changes, unreadable files, invalid JSON, duplicate
identities, unavailable registries and collection ordering. It uses synthetic
registries and an injected resolver; no external computation is performed.

Freshness does not authenticate authorship, approval, source rights or schema
references. It compares observations, without a filesystem transaction across
repositories. Registry changes during a check can require a repeat observation.
An explicitly empty readable registry is allowed; this is not evidence of wider
workflow coverage. Full request/response validation, execution, determinism
qualification, provider memory convergence and remote baseline enforcement remain
separate work. The initiative remains open. Independent provider review remains
pending before merge.
