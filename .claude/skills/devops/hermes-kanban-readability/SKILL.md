---
name: hermes-kanban-readability
description: Reapply the Hermes Kanban dashboard readability customizations (clickable bare URLs in card descriptions + readable card-text font, a visible horizontal scrollbar so all columns are reachable) as a user-override plugin that survives hermes-agent updates. Use when the Kanban board reverts to the Mondwest display font / plain-text Source URLs after a hermes update, or when bootstrapping a machine whose ~/.hermes was wiped.
version: 1.0.0
category: devops
type: workflow
triggers:
  - When the Hermes Kanban board card titles render in a hard-to-read display font (Mondwest) after a hermes update
  - When "Source: https://..." lines in Kanban card descriptions show as plain text instead of clickable links
  - When ~/.hermes was wiped/reinstalled and the Kanban readability customizations are gone
  - When setting up Hermes on a new machine and want the Kanban readability fixes applied
---

# Hermes Kanban Readability

Reapplies two customizations to the Hermes Kanban dashboard plugin and installs
them as a **user-override** so they survive `hermes update` / `git pull` of the
bundled `hermes-agent` checkout.

## The customizations

1. **Clickable bare URLs** — the card-description markdown renderer
   (`renderInline` in `dist/index.js`) only linkified `[text](url)` syntax, so
   GitHub-synced lines like `Source: https://github.com/.../2802` stayed plain
   text. The patched `renderInline` autolinks bare `http(s)://` URLs (stashing
   any markdown links first so they aren't double-wrapped; trailing sentence
   punctuation is kept outside the anchor).
2. **Readable card-text font** — card titles/meta inherit `Mondwest` (a Hermes
   branding *display* face) at ~12.75px, which reads poorly for dense body text.
   A CSS override pins the readable `system-ui` sans stack (the same face the
   column headers already use) and bumps sizes: title → 0.95rem, meta → 0.8rem,
   id → 0.7rem.
3. **Board overflow / scrollbar** — the columns row lays the columns left-to-right
   at a fixed width (wider than most screens) but the bundled CSS hides the
   scrollbar, so off-screen columns are unreachable. The override restores a
   visible horizontal scrollbar and bounds column height so that scrollbar
   stays inside the viewport (`calc(100vh - 290px)`; tune if a layout starts
   lower). All columns become reachable on smaller screens (e.g. ace-linux-2).

## Why a user-override instead of editing the bundled plugin

The bundled plugin lives at `<hermes-agent-repo>/plugins/kanban/dashboard/`,
inside the git checkout — `dist/index.js` and `dist/style.css` are git-tracked
source (no build step), so any in-place edit is reverted on the next
`git pull` / `hermes update`.

Dashboard-plugin discovery (`hermes_cli/web_server.py::_discover_dashboard_plugins`)
scans, in order: **user `~/.hermes/plugins/<name>/dashboard/`** → bundled
`memory/` → bundled `<repo>/plugins/`. It dedups by manifest `name`, **first
match wins**, so a user copy named `kanban` shadows the bundled one — and
`~/.hermes/plugins/` is outside the repo where `git pull` can't touch it.

## How to run

```bash
.claude/skills/devops/hermes-kanban-readability/install.sh
```

Idempotent and self-locating. Honors `HERMES_HOME`, `HERMES_AGENT_REPO`, and
`HERMES_BUNDLED_PLUGINS` env overrides (defaults: `$HOME/.hermes`,
`$HERMES_HOME/hermes-agent`, `$REPO/plugins`). After it runs, hard-refresh the
Kanban tab (Ctrl+Shift+R). **Re-run after every `hermes update`.**

## Verify

Read-only check (run after install / bootstrap; safe anywhere):

```bash
bash .claude/skills/devops/hermes-kanban-readability/verify.sh
```

Exit 0 = PASS (or N/A on a non-Hermes machine — guard no-ops); exit 1 =
Hermes present but override missing/incorrect (then run `install.sh`).
On a machine with a live dashboard it also confirms the board is serving
kanban from the `user` override, not the bundled plugin.

## Recovery / drift handling

- The installer always rebuilds the override from the *current* bundled plugin,
  then re-applies both customizations — so it picks up upstream kanban changes
  while keeping these two fixes layered on top.
- The CSS fix is **append-based** (later rules win on source order), so it's
  robust across upstream restyles.
- The JS fix does a literal find-replace of the original `renderInline` block.
  If upstream changes that function, the installer prints a **WARNING** and
  leaves JS unpatched (rather than silently failing). Re-derive the patched
  function then — see `patches/`.

## Files

| Path | Purpose |
|---|---|
| `install.sh` | Idempotent installer / recovery entrypoint |
| `verify.sh` | Read-only check: PASS/FAIL that the override is installed + correct (N/A on non-Hermes machines) |
| `patches/renderInline.original.js` | Exact clean `renderInline` block to match (provenance: hermes-agent `2c6bbaf35`) |
| `patches/renderInline.patched.js` | Replacement block with bare-URL autolinking |
| `patches/style.append.css` | CSS override appended to the copy's `style.css` |
| `kanban-readability.patch` | Full original `git diff` (reference / provenance) |

## Provenance

Captured against `NousResearch/hermes-agent` commit `2c6bbaf35` (2026-05-26).
Upstream-PR path (not taken here) would make the change durable via normal
pulls; the autolink fix is a clean bugfix candidate, the font swap is a local
preference that may conflict with Hermes's deliberate Mondwest branding.
