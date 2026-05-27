#!/usr/bin/env python3
"""Load workspace-hub kanban YAML manifest into the local Hermes kanban.

Re-runnable. Each task is created in a block-ELIGIBLE status (`running`) and then
immediately given a sticky blocked REASON via `hermes kanban block <id> "<reason>"`.
This sequence matters (verified against hermes v0.14.0 source):

  * `hermes kanban block <id>` (kanban_db.block_task) does
    `UPDATE tasks SET status='blocked' ... WHERE status IN ('running','ready')`
    and ONLY emits the sticky `"blocked"` event row in `task_events` on a
    successful 1-row update. The gateway's `recompute_ready`/`_has_sticky_block`
    keys auto-unblock suppression on that `"blocked"` event being the most recent
    block/unblock event.
  * Therefore a card CREATED already-`blocked` matches 0 rows in block_task,
    returns False, emits NO sticky event, and the gateway auto-unblocks it to
    `ready` anyway (claimable → runaway worker fan-out). Creating `running` first
    makes the running→blocked transition succeed and the sticky event fire.
    (`[[feedback_hermes_blocked_status_auto_unblocked]]`)
  * `triage` is the gateway pipeline ENTRY (a specifier fleshes it out and
    promotes), so it is NOT a safe park either.
    (`[[feedback_hermes_triage_is_pipeline_entry]]`)

Idempotent re-run: `create --json` (kanban._cmd_create → _task_to_dict) emits the
card's CURRENT `status`; on idempotency-key reuse it returns the EXISTING card
with its existing status. We call `block` ONLY when that status is `running` or
`ready` (block-eligible). If it is already `blocked` (sticky), we skip the block
call entirely — this avoids the `_cmd_block` comment-bloat (it appends a
`BLOCKED:` comment BEFORE block_task on every call) and the false failure
(block_task returns False on an already-blocked card → exit 1).

`hermes kanban create` has no blocked-reason flag (verified hermes v0.14.0), so
the reason is applied as a follow-up `block` call. Use --dry-run to preview.
Use --board <slug> for one board.

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

# Durable blocked reason. A blocked card WITHOUT a sticky `"blocked"` event is
# auto-unblocked to `ready` by the Hermes gateway within minutes; the sticky
# event (emitted only by a successful running/ready -> blocked transition) makes
# the park survive and forces explicit human promotion. Keep this non-empty.
BLOCKED_REASON = "kanban-import: promote manually (gateway must not auto-unblock)"

# Card statuses on which `hermes kanban block` will succeed (and emit the sticky
# event). Mirrors kanban_db.block_task's `WHERE status IN ('running','ready')`.
BLOCK_ELIGIBLE = ("running", "ready")


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

    # Create in a block-ELIGIBLE status. A card created already-`blocked` cannot
    # be sticky-blocked (block_task matches 0 rows, emits no sticky event), so
    # the gateway auto-unblocks it. `running` -> `block` DOES emit the sticky
    # event. The card sits `running` only for the microseconds between these two
    # synchronous calls; the loader runs on Manual-orchestration machines (the
    # opt-in marker gates the timer) so there is no dispatcher racing to claim it.
    cmd = ["hermes", "kanban", "--board", slug, "create",
           "--initial-status", "running",
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

    # `create --json` emits the card's CURRENT status; on idempotency-key reuse
    # it returns the EXISTING card (with its existing status). Parse both id and
    # status so we can (a) target the block call and (b) skip it idempotently.
    task_id = None
    status = None
    if not dry and out:
        try:
            data = json.loads(out)
            task_id = data.get("id")
            status = data.get("status")
            print(f"    + {key} -> {task_id or '?'} ({status or '?'})")
        except json.JSONDecodeError:
            print(f"    + {key} (no json)")

    if dry:
        # Preview the block call so --dry-run shows the full intended sequence.
        run(["hermes", "kanban", "--board", slug, "block", "<id>",
             BLOCKED_REASON], dry)
        return True

    if not task_id:
        # create succeeded but we couldn't parse an id — cannot guarantee the
        # safe-park reason was applied. Fail loud rather than leave a card the
        # gateway will auto-unblock.
        print(f"    ERROR {key}: no task id from create; cannot apply "
              f"blocked reason (card may auto-unblock)", file=sys.stderr)
        return False

    # Idempotency: only block a block-ELIGIBLE card. An already-`blocked` card
    # (sticky, from a prior run) is skipped — re-blocking would bloat comments
    # (_cmd_block appends a BLOCKED: comment before block_task) and report a
    # false failure (block_task returns False on a blocked card).
    if status not in BLOCK_ELIGIBLE:
        print(f"      = {key}: already {status!r} (sticky park); skip block")
        return True

    block_cmd = ["hermes", "kanban", "--board", slug, "block",
                 task_id, BLOCKED_REASON]
    brc, _bout, berr = run(block_cmd, dry)
    if brc != 0:
        # The card IS block-eligible, so a failure here is real — fail loud.
        print(f"    ERROR {key}: blocked-reason apply failed: "
              f"{berr.strip()}", file=sys.stderr)
        return False
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
