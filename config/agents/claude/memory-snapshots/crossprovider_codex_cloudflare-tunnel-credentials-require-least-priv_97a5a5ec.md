---
name: crossprovider codex cloudflare-tunnel-credentials-require-least-priv
description: Cloudflare tunnel credentials require least-privilege hardening
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [security, infrastructure, credentials]
---

Existing Cloudflare tunnel configuration typically carries over-broad file permissions and service privileges. Any future tunnel work must include explicit hardening (restrictive file modes, scoped service tokens) and documented disable/rollback procedures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
