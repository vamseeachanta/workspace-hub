---
name: crossprovider gemini repo-root-resolution-needs-directory-context-whe
description: REPO_ROOT resolution needs directory context when invoked from subdirectories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bash, git, script-robustness]
---

Using `git rev-parse --show-toplevel` from script PWD fails when script is invoked from a subdirectory checkout. Use `git -C "$(dirname "$0")" rev-parse --show-toplevel` to resolve relative to script location.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
