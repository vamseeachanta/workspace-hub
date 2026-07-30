---
name: crossprovider codex shell-quoting-for-gsettings-command-construction
description: Shell quoting for gsettings command construction
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [bash, gsettings, shell-quoting, injection-safety]
---

When constructing gsettings commands that contain user strings (error messages, paths), use proper single-quote escaping in bash -c arguments. Define a helper like `shell_quote_word()` that escapes embedded single quotes as `'\''` to prevent injection. This applies anywhere user text flows into shell -c commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
