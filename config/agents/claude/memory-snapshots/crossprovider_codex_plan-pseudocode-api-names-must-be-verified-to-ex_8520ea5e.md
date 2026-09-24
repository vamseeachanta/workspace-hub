---
name: crossprovider codex plan-pseudocode-api-names-must-be-verified-to-ex
description: Plan pseudocode API names must be verified to exist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-verification, retrieval-skepticism, pseudocode]
---

Plans calling methods like GeometryQualityChecker.check() without verifying the actual signature fail silently at implementation. Treat all API names in pseudocode as unverified; check that the method exists, accepts the stated parameters, and returns the expected type before assuming it's callable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
