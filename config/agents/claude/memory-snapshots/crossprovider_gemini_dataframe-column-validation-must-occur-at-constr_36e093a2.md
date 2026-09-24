---
name: crossprovider gemini dataframe-column-validation-must-occur-at-constr
description: DataFrame column validation must occur at construction time
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [dataframe-validation, pandas, api-design]
---

When accepting a DataFrame as a parameter, validate required columns exist in `__post_init__`, not in downstream processing. This fails fast and assigns responsibility to the caller rather than creating cryptic downstream errors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
