"""
ABOUTME: Subagent checkpoint serialization for session handoff
ABOUTME: Outgoing subagent writes findings + next steps; incoming subagent reads and resumes
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_RE_IMPORT = None  # lazy import via _get_frontmatter_re()


def _get_frontmatter_re():
    """Return compiled frontmatter regex (lazy to avoid module-level state)."""
    import re  # noqa: PLC0415
    return re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def read_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a Markdown file. Returns {} on failure."""
    pattern = _get_frontmatter_re()
    try:
        content = path.read_text(encoding="utf-8")
        match = pattern.match(content)
        if not match:
            return {}
        return yaml.safe_load(match.group(1)) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Could not read {path}: {exc}", file=sys.stderr)
        return {}


def collect_wrk_summaries(
    workspace: Path,
    active_wrk_ids: list[str],
) -> list[dict[str, Any]]:
    """
    Build per-WRK summary dicts for all active WRK IDs.

    Searches both pending/ and working/ subdirectories.
    """
    queue_dir = workspace / ".claude" / "work-queue"
    summaries: list[dict[str, Any]] = []

    for wrk_id in active_wrk_ids:
        wrk_id = wrk_id.strip()
        if not wrk_id:
            continue

        wrk_file: Path | None = None
        for sub in ("pending", "working"):
            candidate = queue_dir / sub / f"{wrk_id}.md"
            if candidate.exists():
                wrk_file = candidate
                break

        if wrk_file is None:
            summaries.append(
                {
                    "id": wrk_id,
                    "found": False,
                    "session_state": {},
                    "status": "unknown",
                    "title": "",
                }
            )
            continue

        fm = read_frontmatter(wrk_file)
        summaries.append(
            {
                "id": wrk_id,
                "found": True,
                "file": str(wrk_file),
                "status": fm.get("status", "unknown"),
                "title": fm.get("title", ""),
                "percent_complete": fm.get("percent_complete", 0),
                "session_state": fm.get("session_state", {}),
            }
        )

    return summaries


def read_git_state(workspace: Path) -> dict[str, Any]:
    """Capture current git state for the checkpoint."""
    import subprocess  # noqa: PLC0415

    def run(cmd: list[str]) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception:  # noqa: BLE001
            return ""

    return {
        "branch": run(["git", "symbolic-ref", "--short", "HEAD"]),
        "modified_files": run(["git", "status", "--short"]),
        "recent_commits": run(["git", "log", "--oneline", "-5"]),
    }


