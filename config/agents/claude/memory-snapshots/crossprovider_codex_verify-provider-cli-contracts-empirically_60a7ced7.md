---
name: crossprovider codex verify-provider-cli-contracts-empirically
description: Verify provider CLI contracts empirically
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, integration, testing]
---

External tool invocations (LLM-facing CLIs, shell utilities) must have their stdin/stdout/stderr contracts verified against actual installed behavior or official docs, not assumed from common patterns. Example: `codex exec -` stdin handling is not guaranteed by CLI design; test with real CLI before shipping. Unverified contracts risk silent empty or irrelevant artifact promotion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
