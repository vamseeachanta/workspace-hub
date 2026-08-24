---
name: crossprovider codex fixture-metadata-flags-become-decorative-without
description: Fixture metadata flags become decorative without test enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-08-23
  tags: [testing, fixtures, maintenance]
---

Optional metadata flags in test fixtures (e.g., `use_as_test: true` on YAML rows) become latent debt if the parametrized test doesn't read and assert them. Enforce every flag through actual test assertions or remove it to prevent decay.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
