"""
Session-hook regression tests (R1 + R2).

v6 design:
  - Filesystem-path-only: uses shutil.copy + subprocess.run([..., str(tmp_path), ...]).
    NO Python dotted path referencing the hyphenated llm-wiki directory is ever used.
  - NO __init__.py to copy (markdown_qa/ is not a package).
  - R1: subprocess pytest on injected violations asserts exit 1 + stderr substring.
    -s flag disables per-test capture so pytest_sessionfinish stderr survives.
  - R2 (= structural test #15): sentinel-firing proof that pytest_sessionfinish
    actually registered and ran.

Verify: grep -c 'llm-wiki\\.' scripts/data/llm-wiki/tests/markdown_qa/test_session_hook_regression.py
Expected: 0  (no dotted hyphenated path references)
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent
SOURCE_CONFTEST = THIS_DIR / "conftest.py"
SOURCE_FIXTURES_SAMPLING = THIS_DIR / "fixtures_sampling.py"


# ── R1 ────────────────────────────────────────────────────────────────────────

def test_session_hook_fails_run_on_injected_violation(tmp_path):
    """R1 (v6 update): Inject 3 below-floor per-topic JSONs (MAX_BELOW_FLOOR=2) and
    assert the session hook fails the run with exit code 1 and stderr substring.

    v6 deltas vs v5:
    - NO __init__.py to copy (none exists in markdown_qa/).
    - -s flag disables per-test capture so the pytest_sessionfinish print-to-stderr
      survives subprocess capture across pytest versions.
    """
    # 1. Copy conftest.py and fixtures_sampling.py into tmp_path so pytest discovers
    #    them via normal rootdir walk (filesystem-only, no dotted Python path).
    shutil.copy(SOURCE_CONFTEST, tmp_path / "conftest.py")
    shutil.copy(SOURCE_FIXTURES_SAMPLING, tmp_path / "fixtures_sampling.py")

    # 2. Build a synthetic .artifacts/per-topic dir with 3 below-floor entries
    #    (MAX_BELOW_FLOOR = 2, so 3 violates the floor-occupancy rule).
    synthetic_artifacts = tmp_path / ".artifacts" / "per-topic"
    synthetic_artifacts.mkdir(parents=True)
    for slug in ["a", "b", "c"]:
        (synthetic_artifacts / f"{slug}-heading.json").write_text(
            json.dumps({"slug": slug, "dim": "heading", "score": 0.50})
        )

    # 3. Write a trivial test file so pytest has something to collect.
    (tmp_path / "test_trivial.py").write_text("def test_noop():\n    assert True\n")

    # 4. Invoke pytest with MARKDOWN_QA_ARTIFACTS_DIR redirected to synthetic tree.
    #    -s disables capture so sessionfinish stderr survives; -p no:cacheprovider
    #    prevents cache plugin from altering output.
    env = {
        **os.environ,
        "MARKDOWN_QA_ARTIFACTS_DIR": str(synthetic_artifacts),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-s",
         "-p", "no:cacheprovider"],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"Session hook did not fail run on injected violation; "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert b"FLOOR-OCCUPANCY VIOLATIONS" in result.stderr, (
        f"Expected 'FLOOR-OCCUPANCY VIOLATIONS' in stderr; "
        f"stderr={result.stderr!r}"
    )


# ── R2 (= structural test #15) ────────────────────────────────────────────────

def test_session_hook_actually_fires_sentinel(tmp_path):
    """R2 / structural test #15 (v6 NEW — v6 P1 #2 proof).

    Invokes pytest in tmp_path, points the sentinel env var at a tmp file, and
    asserts the sentinel file exists post-run. This proves pytest_sessionfinish
    was actually registered (conftest.py loaded; sibling import did NOT raise) and
    ran (hook body executed to the write_text call).

    MARKDOWN_QA_ARTIFACTS_DIR is pointed at a non-existent path so the hook's
    empty-artifacts early-return triggers AFTER the sentinel write — confirming the
    sentinel write is unconditional at hook entry.

    If __init__.py accidentally reappears OR a bare sibling import regresses,
    this test FAILS loudly with the exact symptom message in the assertion.
    """
    shutil.copy(SOURCE_CONFTEST, tmp_path / "conftest.py")
    shutil.copy(SOURCE_FIXTURES_SAMPLING, tmp_path / "fixtures_sampling.py")
    (tmp_path / "test_trivial.py").write_text("def test_noop():\n    assert True\n")

    sentinel = tmp_path / ".sessionfinish-fired"
    env = {
        **os.environ,
        "MARKDOWN_QA_SESSIONFINISH_SENTINEL": str(sentinel),
        "MARKDOWN_QA_ARTIFACTS_DIR": str(tmp_path / "nonexistent"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q",
         "-p", "no:cacheprovider"],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Trivial test should pass; stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert sentinel.exists(), (
        "pytest_sessionfinish hook did not fire — conftest.py likely failed to load "
        "(sibling import resolution failed) OR pytest_sessionfinish was not registered. "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert sentinel.read_text() == "fired"
