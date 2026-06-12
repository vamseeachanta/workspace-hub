---
name: crossprovider hermes hermes-model-switching-lacks-shell-aliases-despi
description: Hermes model-switching lacks shell aliases despite full auth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, tooling-friction, quick-access]
---

ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY are all set in environment. Hermes supports -m flag and /model command, but no shell aliases exist (h-opus, h-sonnet, h-gemini not in ~/.bash_aliases). Each model flip requires full CLI flag or interactive wizard, adding friction to horses-for-courses routing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
