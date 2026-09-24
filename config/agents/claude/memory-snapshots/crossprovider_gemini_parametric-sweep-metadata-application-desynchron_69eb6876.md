---
name: crossprovider gemini parametric-sweep-metadata-application-desynchron
description: Parametric sweep metadata–application desynchronization bug
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [antipattern, parametric-studies, configuration-management]
---

Parametric study implementations that store varied parameter values in metadata but apply them only to default configurations create silent failures—cases generate with metadata but variations never reach the solver. Always trace parameter acceptance through to config application, not just storage.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
