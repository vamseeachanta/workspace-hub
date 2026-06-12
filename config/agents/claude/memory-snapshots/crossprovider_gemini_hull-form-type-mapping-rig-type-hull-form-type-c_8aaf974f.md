---
name: crossprovider gemini hull-form-type-mapping-rig-type-hull-form-type-c
description: Hull form type mapping RIG_TYPE → HULL_FORM_TYPE convention
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [vessel-schema, hull-modeling, engineering-convention]
---

RIG_TYPE values (semi_submersible, drillship, jack_up) map to distinct HULL_FORM_TYPE values (semi_sub, drillship, jackup) for hydrodynamic modeling and RAO/diffraction calculations. Two separate enums required; don't collapse into one field.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
