---
name: crossprovider gemini cli-stdin-vs-argv-hazard-in-orchestrated-environ
description: CLI stdin vs argv hazard in orchestrated environments
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [harness, cli-integration, bash-scripting]
---

When bash script is spawned from orchestrator (e.g., agent) with non-tty stdin, CLI tools blocking on stdin waiting for EOF causes hangs. Example: `codex exec [PROMPT]` on argv blocks if caller has unconsumed pipe. Use `-` to force stdin reading or pass via explicit `</dev/null` redirection. Per-invocation fix, not per-script.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
