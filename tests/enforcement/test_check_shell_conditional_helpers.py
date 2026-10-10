"""Tests for scripts/enforcement/check-shell-conditional-helpers.py (#3876).

The defect class: a shell test helper defined only inside a selector branch
(``if [[ $MODE ... ]]; then helper() {...}; fi``) and referenced after that
branch. A targeted run skips the definition, the later call fails inside a
command substitution, and the harness reports green without checking anything.

The checker is static: it flags every reference to a conditionally-defined
function that sits outside the defining block and is not preceded by a
``declare -F <fn>`` or ``require_helpers <fn>`` guard. Fixtures are neutral,
synthetic harnesses written to tmp_path.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "check-shell-conditional-helpers.py"


def _harness(tmp_path: Path, body: str, name: str = "test_fixture.sh") -> Path:
    path = tmp_path / name
    path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8", newline="\n")
    return path


def _run(*paths: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, paths)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_flags_helper_defined_in_selector_branch_and_used_after(tmp_path):
    path = _harness(
        tmp_path,
        """
        #!/usr/bin/env bash
        if [[ "${TARGETED:-0}" != 1 ]]; then
          snapshot() { stat "$1"; }
          before="$(snapshot a)"
        fi
        after="$(snapshot a)"
        [[ "$after" == "$before" ]] && echo PASS
        """,
    )
    result = _run(path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "snapshot" in result.stdout
    assert f"{path.name}:6" in result.stdout


def test_declare_f_guard_before_use_clears_finding(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ "${TARGETED:-0}" != 1 ]]; then
          snapshot() { stat "$1"; }
        fi
        declare -F snapshot >/dev/null || { echo FAIL; exit 1; }
        after="$(snapshot a)"
        """,
    )
    result = _run(path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_require_helpers_guard_clears_finding(tmp_path):
    path = _harness(
        tmp_path,
        """
        case "${MODE:-all}" in
          all) snapshot() { stat "$1"; } ;;
        esac
        require_helpers snapshot || exit 1
        snapshot a
        """,
    )
    assert _run(path).returncode == 0


def test_guard_after_use_does_not_count(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ -n "${X:-}" ]]; then
          helper() { :; }
        fi
        helper
        declare -F helper >/dev/null
        """,
    )
    result = _run(path)
    assert result.returncode == 1
    assert f"{path.name}:4" in result.stdout


def test_unconditional_helper_is_clean(tmp_path):
    path = _harness(
        tmp_path,
        """
        snapshot() { stat "$1"; }
        if [[ "${TARGETED:-0}" != 1 ]]; then
          snapshot a
        fi
        snapshot b
        """,
    )
    assert _run(path).returncode == 0


def test_use_inside_defining_branch_is_clean(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ "${TARGETED:-0}" != 1 ]]; then
          snapshot() {
            stat "$1"
          }
          snapshot a
        fi
        """,
    )
    assert _run(path).returncode == 0


def test_defined_in_every_branch_is_clean(tmp_path):
    path = _harness(
        tmp_path,
        """
        if command -v cygpath >/dev/null 2>&1; then
          native() { cygpath -m "$1"; }
        else
          native() { printf '%s' "$1"; }
        fi
        native x
        """,
    )
    assert _run(path).returncode == 0


def test_define_if_not_already_defined_idiom_is_clean(tmp_path):
    """`if ! declare -F f; then f() {...}; fi` leaves f defined either way."""
    path = _harness(
        tmp_path,
        """
        if ! declare -F _resolver >/dev/null 2>&1; then
          _resolver() { :; }
        fi
        out="$(_resolver --context x)"
        """,
    )
    assert _run(path).returncode == 0


def test_define_if_not_defined_idiom_for_other_name_is_flagged(tmp_path):
    path = _harness(
        tmp_path,
        """
        if ! declare -F other >/dev/null; then
          helper() { :; }
        fi
        helper
        """,
    )
    assert _run(path).returncode == 1


def test_defined_in_some_elif_branches_is_flagged(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ "$A" == 1 ]]; then
          native() { :; }
        elif [[ "$A" == 2 ]]; then
          native() { :; }
        fi
        native
        """,
    )
    assert _run(path).returncode == 1


def test_heredoc_keywords_do_not_confuse_block_depth(tmp_path):
    path = _harness(
        tmp_path,
        """
        probe() {
          python - <<'PY'
        if True:
            print("fi done esac")
        PY
        }
        probe
        """,
    )
    assert _run(path).returncode == 0


def test_function_keyword_form_detected(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ -n "${X:-}" ]]; then
          function helper { :; }
        fi
        out=$(helper)
        """,
    )
    assert _run(path).returncode == 1


def test_word_boundary_and_comments_ignored(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ -n "${X:-}" ]]; then
          helper() { :; }
        fi
        # helper is only defined above
        helper_two=1
        echo "the helper word in a string"
        """,
    )
    assert _run(path).returncode == 0


def test_loop_body_definition_is_conditional(tmp_path):
    path = _harness(
        tmp_path,
        """
        for item in "$@"; do
          helper() { :; }
        done
        helper
        """,
    )
    assert _run(path).returncode == 1


def test_canonical_resync_harness_is_clean():
    """PR #3875 guarded the original incident; the checker must agree."""
    target = REPO_ROOT / "scripts" / "skills" / "tests" / "test_resync_skill_links.sh"
    result = _run(target)
    assert result.returncode == 0, result.stdout


def test_inventory_mode_scans_tracked_shell_tests_and_is_clean():
    """Default mode (no args) covers every tracked shell test harness."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "scanned" in result.stdout
    scanned = int(result.stdout.split("scanned", 1)[1].split()[0])
    assert scanned >= 40
