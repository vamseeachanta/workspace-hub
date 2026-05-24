#!/usr/bin/env python3
"""Load workspace-hub kanban YAML manifest into the local Hermes kanban.

Re-runnable. All tasks land in `triage` status so workers can never auto-claim
imports. Use --dry-run to preview. Use --board <slug> to load a single board.

Reads from: workspace-hub/.claude/memory/kanban/boards/*.yaml
Writes to:  ~/.hermes/kanban.db via `hermes kanban` CLI.

Exit codes: 0 ok, 1 partial (some cards failed), 2 fatal (hermes missing, schema bad).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: uv pip install pyyaml")


KANBAN_ROOT = Path(__file__).resolve().parent.parent
BOARDS_DIR = KANBAN_ROOT / "boards"


def run(cmd: list[str], dry: bool) -> tuple[int, str, str]:
    if dry:
        print(f"  [dry] {' '.join(cmd)}")
        return 0, "", ""
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def hermes_available() -> bool:
    return subprocess.run(["hermes", "--version"], capture_output=True).returncode == 0


def board_exists(slug: str) -> bool:
    p = subprocess.run(
        ["hermes", "kanban", "boards", "list"], capture_output=True, text=True
    )
    if p.returncode != 0:
        return False
    # Output is a human table; slug appears at line start after the status glyph.
    for line in p.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == slug:
            return True
        if len(parts) >= 1 and parts[0] == slug:
            return True
    return False


def ensure_board(board: dict, dry: bool) -> bool:
    slug = board["slug"]
    if not dry and board_exists(slug):
        print(f"  board {slug}: exists, skipping create")
        return True
    cmd = ["hermes", "kanban", "boards", "create", slug,
           "--name", board.get("display_name", slug)]
    if board.get("workspace_path"):
        # set default workdir so cards default to the right repo
        rc, *_ = run(cmd, dry)
        if rc != 0:
            return False
        cmd2 = ["hermes", "kanban", "boards", "set-default-workdir",
                slug, board["workspace_path"]]
        rc2, *_ = run(cmd2, dry)
        return rc2 == 0
    rc, *_ = run(cmd, dry)
    return rc == 0


def create_card(slug: str, card: dict, workspace_path: str | None, dry: bool) -> bool:
    if card.get("source") == "detected_gap":
        return True  # skip; YAML-only

    key = card["idempotency_key"]
    title = card["title"]

    body_parts = []
    if card.get("source_url"):
        body_parts.append(f"Source: {card['source_url']}")
    if card.get("gh_state"):
        body_parts.append(f"GH state: {card['gh_state']}")
    if card.get("gh_labels"):
        body_parts.append(f"GH labels: {', '.join(card['gh_labels'])}")
    if card.get("body_excerpt"):
        body_parts.append("")
        body_parts.append(card["body_excerpt"].strip())
    body = "\n".join(body_parts) if body_parts else ""

    cmd = ["hermes", "kanban", "--board", slug, "create",
           "--initial-status", "blocked",
           "--idempotency-key", key,
           "--created-by", "kanban-loader",
           "--priority", str(card.get("priority", 0)),
           "--json"]
    if workspace_path:
        cmd += ["--workspace", f"dir:{workspace_path}"]
    if body:
        cmd += ["--body", body]
    cmd.append(title)

    rc, out, err = run(cmd, dry)
    if rc != 0:
        print(f"    ERROR {key}: {err.strip() or out.strip()}", file=sys.stderr)
        return False
    if not dry and out:
        try:
            data = json.loads(out)
            print(f"    + {key} -> {data.get('id', '?')}")
        except json.JSONDecodeError:
            print(f"    + {key} (no json)")
    return True


def load_board_file(path: Path, dry: bool) -> tuple[int, int]:
    with path.open() as f:
        doc = yaml.safe_load(f)
    board = doc.get("board")
    cards = doc.get("cards", [])
    if not board:
        print(f"  SKIP {path.name}: no `board:` key")
        return 0, 0

    print(f"\nBoard: {board['slug']}  ({len(cards)} cards)")
    if not ensure_board(board, dry):
        print(f"  FATAL: board create failed for {board['slug']}")
        return 0, len(cards)

    ok = fail = 0
    workspace_path = board.get("workspace_path")
    for card in cards:
        if create_card(board["slug"], card, workspace_path, dry):
            ok += 1
        else:
            fail += 1
    return ok, fail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Print commands, do not execute")
    ap.add_argument("--board", help="Only load this slug (filename stem)")
    args = ap.parse_args()

    if not args.dry_run and not hermes_available():
        print("FATAL: `hermes` CLI not on PATH", file=sys.stderr)
        return 2

    if not BOARDS_DIR.exists():
        print(f"FATAL: {BOARDS_DIR} does not exist", file=sys.stderr)
        return 2

    files = sorted(BOARDS_DIR.glob("*.yaml"))
    if args.board:
        files = [f for f in files if f.stem == args.board]
        if not files:
            print(f"FATAL: no board file for {args.board}", file=sys.stderr)
            return 2

    total_ok = total_fail = total_boards = 0
    for fp in files:
        ok, fail = load_board_file(fp, args.dry_run)
        total_ok += ok
        total_fail += fail
        total_boards += 1

    print(f"\n=== Summary ===")
    print(f"  boards processed: {total_boards}")
    print(f"  cards ok:         {total_ok}")
    print(f"  cards failed:     {total_fail}")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
