#!/usr/bin/env bash
# codex-session-export.sh — Export Codex sessions to orchestrator JSONL format
#
# Converts ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl to
# logs/orchestrator/codex/session_YYYYMMDD.jsonl matching the Claude
# orchestrator format for provider-parity session analysis.
#
# Usage: bash scripts/cron/codex-session-export.sh [--dry-run] [--all]
# Cron: called by comprehensive-learning-nightly.sh
#
# Codex rollout files are mutable and get rewritten as sessions continue.
# This exporter dedupes per tool call so reruns append only new records.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
CODEX_SESSIONS="${HOME}/.codex/sessions"
OUTPUT_DIR="${WORKSPACE_HUB}/logs/orchestrator/codex"
STATE_FILE="${OUTPUT_DIR}/.export-state.json"

DRY_RUN=false
EXPORT_ALL=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --all) EXPORT_ALL=true ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

if [[ ! -d "$CODEX_SESSIONS" ]]; then
  echo "No Codex sessions directory at $CODEX_SESSIONS — skipping"
  exit 0
fi

if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then
  rm -f "$OUTPUT_DIR"/session_*.jsonl "$STATE_FILE"
fi

uv run --no-project python - "$WORKSPACE_HUB" "$CODEX_SESSIONS" "$OUTPUT_DIR" "$STATE_FILE" "$DRY_RUN" "$EXPORT_ALL" <<'PY'
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

workspace_hub = Path(sys.argv[1]).resolve()
codex_sessions = Path(sys.argv[2]).expanduser()
output_dir = Path(sys.argv[3])
state_file = Path(sys.argv[4])
dry_run = sys.argv[5].lower() == "true"
export_all = sys.argv[6].lower() == "true"

TOOL_MAP = {
    "exec_command": "Bash",
    "read_file": "Read",
    "write_file": "Write",
    "apply_diff": "Edit",
    "write_stdin": "Bash",
    "list_directory": "Read",
    "search_files": "Grep",
    "browser": "Browser",
}


def load_state() -> dict:
    if export_all or not state_file.exists():
        return {"sessions": {}}
    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("sessions"), dict):
            return payload
    except Exception:
        pass
    return {"sessions": {}}


def save_state(payload: dict) -> None:
    tmp = state_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(state_file)


def normalize_arguments(raw_args):
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def command_from_args(args: dict) -> str:
    command = str(args.get("command", "") or "")
    cmd_parts = args.get("cmd", [])
    if isinstance(cmd_parts, list):
        suffix = " ".join(part for part in cmd_parts if isinstance(part, str)).strip()
        if suffix:
            command = f"{command} {suffix}".strip() if command else suffix
    return command[:1000]


state = load_state()
state_sessions = state.setdefault("sessions", {})
output_lines: dict[str, list[str]] = defaultdict(list)
exported_records = 0
skipped_sessions = 0
matching_sessions = 0

for session_file in sorted(codex_sessions.glob("**/rollout-*.jsonl")):
    if not session_file.is_file():
        continue

    parts = session_file.parts
    session_date = ""
    for idx in range(len(parts) - 3):
        year, month, day = parts[idx], parts[idx + 1], parts[idx + 2]
        if year.isdigit() and len(year) == 4 and month.isdigit() and len(month) == 2 and day.isdigit() and len(day) == 2:
            session_date = f"{year}{month}{day}"
            break
    if not session_date:
        skipped_sessions += 1
        continue

    try:
        raw_lines = session_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        skipped_sessions += 1
        continue

    matching_sessions += 1
    session_id = ""
    model = "codex"
    exported_ids = set()
    session_key = str(session_file)
    previous = state_sessions.get(session_key, {})
    if isinstance(previous, dict):
        exported_ids = set(previous.get("exported_tool_call_ids", []))
    session_exported_ids = set(exported_ids)

    for raw_line in raw_lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            obj = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        ts = str(obj.get("timestamp", "") or "")
        msg_type = str(obj.get("type", "") or "")
        payload = obj.get("payload", {})
        if not isinstance(payload, dict):
            continue

        if msg_type == "session_meta":
            session_id = str(payload.get("id", session_id) or session_id)
            model = str(payload.get("model_provider", model) or model)
            continue

        if msg_type != "response_item" or payload.get("type") != "function_call":
            continue

        name = str(payload.get("name", "") or "")
        if not name:
            continue
        args = normalize_arguments(payload.get("arguments", {}))
        fingerprint = str(payload.get("call_id", "") or payload.get("id", "") or "")
        if not fingerprint:
            fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "session_file": str(session_file),
                        "session_id": session_id,
                        "timestamp": ts,
                        "name": name,
                        "args": args,
                    },
                    sort_keys=True,
                    default=str,
                ).encode("utf-8")
            ).hexdigest()[:24]
        if fingerprint in exported_ids and not export_all:
            continue

        mapped = TOOL_MAP.get(name, name)
        entry = {
            "ts": ts,
            "hook": "post",
            "tool": mapped,
            "codex_tool": name,
            "project": workspace_hub.name,
            "repo": workspace_hub.name,
            "model": model,
            "session_id": session_id,
            "native_session_file": str(session_file),
            "tool_call_id": fingerprint,
        }
        if name in {"exec_command", "write_stdin"}:
            entry["cmd"] = command_from_args(args)
        elif name in {"read_file", "write_file", "apply_diff", "list_directory"}:
            entry["file"] = str(args.get("path", args.get("file_path", args.get("dir_path", ""))) or "")[:1000]
        elif name == "search_files":
            entry["query"] = str(args.get("pattern", args.get("query", "")) or "")[:1000]
            root = str(args.get("path", args.get("dir_path", "")) or "")
            if root:
                entry["search_root"] = root[:1000]

        output_lines[session_date].append(json.dumps(entry, default=str))
        session_exported_ids.add(fingerprint)
        exported_records += 1

    state_sessions[session_key] = {
        "session_id": session_id,
        "native_session_file": str(session_file),
        "exported_tool_call_ids": sorted(session_exported_ids),
    }

if dry_run:
    for day, lines in sorted(output_lines.items()):
        print(f"[dry-run] Would append {len(lines)} Codex records -> session_{day}.jsonl")
else:
    for day, lines in sorted(output_lines.items()):
        out = output_dir / f"session_{day}.jsonl"
        with out.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    save_state(state)

print(
    f"Codex session export: {exported_records} records exported from {matching_sessions} matching sessions, {skipped_sessions} skipped"
)
PY
