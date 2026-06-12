---
name: crossprovider hermes engineering-calculation-sign-conventions-require
description: Engineering calculation sign conventions require explicit geometric definition
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-calculations, sign-conventions, naval-architecture, hydrodynamics]
---

Multiple independent reviewers found underdefined torque/force sign contracts in #2565 (mixing hydrodynamic stock torque with steering-gear reaction torque). Specify positive rotation sense (e.g., 'rotates rudder toward starboard, viewed from above') instead of semantic labels like 'assists/resists force', which conflate multiple sign inversions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
