#!/usr/bin/env python3
"""Extract a compact per-session digest from Claude Code jsonl transcripts.
Usage: digest.py <machine> <out_dir> <file1.jsonl> [file2.jsonl ...]
Emits one <out_dir>/<machine>__<sessionstem>.json per input. No LLM, no tokens."""
import json, sys, os, statistics
from collections import Counter

def text_of(content):
    """Return concatenated text from a message content (str or list)."""
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                out.append(c.get("text", ""))
    return " ".join(out)

def tool_names(content):
    names = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                names.append(c.get("name", "?"))
    return names

def digest(path, machine):
    proj = os.path.basename(os.path.dirname(path))
    stem = os.path.splitext(os.path.basename(path))[0]
    turns_by_model = Counter()
    out_tokens_by_model = Counter()
    tools = Counter()
    fable_out_lens = []
    user_prompts = []
    first_ts = last_ts = None
    n_user = 0
    with open(path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            ts = ev.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            t = ev.get("type")
            msg = ev.get("message") or {}
            if t == "assistant" and isinstance(msg, dict):
                model = msg.get("model", "?")
                turns_by_model[model] += 1
                usage = msg.get("usage") or {}
                out_tokens_by_model[model] += int(usage.get("output_tokens") or 0)
                content = msg.get("content")
                for nm in tool_names(content):
                    tools[nm] += 1
                if model == "claude-fable-5":  # model-id-ok (corpus baseline model)
                    fable_out_lens.append(len(text_of(content)))
            elif t == "user" and isinstance(msg, dict):
                content = msg.get("content")
                # skip pure tool_result user turns
                txt = text_of(content).strip()
                if isinstance(content, list) and any(
                    isinstance(c, dict) and c.get("type") == "tool_result" for c in content) and not txt:
                    continue
                if txt:
                    n_user += 1
                    if len(user_prompts) < 45:
                        user_prompts.append(txt[:240])
    return {
        "machine": machine,
        "project": proj,
        "session": stem,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "turns_by_model": dict(turns_by_model),
        "fable_turns": turns_by_model.get("claude-fable-5", 0),  # model-id-ok
        "out_tokens_by_model": dict(out_tokens_by_model),
        "tool_histogram": dict(tools.most_common()),
        "fable_out_len_avg": round(statistics.mean(fable_out_lens)) if fable_out_lens else 0,
        "fable_out_len_max": max(fable_out_lens) if fable_out_lens else 0,
        "user_prompt_count": n_user,
        "user_prompts": user_prompts,
    }

def main():
    machine, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    ok = 0
    for path in sys.argv[3:]:
        try:
            d = digest(path, machine)
            if d["fable_turns"] == 0:
                continue
            name = f"{machine}__{d['project'][:40]}__{d['session'][:12]}.json"
            with open(os.path.join(out_dir, name), "w") as o:
                json.dump(d, o, indent=1)
            ok += 1
        except Exception as e:
            print(f"ERR {path}: {e}", file=sys.stderr)
    print(f"{machine}: wrote {ok} digests")

if __name__ == "__main__":
    main()
