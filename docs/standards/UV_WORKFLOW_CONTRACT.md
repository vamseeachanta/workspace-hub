# UV workflow contract

From the repository root, a registered workflow shall run as
`uv run python -m <package> <input.yml>`. The module entrypoint shall pass the
YAML path to an engine, which shall select a router by exact `basename` equality.
An unknown basename shall raise an error and exit nonzero before producing output.
This standard includes an executable synthetic example; it does not establish
downstream adoption or install continuous-integration configuration.

## Revision history

| Revision | Date | What changed and why |
|---|---|---|
| Initial | 2026-10-27 | Define module invocation, distinguish registry formats and add a runnable example to expose routing and metadata drift. |

## Scope and implementation basis

The [original contract plan](../plans/2026-06-17-issue-3067-uv-workflow-contract-doc.md)
records the invocation and legacy registry proposal. The present interpretation
is grounded in the existing
[manifest generator](../../scripts/workflow/generate_workflow_manifest.py),
especially `normalize_row()`, `row_version()` and `build_manifest()`, and its
[fixture tests](../../scripts/workflow/tests/test_generate_workflow_manifest.py).
The [registry reference](../registry/README.md) describes the aggregate manifest,
which is distinct from a repository's source registry.

This change provides a contract and a runnable example only. Package migrations,
downstream registry edits, executable gate templates and deployment are deferred.
No engineering package, external dataset or solver is required by the example.

## Invocation and routing requirements

The working directory shall be the repository root. The input argument names a
YAML file; it is not a substitute subcommand or an inferred workflow selector.
The package's `__main__.py` shall parse that argument and call `engine(inputfile)`.
The engine shall load the mapping and inspect `cfg["basename"]`; it shall dispatch
only to a router registered for that exact string.

The required sequence is `__main__ -> engine -> exact basename -> router`.
Use equality or a dictionary keyed by complete supported strings. A test such as
`basename in "scaled_sum"` accepts substrings and violates this contract.
Unknown, missing or malformed routing keys shall fail before a router runs;
there shall be no default router, substring fallback or success with no work.

In this example, input and output paths are relative to the repository root.
The engine does not change the working directory. The router writes only the
declared result. Production adopters shall separately validate their input
schema, output containment, resource access and error reporting requirements.

## Source registry and version distinctions

Workflow repositories shall keep discovery metadata at
`docs/registry/workflows.yaml`. The hub hosts the standard and aggregate manifest;
the synthetic registry below is not a new live hub registry.

The legacy `schema_version: 1` proposal in the original plan used row fields
`id`, `basename`, `input`, `outputs`, `test` and `runtime`, with a command in
`runtime`. That historical command convention is not the current command source.
Legacy registries remain distinguishable by their declared version; aggregation
does not silently upgrade them. A legacy registry without top-level `invocation`
produces a null invocation and a warning, with no fallback to `test` or `runtime`.

The current additive `schema_version: 2` fixture and field interpretation follow
the linked generator tests (`REG_V2`) and registry reference:

| Field | Current meaning |
|---|---|
| Top-level `schema_version` | Declared source-registry format, recorded as supplied; not a workflow version or manifest-format version. |
| Top-level `invocation` | Module command template with only `{input}` substitution. A row-level command or `test` node is not a fallback. |
| Row `id` | Stable workflow identifier, distinct from the package name. |
| Row `basename` | Exact engine routing key; shall agree with the example YAML. |
| Row `input` | Repository-relative example YAML path, preserved by aggregation. |
| Row `outputs` | Repository-relative expected files or directories; shall agree with router output. |
| Row `test` | Test path or test node reference, separate from invocation. |
| Row `runtime` | Runtime classification such as `offline` or `requires-license`; no command is inferred from it. |
| Row `version`, `status`, `latest` | Workflow revision and selection metadata. Missing row version defaults to `1` in `row_version()`; missing status defaults to `stable`. |
| Row `request_schema`, `response_schema`, `result` | Structured descriptors passed through without string coercion, null when absent. The generator does not validate their full semantics. |
| Row `data_source` | Dependency metadata; a network-required flag does not imply a license requirement. |

The generator forms a qualified workflow identity from repository, row `id` and
row `version`. For unpinned selection it prefers a stable row marked `latest`,
then the highest stable version, then the highest version of any status.
The exact runtime value `requires-license` sets `license_gated`; the synthetic
example uses `offline`. `determinism` remains reserved null in the generator.
The aggregate manifest's own version is independent of source-registry version.
These are observed interpretation rules, not a claim that all registries have
already migrated or that aggregation enforces this entire standard.

For each registered revision, the input, routing key, invocation, test reference
and output declarations shall agree. Each supported workflow shall have a
registered runnable example and a passing test. Versioned rows may share an
example directory; raw directory counts need not equal registry row counts.
Consumers shall expose missing registry entries or unusable invocation metadata,
without inventing commands or silently executing another workflow. Registration
alone is discovery evidence, not permission or proof of readiness; see the
[offline readiness assessment](../registry/workflow-readiness.md).

## Runnable synthetic example

Copy each marked file below, without editing its contents, into an empty
repository root. The minimal project declares PyYAML and uses source-root imports;
it is not a wheel-building example. From that root run:

