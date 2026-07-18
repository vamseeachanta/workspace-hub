---
name: crossprovider codex enforcement-tests-must-cover-all-equivalent-bypa
description: Enforcement tests must cover all equivalent bypass vocabulary
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [testing, enforcement, regression, schema-validation]
---

Testing rejection of one bypass spelling (e.g., paths-ignore in GitHub Actions) while missing equivalent forms (paths) creates regressions. Assert exact allowed schema shape or cover all known equivalent forms.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
