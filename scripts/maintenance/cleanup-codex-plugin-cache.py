#!/usr/bin/env python3
# ABOUTME: Trim overlong local Codex plugin defaultPrompt fields in ~/.codex/.tmp/plugins cache to reduce repeated manifest warnings.

from __future__ import annotations

import json
from pathlib import Path

HOME = Path.home()
PLUGIN_ROOT = HOME / ".codex" / ".tmp" / "plugins" / "plugins"
MAX_LEN = 128
ELLIPSIS = "..."


def shorten(text: str, max_len: int = MAX_LEN) -> str:
    if len(text) <= max_len:
        return text
    limit = max_len - len(ELLIPSIS)
    trimmed = text[:limit].rstrip()
    return trimmed + ELLIPSIS


def main() -> None:
    results = {"patched": [], "checked": 0, "root_exists": PLUGIN_ROOT.exists()}
    if not PLUGIN_ROOT.exists():
        print(json.dumps(results, indent=2))
        return
    for plugin_json in PLUGIN_ROOT.glob("*/.codex-plugin/plugin.json"):
        results["checked"] += 1
        try:
            obj = json.loads(plugin_json.read_text(encoding="utf-8"))
        except Exception:
            continue
        interface = obj.get("interface") or {}
        prompt = interface.get("defaultPrompt")
        if not isinstance(prompt, str) or len(prompt) <= MAX_LEN:
            continue
        new_prompt = shorten(prompt)
        interface["defaultPrompt"] = new_prompt
        obj["interface"] = interface
        plugin_json.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        results["patched"].append({
            "path": str(plugin_json),
            "old_len": len(prompt),
            "new_len": len(new_prompt),
        })
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
