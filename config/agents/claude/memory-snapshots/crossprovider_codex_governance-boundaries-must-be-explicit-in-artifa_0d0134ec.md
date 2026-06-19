---
name: crossprovider codex governance-boundaries-must-be-explicit-in-artifa
description: Governance boundaries must be explicit in artifacts, not just code logic
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [governance, artifacts, policy]
---

If policy says 'report-only for blocked issues' or 'pass reports for non-opted issues', the artifact itself must carry a flag/status marker. Allow/deny logic in code is invisible to downstream consumers and leaves ambiguity about whether a PASS report means closure-ready or informational-only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
