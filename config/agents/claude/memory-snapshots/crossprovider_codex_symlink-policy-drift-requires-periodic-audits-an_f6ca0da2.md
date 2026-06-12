---
name: crossprovider codex symlink-policy-drift-requires-periodic-audits-an
description: Symlink policy drift requires periodic audits and CI enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance, ci-cd, symlinks]
---

Child repos gradually accumulate local SKILL.md copies instead of symlinking to centralized definitions. Audits (audit_skill_symlink_policy.sh) must run regularly and CI must reject non-symlink copies. Drift is silent and pervasive without enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
