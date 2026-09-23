---
name: crossprovider codex tailscale-byte-counters-disagree-by-path-type-cl
description: Tailscale byte counters disagree by path type: CLI vs JSON
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [tailscale, networking, tooling-quirks, metrics]
---

tailscale status (CLI) includes relayed traffic; --json reports only direct-path bytes (often 0 for DERP-relayed peers). Both are correct but measure different things. A generator reading only one field mislabels every relayed peer. Classify peers from CurAddr/Relay field, not byte counts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
