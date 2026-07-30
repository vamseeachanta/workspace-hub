---
name: crossprovider codex model-selection-must-use-inner-validation-folds-
description: Model selection must use inner validation folds only
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [machine-learning, validation, correctness]
---

In nested cross-validation, hyperparameter selection and model choice must use inner validation folds exclusively. Outer folds must be used once, for final evaluation only. Using outer folds for model selection leaks the evaluation set into the training process and makes reported metrics optimistic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
