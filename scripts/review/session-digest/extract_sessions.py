#!/usr/bin/env python3
"""Digest Claude Code and Codex session logs into compact JSONL (stdlib only; #3973).

Run it ON each machine so raw logs never leave their host; copy back only the digest.

    python -I extract_sessions.py --label win1 --out win1.jsonl [--home DIR ...]

Default homes: every C:/Users/* on Windows, otherwise ~. Reads
<home>/.claude/projects/**/*.jsonl and <home>/.codex/{sessions,archived_sessions}/**/*.jsonl.

Per session: provider, path, size, cwd, start/end, model/sandbox/approval, tool counts,
tool errors, interrupts, denials, compactions, operator prompts (truncated) and closing
messages. Digests carry client content: keep them local or in a private repository.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
from pathlib import Path

MAXP = 700
SKIP_PREFIX = ("<system-reminder", "<local-command", "<command-message", "Caveat:",
               "<user-prompt-submit-hook", "<task-notification")
CODEX_SKIP = ("# AGENTS.md", "<environment_context", "<user_instructions", "<permissions",
              "<INSTRUCTIONS", "<turn_aborted", "<subagent_notification")
EXIT_RE = re.compile(r'"?exit_code"?\s*[:=]\s*(-?\d+)')


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") in ("text", "input_text"))
    return ""


def _base(provider: str, path: Path) -> dict:
    return dict(provider=provider, file=str(path), size_mb=round(path.stat().st_size / 1e6, 1),
                subagent=False, prompts=[], outcomes=[], tools=collections.Counter(), tool_errors=0,
                interrupts=0, denials=0, compactions=0, models=collections.Counter(), cwd=None,
                start=None, end=None, error_samples=[], bad_lines=0)


def _records(path: Path, r: dict):
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                r["bad_lines"] += 1
                continue
            if not isinstance(d, dict):
                r["bad_lines"] += 1
                continue
            ts = d.get("timestamp")
            if ts:
                r["start"] = r["start"] or ts
                r["end"] = ts
            yield d, ts


def parse_claude(path) -> dict:
    path = Path(path)
    r = _base("claude", path)
    r["subagent"] = "subagents" in path.parts
    for d, ts in _records(path, r):
        r["cwd"] = r["cwd"] or d.get("cwd")
        t, m = d.get("type"), d.get("message") or {}
        if t == "system" and d.get("subtype") == "compact_boundary":
            r["compactions"] += 1
        elif t == "assistant":
            if m.get("model"):
                r["models"][m["model"]] += 1
            for b in m.get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    r["tools"][b.get("name", "?")] += 1
                elif b.get("type") == "text" and len(b.get("text", "")) > 200 and not r["subagent"]:
                    r["outcomes"] = (r["outcomes"] + [(ts, b["text"][:500])])[-4:]
        elif t == "user":
            c = m.get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                        r["tool_errors"] += 1
                        bt = b.get("content") if isinstance(b.get("content"), str) else _text(b.get("content"))
                        if "doesn't want to proceed" in (bt or ""):
                            r["denials"] += 1
                        elif len(r["error_samples"]) < 12:
                            r["error_samples"].append((bt or "")[:240])
            if d.get("isMeta") or d.get("isCompactSummary") or r["subagent"]:
                continue
            s = _text(c).strip()
            if not s:
                continue
            if s.startswith("[Request interrupted"):
                r["interrupts"] += 1
            elif "<command-name>" in s[:400]:
                name = s.split("<command-name>", 1)[1].split("</command-name>", 1)[0]
                r["prompts"].append((ts, "CMD " + name))
            elif not s.startswith(SKIP_PREFIX):
                r["prompts"].append((ts, s[:MAXP]))
    return r


def parse_codex(path) -> dict:
    path = Path(path)
    r = _base("codex", path)
    r.update(originator=None, cli_version=None, sandbox=None, approval=None)
    seen = set()

    def prompt(ts, s):
        s = (s or "").strip()
        if s and not s.startswith(CODEX_SKIP) and not s.startswith(SKIP_PREFIX) and s[:MAXP] not in seen:
            seen.add(s[:MAXP])
            r["prompts"].append((ts, s[:MAXP]))

    for d, ts in _records(path, r):
        t, p = d.get("type"), d.get("payload") or {}
        if t == "session_meta":
            r["cwd"] = r["cwd"] or p.get("cwd")
            r["originator"], r["cli_version"] = p.get("originator"), p.get("cli_version")
        elif t == "turn_context":
            if p.get("model"):
                r["models"][p["model"]] += 1
            r["approval"] = p.get("approval_policy") if isinstance(p.get("approval_policy"), str) else str(p.get("approval_policy"))
            sp = p.get("sandbox_policy")
            r["sandbox"] = sp.get("type") if isinstance(sp, dict) else sp
        elif t == "compacted":
            r["compactions"] += 1
        elif t == "event_msg":
            pt = p.get("type")
            if pt == "user_message":
                prompt(ts, p.get("message"))
            elif pt == "turn_aborted":
                r["interrupts"] += 1
            elif pt == "context_compacted":
                r["compactions"] += 1
            elif pt == "task_complete" and p.get("last_agent_message"):
                r["outcomes"].append((ts, p["last_agent_message"][:500]))
            elif pt == "exec_command_end" and p.get("exit_code") not in (0, None):
                r["tool_errors"] += 1
        elif t == "response_item":
            pt = p.get("type")
            if pt in ("function_call", "custom_tool_call", "local_shell_call", "web_search_call"):
                r["tools"][p.get("name") or pt] += 1
            elif pt == "message" and p.get("role") == "user":
                prompt(ts, _text(p.get("content")))
            elif pt in ("custom_tool_call_output", "function_call_output"):
                o = p.get("output")
                o = o if isinstance(o, str) else _text(o)
                mm = EXIT_RE.search(o or "")
                if mm and mm.group(1) != "0":
                    r["tool_errors"] += 1
                    if len(r["error_samples"]) < 12:
                        r["error_samples"].append((o or "")[:240])
    return r


def discover(homes) -> list[tuple[str, str]]:
    found = []
    for h in homes:
        h = Path(h)
        found += [("claude", f) for f in glob.glob(str(h / ".claude" / "projects" / "**" / "*.jsonl"), recursive=True)]
        for sub in ("sessions", "archived_sessions"):
            found += [("codex", f) for f in glob.glob(str(h / ".codex" / sub / "**" / "*.jsonl"), recursive=True)]
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="machine label written into every record")
    ap.add_argument("--out", required=True)
    ap.add_argument("--home", action="append", help="home directory to scan (repeatable)")
    a = ap.parse_args(argv)
    homes = a.home or (glob.glob("C:/Users/*") if os.name == "nt" else [os.path.expanduser("~")])
    files = discover(homes)
    with open(a.out, "w", encoding="utf-8") as o:
        for kind, f in files:
            try:
                r = (parse_claude if kind == "claude" else parse_codex)(f)
            except OSError as exc:
                r = dict(provider=kind, file=f, fatal=str(exc))
            r["machine"] = a.label
            for k in ("tools", "models"):
                if k in r:
                    r[k] = dict(r[k])
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"label": a.label, "sessions": len(files), "out": a.out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
