---
name: crossprovider codex security-launchers-need-explicit-trust-boundary-
description: Security launchers need explicit trust-boundary contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, launcher, cross-platform, threat-model]
---

Wrappers around security-critical binaries must document root-attestation schema (path normalization, symlinks, revocation), binary identity validation (resist PATH poisoning), and atomic rollback. Source inspection cannot verify cross-platform CLI behavior; Windows argument preservation, quoting, and metacharacter handling require platform-native testing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
