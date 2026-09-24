---
name: crossprovider codex public-infrastructure-documentation-must-redact-
description: Public infrastructure documentation must redact machine facts using placeholders and legal-deny-list constraints
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-hardening, documentation-compliance, public-docs]
---

Use placeholders for usernames, hostnames, IP addresses, Tailscale device names, SSH keys, and environment-specific paths. Do not publish direct endpoints, peer inventories, admin-console state, or subnet routes. Validate against `.legal-deny-list.yaml` and include `legal-sanity-scan.sh --diff-only` in acceptance criteria. Single Drive searches may stall during tool startup; be aware of one-shot invocation budget.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
