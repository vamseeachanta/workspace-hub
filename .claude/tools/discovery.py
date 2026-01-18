#!/usr/bin/env python3
"""
Discovery module for portable context management imports.

Enables importing context management tools from any repository depth
without PYTHONPATH configuration or hardcoded paths.

This module implements zero-installation import discovery by walking up
the directory tree to locate workspace-hub/.claude/tools/ and add it
to sys.path automatically.
"""

import sys
import os
from pathlib import Path
from typing import Optional


def get_workspace_root() -> Optional[Path]:
    """
    Locate workspace-hub root directory.

    Searches for .git directory or workspace-hub marker to identify root.
    Returns None if not found within reasonable depth.

    Returns:
        Path to workspace-hub root, or None if not found
    """
    current = Path.cwd()

    # Search up to 10 levels (deep enough for nested repos, but not filesystem root)
    for _ in range(10):
        # Check for .git (indicates repository root)
        if (current / ".git").exists():
            # Verify we're in workspace-hub by checking for .claude/tools
            if (current / ".claude" / "tools").exists():
                return current

        # Check for workspace-hub marker files
        if (current / ".claude" / "tools" / "context_manager.py").exists():
            return current

        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    return None


def discover_tools_path() -> Optional[Path]:
    """
    Discover .claude/tools directory from current location.

    Walks up directory tree from current working directory to find
    workspace-hub/.claude/tools/ path.

    Returns:
        Path to .claude/tools/ directory, or None if not found
    """
    workspace_root = get_workspace_root()

    if workspace_root:
        tools_path = workspace_root / ".claude" / "tools"
        if tools_path.exists() and tools_path.is_dir():
            return tools_path

    return None


def add_tools_to_path() -> bool:
    """
    Add discovered .claude/tools/ directory to sys.path.

    Enables imports like: from context_manager import ContextManager
    from any repository depth without additional configuration.

    This is the core function that enables zero-installation usage - call this
    once at the start of any script that needs to import context management tools.

    Returns:
        True if tools path was discovered and added

    Raises:
        ImportError: If tools path cannot be discovered
    """
    tools_path = discover_tools_path()

    if not tools_path:
        raise ImportError(
            "Could not discover .claude/tools/ directory. "
            "Ensure this script is run from within workspace-hub repository "
            "or a subdirectory of workspace-hub."
        )

    tools_str = str(tools_path)

    # Add to sys.path if not already present
    if tools_str not in sys.path:
        sys.path.insert(0, tools_str)

    return True


def get_tools_path() -> Path:
    """
    Get .claude/tools/ path, raising error if not found.

    Convenience function for use in imports or configuration.

    Returns:
        Path to .claude/tools/ directory

    Raises:
        ImportError: If tools path cannot be discovered
    """
    path = discover_tools_path()
    if not path:
        raise ImportError(
            "Cannot locate .claude/tools/. "
            "This script must be run from within workspace-hub repository."
        )
    return path


if __name__ == "__main__":
    # CLI usage: python discovery.py
    # Useful for debugging discovery mechanism
    import json

    root = get_workspace_root()
    tools = discover_tools_path()

    result = {
        "workspace_root": str(root) if root else None,
        "tools_path": str(tools) if tools else None,
        "discoverable": tools is not None,
        "in_sys_path": str(tools) in sys.path if tools else False
    }

    print(json.dumps(result, indent=2))
