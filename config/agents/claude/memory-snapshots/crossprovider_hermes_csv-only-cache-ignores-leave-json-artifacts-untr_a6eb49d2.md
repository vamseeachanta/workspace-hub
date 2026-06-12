---
name: crossprovider hermes csv-only-cache-ignores-leave-json-artifacts-untr
description: CSV-only cache ignores leave JSON artifacts untracked
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, gitignore, generated-artifacts]
---

Repo-structure Phase 1 in assethold#49 added `*.csv` ignore for stock cache but tracked JSON cache files (`_ohlcv.json`, `info.json`, `insider.json`) remain exposed to churn. Future repo-structure phases should evaluate CSV+JSON cache types together during contract scoping to prevent incomplete ignores.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
