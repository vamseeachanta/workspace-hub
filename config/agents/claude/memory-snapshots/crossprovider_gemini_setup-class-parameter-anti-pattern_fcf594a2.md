---
name: crossprovider gemini setup-class-parameter-anti-pattern
description: Setup class parameter anti-pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [antipattern, object-design, silent-failure]
---

Setup or initializer classes that accept parameters (e.g., `WaveLoadingSetup(wave_height=5.0)`) but never apply them to the underlying configuration object silently ignore user input. Audit any `__init__` that stores parameters without tracing them into the configured object's state.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
