"""
ABOUTME: Shell completion script generator for the ace CLI (bash and zsh)
ABOUTME: Outputs sourceable completion scripts that tab-complete subcommand prefixes
"""

from __future__ import annotations

from typing import Literal

from src.ace.router import ROUTES

ShellType = Literal["bash", "zsh"]


def _sorted_prefixes() -> str:
    """Return a space-separated sorted list of known prefixes."""
    return " ".join(sorted(ROUTES.keys()))


def bash_completion() -> str:
    """Return a bash completion script for the ace command."""
    prefixes = _sorted_prefixes()
    return f"""\
# Bash completion for ace
# Source this file or add to ~/.bash_completion.d/ace
_ace_completions() {{
    local cur="${{COMP_WORDS[COMP_CWORD]}}"
    local prefixes="{prefixes}"
    if [[ ${{COMP_CWORD}} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${{prefixes}} --list --help --version" -- "${{cur}}") )
    fi
}}
complete -F _ace_completions ace
"""


def zsh_completion() -> str:
    """Return a zsh completion script for the ace command."""
    prefixes = _sorted_prefixes()
    # Build zsh argument spec entries
    spec_lines = []
    for prefix in sorted(ROUTES.keys()):
        desc = ROUTES[prefix]["description"].replace("'", "\\'")
        spec_lines.append(f"        '{prefix}:{desc}'")
    spec_block = "\n".join(spec_lines)

    return f"""\
#compdef ace
# Zsh completion for ace
# Place in a directory on your $fpath, e.g. ~/.zsh/completions/_ace
_ace() {{
    local -a subcommands
    subcommands=(
{spec_block}
    )
    _arguments \\
        '(- *)--help[Show help]' \\
        '(- *)--list[List all subcommands]' \\
        '(- *)--version[Show version]' \\
        '1: :->subcmd' \\
        '*::arg:->args'

    case $state in
        subcmd)
            _describe 'subcommand' subcommands
            ;;
        args)
            _default
            ;;
    esac
}}
_ace "$@"
"""


def generate(shell: ShellType) -> str:
    """Generate and return a completion script for the requested shell."""
    if shell == "bash":
        return bash_completion()
    if shell == "zsh":
        return zsh_completion()
    raise ValueError(f"Unsupported shell: {shell!r}. Choose 'bash' or 'zsh'.")
