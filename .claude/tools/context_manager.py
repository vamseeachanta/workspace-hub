#!/usr/bin/env python3
"""
ABOUTME: Context management utilities for Claude Code sessions
ABOUTME: Provides %ctx tracking, archiving, and sliding window management
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextManager:
    """
    Manage context usage and prevent overflow in Claude Code sessions.

    Features:
    - %ctx tracking (context percentage)
    - Automatic archiving at threshold
    - Sliding window for message retention
    - Checkpoint creation for state persistence
    """

    # Default token limits (Claude 3.5 Sonnet context window)
    DEFAULT_MAX_TOKENS = 80000
    DEFAULT_ARCHIVE_THRESHOLD = 60000  # 75% of max

    def __init__(
        self,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        archive_threshold: int = DEFAULT_ARCHIVE_THRESHOLD,
        workspace_root: Optional[Path] = None
    ):
        """
        Initialize context manager.

        Args:
            max_tokens: Maximum context window size
            archive_threshold: Token count that triggers archiving
            workspace_root: Root directory for state files
        """
        self.max_tokens = max_tokens
        self.archive_threshold = archive_threshold

        # Resolve workspace root
        if workspace_root:
            self.workspace_root = Path(workspace_root)
        else:
            self.workspace_root = Path.cwd()

        # State paths
        self.state_dir = self.workspace_root / ".claude" / "state"
        self.checkpoint_dir = self.workspace_root / ".claude" / "checkpoints"
        self.archive_dir = self.workspace_root / ".claude" / "archives"
        self.output_dir = self.workspace_root / ".claude" / "outputs"

        # State file
        self.state_file = self.state_dir / "context_state.json"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        for dir_path in [self.state_dir, self.checkpoint_dir,
                         self.archive_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # %ctx - Context Percentage Tracking
    # =========================================================================

    def get_ctx_percentage(self, current_tokens: int) -> float:
        """
        Calculate context usage percentage (%ctx).

        Args:
            current_tokens: Current token count in context

        Returns:
            Percentage of context used (0-100)
        """
        return (current_tokens / self.max_tokens) * 100

    def format_ctx(self, current_tokens: int) -> str:
        """
        Format %ctx for CLI display.

        Args:
            current_tokens: Current token count

        Returns:
            Formatted string like "45.2%ctx"
        """
        pct = self.get_ctx_percentage(current_tokens)
        return f"{pct:.1f}%ctx"

    def get_ctx_status(self, current_tokens: int) -> Dict[str, Any]:
        """
        Get comprehensive context status.

        Args:
            current_tokens: Current token count

        Returns:
            Status dict with percentage, indicator, and recommendation
        """
        pct = self.get_ctx_percentage(current_tokens)

        if pct < 40:
            indicator = "🟢"
            status = "healthy"
            action = "Normal operation"
        elif pct < 60:
            indicator = "🟡"
            status = "elevated"
            action = "Consider summarizing"
        elif pct < 80:
            indicator = "🟠"
            status = "high"
            action = "Archive older exchanges"
        else:
            indicator = "🔴"
            status = "critical"
            action = "Trim to essentials"

        return {
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "percentage": round(pct, 1),
            "formatted": f"{pct:.1f}%ctx",
            "indicator": indicator,
            "status": status,
            "action": action,
            "tokens_remaining": self.max_tokens - current_tokens,
            "should_archive": pct >= 60,
            "is_critical": pct >= 80
        }

    # =========================================================================
    # Archiving and Sliding Window
    # =========================================================================

    def should_archive(self, current_tokens: int) -> bool:
        """Check if archiving should be triggered."""
        return current_tokens > self.archive_threshold

    def archive_exchanges(
        self,
        messages: List[Dict[str, Any]],
        keep_recent: int = 3
    ) -> Dict[str, Any]:
        """
        Archive older message exchanges to reduce context.

        Args:
            messages: List of message dicts
            keep_recent: Number of recent exchanges to keep

        Returns:
            Archive summary with path and stats
        """
        if len(messages) <= keep_recent:
            return {"archived": False, "reason": "Not enough messages to archive"}

        # Split messages
        to_archive = messages[:-keep_recent]
        kept = messages[-keep_recent:]

        # Generate archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"archive_{timestamp}.json"

        # Create archive with summary
        archive_data = {
            "archived_at": datetime.now().isoformat(),
            "message_count": len(to_archive),
            "summary": self._summarize_messages(to_archive),
            "messages": to_archive
        }

        # Write archive
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2, default=str)

        return {
            "archived": True,
            "archive_path": str(archive_file),
            "archived_count": len(to_archive),
            "kept_count": len(kept),
            "summary": archive_data["summary"]
        }

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Generate brief summary of archived messages."""
        if not messages:
            return "No messages"

        # Count by role
        roles = {}
        for msg in messages:
            role = msg.get("role", "unknown")
            roles[role] = roles.get(role, 0) + 1

        role_summary = ", ".join(f"{count} {role}" for role, count in roles.items())
        return f"Archived {len(messages)} messages: {role_summary}"

    def trim_context(
        self,
        messages: List[Dict[str, Any]],
        keep_system: bool = True,
        keep_recent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Trim context to essential messages only.

        Args:
            messages: Full message list
            keep_system: Whether to keep system messages
            keep_recent: Number of recent exchanges to keep

        Returns:
            Trimmed message list
        """
        result = []

        # Keep system messages if requested
        if keep_system:
            result.extend([m for m in messages if m.get("role") == "system"])

        # Keep recent messages
        non_system = [m for m in messages if m.get("role") != "system"]
        result.extend(non_system[-keep_recent:])

        return result

    # =========================================================================
    # Checkpoints
    # =========================================================================

    def create_checkpoint(
        self,
        task_name: str,
        status: str,
        findings: List[str],
        files_modified: List[str],
        next_action: str,
        key_values: Dict[str, Any]
    ) -> str:
        """
        Create a checkpoint file for task state.

        Args:
            task_name: Name of the task
            status: complete|in_progress|blocked
            findings: List of key findings (max 5)
            files_modified: List of file paths
            next_action: Single sentence next step
            key_values: Dict of critical values

        Returns:
            Path to checkpoint file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        safe_name = task_name.lower().replace(" ", "-").replace("_", "-")
        checkpoint_file = self.checkpoint_dir / f"{timestamp}-{safe_name}.md"

        # Format key values
        kv_str = ", ".join(f"{k}={v}" for k, v in key_values.items())

        # Build checkpoint content
        content = f"""## Checkpoint: {task_name}
**Timestamp:** {datetime.now().isoformat()}
**Status:** {status}

**Key Findings:**
"""
        for finding in findings[:5]:  # Max 5 findings
            content += f"- {finding}\n"

        content += f"""
**Files Modified:**
"""
        for file_path in files_modified:
            content += f"- {file_path}\n"

        content += f"""
**Next Action:** {next_action}

**Critical Values:** {kv_str}
"""

        # Write checkpoint
        with open(checkpoint_file, 'w') as f:
            f.write(content)

        return str(checkpoint_file)

    def load_latest_checkpoint(self, task_pattern: Optional[str] = None) -> Optional[Dict]:
        """
        Load the most recent checkpoint, optionally filtered by task name.

        Args:
            task_pattern: Optional pattern to match in filename

        Returns:
            Checkpoint data dict or None
        """
        checkpoints = sorted(self.checkpoint_dir.glob("*.md"), reverse=True)

        for cp_file in checkpoints:
            if task_pattern and task_pattern not in cp_file.name:
                continue

            content = cp_file.read_text()
            return {
                "file": str(cp_file),
                "content": content,
                "timestamp": cp_file.stat().st_mtime
            }

        return None

    # =========================================================================
    # State Management
    # =========================================================================

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save current state to file."""
        state["saved_at"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def update_state(self, **kwargs) -> Dict[str, Any]:
        """Update specific state values."""
        state = self.load_state()
        state.update(kwargs)
        self.save_state(state)
        return state


# =============================================================================
# CLI Functions
# =============================================================================

def print_ctx_status(current_tokens: int) -> None:
    """Print formatted context status to stdout."""
    cm = ContextManager()
    status = cm.get_ctx_status(current_tokens)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Context Status: {status['indicator']} {status['formatted']:>10}                        ║
╠══════════════════════════════════════════════════════════════╣
║  Tokens: {status['current_tokens']:>8,} / {status['max_tokens']:>8,}                         ║
║  Remaining: {status['tokens_remaining']:>8,}                                     ║
║  Status: {status['status']:<12}                                     ║
║  Action: {status['action']:<40}      ║
╚══════════════════════════════════════════════════════════════╝
""")


