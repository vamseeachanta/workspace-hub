---
name: crossprovider codex sklearn-gradientboosting-init-value-is-stored-as
description: sklearn GradientBoosting init_value is stored as probabilities, not log-odds
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sklearn, model-export, calibration]
---

When exporting trained sklearn GradientBoosting models to JSON, the `init_value` field stores class priors as probabilities. Downstream code treating these as raw logits will produce incorrect probability calibration, especially for non-uniform training data. Classification accuracy may be correct due to softmax shift-invariance, but confidence scores will diverge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
