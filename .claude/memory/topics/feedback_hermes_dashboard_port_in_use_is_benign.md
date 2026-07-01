> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-01
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_hermes_dashboard_port_in_use_is_benign.md

---
name: feedback_hermes_dashboard_port_in_use_is_benign
description: "hermes dashboard Errno 98 on :9119 means an instance is already running, not a crash"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8768ca8e-2749-41ce-a654-016aa9569377
---

`hermes dashboard` failing with `[Errno 98] error while attempting to bind on address ('127.0.0.1', 9119): address already in use` is **benign** — it means a dashboard instance is already listening on that port, not that the dashboard is broken or crashed.

**Why:** The dashboard runs on uvicorn/FastAPI; `Errno 98` is a *startup* bind error, never a *runtime* failure. The existing listener is healthy; the new process just can't claim an owned socket. The dashboard binds `127.0.0.1` only (localhost — not reachable cross-machine by design).

**How to apply:**
- Diagnose the owner: `ss -ltnp 'sport = :9119'` → shows the holding pid.
- Confirm health, don't assume broken: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/` (expect 200).
- Hermes runs independent process trees — the **TUI** (`hermes --tui --yolo`) and the **dashboard** (`hermes dashboard`) are separate; killing one doesn't touch the other (verify before any `kill`).
- Default resolution: just open the running URL. Only `kill <pid>` the listener if you genuinely want to restart it; the dashboard is typically a foreground process in another terminal (not supervised, won't respawn).

Relates to [[project_hermes_installation]] and [[feedback_hermes_active_preflight_check]] (preflight `pgrep` before acting on Hermes processes).
