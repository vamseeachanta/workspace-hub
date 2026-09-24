---
name: crossprovider codex latest-without-explicit-source-is-non-reproducib
description: "Latest" without explicit source is non-reproducible
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, versioning, operations]
---

Version pins, package upgrades, or audits that reference 'latest' without naming a source (package channel, installer, SemVer constraint, release URL) are inherently non-deterministic. Each run may produce different results, breaking reproducibility and parity audits. Always use explicit version sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
