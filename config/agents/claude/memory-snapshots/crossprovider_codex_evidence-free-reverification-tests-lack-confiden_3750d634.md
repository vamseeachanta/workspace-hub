---
name: crossprovider codex evidence-free-reverification-tests-lack-confiden
description: Evidence-free reverification tests lack confidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, metadata-validation, evidence-grounding]
---

A test that only checks hardcoded strings (e.g., `license_verified_from: LICENSE` in artifact) will pass even if the verification was never performed. Tests guarding evidence-based claims should validate that concrete public sources (LICENSE files, README, docs URLs) were actually inspected and recorded in metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
