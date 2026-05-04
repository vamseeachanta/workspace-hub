"""
CI smoke: workspace_hub importable + caller scripts compile.

Issue #2532. The Stage Prompt Drift Guard CI job depends on PEP 420 namespace
package resolution: src/workspace_hub/ has NO __init__.py (intentional namespace
package), so the import only succeeds when PYTHONPATH=src is set, because
pyproject.toml's setuptools `include = ["src*"]` installs the literal `src`
package, not `workspace_hub`.

Run with: PYTHONPATH=src python3 -m pytest tests/ci_smoke/test_workspace_hub_importable.py -v
"""
from __future__ import annotations

import importlib
import inspect
import os
import py_compile
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
RESOLVER_REL = Path("src/workspace_hub/workstations/resolver.py")
CALLER_PATHS = [
    REPO_ROOT / "scripts/analysis/claude_session_ecosystem_audit.py",
    REPO_ROOT / "scripts/analysis/provider_session_ecosystem_audit.py",
]


def test_workspace_hub_resolver_importable_with_pythonpath_src():
    """
    Asserts `from workspace_hub.workstations.resolver import WorkstationPathResolver`
    succeeds and the resolved module file is under src/workspace_hub/workstations/resolver.py.

    Pre-condition: PYTHONPATH=src is set (CI does this in enforcement-gate.yml).
    Run locally with: PYTHONPATH=src python3 -m pytest tests/ci_smoke/...
    """
    if "workspace_hub" in sys.modules:
        del sys.modules["workspace_hub"]
    for k in list(sys.modules):
        if k.startswith("workspace_hub."):
            del sys.modules[k]

    resolver_mod = importlib.import_module("workspace_hub.workstations.resolver")
    cls = getattr(resolver_mod, "WorkstationPathResolver")
    assert cls is not None, "WorkstationPathResolver class missing from resolver module"

    resolved_path = Path(inspect.getfile(cls)).resolve()
    expected_path = (REPO_ROOT / RESOLVER_REL).resolve()
    assert resolved_path == expected_path, (
        f"WorkstationPathResolver loaded from {resolved_path}, expected {expected_path}. "
        "If a colliding workspace_hub package is now earlier on sys.path, the namespace package "
        "resolution has shifted and this test catches the drift before the PR-time CI failure."
    )


@pytest.mark.parametrize("caller_path", CALLER_PATHS, ids=[p.name for p in CALLER_PATHS])
def test_audit_scripts_compile_under_pythonpath_src(caller_path):
    """
    Both audit scripts that import `workspace_hub.workstations.resolver` must
    pass py_compile when PYTHONPATH includes src. py_compile catches syntax
    errors but NOT ImportError; the import resolution is exercised by the
    paired test above. This test guards against syntax regressions in callers.
    """
    assert caller_path.exists(), f"Caller script missing: {caller_path}"
    py_compile.compile(str(caller_path), doraise=True)


def test_workspace_hub_import_fails_without_pythonpath_src(tmp_path):
    """
    Regression sentinel: with PYTHONPATH stripped of `src`, `import workspace_hub`
    must fail. If a colliding `workspace_hub` package ever appears earlier on
    sys.path (e.g., a sibling PyPI install, a new top-level workspace_hub/
    directory, or a pip-installable package added to dependencies), this test
    fails — surfacing the silent shadow before CI starts using the wrong package.
    """
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["HOME"] = str(tmp_path)

    result = subprocess.run(
        [sys.executable, "-c", "import workspace_hub.workstations.resolver"],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0, (
        "Expected `import workspace_hub` to FAIL without PYTHONPATH=src. "
        "If this passes, a colliding workspace_hub package is now resolvable from a "
        "default sys.path location and is silently shadowing src/workspace_hub. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr, (
        f"Expected ModuleNotFoundError in stderr; got: {result.stderr!r}"
    )
