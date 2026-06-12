---
name: crossprovider gemini first-ci-bootstrap-surfaces-latent-import-failur
description: First CI bootstrap surfaces latent import failures in existing test suites
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-bootstrap, testing-patterns, tech-debt]
---

When a test suite has never been executed end-to-end in CI (only locally), module renames and import path changes hide until CI runs. Example: aceengineer-admin tests referenced `aceengineer_automation.*` but the package was renamed to `aceengineer_admin`; first CI attempt discovered broken imports. Pattern: bootstrap CI acts as a tech-debt scanner.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
