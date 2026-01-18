"""
ABOUTME: Context Management Package - Workspace-wide, zero-installation distribution
ABOUTME: Enables portable context management across all repositories via simple git sync

This module makes .claude/tools/ a proper Python package, enabling zero-installation
usage across all repositories in workspace-hub. All tools require only:
1. git clone (or git pull) to get latest versions
2. Python 3.8+ with stdlib only (no pip install required)
3. Direct import from any repository depth

Usage Examples:
    # Example 1: Direct import from script in any repository
    from context_manager import ContextManager

    # Example 2: Using discovery for portable imports
    from discovery import add_tools_to_path
    add_tools_to_path()
    from context_manager import ContextManager

    # Example 3: CLI usage (no import needed)
    python .claude/tools/context_manager.py status 50000
"""

# Public API exports - import these for context management
from context_manager import ContextManager
from task_context_wrapper import TaskContextWrapper
from worker_contract import (
    WorkerStatus,
    WorkerResponse,
    WorkerContractValidator,
    create_worker_response
)

__all__ = [
    # Core context management
    'ContextManager',
    'TaskContextWrapper',

    # Worker coordination
    'WorkerStatus',
    'WorkerResponse',
    'WorkerContractValidator',
    'create_worker_response',
]

__version__ = '1.0.0'
__description__ = 'Zero-installation context management for workspace-hub'
