---
name: crossprovider codex defer-ssh-security-hardening-until-after-pre-tra
description: Defer SSH security hardening until after pre-travel configuration testing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-21
  tags: [ssh, security, travel-readiness, pre-flight-checks]
---

Avoid disabling password authentication or making other SSH security changes immediately before travel. Configure and test new auth methods (e.g., public-key SSH from iPhone) in advance while on-site; traveling with a broken SSH config or unconfigured fallback isolates you from the remote system when recovery is difficult. Prefer verification of existing setup to last-minute hardening.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
