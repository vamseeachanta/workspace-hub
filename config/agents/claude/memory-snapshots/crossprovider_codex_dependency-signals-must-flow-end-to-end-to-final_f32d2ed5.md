---
name: crossprovider codex dependency-signals-must-flow-end-to-end-to-final
description: Dependency signals must flow end-to-end to final outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, dependency-semantics, output-verification]
---

When a plan requires consuming a dependency's semantics (e.g., #738's canonical/duplicate/manual-decision signals), validate those signals are in the final output rows, not just in intermediate summaries. Test by inspecting the actual JSON/JSONL outputs for the fields that prove the signals were applied.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
