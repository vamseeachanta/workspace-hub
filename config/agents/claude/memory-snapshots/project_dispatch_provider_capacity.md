---
name: project-dispatch-provider-capacity
description: AI-provider capacity tiers for issue dispatch routing; hermes draws from codex quota so they share one WIP budget; gemini is usage-limited and manual-only
metadata: 
  node_type: memory
  type: project
  originSessionId: 08e3d2f3-8ca3-49c2-bc9d-390a767f25fa
---

Provider capacity model for the kanban issue-dispatch system (decided with user
2026-05-25). Drives the routing rule engine's defaults and WIP caps.

- **Workhorse — `claude`, `codex`:** highest token availability. Default
  auto-route targets, highest WIP caps.
- **Shared pool — `hermes`:** Hermes runs *via codex*, so a hermes dispatch
  **consumes codex quota**. The dispatcher must model ONE shared `codex+hermes`
  budget and count hermes dispatches against codex's cap — separate caps
  (`codex:2` + `hermes:2`) would permit 4 concurrent draws on one budget and
  blow the quota. See [[project_hermes_codex_quota]] (#6551).
- **Scarce — `gemini`:** usage-limited. Never auto-route for backlog clearing;
  honor only an explicit human-set `ai:gemini` label, small cap, single-shot
  tasks (e.g. one cross-review opinion). Note Gemini's sandbox/overlay limits
  [[feedback_gemini_sandbox_overlay_blindness]].

**Why:** user stated "gemini has usage limit; hermes runs via codex; claude and
codex are highest token availability." The hermes↔codex coupling is the
load-bearing constraint — naive per-provider WIP caps silently exhaust codex.

**How to apply:** in the dispatch rule engine, treat `{codex, hermes}` as a
single budget pool; default backlog routing to claude/codex only; require
explicit label for gemini. Provider chosen per-issue via `ai:` label (not
machine-bound).

**Machine roster (canonical = pre-existing in-the-wild scheme, adopted
2026-05-25, 0 cards relabeled):** dev-primary (linux, hostname ace-linux-1,
this box), dev-secondary (linux), licensed-win-1 / licensed-win-2 (Windows,
OrcaWave/AQWA/OrcaFlex licensed — solver/hydro route here), home-win,
macbook-portable, multi. Aliases: acma-ws014 == licensed-win-2 (same box);
ace-linux-1/2 == dev-primary/secondary. Source of truth = GitHub labels;
config at `.claude/memory/kanban/routing-rules.yaml`, scripts at
`scripts/dispatch/{route,dispatch}.py`.

Related: [[feedback_cross_provider_agent_liveness]] (the live-capacity board this
routing reads), [[feedback_cross_machine_execution]] (git-queue dispatch).
