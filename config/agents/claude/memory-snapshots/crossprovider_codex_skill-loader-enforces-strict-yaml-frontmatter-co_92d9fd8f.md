---
name: crossprovider codex skill-loader-enforces-strict-yaml-frontmatter-co
description: Skill loader enforces strict YAML frontmatter contract
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [skills, loader, yaml-frontmatter]
---

Skill manifests must include `---` delimiters and a mandatory `description` field. Malformed skills are silently skipped with vague warnings. Debugging requires inspecting the loader's exact contract rather than inferring from error messages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
