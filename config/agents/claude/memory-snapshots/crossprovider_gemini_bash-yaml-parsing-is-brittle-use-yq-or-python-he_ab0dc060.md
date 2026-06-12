---
name: crossprovider gemini bash-yaml-parsing-is-brittle-use-yq-or-python-he
description: Bash YAML parsing is brittle; use yq or Python helpers
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [bash, yaml-parsing, maintainability]
---

Bash regexes and string manipulation to parse YAML (e.g. in test-task.sh module-map lookup) are fragile and break on formatting changes. Replace with `yq` CLI or small Python scripts using pyyaml for maintainability. (WRK-119 review, critical finding)

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
