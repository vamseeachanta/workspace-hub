---
name: crossprovider codex physical-quantity-specifications-must-be-canonic
description: Physical quantity specifications must be canonical across backend implementations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-backend-conformance, physics-specification, cross-platform-determinism]
---

Wave amplitude vs wave height normalization, frequency domain (Hz vs rad/s, absolute vs encounter), rotational conventions, and heading periodicity/interpolation are not documentation details—they are required to prevent incompatible backends from emitting different physical quantities while satisfying stated conformance gates. Omitting them allows contradictory implementations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
