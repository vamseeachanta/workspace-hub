# Chrome Claude Extension — Install and Config Guide

> WRK-228 | IT reference | Created: 2026-02-24

## Overview

The Claude in Chrome extension (Beta) extends Claude Code sessions into the browser,
enabling image paste, screenshot upload, and web-context sharing without manual copy-paste.

This document is the canonical reference for consistent extension setup across all machines.

---

## Extension Details

| Field | Value |
|---|---|
| Extension name | Claude (Claude in Chrome) |
| Extension ID | `fcoeoabgfenejglbffodgkkbkcdhcgfn` |
| Minimum version target | **1.0.55** |
| Chrome Web Store URL | `https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn` |

---

## Installation Steps

### Linux (ace-linux-1, ace-linux-2)

1. Open Chrome (must be the profile used for Claude Code sessions — default: `Default` profile)
2. Navigate to: `https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn`
3. Click **Add to Chrome** and confirm the permission prompt
4. Verify the extension icon appears in the toolbar (puzzle icon → pin if needed)
5. Sign in with the same Anthropic account used for Claude Code CLI

### Windows Git Bash (ACMA-ANSYS05, acma-ws014)

Same steps as Linux — Chrome installation is identical. Use the Chrome profile
that matches the user session (default profile unless explicitly separated).

---

## Verification

After installing, confirm the extension is active:

```bash
# Linux: check extension manifest via filesystem
EXT_DIR="$HOME/.config/google-chrome/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn"
python3 -c "
import json, glob, pathlib
mfiles = glob.glob('${EXT_DIR}/*/manifest.json')
if not mfiles:
    print('FAIL: extension directory not found')
else:
    d = json.loads(pathlib.Path(mfiles[0]).read_text())
    print(f'OK  name={d.get(\"name\")} version={d.get(\"version\")}')
"
```

Expected output: `OK  name=Claude version=1.0.55` (or higher)

---

## Machine Status

| Machine | OS | Version | Date Verified | Notes |
|---|---|---|---|---|
| ace-linux-1 | Ubuntu 24.04 | 1.0.55 | 2026-02-24 | Default profile |
| ace-linux-2 | Linux | TBD | — | Pending audit |
| ACMA-ANSYS05 | Windows 11 | TBD | — | Pending audit |
| acma-ws014 | Windows 11 | TBD | — | Pending audit |

---

## Update Procedure

Chrome extensions auto-update when Chrome is open. To force an immediate update:

1. Open Chrome → navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle, top right)
3. Click **Update** (top left button that appears in Developer mode)
4. Verify the version number has incremented in the extension card

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Extension not visible after install | Not pinned to toolbar | Click puzzle icon → pin Claude extension |
| Paste image fails | Extension not signed in | Click extension icon → sign in with Anthropic account |
| Extension missing entirely | Chrome profile mismatch | Confirm correct Chrome profile is active (check `chrome://settings/`) |
| Version stuck below 1.0.55 | Auto-update disabled | Run manual update via `chrome://extensions/` Developer mode |

---

## Auto-start Chrome (optional)

Chrome does not auto-start by default on Linux desktops. The extension is only active
when Chrome is running. For environments where the extension is needed for every Claude
session, configure Chrome to launch at login:

```bash
# Linux: create autostart entry (runs Chrome minimised to background)
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/google-chrome.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Google Chrome (background)
Exec=google-chrome --no-startup-window
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

This is **optional** — only configure if you want Chrome running at all times for
seamless image paste. Most users launch Chrome manually when needed.

---

## Related

- `specs/modules/terminal-ux/cross-machine-audit.md` — full terminal UX audit
- `scripts/readiness/nightly-readiness.sh` — R-UX check flags absent extension
- WRK-228 — Cross-machine terminal UX consistency work item
