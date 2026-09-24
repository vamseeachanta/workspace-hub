---
name: crossprovider codex status-schema-validation-needs-completeness-audi
description: Status schema validation needs completeness audit against all setup-critical state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, setup, completeness, harness-parity]
---

Plans claiming machine harness parity must audit and include ALL setup-critical dimensions: submodule initialization, repo hooks, shell profiles, npm global prefix, cron vs Task Scheduler, SSH key presence, `.env` files, Python/uv availability, and platform-specific tools (Git Bash). Subset schemas miss critical gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
