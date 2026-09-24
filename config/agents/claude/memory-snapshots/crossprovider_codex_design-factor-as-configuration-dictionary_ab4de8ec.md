---
name: crossprovider codex design-factor-as-configuration-dictionary
description: Design factor as configuration dictionary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [engineering-standards, design-patterns, configuration]
---

Use dictionaries to map safety classes or standards to design factors (e.g., GAMMA_SC = {"low": 1.046, "normal": 1.138, "high": 1.308}). This pattern enables standards-compliant calculations across multiple safety classes without hardcoded multipliers scattered through calculation code, improving auditability and maintainability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
