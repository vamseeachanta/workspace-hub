---
name: crossprovider codex quorum-degradation-rules-require-provider-failur
description: Quorum degradation rules require provider-failure classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, multi-provider, quorum-gates]
---

Multi-provider review gates that allow degraded quorum must distinguish quota exhaustion (acceptable) from local auth/config failures (requires explicit downgrade or restoration). Otherwise T3 requirements can be indefinitely bypassed via transient auth issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