def write_checkpoint(
    workspace: Path,
    active_wrk_ids: list[str],
    modified_files: list[str],
    output_path: Path,
) -> None:
    """
    Serialize full subagent checkpoint to a JSON file.

    The outgoing subagent calls this. The incoming subagent reads the JSON
    to understand where to resume without re-reading all WRK files.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git_state = read_git_state(workspace)
    wrk_summaries = collect_wrk_summaries(workspace, active_wrk_ids)

    checkpoint: dict[str, Any] = {
        "schema_version": "1.0",
        "created_at": ts,
        "workspace": str(workspace),
        "active_wrk_items": wrk_summaries,
        "modified_files": [f for f in modified_files if f],
        "git_state": git_state,
        "handoff_instructions": (
            "Read each item in active_wrk_items. "
            "Focus on session_state.next_steps to determine what to do. "
            "Do not redo steps already completed."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False))
    print(f"Checkpoint written to {output_path}")


def read_checkpoint(checkpoint_path: Path) -> dict[str, Any]:
    """
    Load a checkpoint file written by an outgoing subagent.

    Returns the parsed dict, or raises FileNotFoundError / ValueError.
    """
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    raw = checkpoint_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in checkpoint: {exc}") from exc

    schema = data.get("schema_version", "unknown")
    if schema != "1.0":
        print(
            f"WARNING: Checkpoint schema '{schema}' differs from expected '1.0'.",
            file=sys.stderr,
        )

    return data


def format_handoff_prompt(checkpoint: dict[str, Any]) -> str:
    """
    Render a human-readable handoff summary from a checkpoint dict.

    Designed to be prepended to a new subagent's initial prompt.
    """
    lines: list[str] = [
        "# Subagent Handoff — Context Checkpoint",
        f"Checkpoint created: {checkpoint.get('created_at', 'unknown')}",
        "",
        "## Active WRK Items",
    ]

    for item in checkpoint.get("active_wrk_items", []):
        wrk_id = item.get("id", "?")
        title = item.get("title", "")
        pct = item.get("percent_complete", "?")
        lines.append(f"### {wrk_id}: {title} ({pct}% complete)")

        ss = item.get("session_state", {})
        if ss.get("progress_notes"):
            lines.append(f"Progress: {ss['progress_notes']}")

        next_steps = ss.get("next_steps", [])
        if next_steps:
            lines.append("Next steps:")
            for step in next_steps[:5]:
                lines.append(f"  - {step}")
        lines.append("")

    modified = checkpoint.get("modified_files", [])
    if modified:
        lines.append("## Modified Files (uncommitted)")
        for f in modified:
            lines.append(f"  - {f}")
        lines.append("")

    git = checkpoint.get("git_state", {})
    if git.get("branch"):
        lines.append(f"## Git Branch: {git['branch']}")
        if git.get("recent_commits"):
            lines.append("Recent commits:")
            for commit_line in git["recent_commits"].splitlines():
                lines.append(f"  {commit_line}")
        lines.append("")

    lines.append(checkpoint.get("handoff_instructions", ""))
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serialize or read subagent checkpoint state."
    )
    sub = parser.add_subparsers(dest="command")

    # write sub-command
    write_cmd = sub.add_parser("write", help="Write a new checkpoint")
    write_cmd.add_argument("--workspace", required=True, help="Path to workspace root")
    write_cmd.add_argument(
        "--active-wrk",
        required=True,
        help="Comma-separated WRK IDs (e.g. WRK-387,WRK-388)",
    )
    write_cmd.add_argument(
        "--modified-files",
        default="",
        help="Comma-separated modified file paths",
    )
    write_cmd.add_argument(
        "--output",
        required=True,
        help="Output JSON file path",
    )

    # read sub-command
    read_cmd = sub.add_parser("read", help="Read a checkpoint and print handoff prompt")
    read_cmd.add_argument("--checkpoint", required=True, help="Path to checkpoint JSON")

    # Legacy flat-arg interface used by refresh-context.sh
    parser.add_argument("--workspace", help=argparse.SUPPRESS)
    parser.add_argument("--active-wrk", help=argparse.SUPPRESS)
    parser.add_argument("--modified-files", default="", help=argparse.SUPPRESS)
    parser.add_argument("--output", help=argparse.SUPPRESS)

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    # Legacy flat invocation (no sub-command): behave as write
    if args.command is None:
        if not args.workspace or not args.active_wrk or not args.output:
            parser.print_help()
            sys.exit(1)
        workspace = Path(args.workspace)
        active_wrk_ids = [x.strip() for x in args.active_wrk.split(",") if x.strip()]
        modified_files = [
            f.strip()
            for f in args.modified_files.split(",")
            if f.strip()
        ]
        write_checkpoint(
            workspace=workspace,
            active_wrk_ids=active_wrk_ids,
            modified_files=modified_files,
            output_path=Path(args.output),
        )
        return

    if args.command == "write":
        workspace = Path(args.workspace)
        active_wrk_ids = [x.strip() for x in args.active_wrk.split(",") if x.strip()]
        modified_files = [
            f.strip()
            for f in args.modified_files.split(",")
            if f.strip()
        ]
        write_checkpoint(
            workspace=workspace,
            active_wrk_ids=active_wrk_ids,
            modified_files=modified_files,
            output_path=Path(args.output),
        )

    elif args.command == "read":
        checkpoint = read_checkpoint(Path(args.checkpoint))
        print(format_handoff_prompt(checkpoint))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
