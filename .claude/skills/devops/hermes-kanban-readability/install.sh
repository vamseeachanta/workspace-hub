#!/usr/bin/env bash
#
# Reinstall the Hermes Kanban readability customizations as a USER-OVERRIDE
# dashboard plugin, so they survive `hermes update` / `git pull` of the
# bundled hermes-agent checkout.
#
# The bundled plugin lives inside the hermes-agent git repo, so any edit
# there is reverted on update. Dashboard-plugin discovery scans user plugins
# FIRST (web_server.py::_discover_dashboard_plugins), so a copy named
# "kanban" under $HERMES_HOME/plugins/ shadows the bundled one and lives
# outside the repo where git pull can't touch it.
#
# This script is idempotent — safe to re-run anytime, and the canonical
# recovery path if $HERMES_HOME is ever wiped. Re-run after each
# `hermes update`.
#
# What it does (always from the *current* bundled plugin, never prior state):
#   1. Copy the bundled kanban dashboard plugin -> $HERMES_HOME/plugins/kanban/
#   2. Replace renderInline() in dist/index.js so bare URLs (e.g.
#      "Source: https://...") render as clickable links.
#   3. Append a CSS block to dist/style.css so card text uses a readable
#      sans face at a larger size instead of the Mondwest display font.
#   4. Best-effort: ask a running dashboard to rescan plugins.
#
# Drift-aware: if upstream changes renderInline, step 2 prints a WARNING
# and leaves the JS unpatched rather than silently doing nothing. Re-derive
# from patches/renderInline.{original,patched}.js (see also
# kanban-readability.patch for the original provenance diff).
#
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO="${HERMES_AGENT_REPO:-$HERMES_HOME/hermes-agent}"
BUNDLED="${HERMES_BUNDLED_PLUGINS:-$REPO/plugins}/kanban/dashboard"
DEST="$HERMES_HOME/plugins/kanban/dashboard"

ORIG="$SKILL_DIR/patches/renderInline.original.js"
PATCHED="$SKILL_DIR/patches/renderInline.patched.js"
CSS_APPEND="$SKILL_DIR/patches/style.append.css"
CSS_MARKER="kanban-readability skill override"

echo "[kanban-readability] bundled : $BUNDLED"
echo "[kanban-readability] dest    : $DEST"

if [ ! -d "$BUNDLED" ]; then
  echo "ERROR: bundled kanban dashboard not found at $BUNDLED" >&2
  echo "       Set HERMES_AGENT_REPO or HERMES_BUNDLED_PLUGINS to locate it." >&2
  exit 1
fi
for f in "$ORIG" "$PATCHED" "$CSS_APPEND"; do
  [ -f "$f" ] || { echo "ERROR: missing skill asset: $f" >&2; exit 1; }
done

# 1. fresh copy of the bundled plugin (start clean every run)
mkdir -p "$DEST/dist"
cp -f "$BUNDLED/manifest.json" "$DEST/"
[ -f "$BUNDLED/plugin_api.py" ] && cp -f "$BUNDLED/plugin_api.py" "$DEST/"
cp -f "$BUNDLED/dist/index.js" "$BUNDLED/dist/style.css" "$DEST/dist/"
rm -rf "$DEST/dist/__pycache__" "$DEST/__pycache__" 2>/dev/null || true

# 2. JS: replace renderInline (idempotent + drift-aware)
python3 - "$DEST/dist/index.js" "$ORIG" "$PATCHED" <<'PY'
import sys
target, orig_f, patched_f = sys.argv[1:4]
src     = open(target, encoding="utf-8").read()
orig    = open(orig_f, encoding="utf-8").read().rstrip("\n")
patched = open(patched_f, encoding="utf-8").read().rstrip("\n")
if "bare-URL autolinker" in src:
    print("[js] already patched — skipping")
    sys.exit(0)
if orig not in src:
    sys.stderr.write(
        "[js] WARNING: original renderInline block not found in bundled "
        "index.js — upstream likely changed it. Bare-URL autolinking NOT "
        "applied. Re-derive from patches/renderInline.{original,patched}.js.\n")
    sys.exit(3)
open(target, "w", encoding="utf-8").write(src.replace(orig, patched, 1))
print("[js] renderInline patched — bare-URL autolinking enabled")
PY
js_rc=$?
[ "$js_rc" -eq 3 ] && echo "[kanban-readability] continuing; JS step needs manual attention (see warning above)"

# 3. CSS: append readable-font override (idempotent)
if grep -qF "$CSS_MARKER" "$DEST/dist/style.css"; then
  echo "[css] override already present — skipping"
else
  printf '\n' >> "$DEST/dist/style.css"
  cat "$CSS_APPEND" >> "$DEST/dist/style.css"
  echo "[css] readable-font override appended"
fi

# 4. best-effort: tell a running dashboard to rescan (GET, auth-whitelisted)
port="$(ss -ltnp 2>/dev/null | grep -oE '127\.0\.0\.1:9[0-9]{3}' | head -1 | cut -d: -f2 || true)"
if [ -n "${port:-}" ] && command -v curl >/dev/null 2>&1; then
  if curl -fsS "http://127.0.0.1:${port}/api/dashboard/plugins/rescan" >/dev/null 2>&1; then
    echo "[rescan] dashboard on :$port rescanned plugins"
  else
    echo "[rescan] could not auto-rescan on :$port — hard-refresh the Kanban tab (Ctrl+Shift+R)"
  fi
else
  echo "[rescan] no local dashboard detected — it will pick up the override on next start"
fi

echo "[kanban-readability] done."
