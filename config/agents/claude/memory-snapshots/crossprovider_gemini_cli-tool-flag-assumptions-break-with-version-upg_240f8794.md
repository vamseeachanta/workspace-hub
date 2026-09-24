---
name: crossprovider gemini cli-tool-flag-assumptions-break-with-version-upg
description: CLI tool flag assumptions break with version upgrades
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling, environment-drift, reliability]
---

Assuming specific tool CLI flags (e.g., `uv pip list --outdated --format=json`) without version pinning can cause silent failures when environments upgrade. Always test against the installed version or pin the tool version explicitly in dependencies.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
