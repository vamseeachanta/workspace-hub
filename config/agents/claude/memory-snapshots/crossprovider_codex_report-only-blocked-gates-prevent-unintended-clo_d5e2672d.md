---
name: crossprovider codex report-only-blocked-gates-prevent-unintended-clo
description: Report-only-blocked gates prevent unintended closure of complex issues
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, safety-gates, issue-closure]
---

Repo enforces explicit flags (report_only, closeout_state, blocking_status) in gate-evaluation code. A record with these fields set properly is rejected at closure time, even if generated artifact summary suggests completion. Verify via actual gate evaluation function before claiming readiness, not by inspecting summaries alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
