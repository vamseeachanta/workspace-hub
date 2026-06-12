---
name: crossprovider gemini repository-state-framing-must-be-truthful-not-as
description: Repository state framing must be truthful, not aspirational
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [documentation, scope, accuracy, problem-framing]
---

Stating "no pyproject.toml exists" when it exists but is unused creates wrong scope decisions. Accurate framing: "code exists but is unused/tracked-dead-code" enables better downstream choices (#2443).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
