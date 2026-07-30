---
name: crossprovider codex ssh-dispatcher-boundary-submission-vs-job-lifeti
description: SSH dispatcher boundary: submission vs. job lifetime ownership
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, operations]
---

A dispatcher over SSH should handle job submission and status inspection only. A node-local runner (systemd-run, tmux) should own solver lifetime, logging, exit status, result manifest, and reporting. This keeps the SSH control path separate from the job's fate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
