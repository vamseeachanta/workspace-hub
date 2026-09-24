---
name: crossprovider codex yaml-regex-pattern-escaping-hazard
description: YAML regex pattern escaping hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [yaml, regex, config-encoding, parser-behavior]
---

Regex patterns stored in YAML with backslash escapes (e.g., `\b` for word boundaries) are interpreted as literal backslashes by the YAML loader. The pattern must use raw string syntax in Python or explicit escaping to preserve regex semantics at runtime. Test regex behavior directly when loading from config YAML.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
