---
name: crossprovider gemini bash-yaml-normalization-requires-external-tool-o
description: Bash YAML normalization requires external tool or Python
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [yaml, bash-limitations, tool-choice]
---

Bash cannot safely merge/normalize YAML (adding fields, restructuring). Use `yq`, embedded Python snippet, or delegate to Python wrapper. Bash string operations corrupt YAML structure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
