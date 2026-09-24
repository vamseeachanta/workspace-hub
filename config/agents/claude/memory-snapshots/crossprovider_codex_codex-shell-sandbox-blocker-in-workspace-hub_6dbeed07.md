---
name: crossprovider codex codex-shell-sandbox-blocker-in-workspace-hub
description: Codex shell sandbox blocker in workspace-hub
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, environment, workaround]
---

Local shell access in Codex sessions consistently fails with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` before commands execute. Workaround: use GitHub MCP connector to verify repository state (commits, files, paths) instead of local shell when read-only inspection is sufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
