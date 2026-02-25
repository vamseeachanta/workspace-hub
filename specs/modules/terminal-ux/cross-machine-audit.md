# Cross-Machine Terminal UX Audit

> WRK-228 | Phase 1 deliverable | Audited: 2026-02-24 | Machine: ace-linux-1

## Scope

| Machine | OS | Terminal | Role |
|---|---|---|---|
| ace-linux-1 | Ubuntu 24.04 LTS (Noble) | GNOME Terminal (VTE 7600) | Nightly cron host — **audited** |
| ace-linux-2 | Linux | Unknown | Contributing machine — TBD |
| ACMA-ANSYS05 | Windows 11 / MINGW64 | Windows Terminal + Git Bash | Dev workstation — TBD |
| acma-ws014 | Windows 11 / MINGW64 | Windows Terminal + Git Bash | Dev workstation — TBD |

---

## 1. Keybindings Audit

### ace-linux-1 (current state)

| Setting | Value | Status |
|---|---|---|
| `~/.claude/keybindings.json` | **ABSENT** — file does not exist | Gap |
| Submit prompt shortcut | Default: `Alt+Enter` (Linux Claude Code default) | Inconsistent with Windows |
| Windows Git Bash default | `Ctrl+Enter` | Inconsistent with Linux |

**Finding:** No `~/.claude/keybindings.json` exists on ace-linux-1. Claude Code on Linux defaults
to `Alt+Enter` to submit. Windows Git Bash uses `Ctrl+Enter`. This mismatch is the primary
friction source when switching between machines.

**Resolution:** Create `~/.claude/keybindings.json` on each Linux machine to explicitly bind
`Ctrl+Enter` as the submit key, matching Windows behaviour. The canonical template is:

```json
{
  "submitPrompt": "ctrl+enter"
}
```

Install with `new-machine-setup.sh` (Step 3, extended to handle keybindings).

---

## 2. Terminal Emulator Config

### ace-linux-1

| Item | Value |
|---|---|
| Terminal | GNOME Terminal (detected via `GNOME_TERMINAL_SERVICE` env var) |
| VTE version | 7600 |
| `TERM` | `xterm-256color` |
| OS | Ubuntu 24.04.4 LTS |
| Shell | bash |
| `~/.inputrc` | **ABSENT** |
| `~/.zshrc` | Not present — bash only |

**Relevant `~/.bashrc` state:**

- `bashrc-snippets.sh` is **NOT yet sourced** (workspace-hub marker not found in `~/.bashrc`)
- `WORKSPACE_HUB` env var is not set in the current shell environment
- `CLAUDE_SCREENSHOT_DIR` env var is **unset**

**GNOME Terminal keybindings** are set via gsettings / dconf. Default tab navigation:
`Ctrl+PageUp` / `Ctrl+PageDown`. No custom override configured.

### Windows (ACMA-ANSYS05 / acma-ws014) — not yet audited

Pending access. Expected configuration:
- Windows Terminal with Git Bash (MINGW64) profile
- `Ctrl+Enter` for submit (Windows Claude Code default)
- `Alt+Tab` is OS-level window switching (not tab navigation within terminal)

---

## 3. Screenshot Folder

### ace-linux-1

| Item | Value | Status |
|---|---|---|
| GNOME default screenshots dir | `~/Pictures/Screenshots/` | Present, contains 17 files |
| `CLAUDE_SCREENSHOT_DIR` env var | **UNSET** | Gap |
| Screenshot tool | GNOME built-in (Print Screen / portal) | OK |
| Claude Code accessibility | Manual — user must navigate to `~/Pictures/Screenshots/` | Gap |

**Finding:** Screenshots are stored in `~/Pictures/Screenshots/` via the GNOME screenshot portal.
No `CLAUDE_SCREENSHOT_DIR` env var is set, so Claude Code cannot auto-locate screenshots.

**Resolution:** Set `CLAUDE_SCREENSHOT_DIR` in `bashrc-snippets.sh` with a platform-aware
default (Linux: `~/Pictures/Screenshots`, Windows: `%USERPROFILE%\Pictures\Screenshots`).

---

## 4. Chrome Claude Extension

### ace-linux-1

| Item | Value | Status |
|---|---|---|
| Extension ID | `fcoeoabgfenejglbffodgkkbkcdhcgfn` | Present |
| Extension name | Claude (Claude in Chrome Beta) | OK |
| Version | **1.0.55** | Current as of audit date |
| Chrome profile | Default | OK |
| Auto-start Chrome | Not configured via autostart or systemd user service | Gap |

**Finding:** Chrome extension is installed and at version 1.0.55. Chrome does not auto-start
on login. The extension is only active when the user manually opens Chrome.

**Resolution:** Document the canonical install/config steps in `admin/it/chrome-claude-setup.md`.
For now, auto-start is not enforced — this is user preference. The readiness check flags if
the extension is absent.

---

## 5. Session Behaviour Mining

Session signal files reviewed in `.claude/state/session-signals/` (2026-02-20):
- No explicit paste-fail or wrong-key events detected in JSONL signals reviewed
- Session logs do not yet contain structured friction-event fields
- The `GNOME_TERMINAL_SERVICE` presence confirms GNOME Terminal is active for Claude Code sessions

**Friction pattern inferred from WRK description:**
- `Alt+Enter` vs `Ctrl+Enter` mismatch when switching between Linux and Windows sessions
- Screenshot folder not accessible without manual navigation
- Chrome extension status unknown across sessions

---

## 6. Gap Summary

| Gap | Severity | Machine(s) | Fix |
|---|---|---|---|
| `~/.claude/keybindings.json` absent — submit key inconsistent | High | ace-linux-1, ace-linux-2 | Create keybindings.json via new-machine-setup.sh |
| `CLAUDE_SCREENSHOT_DIR` unset | High | ace-linux-1, ace-linux-2 | Add to bashrc-snippets.sh |
| `bashrc-snippets.sh` not sourced in `~/.bashrc` | Medium | ace-linux-1 | Re-run new-machine-setup.sh |
| Chrome extension auto-start not configured | Low | ace-linux-1 | Document only — user choice |
| ace-linux-2 / Windows machines not audited | Medium | ace-linux-2, ACMA-ANSYS05 | Run audit on each machine |
| Keybindings target: `Ctrl+Enter` on Linux | High | ace-linux-1, ace-linux-2 | Deploy keybindings.json |

---

## 7. Phase 2 Actions

Based on this audit, the following Phase 2 work is required:

1. **keybindings.json** — create `config/claude/keybindings.json` as canonical template;
   deploy to `~/.claude/keybindings.json` via `new-machine-setup.sh`
2. **CLAUDE_SCREENSHOT_DIR** — add to `config/shell/bashrc-snippets.sh` with Linux default
   `${HOME}/Pictures/Screenshots`; Windows default `${USERPROFILE}/Pictures/Screenshots`
3. **Chrome extension doc** — `admin/it/chrome-claude-setup.md` with install steps and
   version target (1.0.55+)
4. **Readiness check** — add `R-UX` check to `scripts/readiness/nightly-readiness.sh`
   flagging: missing keybindings.json, unset CLAUDE_SCREENSHOT_DIR, absent Chrome extension
5. **Audit remaining machines** — run equivalent audit on ace-linux-2 and ACMA-ANSYS05

---

## 8. Related Work Items

- WRK-229 — AI agent QA loop (HTML output standard, complementary)
- WRK-295 — Bidirectional SSH key auth
- WRK-313 — New-machine setup (bootstrap script)
