---
name: crossprovider gemini sklearn-json-exports-lose-init-value-probability
description: sklearn JSON exports lose init_value; probability calibration silently breaks
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ml, sklearn, serialization]
---

Custom JSON serialization of GradientBoostingClassifier must include init_value or predict_proba() diverges from sklearn. Classification stays correct on balanced data, but confidence scores become unreliable, causing silent failures in threshold-based logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
