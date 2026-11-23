#!/usr/bin/env bash
# gemini-session-export.sh — Export Gemini native sessions to orchestrator JSONL format
#
# Converts native Gemini session JSON files under ~/.gemini/tmp/<project>/chats and
# ~/.gemini/tmp/<projectHash>/chats into logs/orchestrator/gemini/session_YYYYMMDD.jsonl
# for provider-parity session analysis.
#
# Usage: bash scripts/cron/gemini-session-export.sh [--dry-run] [--all]
# Cron: called by comprehensive-learning-nightly.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_HUB="$(cd "$SCRIPT_DIR/../.." && pwd)"
GEMINI_TMP="${HOME}/.gemini/tmp"
OUTPUT_DIR="${WORKSPACE_HUB}/logs/orchestrator/gemini"
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

if [[ ! -d "$GEMINI_TMP" ]]; then
  echo "No Gemini tmp directory at $GEMINI_TMP — skipping"
  exit 0
fi

if [[ "$EXPORT_ALL" == "true" && "$DRY_RUN" == "false" ]]; then
  rm -f "$OUTPUT_DIR"/session_*.jsonl "$STATE_FILE"
fi

uv run --no-project python - "$WORKSPACE_HUB" "$GEMINI_TMP" "$OUTPUT_DIR" "$STATE_FILE" "$DRY_RUN" "$EXPORT_ALL" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

workspace_hub = Path(sys.argv[1]).resolve()
gemini_tmp = Path(sys.argv[2]).expanduser()
output_dir = Path(sys.argv[3])
state_file = Path(sys.argv[4])
dry_run = sys.argv[5].lower() == "true"
export_all = sys.argv[6].lower() == "true"

repo_name = workspace_hub.name
repo_hash = hashlib.sha256(str(workspace_hub).encode("utf-8")).hexdigest()

candidate_dirs = [
    gemini_tmp / repo_name / "chats",
    gemini_tmp / repo_hash / "chats",
]

TOOL_MAP = {
    "run_shell_command": "Bash",
    "read_file": "Read",
    "list_directory": "Read",
    "write_file": "Write",
    "replace": "Edit",
    "grep_search": "Grep",
    "glob": "Grep",
    "search_file_content": "Grep",
    "google_web_search": "Browser",
    "write_todos": "Write",
    "codebase_investigator": "ToolSearch",
    "cli_help": "ToolSearch",
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


def iso_to_day(ts: str) -> str:
    if not ts:
        return datetime.now(timezone.utc).strftime("%Y%m%d")
    try:
        normalized = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).strftime("%Y%m%d")
    except Exception:
        digits = "".join(ch for ch in ts if ch.isdigit())
        if len(digits) >= 8:
            return digits[:8]
        return datetime.now(timezone.utc).strftime("%Y%m%d")


def extract_response_payload(tool_call: dict) -> dict:
    for item in tool_call.get("result", []) or []:
        if not isinstance(item, dict):
            continue
        function_response = item.get("functionResponse")
        if not isinstance(function_response, dict):
            continue
        response = function_response.get("response")
        if isinstance(response, dict):
            return response
    return {}


def classify_entry(tool_name: str, args: dict, response: dict) -> dict:
    entry = {}
    if tool_name == "run_shell_command":
        entry["cmd"] = str(args.get("command", ""))[:1000]
    elif tool_name in {"read_file", "write_file", "replace"}:
        entry["file"] = str(args.get("file_path", args.get("path", "")))[:1000]
    elif tool_name == "list_directory":
        entry["file"] = str(args.get("dir_path", ""))[:1000]
    elif tool_name in {"grep_search", "glob", "google_web_search", "codebase_investigator", "cli_help"}:
        query = args.get("pattern", args.get("query", args.get("objective", args.get("question", ""))))
        entry["query"] = str(query)[:1000]
        search_root = args.get("dir_path", "")
        if search_root:
            entry["search_root"] = str(search_root)[:1000]
    elif tool_name == "write_todos":
        todos = args.get("todos", [])
        entry["todo_count"] = len(todos) if isinstance(todos, list) else 0
    if response.get("error"):
        entry["error"] = str(response.get("error"))[:1000]
    return entry


