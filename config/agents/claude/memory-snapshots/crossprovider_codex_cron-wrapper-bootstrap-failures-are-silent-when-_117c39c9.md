---
name: crossprovider codex cron-wrapper-bootstrap-failures-are-silent-when-
description: Cron wrapper bootstrap failures are silent when log directory creation is post-redirection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, bootstrap, shell-scripts, directory-initialization]
---

Shell wrappers that create log directories fail silently when outer cron redirection targets non-existent paths before the wrapper executes. Directory existence in the repository checkout does not guarantee it in all deployment contexts. Move directory creation before outer redirection or use inline mkdir.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
