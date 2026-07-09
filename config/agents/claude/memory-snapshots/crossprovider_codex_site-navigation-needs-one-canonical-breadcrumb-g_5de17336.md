---
name: crossprovider codex site-navigation-needs-one-canonical-breadcrumb-g
description: Site navigation needs one canonical breadcrumb generator
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [navigation, architecture, frontend]
---

When multiple generators produce pages independently, each invents its own trail idiom/label, leading to collision ("Life-cycle hub" vs "Life-cycle Insights hub") and dead-ends. Require a shared helper module injected into all generators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
