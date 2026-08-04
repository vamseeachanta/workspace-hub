---
name: crossprovider codex provider-routing-unknown-providers-default-to-au
description: Provider routing: unknown providers default to auto_routable=true
metadata:
  type: reference
  source: codex
  bridged: 2026-08-01
  tags: [routing, provider-lifecycle, config-safety]
---

In route.py, `.get(prov, {}).get("auto_routable", True)` means removing a provider from config (e.g., gemini→agy) without exhaustive usage audit can silently enable stale labels to route to undefined handlers. Provider vocab lifecycle requires tombstones or explicit unknown-provider guards.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
