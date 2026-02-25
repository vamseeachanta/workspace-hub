"""
ABOUTME: Unit tests for the ace CLI entry point argument parsing and dispatch
ABOUTME: Covers --help, --version, --list, --completion, and subcommand delegation
"""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.ace import __version__
from src.ace.cli import main
from src.ace.router import ROUTES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(args: list[str]) -> tuple[int, str, str]:
    """
    Run main(args) and capture stdout/stderr and the SystemExit code.

    Returns (exit_code, stdout, stderr).
    """
    with pytest.raises(SystemExit) as exc_info:
        main(args)
    return exc_info.value.code, "", ""


def _run_captured(args: list[str], capsys) -> tuple[int, str, str]:
    """Run main(args) capturing output; returns (exit_code, out, err)."""
    with pytest.raises(SystemExit) as exc_info:
        main(args)
    captured = capsys.readouterr()
    return exc_info.value.code, captured.out, captured.err


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------


class TestHelpFlag:
    def test_help_exits_zero(self, capsys):
        code, _, _ = _run_captured(["--help"], capsys)
        assert code == 0

    def test_short_h_exits_zero(self, capsys):
        code, _, _ = _run_captured(["-h"], capsys)
        assert code == 0

    def test_no_args_exits_zero_with_usage(self, capsys):
        code, out, _ = _run_captured([], capsys)
        assert code == 0
        assert "ace" in out.lower()

    def test_help_output_contains_usage(self, capsys):
        _, out, _ = _run_captured(["--help"], capsys)
        assert "Usage" in out or "usage" in out


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------


class TestVersionFlag:
    def test_version_exits_zero(self, capsys):
        code, _, _ = _run_captured(["--version"], capsys)
        assert code == 0

    def test_version_output_contains_version_string(self, capsys):
        _, out, _ = _run_captured(["--version"], capsys)
        assert __version__ in out

    def test_version_short_flag(self, capsys):
        code, out, _ = _run_captured(["-V"], capsys)
        assert code == 0
        assert __version__ in out


# ---------------------------------------------------------------------------
# --list
# ---------------------------------------------------------------------------


class TestListFlag:
    def test_list_exits_zero(self, capsys):
        code, _, _ = _run_captured(["--list"], capsys)
        assert code == 0

    def test_list_short_flag_exits_zero(self, capsys):
        code, _, _ = _run_captured(["-l"], capsys)
        assert code == 0

    def test_list_output_contains_all_prefixes(self, capsys):
        _, out, _ = _run_captured(["--list"], capsys)
        for prefix in ROUTES:
            assert prefix in out, f"Prefix '{prefix}' not in --list output"


# ---------------------------------------------------------------------------
# --completion
# ---------------------------------------------------------------------------


class TestCompletionFlag:
    def test_completion_bash_exits_zero(self, capsys):
        code, _, _ = _run_captured(["--completion", "bash"], capsys)
        assert code == 0

    def test_completion_bash_output_contains_ace(self, capsys):
        _, out, _ = _run_captured(["--completion", "bash"], capsys)
        assert "ace" in out

    def test_completion_bash_contains_prefixes(self, capsys):
        _, out, _ = _run_captured(["--completion", "bash"], capsys)
        for prefix in ROUTES:
            assert prefix in out

    def test_completion_zsh_exits_zero(self, capsys):
        code, _, _ = _run_captured(["--completion", "zsh"], capsys)
        assert code == 0

    def test_completion_zsh_output_has_compdef(self, capsys):
        _, out, _ = _run_captured(["--completion", "zsh"], capsys)
        assert "#compdef ace" in out

    def test_completion_no_shell_exits_1(self, capsys):
        code, _, err = _run_captured(["--completion"], capsys)
        assert code == 1
        assert "bash" in err or "zsh" in err

    def test_completion_unsupported_shell_exits_1(self, capsys):
        code, _, err = _run_captured(["--completion", "fish"], capsys)
        assert code == 1
        assert "fish" in err or "unsupported" in err.lower()


# ---------------------------------------------------------------------------
# Subcommand delegation
# ---------------------------------------------------------------------------


class TestSubcommandDelegation:
    def test_known_prefix_calls_route(self, tmp_path, capsys):
        """main() calls route() for a known prefix."""
        prefix = list(ROUTES.keys())[0]

        with patch("src.ace.cli.route", return_value=0) as mock_route:
            with pytest.raises(SystemExit) as exc_info:
                main([prefix, "--help"])

        assert exc_info.value.code == 0
        mock_route.assert_called_once_with(prefix, ["--help"])

    def test_exit_code_propagated_from_route(self, capsys):
        """SystemExit code equals the return value of route()."""
        prefix = list(ROUTES.keys())[0]

        with patch("src.ace.cli.route", return_value=7):
            with pytest.raises(SystemExit) as exc_info:
                main([prefix])

        assert exc_info.value.code == 7

    def test_unknown_prefix_exits_non_zero(self, capsys):
        """Unknown prefix results in non-zero exit."""
        code, _, err = _run_captured(["zzz_no_such_prefix"], capsys)
        assert code != 0
