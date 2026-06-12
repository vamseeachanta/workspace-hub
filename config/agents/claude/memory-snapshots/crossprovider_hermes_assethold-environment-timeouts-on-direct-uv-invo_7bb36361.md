---
name: crossprovider hermes assethold-environment-timeouts-on-direct-uv-invo
description: assethold environment timeouts on direct uv invocations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [assethold, environment-friction, timeout-constraint, uv-run]
---

`uv run` direct tool invocations on assethold timeout at 240s+ (flake8 at 240s, pytest at 300s typical). This is a consistent pattern suggesting significant environment setup overhead, not one-off. Plan for 300s timeouts when running analysis/test tasks in this repo; consider splitting work or using streaming output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
