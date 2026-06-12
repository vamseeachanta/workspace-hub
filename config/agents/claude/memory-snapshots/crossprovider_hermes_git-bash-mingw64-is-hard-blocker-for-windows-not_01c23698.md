---
name: crossprovider hermes git-bash-mingw64-is-hard-blocker-for-windows-not
description: Git Bash (MINGW64) is hard blocker for Windows, not optional
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [windows-setup, shell, path-semantics]
---

Windows machines must use Git Bash/MINGW64, not cmd.exe. Specific path assumptions follow (D:\workspace-hub seen as /d/workspace-hub in Git Bash). Script sourcing behavior and $PATH differ between shells; bare python3 or uv paths fail in cmd.exe but work in Bash. Treat as a prerequisite, not a configuration choice.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
