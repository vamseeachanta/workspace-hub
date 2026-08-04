---
name: crossprovider codex security-trust-boundaries-need-cryptographic-att
description: Security trust boundaries need cryptographic attestation, not PATH lookups
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [security, launcher, threat-model]
---

Launcher designs that rely on Git-root matching or "binary outside launcher dir" as a security boundary miss attack surfaces: `-C`/`--cd` flags, symlinks, junctions, worktrees, PATH poisoning, and malicious environment overrides. Real binary must be cryptographically attested (digest/version/ownership validated) and absolute; static policy checks are not containment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
