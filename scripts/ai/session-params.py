#!/usr/bin/env python3
# ABOUTME: Emit session_params JSONL events for each AI provider (Claude, Codex, Gemini).
# Usage: uv run --no-project python session-params.py
# Output: one JSONL line per provider to stdout.

import json
import os
import re
import sys
import time
from pathlib import Path

# Context window map: model alias → K tokens
CTX_MAP: dict[str, int] = {
    # Claude
    "sonnet": 200,
    "claude-sonnet-4-6": 200,
    "opus": 200,
    "claude-opus-4-6": 200,
    "haiku": 200,
    "claude-haiku-4-5": 200,
    # Codex / OpenAI
    "gpt-5.4": 128,
    "gpt-5.3-codex": 128,
    "gpt-5.2-codex": 128,
    "o4-mini": 200,
    "o3": 200,
    # Gemini
    "gemini-3.1-pro-preview": 1000,
    "gemini-2.5-pro": 1000,
    "gemini-2.0-flash": 1000,
}

DEFAULT_CTX = 128


def ctx_k(model_alias: str) -> int:
    return CTX_MAP.get((model_alias or "").lower(), DEFAULT_CTX)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_toml_key(path: Path, key: str) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(rf'^\s*{re.escape(key)}\s*=\s*["\']?([^"\'#\n]+)["\']?', line)
            if m:
                return m.group(1).strip().strip("\"'")
    except Exception:
        pass
    return ""


def emit(provider: str, model: str, context_k: int, effort: str) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(json.dumps({
        "event": "session_params",
        "provider": provider,
        "model": model or "not-set",
        "context_k": context_k,
        "effort": effort or "—",
        "ts": ts,
    }))


def main() -> None:
    home = Path.home()
    ws = Path(__file__).resolve().parents[2]

    # Claude
    claude_cfg = read_json(home / ".claude" / "settings.json")
    repo_cfg = read_json(ws / ".claude" / "settings.json")
    model = claude_cfg.get("model") or "not-set"
    thinking = repo_cfg.get("thinking") or claude_cfg.get("thinking")
    effort = "thinking=on" if thinking else "thinking=off"
    emit("claude", model, ctx_k(model), effort)

    # Codex — repo-local config overrides user config
    codex_repo = ws / ".codex" / "config.toml"
    codex_user = home / ".codex" / "config.toml"
    codex_src = codex_repo if codex_repo.exists() else codex_user
    codex_model = read_toml_key(codex_src, "model") or "not-set"
    codex_effort = read_toml_key(codex_src, "model_reasoning_effort") or "—"
    emit("codex", codex_model, ctx_k(codex_model), f"effort={codex_effort}")

    # Gemini
    gemini_cfg = read_json(home / ".gemini" / "settings.json")
    gemini_model_raw = gemini_cfg.get("model") or {}
    if isinstance(gemini_model_raw, dict):
        gemini_model = gemini_model_raw.get("name") or "not-set"
    else:
        gemini_model = str(gemini_model_raw) or "not-set"
    gemini_thinking = gemini_cfg.get("thinking", {})
    if gemini_thinking and isinstance(gemini_thinking, dict):
        gemini_effort = f"thinking_budget={gemini_thinking.get('budget', '—')}"
    else:
        gemini_effort = "—"
    emit("gemini", gemini_model, ctx_k(gemini_model), gemini_effort)


if __name__ == "__main__":
    main()
