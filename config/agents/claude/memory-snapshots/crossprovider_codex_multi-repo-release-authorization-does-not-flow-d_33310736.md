---
name: crossprovider codex multi-repo-release-authorization-does-not-flow-d
description: Multi-repo release: authorization does not flow downstream
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [multi-repo, release-coordination, authorization]
---

Parent issue approval does not authorize child implementation across repository boundaries. Each repo boundary requires independent review and explicit approval (e.g., approving parent #3559 does not authorize aceengineer-website #74 implementation). Immutability proofs require exact-SHA reads; floating refs and omitted revisions are not evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
