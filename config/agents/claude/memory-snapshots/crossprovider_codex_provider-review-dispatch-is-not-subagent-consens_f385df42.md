---
name: crossprovider codex provider-review-dispatch-is-not-subagent-consens
description: Provider review dispatch is not subagent consensus
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent, review-gating, provider-dispatch]
---

Running three parallel subagent reviews produces useful local signal and can surface common defects, but subagent verdicts are NOT the same as formal provider CLI tool verdicts. T3 gate requires dispatching actual Claude/Codex/Gemini reviewers (via provider CLIs or fanout scripts), not treating subagent work as provider consensus. Main session must verify the formal provider results independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
