#!/usr/bin/env python3
# ABOUTME: Emit session_params JSONL events for each AI provider (Claude, Codex, Agy).
# Usage: uv run --no-project python session-params.py
# Output: one JSONL line per provider to stdout.

import json
import os
import re
import sys
import time
from pathlib import Path

# Context windows read from config/agents/model-registry.yaml context_windows_k
# (single source per #3038); FALLBACK_CTX_MAP covers registry-absent runs.
MODEL_REGISTRY = Path(__file__).resolve().parents[2] / "config" / "agents" / "model-registry.yaml"

FALLBACK_CTX_MAP: dict[str, int] = {
    "claude-opus-4-8[1m]": 1000,  # model-id-ok — primary since #3051 (the [1m] suffix parser also yields 1000)
    "claude-fable-5": 1000,       # model-id-ok — deprecated 2026-06-13; retained as a soft fallback
    "claude-sonnet-4-6": 200,
    "claude-opus-4-8": 200,
    "claude-haiku-4-5": 200,
    "gpt-5.5": 128,
    "gemini-2.5-pro": 1000,
}

# Short aliases resolve to full model ids before lookup
ALIAS_MAP: dict[str, str] = {
    "opus-1m": "claude-opus-4-8[1m]",  # model-id-ok — 1M-Opus primary
    "fable": "claude-opus-4-8[1m]",    # model-id-ok — deprecated alias, forwarded to the new primary
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
    # agy persists its model as a DISPLAY LABEL (set-antigravity-default-model.sh)
    "gemini 3.1 pro (high)": "gemini-3.1-pro-preview",
    "gemini 3.1 pro": "gemini-3.1-pro-preview",
}

DEFAULT_CTX = 128


def _load_registry_ctx() -> dict[str, int]:
    """Parse the flat context_windows_k map (no yaml dep — runs --no-project)."""
    try:
        text = MODEL_REGISTRY.read_text(encoding="utf-8")
    except OSError:
        return dict(FALLBACK_CTX_MAP)
    block = re.search(r"^context_windows_k:\n((?:[ \t]+\S+:[ \t]*\d+.*\n)+)", text, re.MULTILINE)
    if not block:
        return dict(FALLBACK_CTX_MAP)
    out: dict[str, int] = {}
    for m in re.finditer(r"^[ \t]+(\S+):[ \t]*(\d+)", block.group(1), re.MULTILINE):
        out[m.group(1).lower()] = int(m.group(2))
    return out or dict(FALLBACK_CTX_MAP)


CTX_MAP: dict[str, int] = _load_registry_ctx()


def ctx_k(model_alias: str) -> int:
    key = (model_alias or "").lower()
    # Context-variant suffix, e.g. "claude-fable-5[1m]" — explicit window wins
    suffix = re.search(r"\[(\d+)(k|m)\]$", key)
    key = re.sub(r"\[[^\]]*\]$", "", key)
    if suffix:
        return int(suffix.group(1)) * (1000 if suffix.group(2) == "m" else 1)
    key = ALIAS_MAP.get(key, key)
    return CTX_MAP.get(key, DEFAULT_CTX)


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

    # Agy (Antigravity CLI — settings under ~/.gemini/antigravity-cli/, #3573)
    agy_cfg = read_json(home / ".gemini" / "antigravity-cli" / "settings.json")
    agy_model_raw = agy_cfg.get("model") or {}
    if isinstance(agy_model_raw, dict):
        agy_model = agy_model_raw.get("name") or "not-set"
    else:
        agy_model = str(agy_model_raw) or "not-set"
    emit("agy", agy_model, ctx_k(agy_model), "—")


if __name__ == "__main__":
    main()
