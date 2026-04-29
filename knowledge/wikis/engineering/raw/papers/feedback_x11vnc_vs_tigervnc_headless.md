> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_x11vnc_vs_tigervnc_headless.md

---
name: x11vnc-vs-tigervnc-headless-rule
description: On a headless Ubuntu host (no graphical login), x11vnc is the wrong tool — it crashloops because there's no display to mirror; use TigerVNC vncserver on its own display number instead
type: feedback
originSessionId: 31e065de-df6a-44e0-9c18-5025ace15758
---
When a remote Ubuntu host is operated headlessly (SSH/Tailscale only, nobody graphically logs in), do NOT pick x11vnc for VNC. x11vnc is a screen-mirror — it attaches to an *existing* X display owned by a logged-in user. With no GUI session, x11vnc exits 1 immediately and a `Restart=on-failure` unit will crashloop forever (verified 2026-04-27 on ace-linux-2: 67,189 restarts in 4 days). Pick `tigervnc-standalone-server` and run `vncserver :1` instead — it creates its own X display and doesn't depend on anyone being logged in.

**Why:** This was the actual root cause of "VNC not working" on ace-linux-2 (2026-04-27). The unit had been failing since boot but went unnoticed because no one was watching the journal. The fix wasn't to patch the x11vnc invocation — it was to switch architectures to a headless-style VNC server (TigerVNC `:1`).

**How to apply:**
- First-time setup on a headless host → reach for TigerVNC, not x11vnc
- Triaging "vnc not working" on Ubuntu 24.04 → check `loginctl list-sessions` for `Type=tty` only as a tell that x11vnc is the wrong tool
- A unit in `activating (auto-restart)` with a high restart counter → don't try to fix the ExecStart; question whether the server type matches the access pattern
- Ubuntu 24.04 / GNOME 46 specific: don't try to enable gnome-remote-desktop's VNC backend (deprecated, view-only by default); use its RDP path or TigerVNC
- Companion runbook: `.claude/skills/operations/devops/remote-desktop-headless-ubuntu/SKILL.md`
