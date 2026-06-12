---
name: crossprovider gemini hardcoded-machine-names-in-generated-metadata-br
description: Hardcoded machine names in generated metadata break cross-machine deployments
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [metadata, multi-machine, environment]
---

WRK metadata hardcoded with `computer: ace-linux-1` diverges when script runs elsewhere. Use `platform.node()` or read from environment to keep metadata accurate across machines.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
