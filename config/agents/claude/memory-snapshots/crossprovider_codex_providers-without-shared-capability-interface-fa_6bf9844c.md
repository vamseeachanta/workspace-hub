---
name: crossprovider codex providers-without-shared-capability-interface-fa
description: Providers without shared capability interface fail at runtime
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [architecture, interface-design]
---

When `BaseProvider` declares only generic methods and routing code directly invokes domain-specific methods (e.g., `search_ownership`), implementations lacking those methods fail with `AttributeError`. Define explicit capability interfaces and route via capability, not just provider type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