def cli_main():
    """CLI entry point for context management."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: context_manager.py <command> [args]")
        print("")
        print("Commands:")
        print("  status <tokens>    Show context status for token count")
        print("  checkpoint <name>  Create a checkpoint")
        print("  archive            Archive old exchanges")
        print("  clean              Clean old archives")
        sys.exit(1)

    command = sys.argv[1]
    cm = ContextManager()

    if command == "status":
        if len(sys.argv) < 3:
            print("Usage: context_manager.py status <current_tokens>")
            sys.exit(1)
        tokens = int(sys.argv[2])
        print_ctx_status(tokens)

    elif command == "checkpoint":
        name = sys.argv[2] if len(sys.argv) > 2 else "manual-checkpoint"
        path = cm.create_checkpoint(
            task_name=name,
            status="in_progress",
            findings=["Manual checkpoint created"],
            files_modified=[],
            next_action="Continue from checkpoint",
            key_values={"created": "manual"}
        )
        print(f"Checkpoint created: {path}")

    elif command == "archive":
        print("Archive functionality requires message history")
        print("Use in Python: cm.archive_exchanges(messages)")

    elif command == "clean":
        # Clean archives older than 7 days
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=7)
        cleaned = 0
        for archive in cm.archive_dir.glob("archive_*.json"):
            if datetime.fromtimestamp(archive.stat().st_mtime) < cutoff:
                archive.unlink()
                cleaned += 1
        print(f"Cleaned {cleaned} old archives")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
