"""Independent fixtures for the collection invariant in issue #3790.

Expected sets below are calculated by listing the fixture files and subtracting
the files with observed items or reasoned module skips, never by calling the
implementation to obtain an expected value. Hook semantics follow the pytest
reference: https://docs.pytest.org/en/stable/reference/reference.html#collection-hooks
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/testing/collection_audit.py"


@pytest.fixture
def audit():
    spec = importlib.util.spec_from_file_location("collection_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run_pytest(tmp_path, *, files=None, ini="", conftest="", args=(), collect_only=True,
               enabled=True):
    """Collect only synthetic code; do not load the surrounding repository."""
    root = tmp_path / "repo"
    root.mkdir()
    write(root, "pytest.ini", "[pytest]\n" + ini)
    for path, text in (files or {"tests/test_visible.py": "def test_ok(): pass\n"}).items():
        write(root, path, text)
    if conftest:
        write(root, "conftest.py", conftest)
    report = tmp_path / "report.json"
    env = {
        key: value for key, value in os.environ.items()
        if not key.startswith(("PYTEST_", "GIT_"))
    }
    env["PYTHONPATH"] = str(SCRIPT.parent)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "collection_audit",
         *(["--audit-test-collection", str(report)] if enabled else []),
         *(["--collect-only"] if collect_only else []), "-q",
         "-p", "no:cacheprovider", *args],
        cwd=root, env=env, text=True, capture_output=True, timeout=60, check=False,
    )
    if enabled:
        assert report.exists(), result.stdout + result.stderr
        return result, json.loads(report.read_text(encoding="utf-8"))
    assert not report.exists()
    return result, None


def rows(report):
    return {row["path"]: row for row in report["files"]}


def test_inventory_is_independent_of_pytest_filters(audit, tmp_path):
    """Hand inventory: both filename conventions and a configured extra pattern."""
    for name in ("test_one.py", "legacy/two_test.py", ".hidden/test_three.py",
                 "cases/check_four.py", "helper.py", ".git/test_internal.py"):
        write(tmp_path, name, "raise RuntimeError('must not import')\n")
    assert audit.inventory(tmp_path, ["check_*.py"]) == [
        ".hidden/test_three.py", "cases/check_four.py", "legacy/two_test.py", "test_one.py",
    ]


def test_inventory_does_not_follow_directory_links(audit, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "repo"
    root.mkdir()
    (root / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(audit.InventoryError, match="symlink-directory: linked"):
        audit.inventory(root)


def test_inventory_rejects_linked_candidate(audit, tmp_path):
    target = write(tmp_path, "helper.py", "")
    (tmp_path / "test_link.py").symlink_to(target)
    with pytest.raises(audit.InventoryError, match="symlink-file: test_link.py"):
        audit.inventory(tmp_path)


def test_inventory_requires_existing_directory(audit, tmp_path):
    with pytest.raises(audit.InventoryError, match="not a directory"):
        audit.inventory(tmp_path / "missing")


def test_inventory_surfaces_traversal_errors(audit, tmp_path, monkeypatch):
    def denied(*args, **kwargs):
        kwargs["onerror"](PermissionError("synthetic denied traversal"))
        return iter(())
    monkeypatch.setattr(audit.os, "walk", denied)
    with pytest.raises(audit.InventoryError, match="unreadable directory"):
        audit.inventory(tmp_path)


def test_inventory_cli_never_imports_tests(tmp_path):
    write(tmp_path, "test_inert.py", "raise RuntimeError('must not import')\n")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--inventory", str(tmp_path)],
        text=True, capture_output=True, timeout=60, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["status"] == "NOT_EVALUATED"
    assert report["files"] == [{"path": "test_inert.py", "status": "NOT_EVALUATED"}]


@pytest.mark.parametrize("ini,conftest,args,hidden", [
    ("testpaths = tests\n", "", (), "outside/test_hidden.py"),
    ("norecursedirs = legacy\n", "", (), "legacy/test_hidden.py"),
    ("", "", ("--ignore=legacy",), "legacy/test_hidden.py"),
    ("", "", ("--ignore-glob=legacy/*",), "legacy/test_hidden.py"),
    ("", "collect_ignore = ['legacy/test_hidden.py']\n", (), "legacy/test_hidden.py"),
    ("", "collect_ignore_glob = ['legacy/test_*.py']\n", (), "legacy/test_hidden.py"),
    ("", ("def pytest_ignore_collect(collection_path):\n"
     "    return collection_path.name == 'legacy' or None\n"), (), "legacy/test_hidden.py"),
])
def test_a_new_hidden_file_fails_the_guard(tmp_path, ini, conftest, args, hidden):
    """Hand difference: {visible, hidden} - {visible} = {hidden}, for each filter."""
    result, report = run_pytest(
        tmp_path, ini=ini, conftest=conftest, args=args,
        files={"tests/test_visible.py": "def test_ok(): pass\n",
               hidden: "raise RuntimeError('hidden files must not be imported')\n"},
    )
    assert result.returncode == pytest.ExitCode.TESTS_FAILED, result.stdout
    assert report["status"] == "FAIL"
    assert rows(report)[hidden]["status"] == "not_collected"
    assert "collection audit" in result.stdout.lower()


def test_every_pytest_file_is_collected_or_explicitly_excluded(tmp_path):
    """Hand difference: three files minus two collected and one skipped is empty."""
    result, report = run_pytest(tmp_path, files={
        "tests/test_visible.py": "def test_ok(): pass\n",
        "tests/test_conditional.py": "import pytest\n"
        "@pytest.mark.skipif(True, reason='synthetic unavailable platform')\n"
        "def test_conditional(): pass\n",
        "tests/test_module_skip.py": "import pytest\n"
        "pytest.skip('synthetic unavailable dependency', allow_module_level=True)\n",
    })
    assert result.returncode == 0, result.stdout + result.stderr
    assert report["status"] == "PASS"
    assert {r["status"] for r in report["files"]} == {"collected", "skipped"}
    assert rows(report)["tests/test_module_skip.py"]["reason"]


@pytest.mark.parametrize("marker", ["skip", "skipif(True)", "skip(reason='  ')"])
def test_exclusion_markers_carry_a_reason(tmp_path, marker):
    result, report = run_pytest(tmp_path, files={
        "test_condition.py": "import pytest\n"
        f"@pytest.mark.{marker}\ndef test_case(): pass\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED, result.stdout
    assert any("missing-marker-reason" in e for e in report["errors"])


def test_reason_as_positional_skip_argument_is_observed(tmp_path):
    result, report = run_pytest(tmp_path, files={
        "test_condition.py": "import pytest\n"
        "@pytest.mark.skip('explicit condition')\n"
        "def test_case(): pass\n",
    })
    assert result.returncode == 0, result.stdout
    assert rows(report)["test_condition.py"]["markers"] == [
        {"name": "skip", "reason": "explicit condition"},
    ]


@pytest.mark.parametrize("registered,reason,expected", [
    (True, "reason='synthetic dependency unavailable'", 0),
    (True, "", pytest.ExitCode.TESTS_FAILED),
    (False, "reason='synthetic dependency unavailable'", pytest.ExitCode.TESTS_FAILED),
])
def test_deselected_condition_requires_registered_reason(tmp_path, registered, reason, expected):
    result, report = run_pytest(
        tmp_path, ini="markers = conditional: synthetic condition\n" if registered else "",
        args=("-m", "not conditional"), files={
            "test_condition.py": "import pytest\n"
            f"@pytest.mark.conditional({reason})\ndef test_case(): pass\n",
            "test_visible.py": "def test_ok(): pass\n",
        },
    )
    assert result.returncode == expected, result.stdout + result.stderr
    assert rows(report)["test_condition.py"]["deselected_count"] == 1


def test_marker_on_hidden_file_cannot_excuse_invisibility(tmp_path):
    result, report = run_pytest(tmp_path, ini="norecursedirs = legacy\n", files={
        "test_visible.py": "def test_ok(): pass\n",
        "legacy/test_hidden.py": "import pytest\n"
        "@pytest.mark.skip(reason='plausible comment')\ndef test_hidden(): pass\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert rows(report)["legacy/test_hidden.py"]["status"] == "not_collected"


def test_empty_pytest_shaped_file_remains_unresolved(tmp_path):
    result, report = run_pytest(tmp_path, files={
        "test_visible.py": "def test_ok(): pass\n", "test_empty.py": "# no tests\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert rows(report)["test_empty.py"]["status"] == "not_collected"


def test_nonstandard_patterns_extend_the_inventory(tmp_path):
    result, report = run_pytest(tmp_path, ini="python_files = check_*.py\n", files={
        "check_visible.py": "def test_ok(): pass\n",
        "test_hidden.py": "def test_hidden(): pass\n",
        "hidden_test.py": "def test_other(): pass\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert set(rows(report)) == {"check_visible.py", "test_hidden.py", "hidden_test.py"}
    assert rows(report)["check_visible.py"]["status"] == "collected"


def test_collection_error_never_becomes_a_pass(tmp_path):
    result, report = run_pytest(tmp_path, files={"test_broken.py": "def broken(\n"})
    assert result.returncode == pytest.ExitCode.INTERRUPTED
    assert report["status"] == "FAIL"
    assert rows(report)["test_broken.py"]["status"] == "collection_error"


def test_partial_path_selection_does_not_claim_full_coverage(tmp_path):
    result, report = run_pytest(tmp_path, files={
        "test_one.py": "def test_one(): pass\n",
        "test_two.py": "def test_two(): pass\n",
    }, args=("test_one.py",))
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert rows(report)["test_two.py"]["status"] == "not_collected"


def test_runtime_failure_preserves_pytest_exit_code(tmp_path):
    result, report = run_pytest(tmp_path, files={"test_fail.py": "def test_fail(): assert False\n"},
                                collect_only=False)
    # Collection coverage does not certify the result of executing the tests.
    assert result.returncode == pytest.ExitCode.TESTS_FAILED, result.stdout
    assert report["status"] == "PASS"


def test_report_contains_only_relative_paths(tmp_path):
    result, report = run_pytest(tmp_path)
    assert result.returncode == 0
    assert str(tmp_path) not in json.dumps(report)
    assert rows(report)["tests/test_visible.py"]["item_count"] == 1


def test_empty_module_skip_reason_fails(tmp_path):
    result, report = run_pytest(tmp_path, files={
        "test_visible.py": "def test_ok(): pass\n",
        "test_skip.py": "import pytest\npytest.skip('', allow_module_level=True)\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert any("missing-module-skip-reason" in e for e in report["errors"])


def test_empty_inventory_cannot_claim_a_pass(tmp_path):
    result, report = run_pytest(tmp_path, files={"helper.py": "# no candidates\n"})
    assert result.returncode == pytest.ExitCode.NO_TESTS_COLLECTED
    assert report["status"] == "FAIL"
    assert "empty-inventory" in report["errors"]


def test_ignore_rules_do_not_shrink_the_inventory(tmp_path):
    result, report = run_pytest(tmp_path, ini="norecursedirs = .hidden\n", files={
        "test_visible.py": "def test_ok(): pass\n",
        ".gitignore": ".hidden/\n", ".hidden/test_hidden.py": "def test_hidden(): pass\n",
    })
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert rows(report)[".hidden/test_hidden.py"]["status"] == "not_collected"


def test_unfinished_collection_is_explicit(tmp_path):
    result, report = run_pytest(tmp_path, conftest=
        "import pytest\ndef pytest_collection(session):\n"
        "    pytest.exit('synthetic interruption', returncode=2)\n")
    assert result.returncode == pytest.ExitCode.INTERRUPTED
    assert report["status"] == "FAIL"
    assert "collection-incomplete" in report["errors"]


def test_generated_hidden_candidate_is_detected(tmp_path):
    result, report = run_pytest(tmp_path, conftest=
        "from pathlib import Path\ndef pytest_collection_modifyitems(items):\n"
        "    path = Path('legacy/test_generated.py')\n"
        "    path.parent.mkdir()\n"
        "    path.write_text('def test_generated(): pass')\n")
    assert result.returncode == pytest.ExitCode.TESTS_FAILED
    assert rows(report)["legacy/test_generated.py"]["status"] == "not_collected"


def test_parent_traversal_is_outside_the_audited_root(audit, tmp_path):
    instance = audit.CollectionAudit.__new__(audit.CollectionAudit)
    instance.root = tmp_path
    instance.errors = set()
    assert instance.relative("../outside.py") is None
    assert instance.errors == {"outside-root-collection"}


def test_loading_plugin_without_option_preserves_collection(tmp_path):
    result, report = run_pytest(tmp_path, ini="testpaths = tests\n", enabled=False, files={
        "tests/test_visible.py": "def test_ok(): pass\n",
        "legacy/test_hidden.py": "raise RuntimeError('must stay unimported')\n",
    })
    assert result.returncode == 0, result.stdout + result.stderr
    assert report is None
