---
name: crossprovider codex state-directory-security-verify-ownership-and-no
description: State directory security: verify ownership and non-symlink before use
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [file-safety, state-management, privilege-escalation, tmpdir]
---

Voice dictation state files (PID, metadata, WAV recordings) should live in XDG_RUNTIME_DIR or TMPDIR, not in shared directories. Before creating or writing state, validate the directory is not a symlink and is owned by the current user (using `[[ ! -L "$dir" ]] && [[ -O "$dir" ]]`). Prevents privilege escalation via symlink tricks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
