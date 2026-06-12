---
name: crossprovider gemini skill-directory-readme-md-is-an-anti-pattern-not
description: Skill directory README.md is an anti-pattern, not a requirement
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [skill-audit, yaml-parsing, false-positive-prevention]
---

Almost all 500+ skill directories in `.claude/skills/` use only SKILL.md; README.md presence is rare and indicates anti-pattern style. Any audit checking for README.md will generate ~500 false positives. Use structured YAML parsing (e.g., `yq`) instead of brittle Bash regex when auditing skill metadata to avoid these traps.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
