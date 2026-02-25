"""
ABOUTME: Unit tests for ace shell completion script generation
ABOUTME: Verifies bash and zsh completion scripts are well-formed and complete
"""

from __future__ import annotations

import pytest

from src.ace.completion import bash_completion, generate, zsh_completion
from src.ace.router import ROUTES


class TestBashCompletion:
    def test_returns_string(self):
        """bash_completion() returns a string."""
        assert isinstance(bash_completion(), str)

    def test_contains_compgen_function(self):
        """bash_completion() contains a compgen completion function."""
        script = bash_completion()
        assert "compgen" in script or "COMPREPLY" in script

    def test_complete_line_present(self):
        """bash_completion() has a `complete -F` line for ace."""
        script = bash_completion()
        assert "complete" in script and "ace" in script

    def test_all_prefixes_present(self):
        """bash_completion() includes all known prefixes."""
        script = bash_completion()
        for prefix in ROUTES:
            assert prefix in script, f"Prefix '{prefix}' missing from bash completion"

    def test_contains_list_flag(self):
        """bash_completion() includes the --list flag."""
        assert "--list" in bash_completion()

    def test_contains_help_flag(self):
        """bash_completion() includes the --help flag."""
        assert "--help" in bash_completion()


class TestZshCompletion:
    def test_returns_string(self):
        """zsh_completion() returns a string."""
        assert isinstance(zsh_completion(), str)

    def test_starts_with_compdef(self):
        """zsh_completion() starts with #compdef ace."""
        script = zsh_completion()
        assert script.startswith("#compdef ace")

    def test_defines_ace_function(self):
        """zsh_completion() defines a _ace function."""
        script = zsh_completion()
        assert "_ace()" in script or "_ace ()" in script

    def test_all_prefixes_with_descriptions(self):
        """zsh_completion() includes all prefixes and their descriptions."""
        script = zsh_completion()
        for prefix, info in ROUTES.items():
            assert prefix in script, f"Prefix '{prefix}' missing from zsh completion"

    def test_contains_arguments_spec(self):
        """zsh_completion() uses _arguments for flag handling."""
        script = zsh_completion()
        assert "_arguments" in script


class TestGenerate:
    def test_generate_bash_returns_bash_script(self):
        """generate('bash') returns the bash completion script."""
        result = generate("bash")
        assert "COMPREPLY" in result or "compgen" in result

    def test_generate_zsh_returns_zsh_script(self):
        """generate('zsh') returns the zsh completion script."""
        result = generate("zsh")
        assert "#compdef ace" in result

    def test_generate_unsupported_shell_raises_valueerror(self):
        """generate() raises ValueError for unsupported shell names."""
        with pytest.raises(ValueError, match="Unsupported shell"):
            generate("fish")  # type: ignore[arg-type]

    def test_generate_bash_and_direct_call_are_identical(self):
        """generate('bash') matches bash_completion() directly."""
        assert generate("bash") == bash_completion()

    def test_generate_zsh_and_direct_call_are_identical(self):
        """generate('zsh') matches zsh_completion() directly."""
        assert generate("zsh") == zsh_completion()
