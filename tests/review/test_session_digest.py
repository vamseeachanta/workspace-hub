"""Tests for scripts/review/session-digest/ (#3973 D5/D6: repeatable session review).

The extractor turns Claude Code and Codex session logs into compact digests
(prompts, closing messages, counts) so a reviewer can read months of sessions.
Logs and digests contain client content and are never committed; only the tool is.
"""
import importlib.util
import json
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "scripts" / "review" / "session-digest"


def load(name):
    spec = importlib.util.spec_from_file_location(name, DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def jl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return path


def test_claude_session_prompts_tools_errors_and_interrupts(tmp_path):
    ex = load("extract_sessions")
    p = jl(tmp_path / "s.jsonl", [
        {"type": "user", "timestamp": "2026-10-01T10:00:00Z", "cwd": "D:\\ws", "message": {"role": "user", "content": "review the CFD lanes"}},
        {"type": "user", "timestamp": "2026-10-01T10:00:01Z", "isMeta": True, "message": {"content": "meta text"}},
        {"type": "user", "timestamp": "2026-10-01T10:00:02Z", "message": {"content": "<system-reminder>x</system-reminder>"}},
        {"type": "assistant", "timestamp": "2026-10-01T10:00:03Z", "message": {"model": "m1", "content": [
            {"type": "tool_use", "name": "Bash", "input": {}}, {"type": "text", "text": "A" * 250}]}},
        {"type": "user", "timestamp": "2026-10-01T10:00:04Z", "message": {"content": [
            {"type": "tool_result", "is_error": True, "content": "Exit code 1 boom"}]}},
        {"type": "user", "timestamp": "2026-10-01T10:00:05Z", "message": {"content": [
            {"type": "tool_result", "is_error": True, "content": "The user doesn't want to proceed with this tool use."}]}},
        {"type": "user", "timestamp": "2026-10-01T10:00:06Z", "message": {"content": "[Request interrupted by user]"}},
        {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-10-01T10:00:07Z"},
        "not json at all",
    ])
    p.write_text(p.read_text(encoding="utf-8").replace('"not json at all"', "{broken"), encoding="utf-8")
    r = ex.parse_claude(p)
    assert [t for _, t in r["prompts"]] == ["review the CFD lanes"]
    assert r["tools"] == {"Bash": 1} and r["tool_errors"] == 2 and r["denials"] == 1
    assert r["interrupts"] == 1 and r["compactions"] == 1 and r["bad_lines"] == 1
    assert r["cwd"] == "D:\\ws" and r["start"] == "2026-10-01T10:00:00Z"
    assert len(r["outcomes"]) == 1 and r["error_samples"] == ["Exit code 1 boom"]


def test_claude_subagent_logs_keep_counts_but_no_prompts(tmp_path):
    ex = load("extract_sessions")
    p = jl(tmp_path / "proj" / "sess" / "subagents" / "agent-1.jsonl", [
        {"type": "user", "timestamp": "t", "message": {"content": "parent briefing"}},
        {"type": "assistant", "timestamp": "t", "message": {"content": [{"type": "tool_use", "name": "Read"}]}}])
    r = ex.parse_claude(p)
    assert r["subagent"] is True and r["prompts"] == [] and r["tools"] == {"Read": 1}


def test_codex_both_rollout_formats_and_dedup(tmp_path):
    ex = load("extract_sessions")
    p = jl(tmp_path / "rollout.jsonl", [
        {"type": "session_meta", "timestamp": "2026-09-01T00:00:00Z", "payload": {"cwd": "D:\\ws", "originator": "codex_exec", "cli_version": "0.161.0"}},
        {"type": "turn_context", "timestamp": "t", "payload": {"model": "gpt-x", "approval_policy": "never", "sandbox_policy": {"type": "read-only"}}},
        {"type": "response_item", "timestamp": "t1", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "# AGENTS.md instructions ..."}]}},
        {"type": "response_item", "timestamp": "t2", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "fix the parser"}]}},
        {"type": "event_msg", "timestamp": "t2", "payload": {"type": "user_message", "message": "fix the parser"}},
        {"type": "response_item", "timestamp": "t3", "payload": {"type": "custom_tool_call", "name": "exec"}},
        {"type": "response_item", "timestamp": "t4", "payload": {"type": "custom_tool_call_output", "output": "{\"exit_code\":2}"}},
        {"type": "event_msg", "timestamp": "t5", "payload": {"type": "turn_aborted"}},
        {"type": "compacted", "timestamp": "t6", "payload": {}},
        {"type": "event_msg", "timestamp": "t7", "payload": {"type": "task_complete", "last_agent_message": "done: 3 tests pass"}},
    ])
    r = ex.parse_codex(p)
    assert [t for _, t in r["prompts"]] == ["fix the parser"]
    assert r["originator"] == "codex_exec" and r["sandbox"] == "read-only" and r["models"] == {"gpt-x": 1}
    assert r["tools"] == {"exec": 1} and r["tool_errors"] == 1 and r["interrupts"] == 1 and r["compactions"] == 1
    assert r["outcomes"] == [("t7", "done: 3 tests pass")]


def test_discover_finds_both_providers_under_given_homes(tmp_path):
    ex = load("extract_sessions")
    home = tmp_path / "home"
    jl(home / ".claude" / "projects" / "p" / "a.jsonl", [{"type": "user", "message": {"content": "hi"}}])
    jl(home / ".codex" / "sessions" / "2026" / "10" / "r.jsonl", [{"type": "session_meta", "payload": {}}])
    jl(home / ".codex" / "archived_sessions" / "r2.jsonl", [{"type": "session_meta", "payload": {}}])
    found = ex.discover([home])
    assert sorted(kind for kind, _ in found) == ["claude", "codex", "codex"]


def test_build_digests_splits_at_session_boundaries_and_skips_subagents(tmp_path):
    bd = load("build_digests")
    rows = []
    for i in range(6):
        rows.append({"machine": "m", "provider": "claude", "subagent": False, "file": f"s{i}.jsonl",
                     "start": f"2026-10-0{i + 1}T00:00:00Z", "end": "e", "cwd": "c", "size_mb": 0.1,
                     "tools": {}, "tool_errors": 0, "interrupts": 0, "denials": 0, "compactions": 0,
                     "prompts": [["t", "x" * 400]], "outcomes": [], "error_samples": []})
    rows.append(dict(rows[0], subagent=True, file="sub.jsonl"))
    out = tmp_path / "out"
    chunks = bd.build(rows, out, limit=1200)
    assert len(chunks) >= 2
    text = "".join(c.read_text(encoding="utf-8") for c in chunks)
    assert text.count("=== SESSION ") == 6 and "sub.jsonl" not in text
    for c in chunks:
        assert c.read_text(encoding="utf-8").startswith("\n=== SESSION ")
