"""
ABOUTME: ace CLI entry point — parses top-level flags and delegates to router
ABOUTME: Single workspace-hub command that routes to all submodule tool CLIs
"""

from __future__ import annotations

import sys
from typing import List, NoReturn

from src.ace import __version__
from src.ace.completion import generate as generate_completion
from src.ace.router import ROUTES, list_routes, route

_USAGE = """\
ace — unified workspace-hub CLI

Usage:
  ace <prefix> [args...]      Delegate to a repo tool
  ace --list                  List all available subcommands
  ace --completion bash|zsh   Print a shell completion script
  ace --version               Show ace version
  ace --help                  Show this help

Examples:
  ace dm fatigue --help
  ace wed bsee --field MC252
  ace ah portfolio
  ace --completion bash >> ~/.bash_completion.d/ace
"""


def _parse_top_level(argv: List[str]):
    """
    Split argv into (flag, remainder) where flag is a top-level option or None.

    Returns one of:
      ("--help",    [])
      ("--version", [])
      ("--list",    [])
      ("--completion", ["bash"|"zsh"])
      (None,        [prefix, ...rest])
    """
    if not argv:
        return "--help", []

    first = argv[0]

    if first in ("-h", "--help"):
        return "--help", []
    if first in ("-V", "--version"):
        return "--version", []
    if first in ("-l", "--list"):
        return "--list", []
    if first == "--completion":
        return "--completion", argv[1:]

    return None, argv


def main(argv: List[str] | None = None) -> NoReturn:
    """Main entry point for the ace CLI."""
    if argv is None:
        argv = sys.argv[1:]

    flag, rest = _parse_top_level(argv)

    if flag == "--help":
        print(_USAGE)
        sys.exit(0)

    if flag == "--version":
        print(f"ace {__version__}")
        sys.exit(0)

    if flag == "--list":
        print(list_routes())
        sys.exit(0)

    if flag == "--completion":
        if not rest:
            print(
                "ace: --completion requires a shell argument: bash or zsh",
                file=sys.stderr,
            )
            sys.exit(1)
        shell = rest[0]
        if shell not in ("bash", "zsh"):
            print(
                f"ace: unsupported shell '{shell}'. Choose 'bash' or 'zsh'.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(generate_completion(shell))
        sys.exit(0)

    # Delegate to a subcommand
    if not rest:
        print(_USAGE)
        sys.exit(0)

    prefix = rest[0]
    extra_args = rest[1:]
    exit_code = route(prefix, extra_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
