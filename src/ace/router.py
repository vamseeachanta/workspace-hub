"""
ABOUTME: Subcommand routing table and subprocess delegation for the ace CLI
ABOUTME: Maps prefix aliases to repo tools and invokes them via subprocess
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Routing table
#   key   — short prefix used on the command line (e.g. "dm")
#   value — dict with:
#     repo     : submodule directory name relative to workspace root
#     command  : console-script name installed by that repo's pyproject.toml,
#                OR a dotted "module:function" string used with `python -m`
#     description: one-line description for `ace --list`
# ---------------------------------------------------------------------------
ROUTES: Dict[str, Dict[str, str]] = {
    "dm": {
        "repo": "digitalmodel",
        "command": "digital_model",
        "description": "Digitalmodel engineering analysis tools",
    },
    "wed": {
        "repo": "worldenergydata",
        "command": "worldenergydata",
        "description": "World energy data aggregation and analysis",
    },
    "ah": {
        "repo": "assethold",
        "command": "assethold",
        "description": "Asset portfolio management and analysis",
    },
    "au": {
        "repo": "assetutilities",
        "command": "assetutils-devtools",
        "description": "Asset utilities development tools",
    },
    "fdw": {
        "repo": "frontierdeepwater",
        "command": "frontierdeepwater",
        "description": "Frontier deepwater project tools",
    },
    "spm": {
        "repo": "saipem",
        "command": "saipem",
        "description": "Saipem offshore engineering analysis",
    },
    "doris": {
        "repo": "doris",
        "command": "doris",
        "description": "Doris subsea pipeline analysis tools",
    },
    "ogm": {
        "repo": "OGManufacturing",
        "command": "ogmanufacturing",
        "description": "Oil and gas manufacturing CAD/CAM tools",
    },
    "acd": {
        "repo": "achantas-data",
        "command": "achantas-data",
        "description": "Achantas data processing tools",
    },
    "sea": {
        "repo": "seanation",
        "command": "seanation",
        "description": "SeaNation offshore drilling analysis",
    },
    "sdw": {
        "repo": "sd-work",
        "command": "sd-work",
        "description": "SD-work engineering tools",
    },
}


def workspace_root() -> Path:
    """Return the workspace-hub root directory."""
    return Path(__file__).parent.parent.parent


def resolve_repo_python(repo_dir: Path) -> Optional[Path]:
    """
    Find a Python interpreter for the given repo directory.

    Search order:
    1. <repo>/.venv/bin/python
    2. <repo>/.venv/bin/python3
    3. sys.executable (fall back to current interpreter)
    """
    for candidate in (".venv/bin/python", ".venv/bin/python3"):
        p = repo_dir / candidate
        if p.is_file():
            return p
    return Path(sys.executable)


def resolve_command_argv(
    route: Dict[str, str],
    repo_dir: Path,
    extra_args: List[str],
) -> Tuple[List[str], Path]:
    """
    Build the argv list for subprocess and the working directory.

    Returns (argv, cwd). cwd is always repo_dir so submodule tools find
    their local configuration files regardless of invocation location.

    Strategy:
    - Look for <repo>/.venv/bin/<command>  (venv-installed script)
    - Look for <repo>/<command>            (plain script in repo root)
    - Fall back to `python -m <command>`   using the repo's Python
    """
    command = route["command"]
    python = resolve_repo_python(repo_dir)

    venv_script = repo_dir / ".venv" / "bin" / command
    if venv_script.is_file():
        return ([str(venv_script)] + extra_args, repo_dir)

    repo_script = repo_dir / command
    if repo_script.is_file():
        return ([str(python), str(repo_script)] + extra_args, repo_dir)

    # Fall back: python -m <module-name> where module is command with hyphens->underscores
    module_name = command.replace("-", "_")
    return ([str(python), "-m", module_name] + extra_args, repo_dir)


def list_routes() -> str:
    """Return a formatted listing of all available subcommands."""
    lines = ["Available subcommands:\n"]
    width = max(len(k) for k in ROUTES) + 2
    for prefix, info in sorted(ROUTES.items()):
        repo = info["repo"]
        desc = info["description"]
        lines.append(f"  {prefix:<{width}} {desc}  [{repo}]")
    lines.append(
        "\nUsage: ace <prefix> [args...]   e.g. ace dm fatigue --help"
    )
    return "\n".join(lines)


def route(prefix: str, extra_args: List[str]) -> int:
    """
    Delegate to the appropriate repo tool.

    Returns the subprocess exit code, or a non-zero code on routing failure.
    """
    if prefix not in ROUTES:
        known = ", ".join(sorted(ROUTES.keys()))
        print(
            f"ace: unknown subcommand '{prefix}'\n"
            f"Known prefixes: {known}\n"
            f"Run 'ace --list' to see all available subcommands.",
            file=sys.stderr,
        )
        return 2

    info = ROUTES[prefix]
    root = workspace_root()
    repo_dir = root / info["repo"]

    if not repo_dir.is_dir():
        print(
            f"ace: repo directory not found: {repo_dir}\n"
            f"The '{prefix}' subcommand requires the '{info['repo']}' submodule "
            f"to be present and checked out.",
            file=sys.stderr,
        )
        return 3

    argv, cwd = resolve_command_argv(info, repo_dir, extra_args)

    try:
        result = subprocess.run(argv, cwd=cwd)
        return result.returncode
    except FileNotFoundError:
        print(
            f"ace: command not found: {argv[0]}\n"
            f"The '{info['command']}' tool for repo '{info['repo']}' does not appear "
            f"to be installed. Run 'pip install -e {repo_dir}' to install it.",
            file=sys.stderr,
        )
        return 4
    except PermissionError:
        print(
            f"ace: permission denied executing: {argv[0]}",
            file=sys.stderr,
        )
        return 5
