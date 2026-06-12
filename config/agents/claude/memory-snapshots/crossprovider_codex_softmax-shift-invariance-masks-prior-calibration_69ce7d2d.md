---
name: crossprovider codex softmax-shift-invariance-masks-prior-calibration
description: Softmax shift-invariance masks prior-calibration bugs until data distribution skew
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [ml-export, calibration, testing-gaps]
---

ML models exported with class priors as logits work correctly for classification (softmax is shift-invariant) but miscalibrate confidence scores. Balanced training data hides this until retraining on skewed distributions, where sklearn's predict_proba diverges from the exported model's scores.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
