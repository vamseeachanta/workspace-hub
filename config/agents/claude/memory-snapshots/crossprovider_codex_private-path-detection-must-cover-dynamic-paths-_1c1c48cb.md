---
name: crossprovider codex private-path-detection-must-cover-dynamic-paths-
description: Private-path detection must cover dynamic paths (/tmp, relative, /Users), not just /home
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, security-validation, path-detection]
---

Issue #290 repeated checking only /home/... absolute paths, missing /tmp browser evidence and relative browser-evidence/.../profile paths. Fix: use glob-like regexes (^(/tmp|/var|/Users|browser-evidence) or tmp_root.exists()) and parent-directory walking to detect repo-local capture paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
