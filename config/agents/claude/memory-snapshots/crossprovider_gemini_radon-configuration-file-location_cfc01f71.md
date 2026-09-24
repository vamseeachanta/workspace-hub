---
name: crossprovider gemini radon-configuration-file-location
description: Radon configuration file location
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [radon, static-analysis, configuration]
---

Radon does not natively read from `[tool.radon]` in pyproject.toml. Use `.radon.cfg` or `setup.cfg` instead for robust, standard configuration that works across Radon versions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
