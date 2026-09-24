---
name: crossprovider gemini bash-date-d-portability-breaks-on-macos-silently
description: Bash date -d portability breaks on macOS silently
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, portability, date-parsing]
---

The `date -d` flag is a GNU Coreutils extension that does not exist on macOS/BSD. When stderr is redirected to /dev/null, the command fails silently and returns empty strings, causing downstream logic to behave incorrectly (e.g., all locks appear stale on macOS). Fix: use OS detection or a Python one-liner for cross-platform date parsing.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
