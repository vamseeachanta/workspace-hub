---
name: crossprovider gemini spec-centralization-prevents-agent-routing-ambig
description: Spec centralization prevents agent routing ambiguity
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [specs, centralization, architecture, governance]
---

Single source of truth: work queue at .claude/work-queue/, specs at specs/wrk/WRK-<id>/ and specs/repos/<repo>/. Child repos get pointer stubs instead of local specs. Reduces multiple-source-of-truth confusion for agent dispatch.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
