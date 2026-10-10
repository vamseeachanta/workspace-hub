"""Scope and guard regressions for check-shell-conditional-helpers.py (#3876).

Each case here was a false negative found by adversarial review r1 (Codex and
Claude) on the first implementation; see the base suite for the core contract.
Fixtures are neutral, synthetic harnesses written to tmp_path.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

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


def test_guard_inside_another_selector_does_not_count(tmp_path):
    """A guard skipped by the same selector proves nothing (review r1)."""
    path = _harness(
        tmp_path,
        """
        if [[ "${MODE:-target}" == all ]]; then snapshot() { :; }; fi
        if [[ "${MODE:-target}" == all ]]; then require_helpers snapshot; fi
        out="$(snapshot)"
        """,
    )
    assert _run(path).returncode == 1


def test_short_circuit_definition_is_conditional(tmp_path):
    path = _harness(
        tmp_path,
        """
        [[ "${TARGETED:-0}" != 1 ]] && snapshot() { printf x; }
        after="$(snapshot)"
        """,
    )
    result = _run(path)
    assert result.returncode == 1
    assert f"{path.name}:2" in result.stdout


def test_or_list_definition_is_conditional(tmp_path):
    path = _harness(
        tmp_path,
        """
        [[ -n "${SKIP:-}" ]] || snapshot() { printf x; }
        snapshot
        """,
    )
    assert _run(path).returncode == 1


def test_backtick_substitution_call_is_seen(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ "${TARGETED:-0}" != 1 ]]; then snapshot() { printf x; }; fi
        before=`snapshot`
        """,
    )
    result = _run(path)
    assert result.returncode == 1
    assert f"{path.name}:2" in result.stdout


def test_backtick_inside_double_quotes_is_seen(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ -n "${X:-}" ]]; then snapshot() { printf x; }; fi
        echo "value: `snapshot`"
        """,
    )
    assert _run(path).returncode == 1


@pytest.mark.parametrize(
    "opener,term", [("<<'EOF-MARK'", "EOF-MARK"), ('<<-"END.TXT"', "END.TXT")]
)
def test_heredoc_terminator_with_punctuation_is_skipped(tmp_path, opener, term):
    """A literal `fi` in the heredoc must not close the real if-block."""
    path = _harness(
        tmp_path,
        f"""
        if [[ -n "${{X:-}}" ]]; then
          cat {opener}
        fi
        {term}
          helper() {{ :; }}
        fi
        helper
        """,
    )
    result = _run(path)
    assert result.returncode == 1, result.stdout
    assert f"{path.name}:7" in result.stdout


@pytest.mark.parametrize(
    "body",
    [
        # defined inside another function's body, which runs only in one mode
        'setup() { helper() { :; }; }\nif [[ "$X" == 1 ]]; then setup; fi\nx="$(helper)"\n',
        # defined in a brace group behind a selector
        '[[ "$X" == 1 ]] && { helper() { :; }; }\nhelper\n',
        # defined in a subshell: never visible to the parent
        "( helper() { :; } )\nhelper\n",
    ],
    ids=["function-body", "brace-group", "subshell"],
)
def test_nested_scope_definitions_are_conditional(tmp_path, body):
    assert _run(_harness(tmp_path, body)).returncode == 1


@pytest.mark.parametrize(
    "guard",
    [
        "declare -F helper >/dev/null || true",
        "declare -F helper >/dev/null",
        "never() { declare -F helper || exit 1; }",
    ],
    ids=["or-true", "result-ignored", "uncalled-function"],
)
def test_guard_must_be_acted_on_and_reachable(tmp_path, guard):
    path = _harness(
        tmp_path,
        f"""
        if [[ -n "${{X:-}}" ]]; then helper() {{ :; }}; fi
        {guard}
        helper
        """,
    )
    assert _run(path).returncode == 1


def test_guard_on_continuation_line_counts(tmp_path):
    path = _harness(
        tmp_path,
        """
        if [[ -n "${X:-}" ]]; then helper() { :; }; fi
        declare -F helper >/dev/null && echo PASS \\
          || { echo FAIL; exit 1; }
        helper
        """,
    )
    assert _run(path).returncode == 0


@pytest.mark.parametrize(
    "call",
    [
        "FOO=1 helper",
        "command helper",
        "run_step label helper arg",
        "echo $'it\\'s'; helper",
    ],
    ids=["env-prefix", "command-builtin", "run-step-arg", "ansi-c-quote"],
)
def test_indirect_call_forms_are_seen(tmp_path, call):
    path = _harness(
        tmp_path,
        f"""
        if [[ -n "${{X:-}}" ]]; then helper() {{ :; }}; fi
        {call}
        """,
    )
    assert _run(path).returncode == 1
