from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .accounts import load_account_scope, resolve_state_dir
from .labels import ensure_labels
from .paths import resolve_log_path
from .report import pending_work_report
from .store import QueueStateError, sweep_grace


def main(argv: list[str] | None = None, gmail_client_factory=None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.state_dir:
        log_path = Path(args.state_dir).expanduser() / "queue-state.jsonl"
        account_config = Path(args.state_dir).expanduser() / "accounts.yaml"
    else:
        log_path = resolve_log_path()
        account_config = resolve_state_dir() / "accounts.yaml"
    scope = load_account_scope(account_config)

    if args.command == "report":
        payload = pending_work_report(log_path, account_scope=scope)
    elif args.command == "labels":
        payload = ensure_labels(
            account_scope=scope,
            gmail_client_factory=gmail_client_factory,
            apply=args.apply,
        )
    elif args.command == "sweep":
        try:
            payload = sweep_grace(
                log_path,
                now_utc=args.now_utc or _now_utc(),
                dry_run=not args.apply,
                reactivation_precheck=_load_precheck(args.precheck_json),
            )
        except QueueStateError as exc:
            parser.error(str(exc))
    else:
        parser.print_help()
        return 2

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Email queue-state operator CLI")
    parser.add_argument("--state-dir", help="Runtime state directory")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("report", help="Show pending work status")

    labels = subparsers.add_parser("labels", help="Plan or create Gmail labels")
    labels.add_argument("--apply", action="store_true", help="Create missing labels")

    sweep = subparsers.add_parser("sweep", help="Move grace-expired completed threads to purged")
    sweep_mode = sweep.add_mutually_exclusive_group()
    sweep_mode.add_argument("--dry-run", action="store_true", help="Plan only; no state changes")
    sweep_mode.add_argument("--apply", action="store_true", help="Append purge transitions")
    sweep.add_argument("--precheck-json", help="Required clean precheck JSON for --apply")
    sweep.add_argument("--now-utc", help="UTC timestamp for deterministic sweeps")
    return parser


def _load_precheck(path: str | None):
    if not path:
        return None
    with Path(path).expanduser().open(encoding="utf-8") as handle:
        return json.load(handle)


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
