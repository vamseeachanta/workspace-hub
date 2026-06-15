---
name: crossprovider codex glob-routing-patterns-can-overmatch-unintentiona
description: Glob routing patterns can overmatch unintentionally
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [routing, patterns, specificity, correctness]
---

Rule `domain: hydro*` matches `hydrocarbon`, `hydrostatic`, `hydro-anything`, not just `hydro` and `hydro-*` subdomains. Use explicit subdomain syntax or `domain == base or domain.startswith(base + '-')` to avoid overmatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
