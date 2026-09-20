#!/usr/bin/env python3
"""Bounded native startup probes; all evidence remains in a supplied private directory."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import stat
import sys


PROTECTED_FILES = ("settings.json", "settings.local.json", ".credentials.json",
                   "plugins/installed_plugins.json", "plugins/known_marketplaces.json",
                   "plugins/config.json", "plugins/settings.json")
PROTECTED_TREES = ("rules", "hooks")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    if json.loads(path.read_text(encoding="utf-8")) != value:
        raise ValueError("Evidence readback failed")


def reject_link_chain(path):
    for item in (path, *path.parents):
        if os.path.lexists(item):
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
                raise ValueError("Protected path has a linked/reparse ancestor")


def protected_state(home, *, admission=False):
    user = Path(home) / ".claude"
    reject_link_chain(user)
    names = set(PROTECTED_FILES)
    for tree in PROTECTED_TREES:
        directory = user / tree
        reject_link_chain(directory)
        if directory.exists():
            for parent, dirs, files in os.walk(directory, followlinks=False):
                for item in dirs:
                    reject_link_chain(Path(parent) / item)
                names.update((Path(parent) / item).relative_to(user).as_posix() for item in files)
    names.discard("rules/workspace-soul.md")
    records = []
    for name in sorted(names):
        path = user / name
        reject_link_chain(path)
        info = path.stat() if path.exists() else None
        if info and not stat.S_ISREG(info.st_mode):
            raise ValueError("Protected file is not regular")
        record = {"path": name, "type": "regular" if info else "absent",
                  "mode": stat.S_IMODE(info.st_mode) if info else None,
                  "attributes": getattr(info, "st_file_attributes", 0) if info else None}
        if not admission or name != ".credentials.json":
            record["sha256"] = sha(path) if info else None
        records.append(record)
    return records


def protected_admission_state(home):
    """Credential rotation is not instruction drift; all policy content remains bound."""
    return protected_state(home, admission=True)


def project_state(repo):
    records = []
    for directory in (repo, *repo.parents):
        for name in ("settings.json", "settings.local.json"):
            path = directory / ".claude" / name
            reject_link_chain(path)
            info = path.stat() if path.exists() else None
            if info and not stat.S_ISREG(info.st_mode):
                raise ValueError("Project settings not regular")
            records.append({"path": str(path), "sha256": sha(path) if info else None,
                            "mode": stat.S_IMODE(info.st_mode) if info else None,
                            "attributes": getattr(info, "st_file_attributes", 0) if info else None})
    return records


def tool_blocks(events, kind):
    return [block for event in events for block in event.get("message", {}).get("content", [])
            if isinstance(block, dict) and block.get("type") == kind]


def validate_read(events, path, denied=False):
    calls = tool_blocks(events, "tool_use")
    if len(calls) != 1 or calls[0].get("name") != "Read":
        raise ValueError("Exactly one Read required")
    supplied = calls[0].get("input", {}).get("file_path", "")
    if not Path(supplied).is_absolute() or Path(supplied) != Path(path):
        raise ValueError("Read path outside exact fixture")
    results = tool_blocks(events, "tool_result")
    if len(results) != 1 or results[0].get("tool_use_id") != calls[0].get("id"):
        raise ValueError("Exact Read result missing")
    if bool(results[0].get("is_error")) != denied:
        raise ValueError("Read result did not match enforcement control")


def validate_events(events, global_token, project_token, read_path=None):
    init = next(e for e in events if e.get("type") == "system" and e.get("subtype") == "init")
    if init.get("tools") != (["Read"] if read_path else []) or init.get("mcp_servers") != []:
        raise ValueError("Startup probe was not tools/MCP disabled")
    if not any(p.get("name") == "agents-md" and p.get("source") == "agents-md@builtin"
               for p in init.get("plugins", [])):
        raise ValueError("Native AGENTS plugin not observed")
    if read_path:
        validate_read(events, read_path)
    elif tool_blocks(events, "tool_use"):
        raise ValueError("Tool attempt invalidated startup probe")
    result = next(e for e in events if e.get("type") == "result")
    if result.get("is_error") or result.get("permission_denials"):
        raise ValueError("Provider result failed or encountered a denial")
    body = result["result"].strip().removeprefix("```json").removesuffix("```").strip()
    expected = {"global_token": global_token, "project_token": project_token}
    if json.loads(body) != expected:
        raise ValueError("Native instruction response mismatch")
    return {"status": "PASS", "tokens": expected,
            "models": list(result.get("modelUsage", {})),
            "limits": "Startup only; lazy nested discovery and other hosts not tested"}


def probe_prompt(global_mode="canary", project_mode="fixture", allow_read=False):
    global_question = ("the feedback identifier for the Edit tool freshness window rule"
                       if global_mode == "canonical" else "the deployment_probe global_token")
    project_question = ("only the readiness contract path (not the upgrade playbook) in the repository instructions"
                        if project_mode == "repository" else "the deployment_probe project_token")
    if global_mode == "bounds":
        global_question = "the deployment_probe beginning_token and global_token joined with |"
    if project_mode == "lazy":
        project_question = "the deployment_probe lazy_token discovered after the Read"
    restriction = " Perform exactly one Read of the supplied path, then no further tools." if allow_read else " Do not use tools."
    return ("Return only JSON with global_token set to " + global_question +
            " and project_token set to " + project_question +
            ", from loaded instructions. For missing values use NOT_LOADED." + restriction)


def check_prompt(prompt, global_token, project_token):
    if any(token != "NOT_LOADED" and token in prompt for token in (global_token, project_token)):
        raise ValueError("Canary leaked into the request")


def native_call(cli, cwd, output, name, prompt, settings=None):
    args = [str(cli), "--print", "--tools", "", "--strict-mcp-config", "--mcp-config",
            '{"mcpServers":{}}', "--no-chrome", "--no-session-persistence",
            "--max-budget-usd", "1", "--output-format", "stream-json", "--verbose"]
    if settings is not None:
        args[3] = "Read"
        args += ["--settings", json.dumps(settings), "--permission-mode", "dontAsk"]
    write_json(output / (name + ".request.json"), {"command": args, "cwd": str(cwd),
               "prompt": prompt, "observed_at": datetime.now(timezone.utc).isoformat()})
    try:
        result = subprocess.run(args, input=prompt.encode(), cwd=cwd, capture_output=True, timeout=90)
    except subprocess.TimeoutExpired as failure:
        for suffix, value in (("stdout.jsonl", failure.stdout), ("stderr.txt", failure.stderr)):
            with (output / (name + "." + suffix)).open("xb") as stream:
                stream.write(value or b"")
        write_json(output / (name + ".timeout.json"), {"status": "BLOCKED", "retry": False})
        raise
    for suffix, value in (("stdout.jsonl", result.stdout), ("stderr.txt", result.stderr)):
        with (output / (name + "." + suffix)).open("xb") as stream:
            stream.write(value)
    if result.returncode:
        raise ValueError("Native provider failed; inspect retained private stderr")
    return [json.loads(line) for line in result.stdout.decode("utf-8").splitlines() if line.strip()]


def guard_settings(allowed, audit):
    guard = Path(__file__).with_name("claude_probe_read_guard.py")
    return {"hooks": {"PreToolUse": [{"matcher": "Read", "hooks": [{"type": "command",
            "command": str(Path(sys.executable).resolve()),
            "args": ["-I", "-B", str(guard.resolve()), "--allowed-file", str(allowed),
                     "--expected-sha256", sha(allowed), "--audit-file", str(audit)],
            "timeout": 10}]}]}}


def validate_audit(audit, events, requested, decision):
    rows = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line]
    calls = tool_blocks(events, "tool_use")
    if (len(rows) != 1 or len(calls) != 1 or rows[0].get("decision") != decision
            or rows[0].get("tool_name") != "Read"
            or rows[0].get("tool_use_id") != calls[0].get("id")
            or Path(rows[0].get("requested_path", "")) != requested):
        raise ValueError("Actual hook enforcement not established")


def run_probe(cli, cwd, output, name, global_token, project_token,
              global_mode="canary", project_mode="fixture", read_path=None):
    prompt = probe_prompt(global_mode, project_mode, allow_read=read_path is not None)
    settings = None
    audit = output / (name + ".audit.jsonl")
    if read_path:
        prompt = "First Read exactly " + str(read_path) + ". " + prompt
        settings = guard_settings(read_path, audit)
    check_prompt(prompt, global_token, project_token)
    events = native_call(cli, cwd, output, name, prompt, settings)
    verdict = validate_events(events, global_token, project_token, read_path)
    if read_path:
        validate_audit(audit, events, read_path, "allow")
    verdict["stdout_sha256"] = sha(output / (name + ".stdout.jsonl"))
    write_json(output / (name + ".verdict.json"), verdict)
    return verdict


def guard_controls(cli, output):
    help_result = subprocess.run([str(cli), "--help"], capture_output=True, timeout=15, check=True)
    if any(flag not in help_result.stdout for flag in (b"--settings", b"--permission-mode", b"--tools")):
        raise ValueError("Ephemeral enforcement settings unsupported")
    (output / "guard-help.txt").write_bytes(help_result.stdout)
    folder = output / "guard-controls"
    folder.mkdir()
    allowed, other = folder / "allowed.txt", folder / "other.txt"
    allowed.write_text("Harmless control.\n")
    other.write_text("Harmless denied control.\n")
    results = {}
    for decision, requested in (("allow", allowed), ("deny", other)):
        name = "guard-control-" + decision
        audit = output / (name + ".audit.jsonl")
        prompt = "Attempt exactly one Read of " + str(requested) + ". Do not retry or use other tools."
        events = native_call(cli, folder, output, name, prompt, guard_settings(allowed, audit))
        init = next(e for e in events if e.get("type") == "system" and e.get("subtype") == "init")
        if init.get("tools") != ["Read"] or init.get("mcp_servers") != []:
            raise ValueError("Unexpected enforcement-control tools")
        validate_read(events, requested, denied=decision == "deny")
        validate_audit(audit, events, requested, decision)
        result = next(e for e in events if e.get("type") == "result")
        if result.get("is_error") or (decision == "allow" and result.get("permission_denials")):
            raise ValueError("Enforcement control did not complete")
        results[decision] = "PASS"
    write_json(output / "guard-controls.json", results)
    return results
