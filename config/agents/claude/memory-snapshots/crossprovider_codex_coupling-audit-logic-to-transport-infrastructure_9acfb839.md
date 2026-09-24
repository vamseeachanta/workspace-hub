---
name: crossprovider codex coupling-audit-logic-to-transport-infrastructure
description: Coupling audit logic to transport/infrastructure is brittle
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, maintainability, separation-of-concerns]
---

Collection and audit scripts that hard-code connection details (SSH usernames, Tailscale IPs, host-specific paths) become fragile when hostnames or network topology change. Keep collectors pure; move transport/inventory config to a separate file so audit logic remains independent of infrastructure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
