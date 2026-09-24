---
name: crossprovider codex authoritative-source-domains-are-bounded-not-uni
description: Authoritative source domains are bounded, not universal
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, enforcement, authority-boundaries]
---

Local enforcement hooks (e.g., `.claude/hooks/plan-approval-gate.sh`) are authoritative only for their specific domain (local gate behavior/safe-path assumptions), not for related semantics governed by other documents (e.g., GitHub-side approval workflow governed by `docs/plans/README.md`). Do not assume one authority covers adjacent domains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
