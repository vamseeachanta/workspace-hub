---
name: crossprovider codex infrastructure-configuration-should-separate-sin
description: Infrastructure configuration should separate single-source-of-truth registries from operational procedures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure-documentation, configuration-management, operational-procedures]
---

Store machine identities, IPs, hostnames, Tailscale addresses, and SSH keys in one canonical registry (e.g., `workstations/registry.yaml`); never duplicate in helper scripts or runbooks. Operational procedures (durable L3) and execution artifacts (L5) are distinct layers; handoff docs (L6) must not become canonical. Mark competing/stale docs as legacy and point to the authoritative runbook.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