state = load_state()
state_sessions = state.setdefault("sessions", {})
output_lines: dict[str, list[str]] = defaultdict(list)
seen_files: set[Path] = set()
exported = 0
skipped = 0
matched_sessions = 0

for chats_dir in candidate_dirs:
    if not chats_dir.exists():
        continue
    for session_file in sorted(chats_dir.glob("session-*.json")):
        try:
            resolved = session_file.resolve()
        except Exception:
            resolved = session_file
        if resolved in seen_files:
            continue
        seen_files.add(resolved)
        try:
            session = json.loads(session_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            skipped += 1
            continue

        if session.get("projectHash") != repo_hash:
            continue
        matched_sessions += 1

        session_id = str(session.get("sessionId", "") or "")
        session_kind = str(session.get("kind", "") or "")
        session_summary = str(session.get("summary", "") or "")[:500]
        start_time = str(session.get("startTime", "") or "")
        last_updated = str(session.get("lastUpdated", "") or "")
        model_fallback = "gemini"

        exported_ids = set(state_sessions.get(session_id, {}).get("exported_tool_call_ids", [])) if session_id else set()
        messages = session.get("messages", []) or []
        session_exported_ids = set(exported_ids)

        for message in messages:
            if not isinstance(message, dict):
                continue
            if message.get("type") != "gemini":
                continue
            model = str(message.get("model", model_fallback) or model_fallback)
            message_ts = str(message.get("timestamp", "") or start_time)
            tool_calls = message.get("toolCalls", []) or []
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                tool_id = str(tool_call.get("id", "") or "")
                tool_name = str(tool_call.get("name", "") or "")
                if not tool_name:
                    continue
                fingerprint = tool_id or hashlib.sha256(
                    json.dumps(
                        {
                            "session_id": session_id,
                            "timestamp": tool_call.get("timestamp", message_ts),
                            "name": tool_name,
                            "args": tool_call.get("args", {}),
                        },
                        sort_keys=True,
                        default=str,
                    ).encode("utf-8")
                ).hexdigest()[:24]
                if fingerprint in exported_ids and not export_all:
                    continue

                args = tool_call.get("args", {})
                if not isinstance(args, dict):
                    args = {}
                response = extract_response_payload(tool_call)
                record_ts = str(tool_call.get("timestamp", "") or message_ts or start_time)
                output_day = iso_to_day(record_ts)
                mapped_tool = TOOL_MAP.get(tool_name, tool_name)
                entry = {
                    "ts": record_ts,
                    "hook": "post",
                    "tool": mapped_tool,
                    "gemini_tool": tool_name,
                    "project": repo_name,
                    "repo": repo_name,
                    "model": model,
                    "session_id": session_id,
                    "project_hash": repo_hash,
                    "session_kind": session_kind,
                    "session_summary": session_summary,
                    "native_session_file": str(session_file),
                    "tool_status": str(tool_call.get("status", "") or ""),
                    "msg_id": str(message.get("id", "") or ""),
                    "tool_call_id": fingerprint,
                }
                entry.update(classify_entry(tool_name, args, response))
                output_lines[output_day].append(json.dumps(entry, default=str))
                session_exported_ids.add(fingerprint)
                exported += 1

        if session_id:
            state_sessions[session_id] = {
                "last_updated": last_updated,
                "native_session_file": str(session_file),
                "exported_tool_call_ids": sorted(session_exported_ids),
            }

if dry_run:
    for day, lines in sorted(output_lines.items()):
        print(f"[dry-run] Would append {len(lines)} Gemini records -> session_{day}.jsonl")
else:
    for day, lines in sorted(output_lines.items()):
        out = output_dir / f"session_{day}.jsonl"
        with out.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    save_state(state)

print(f"Gemini session export: {exported} records exported from {matched_sessions} matching sessions, {skipped} skipped")
PY
