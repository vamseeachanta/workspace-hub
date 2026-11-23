#!/usr/bin/env bash
# set-antigravity-default-model.sh — Pin the Antigravity CLI (`agy`) default model
# to the ecosystem-canonical lane on this machine.
#
# WHY: agy is the Gemini delegation lane for the repo ecosystem (Google AI Pro
# subscription). We standardize on ONE default model so every machine and every
# repo opened with agy behaves identically. The model is a single declared value
# below — change it here, re-bootstrap, and the whole fleet converges.
#
# WHERE: agy persists its model as a DISPLAY LABEL in a user-global file
# (~/.gemini/antigravity-cli/settings.json). The file is per-machine and shares
# space with machine-local prefs (e.g. colorScheme), so we MERGE the single
# `model` key and never overwrite the file.
#
# UNCONDITIONAL by design (per #2751 r2 C1 precedent for SOUL install): we set
# the key even if agy isn't installed yet, so a fresh machine converges BEFORE
# its first agy run rather than only after. agy reads this file on launch.
#
# Idempotent — safe to re-run; only writes when the value actually differs.
#
# Usage (standalone):
#   bash scripts/agents/set-antigravity-default-model.sh
# Also invoked automatically by scripts/memory/bootstrap-machine.sh.

set -euo pipefail

# --- Declared config: the one canonical default lane -------------------------
# Must match the exact label agy persists via its `/model` switcher.
AGY_DEFAULT_MODEL="${AGY_DEFAULT_MODEL:-Gemini 3.1 Pro (High)}"

# agy's user-global settings file (label-keyed, not internal-id-keyed; distinct
# from the regular Gemini CLI's ~/.gemini/settings.json).
AGY_SETTINGS="${HOME}/.gemini/antigravity-cli/settings.json"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# Portable python (Linux/macOS: python3; Windows MINGW: python).
PY="$(command -v python3 || command -v python || true)"
if [[ -z "${PY}" ]]; then
    echo -e "${YELLOW}⚠️   No python found — cannot safely merge JSON; skipping agy model pin.${NC}" >&2
    exit 0
fi

# Merge the single `model` key, preserving all other keys. Emits changed/nochange.
result="$("${PY}" - "${AGY_SETTINGS}" "${AGY_DEFAULT_MODEL}" <<'PY'
import json, os, sys

path, model = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}  # corrupt/empty — rewrite cleanly with our key
if not isinstance(data, dict):
    data = {}

if data.get("model") == model:
    print("nochange")
else:
    data["model"] = model
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.replace(tmp, path)  # atomic
    print("changed")
PY
)"

case "${result}" in
    nochange)
        echo -e "${GREEN}✅  agy default model already '${AGY_DEFAULT_MODEL}' — nothing to do.${NC}" ;;
    changed)
        echo -e "${CYAN}Set agy default model → '${AGY_DEFAULT_MODEL}' (${AGY_SETTINGS}).${NC}" ;;
    *)
        echo -e "${YELLOW}⚠️   Unexpected result pinning agy model: ${result}${NC}" >&2 ;;
esac
