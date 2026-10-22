"""Execute the testing standard's disposable CLI worked example.

Expected outcomes are derived independently from Python 3.11 command-line
path initialization and pytest 8.4 importlib/exit-code semantics, cited in the
standard. No production runner or repository test suite is invoked by a child.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs/modules/testing/TESTING_FRAMEWORK_STANDARDS.md"
PROMPT = ROOT / "scripts/review/plan-review-prompt.md"
START = "<!-- python-entrypoint-probe:start -->"
END = "<!-- python-entrypoint-probe:end -->"


def documented_recipe():
    text = STANDARD.read_text()
    assert START in text, "The canonical testing standard needs the CLI recipe"
    section = text.split(START, maxsplit=1)[1].split(END, maxsplit=1)[0]
    return section.split("```python\n", maxsplit=1)[1].split("```", maxsplit=1)[0]


@pytest.fixture(scope="module")
def example_results(tmp_path_factory):
    scratch = tmp_path_factory.mktemp("entrypoint contract")
    env = os.environ.copy()
    # Deliberately poison inherited inputs: the recipe must sanitize its children.
    env["PYTHONPATH"] = str(ROOT)
    env["PYTEST_ADDOPTS"] = "--invalid-inherited-option"
    env["PYTEST_PLUGINS"] = "missing_inherited_plugin"
    env["TMPDIR"] = str(scratch)
    # Test harness budget; not a product acceptance limit.
    env["PROBE_TIMEOUT_SECONDS"] = "30"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    recipe = scratch / "probe_entrypoint.py"
    recipe.write_text(documented_recipe())
    result = subprocess.run(
        [sys.executable, str(recipe)],
        cwd=scratch,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("location", ["checkout", "outside"])
@pytest.mark.parametrize("operation", ["collect", "run"])
def test_bootstrapped_script_imports_and_preserves_cwd(
    example_results, location, operation
):
    """Root bootstrap makes the sentinel importable; one target is collected.

    The sentinel checks its imported file, value and caller cwd on import.
    Therefore collection success also establishes those checks ran. Execution
    additionally exercises the single synthetic test body.
    """
    row = example_results[f"good-{location}-{operation}"]
    assert row["outcome"] == "OK"
    assert row["sentinel_seen"] is True
    assert row["test_body_seen"] is (operation == "run")


@pytest.mark.parametrize("location", ["checkout", "outside"])
@pytest.mark.parametrize("operation", ["collect", "run"])
def test_root_discovery_without_bootstrap_fails(example_results, location, operation):
    """Script directory lacks the root; importlib adds no package search path.

    Expected collection interruption follows from the deliberately omitted
    bootstrap, independently of whether the synthetic test body is requested.
    """
    row = example_results[f"broken-{location}-{operation}"]
    assert row["outcome"] == "INTERRUPTED"
    assert row["import_error"] is True
    assert row["sentinel_seen"] is False
    assert row["test_body_seen"] is False


def test_module_invocation_masks_the_broken_runner(example_results):
    """The module form adds checkout cwd; the broken script is never exercised."""
    assert example_results["module-checkout-collect"]["outcome"] == "OK"
    assert example_results["module-checkout-collect"]["sentinel_seen"] is True
    assert example_results["module-checkout-collect"]["test_body_seen"] is False


@pytest.mark.parametrize("location", ["checkout", "outside"])
def test_script_propagates_failed_test_exit_code(example_results, location):
    """The sole test deliberately asserts false; pytest reports TESTS_FAILED."""
    assert example_results[f"failing-{location}-run"]["outcome"] == "TESTS_FAILED"
    assert example_results[f"failing-{location}-run"]["sentinel_seen"] is True
    assert example_results[f"failing-{location}-run"]["test_body_seen"] is True


def test_plan_review_links_the_canonical_contract():
    """The review prompt points to the maintained standard instead of a copy."""
    assert "docs/modules/testing/TESTING_FRAMEWORK_STANDARDS.md" in PROMPT.read_text()
    assert "#python-cli-and-pytest-runner-entrypoint-review" in PROMPT.read_text()
