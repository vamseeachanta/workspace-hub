---
name: crossprovider hermes wrapper-runner-config-handoff-fails-when-wrapper
description: Wrapper/runner config handoff fails when wrapper doesn't export resolved values
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [integration, config-handoff, environment-variables]
---

Bootstrap wrappers that resolve config (e.g., bashrc path) but don't export it to the runner lose the resolution. Runner then defaults to hardcoded fallback paths and fails silently. Both agent ownership boundaries and explicit value passing (via env vars) are required.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