```bash
uv run python -m toy_workflow examples/workflows/scaled_sum/input.yml
uv run python tests/workflows/test_scaled_sum.py
```

### Synthetic arithmetic basis

The fixture's dimensionless values are deliberately chosen as `2`, `3` and `5`,
with multiplier `4`. The independent hand calculation is
`(2 + 3 + 5) * 4 = 10 * 4 = 40`. This paragraph is the source for the input
constants and expected total in both tests; no engineering constant is implied.
The project version `0.0.0` is arbitrary synthetic packaging metadata. Registry
schema `2` and workflow version `1` follow the linked `REG_V2` fixture; those
identifiers carry no arithmetic meaning.

<!-- example-file: pyproject.toml -->
```toml
[project]
name = "toy-workflow-example"
version = "0.0.0"
dependencies = ["PyYAML"]
```

<!-- example-file: toy_workflow/__init__.py -->
```python
"""Synthetic workflow package for the UV workflow contract."""
```

<!-- example-file: toy_workflow/__main__.py -->
```python
import argparse

from .engine import engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile")
    args = parser.parse_args()
    engine(args.inputfile)


if __name__ == "__main__":
    main()
```

<!-- example-file: toy_workflow/engine.py -->
```python
from pathlib import Path

import yaml

from .router import scaled_sum


def engine(inputfile):
    cfg = yaml.safe_load(Path(inputfile).read_text(encoding="utf-8"))
    if not isinstance(cfg, dict) or cfg.get("basename") != "scaled_sum":
        raise ValueError("unknown basename")
    return scaled_sum(cfg)
```

<!-- example-file: toy_workflow/router.py -->
```python
import json
from pathlib import Path


def scaled_sum(cfg):
    result = {"total": sum(cfg["values"]) * cfg["multiplier"]}
    output = Path(cfg["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return result
```

<!-- example-file: examples/workflows/scaled_sum/input.yml -->
```yaml
basename: scaled_sum
# Source: Synthetic arithmetic basis above; (2 + 3 + 5) * 4 = 40.
values: [2, 3, 5]
multiplier: 4
output: results/scaled_sum.json
```

<!-- example-file: docs/registry/workflows.yaml -->
```yaml
# Versions follow REG_V2 in the linked manifest-generator tests.
schema_version: 2
invocation: "uv run python -m toy_workflow {input}"
workflows:
  - id: scaled_sum
    version: 1
    status: stable
    latest: true
    basename: scaled_sum
    input: examples/workflows/scaled_sum/input.yml
    outputs: [results/scaled_sum.json]
    test: tests/workflows/test_scaled_sum.py
    runtime: offline
    result:
      kind: files
      outputs: [results/scaled_sum.json]
```

<!-- example-file: tests/workflows/test_scaled_sum.py -->
```python
import json
from pathlib import Path
import subprocess
import sys
import unittest


class ScaledSumTest(unittest.TestCase):
    def test_known_input(self):
        subprocess.run(
            [sys.executable, "-m", "toy_workflow",
             "examples/workflows/scaled_sum/input.yml"],
            check=True,
        )
        result = json.loads(Path("results/scaled_sum.json").read_text())
        # Source: Synthetic arithmetic basis; (2 + 3 + 5) * 4 = 40 by hand.
        self.assertEqual(result, {"total": 40})


if __name__ == "__main__":
    unittest.main()
```

The successful invocation writes `results/scaled_sum.json` containing
`{"total": 40}`, as calculated above. Changing only `basename` to `scaled` or
`scaled_sum_extra` shall exit nonzero with `ValueError: unknown basename`.
An unsuccessful invocation shall not create output; it does not delete an
earlier successful result. Test rejection in a fresh directory to distinguish
new output from a retained result.

## Packaging and future integration

An adopting package shall include runtime resources such as base configurations,
templates and package-loaded YAML in its built wheel, using the build backend's
package-data configuration. A successful run in a source checkout cannot prove
wheel contents. Verify a built wheel in a clean environment before claiming
installed-package support; that check is outside this source-only example.

A future CI implementation should provision a clean dependency environment,
enumerate registered revisions, invoke each declared example from the repository
root, assert declared outputs exist and are nonempty, and run the referenced
tests, including unknown-route rejection. Data-dependent workflows need an
offline fixture or an explicit live-dependency declaration. Licensed execution
needs its own authorized environment; metadata alone does not authorize it.
No executable CI template, hook or gate is supplied by this standard.

## Verification and limits

The [contract test](../../tests/docs/test_uv_workflow_contract_example.py) extracts
every marked file verbatim into temporary storage. It invokes the module through
the Python interpreter selected by UV, checks the independently calculated total,
rejects unknown basenames including substrings, runs the documented test reference
and compares the registry with `normalize_row()` without resolving sibling
repositories. It also checks local document links.

```bash
uv run --no-project --with pytest --with pyyaml python -m pytest tests/docs/test_uv_workflow_contract_example.py -q -rA -p no:cacheprovider
```

This verifies the source example and current normalization agreement. It does not
test UV dependency resolution inside a new project, wheel installation, downstream
package behavior, live readiness or CI adoption. The example is trusted synthetic
input and is not a production input-validation or filesystem-security library.
