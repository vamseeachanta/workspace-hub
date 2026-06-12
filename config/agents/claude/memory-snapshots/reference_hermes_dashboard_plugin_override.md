---
name: reference_hermes_dashboard_plugin_override
description: How to make Hermes web-dashboard plugin customizations (kanban etc.) survive hermes-agent updates — user-override path shadows bundled.
metadata: 
  node_type: memory
  type: reference
  originSessionId: dc4a5161-d1a3-4f02-9ac3-806f783b94a4
---

Hermes web-dashboard plugins are discovered by `hermes_cli/web_server.py::_discover_dashboard_plugins`, which scans **user `~/.hermes/plugins/<name>/dashboard/` FIRST**, then bundled `<hermes-agent-repo>/plugins/`. Dedup is by manifest `name`, **first match wins** — so a user copy named `kanban` shadows the bundled one. `~/.hermes/plugins/` is outside the git checkout, so `hermes update` / `git pull` can't revert it. Editing the bundled `plugins/*/dashboard/dist/*` in-place is futile — those files are git-tracked source (no build step) and revert on update.

To activate without restarting the standalone `hermes dashboard` process (separate PID from the gateway), the SPA exposes its ephemeral token as `window.__HERMES_SESSION_TOKEN__`; call `GET /api/dashboard/plugins/rescan` with header `X-Hermes-Session-Token`. `/api/dashboard/plugins/rescan` is NOT auth-whitelisted (only `/api/dashboard/plugins` is).

Durable recovery skill (regenerates the override from current bundled + reapplies fixes, idempotent): `workspace-hub/.claude/skills/devops/hermes-kanban-readability/` — fixes are bare-URL autolinking in `renderInline` + readable card-text font over Mondwest display font + visible horizontal scrollbar with `max-height: calc(100vh - 290px)` (board overflowed hidden-scrollbar). `verify.sh` = PASS/FAIL/N-A check. Re-run `install.sh` after each `hermes update`. Bootstrap §2.7 (in `scripts/memory/bootstrap-machine.sh`) auto-reinstalls on bootstrap. NOTE: repo has `core.fileMode=false`, so committed shell scripts need explicit `git update-index --cacheinfo 100755` or git stores them non-exec (broke a `-x` hook guard once — invoke via `bash <script>` + guard on `-f` not `-x`). See [[feedback_html_default_artifact]].

**Board DATA (cards) is a separate two-step sync, NOT automatic:** `.claude/memory/kanban/boards/*.yaml` is the git-tracked source-of-truth (intent); per-machine `~/.hermes/kanban.db` is runtime. `git pull` moves YAML but the cards only appear after `.claude/memory/kanban/scripts/load.py` *replays* YAML→runtime (idempotent, upserts by `gh:` key, additive — never deletes/syncs-back; runtime→YAML is NOT captured). Fresh machine shows only an empty default board until `load.py` runs. Opt-in auto-load: bootstrap §2.8 installs a `post-merge` hook calling `scripts/memory/kanban-autoload.sh`, gated on marker `~/.hermes/kanban-autoload.enabled` (safe no-op without it) — **enable ONLY on Manual-orchestration machines** (loader sets real card status, so an auto-dispatcher could claim 1000s of loaded cards into a worker swarm). Closed #2805.
