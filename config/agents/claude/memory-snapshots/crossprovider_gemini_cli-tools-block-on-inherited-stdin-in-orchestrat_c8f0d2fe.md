---
name: crossprovider gemini cli-tools-block-on-inherited-stdin-in-orchestrat
description: CLI tools block on inherited stdin in orchestrated bash contexts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling-quirk, bash-scripting, orchestration, cli-debugging]
---

When a bash script passes input to a CLI tool via positional argument instead of stdin, the tool can block on inherited stdin from an orchestrator (e.g., spawned agent), waiting for EOF. Explicitly redirect stdin from /dev/null or use the CLI's native stdin support (`-` flag or stdin-only mode) to prevent hangs in non-tty environments.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
