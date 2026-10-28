"""Contract for the tracked test quarantine (owner ruling 2026-10-28).

The root conftest.py marks every test listed in tests/quarantine.txt as
xfail(strict=False). Expected outcomes below are written by hand from pytest's
documented xfail semantics: a failing quarantined test reports XFAIL and the
run passes; a passing quarantined test reports XPASS and the run still passes;
an unlisted failing test fails the run.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _conftest():
    spec = importlib.util.spec_from_file_location("root_conftest", ROOT / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matching_rules():
    module = _conftest()
    entries = {
        "tests/a/test_x.py::test_exact[p1]": "one parameter",
        "tests/a/test_x.py::test_all_params": "every parameter",
        "tests/a/test_whole.py": "whole file",
    }
    assert module.quarantine_reason("tests/a/test_x.py::test_exact[p1]", entries) == "one parameter"
    assert module.quarantine_reason("tests/a/test_x.py::test_exact[p2]", entries) is None
    assert module.quarantine_reason("tests/a/test_x.py::test_all_params[q]", entries) == "every parameter"
    assert module.quarantine_reason("tests/a/test_whole.py::TestC::test_m", entries) == "whole file"
    assert module.quarantine_reason("tests/a/test_other.py::test_exact", entries) is None


def test_load_quarantine_reads_reasons(tmp_path):
    module = _conftest()
    path = tmp_path / "quarantine.txt"
    path.write_text("# header comment\n\ntests/a/test_x.py::test_y  # broken on main (#1)\n"
                    "tests/a/test_z.py\n", encoding="utf-8")
    assert module.load_quarantine(path) == {
        "tests/a/test_x.py::test_y": "broken on main (#1)",
        "tests/a/test_z.py": "quarantined: fails on main",
    }


def test_every_entry_names_a_test_file_and_a_reason():
    module = _conftest()
    entries = module.load_quarantine()
    for node, reason in entries.items():
        path = node.split("::", 1)[0]
        assert (ROOT / path).is_file(), f"stale quarantine entry: {node}"
        assert re.search(r"#\d+", reason), f"quarantine entry lacks a tracking issue: {node}"


def test_quarantined_failure_is_xfail_and_run_stays_green(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    (tmp_path / "conftest.py").write_bytes((ROOT / "conftest.py").read_bytes())
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "quarantine.txt").write_text(
        "tests/test_sample.py::test_listed_fails  # known (#1)\n"
        "tests/test_sample.py::test_listed_passes  # fixed (#1)\n", encoding="utf-8")
    (tests / "test_sample.py").write_text(textwrap.dedent("""
        def test_listed_fails():
            assert False

        def test_listed_passes():
            assert True

        def test_unlisted_passes():
            assert True
    """), encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rxX", "-p", "no:cacheprovider",
                          "tests"], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "1 passed, 1 xfailed, 1 xpassed" in run.stdout

    (tests / "test_sample.py").write_text("def test_unlisted_fails():\n    assert False\n",
                                          encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                         cwd=tmp_path, capture_output=True, text=True, check=False)
    assert run.returncode == 1, run.stdout + run.stderr


def test_quarantined_file_with_import_error_is_skipped(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\n", encoding="utf-8")
    (tmp_path / "conftest.py").write_bytes((ROOT / "conftest.py").read_bytes())
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "quarantine.txt").write_text("tests/test_broken.py  # missing package (#1)\n",
                                          encoding="utf-8")
    (tests / "test_broken.py").write_text("import package_that_does_not_exist\n",
                                          encoding="utf-8")
    (tests / "test_fine.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                         cwd=tmp_path, capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "1 passed, 1 skipped" in run.stdout

    (tests / "quarantine.txt").write_text("", encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                         cwd=tmp_path, capture_output=True, text=True, check=False)
    assert run.returncode == 2, run.stdout + run.stderr
