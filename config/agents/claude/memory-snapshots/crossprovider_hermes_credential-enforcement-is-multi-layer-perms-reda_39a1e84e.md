---
name: crossprovider hermes credential-enforcement-is-multi-layer-perms-reda
description: Credential enforcement is multi-layer: perms + redaction + storage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, credentials, hygiene]
---

.env file permissions (mode 0600, owner vamsee:vamsee), redaction in all outputs/logs/commits/chat, and password-manager-backed storage. All three layers required; missing one layer creates leakage risk. Non-negotiable for sensitive tokens.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
