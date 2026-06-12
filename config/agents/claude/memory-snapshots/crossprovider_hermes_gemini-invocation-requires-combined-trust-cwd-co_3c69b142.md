---
name: crossprovider hermes gemini-invocation-requires-combined-trust-cwd-co
description: Gemini invocation requires combined trust + cwd contract
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gemini-cli, artifact-generation, sandboxing]
---

GEMINI_CLI_TRUST_WORKSPACE=true alone is insufficient; must preserve neutral-cwd workaround (cd /tmp) to avoid local `.gemini/agents/*.md` permissionMode validation errors. Trust gate and agent-load mitigation are both required or one failure mode swaps for another. Found in #2502 plan-review producer redesign.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
