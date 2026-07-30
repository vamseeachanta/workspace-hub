---
name: crossprovider codex trace-parameter-threading-in-cli-api-design
description: Trace parameter threading in CLI/API design
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [api-design, parameter-threading, code-review]
---

When reviewing a command-line interface or API, verify any accepted parameters are actually used end-to-end from parsing through semantic application. Flag acceptance doesn't guarantee usage; a parameter can be parsed but unused, ignored, or incorrectly threaded through the call chain.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
