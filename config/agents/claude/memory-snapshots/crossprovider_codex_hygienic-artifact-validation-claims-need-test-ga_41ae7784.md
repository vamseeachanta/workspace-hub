---
name: crossprovider codex hygienic-artifact-validation-claims-need-test-ga
description: Hygienic artifact validation claims need test gates and actual scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [governance, testing, validation]
---

Prose assertions like 'we will exclude secrets' without tests or scanning behavior are not enforceable. Hygiene rules must include acceptance tests that run a scanner and verify it rejects credentials, raw paths, and off-scope material.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
