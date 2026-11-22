# Installed-wheel resolver provenance

The smoke builds the repository's existing wheel, installs it in an isolated
external environment and checks every loaded concrete project module after an
in-memory resolver lookup. It complements the source and synthetic-layout tests;
it does not qualify other entry points or distribution resources.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-28 | Add an actual wheel installation because synthetic layouts cannot establish installed-module provenance. |

## Public smoke recipe

Run from the repository root with Python satisfying `project.requires-python`,
the existing `uv` executable and network access for build requirements and PyYAML.
Export `UV_BIN` for that executable and `TMPDIR` for a writable scratch directory
outside the checkout. Preserve the environment's configured `UV_CACHE_DIR`.
No project environment, editable installation or full dependency synchronization
is needed.

```sh
set -eu
: "${UV_BIN:?Set UV_BIN to the existing uv executable}"
: "${TMPDIR:?Set TMPDIR to scratch outside the checkout}"
export PYTHONDONTWRITEBYTECODE=1
smoke_scratch=$(mktemp -d "$TMPDIR/installed-wheel.XXXXXXXX")
"$UV_BIN" run --no-project python tests/ci_smoke/test_installed_wheel_provenance.py \
  --uv "$UV_BIN" --scratch "$smoke_scratch"
```

This command launches the public script as a subprocess. The script copies
`pyproject.toml` and `src` into a disposable source tree, excluding bytecode and
old build metadata. These are the current backend's required build inputs;
packaging metadata is copied unchanged. The declared setuptools backend builds
one wheel there. Build requirements are installed in a separate build environment.
The backend's build tree, temporary files, wheel, runtime environment and
`report.json` stay in scratch; dependency downloads use the configured uv cache.
A fresh scratch directory is required for each invocation, preventing stale-wheel
reuse. No wheel or environment output belongs in Git.

The runtime environment is created without pip or system site packages. Only
the wheel and its unconditional PyYAML requirement from wheel metadata are
installed, using `--no-deps`. The external interpreter verifies the installed
distribution names. It runs outside the checkout with `-I -B`, with `PYTHONPATH`,
Python installation overrides and inherited Git bindings removed. It obtains
purelib from its own `sysconfig`, checks the virtual environment and user-site
settings, and rejects checkout entries in `sys.path`.

## Route and independent membership oracle

The entry module is discovered by locating the resolver file in the wheel and
converting that member's path into an import name. With the current packaging
configuration, the actual entry is `src.workspace_hub.workstations.resolver`,
rather than the source-smoke name `workspace_hub.workstations.resolver`.
No import path or packaging configuration is changed to bridge that difference.

The independent route oracle follows these inspected files and static imports:

| Concrete module | Wheel member and reason |
| --- | --- |
| `src` | `src/__init__.py`, the installed top-level package initializer. |
| `src.workspace_hub.workstations` | `src/workspace_hub/workstations/__init__.py`, which imports the resolver. |
| `src.workspace_hub.workstations.resolver` | `src/workspace_hub/workstations/resolver.py`, the selected entry module; its other imports are standard-library modules and PyYAML. |

`src.workspace_hub` is a namespace package with no concrete file. The distinction
follows PEP 420: only a module whose spec has no origin and has submodule search
locations receives the namespace exception. A concrete module without a file is
rejected. Namespace search paths themselves are outside this concrete-file check.

The checker inventories Python module names from all wheel members, enumerates
already-loaded modules after the lookup, checks exact package boundaries for
additional project names, and checks resolved paths against purelib by path
components. Concrete project names must also appear in the wheel inventory and
match their wheel member. The separately specified route membership must be
present; a top-level package prefix alone cannot establish coverage. This route
has no lazy project imports. The disposable fixture also exercises a lazy import
before enumeration.

The exercise is exactly `WorkstationPathResolver({}).resolve_machine("unregistered")`,
whose expected result is `None`: hand inspection of `resolve_machine` shows that
an empty identifier mapping cannot supply a key. It reads no registry, calls no
service and uses no operational data. No packaged project resource is read by
the inspected initializers or resolver import. An audit hook rejects any file
open during construction and lookup, after import. This is an explicit absence
of resource coverage, not a packaged-resource provenance qualification.

## Adversarial placement fixtures

Each fixture imports actual files and completes the entry operation before the
provenance assertion. Expected membership and placement come from fixture writes,
independently of the checker. The top-level package and entry stay inside the
expected root. The entry imports `nested` immediately and `lazy` on invocation.

| Placement | Expected outcome and independent reason |
| --- | --- |
| Nested file in an outside directory | Rejected: the nested module's resolved path is outside the root, despite the top-level package being inside. |
| Nested file under sibling `purelib-extra` | Rejected: the string starts with `purelib`, but the directory component differs. |
| Nested file linked from inside to outside | Rejected: resolving the symlink escapes the root. Symlink creation/import must succeed; unsupported filesystems cause an acceptance error, never a skip. |
| All project files inside, unrelated package outside | Allowed: the exact expected project membership remains unchanged; a package whose name adds `_extra` does not share the project package boundary. |

The fixture's expected set is the package initializer plus its entry, nested and
lazy files, as written explicitly by the fixture. No expected value is obtained
by calling the provenance checker.

## Pytest verification

Run these commands serially with the repository's pytest configuration. A fresh
external base directory retains each run's artifacts. PyYAML is explicitly
supplied for the existing source-smoke test, which imports it directly.

```sh
"$UV_BIN" run --no-project --with pytest --with 'PyYAML>=6.0' python -m pytest \
  tests/ci_smoke/test_module_provenance.py -q -rA -p no:cacheprovider \
  --basetemp="$(mktemp -d "$TMPDIR/provenance-source.XXXXXXXX")"
"$UV_BIN" run --no-project --with pytest python -m pytest \
  tests/ci_smoke/test_installed_wheel_provenance.py -q -rA -p no:cacheprovider \
  --basetemp="$(mktemp -d "$TMPDIR/provenance-wheel.XXXXXXXX")"
```

Before this addition, the existing file collected and passed 15 cases with
PyYAML supplied, with no failures or skips. After the addition, that unchanged
file still passes all 15, and the new file collects and passes 5, with no failures
or skips. These counts are the cases listed by the two pytest runs, including
parametrization in the existing file; they are observations, not acceptance
threshold constants. The pytest-only baseline without PyYAML passed 13 and failed
2 at the unchanged dependency import; supplying the declared dependency resolves
those failures.

## Evidence boundaries and follow-up

- Source-smoke coverage remains in the unchanged `test_module_provenance.py`.
- Synthetic-layout and namespace fixtures remain in that same unchanged file.
- Real-wheel coverage is limited to the resolver construction and no-match lookup
  described above and all project modules loaded by that route.
- Resource coverage is absent; no packaged project resource is exercised.
- Other CLI routes, entry points and resources remain open under issue #3438.

The installed module names reflect the current wheel layout and do not repair
or qualify consumer import conventions. The module inventory handles this pure
Python wheel; extension modules and relocated wheel data would require additional
inventory rules. A future packaging change must update the independent oracle
through review rather than infer expected membership from the modules observed.

The fixture rules and expected lookup result above are derived directly from
file placement and the inspected static imports. The namespace citation is
PEP 420, *Implicit Namespace Packages*. Interpreter isolation and exit-status
conventions follow the Python command-line and subprocess interfaces; no
engineering coefficient or numerical tolerance is introduced.
