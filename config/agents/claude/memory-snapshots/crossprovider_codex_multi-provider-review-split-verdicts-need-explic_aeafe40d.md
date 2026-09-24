---
name: crossprovider codex multi-provider-review-split-verdicts-need-explic
description: Multi-provider review split verdicts need explicit handling, not auto-cycling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cross-review, verdicts, aggregation]
---

Issue #2460 iterations saw verdicts like Claude MINOR + Codex MAJOR + Gemini APPROVE across r11-r14. Standard practice was to rerun when any provider returned MAJOR, but consensus emerges from aggregating context. Treat split verdicts as a data point requiring explicit disposition, not automatic re-cycle trigger. Document the split and consensus outcome.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
