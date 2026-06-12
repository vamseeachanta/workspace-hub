---
name: crossprovider gemini parameter-accepting-setup-classes-must-apply-val
description: Parameter-accepting setup classes must apply values to underlying engine config
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [initialization, parameter-flow, configuration]
---

Setup classes that accept parameters (e.g., `WaveLoadingSetup(wave_height=...)`) must actually use those values to configure the underlying engine's state. Storing parameters as metadata while leaving engine configuration at defaults silently produces incorrect physics. Validate in __post_init__ that all inputs flow through to the engine.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
