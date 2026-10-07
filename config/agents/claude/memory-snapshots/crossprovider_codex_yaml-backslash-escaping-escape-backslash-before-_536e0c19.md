---
name: crossprovider codex yaml-backslash-escaping-escape-backslash-before-
description: YAML backslash escaping: escape backslash before quote in double-quoted strings
metadata:
  type: reference
  source: codex
  bridged: 2026-07-31
  tags: [yaml, escaping, windows-paths, powershell]
---

Windows paths (D:\ws) in YAML must escape backslashes before quote characters: replace '\' with '\\' first, then '"' with '\"'. Reversing the order re-escapes the fix. In PowerShell -replace, the regex pattern '\\' matches one backslash; the replacement '\\\\' (four backslashes) emits two.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
