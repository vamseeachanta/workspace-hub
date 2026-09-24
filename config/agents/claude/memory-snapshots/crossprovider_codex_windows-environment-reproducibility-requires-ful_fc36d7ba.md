---
name: crossprovider codex windows-environment-reproducibility-requires-ful
description: Windows environment reproducibility requires full specification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [adversarial-review, windows-validation, environment-setup, reproducibility]
---

Validation on licensed Windows software (OrcFxAPI) needs explicit environment spec: Python discovery, binding installation/version, working directory, PYTHONPATH, how to verify readiness before subprocess launch. Ad-hoc subprocess invocation without environment pinning makes validation unreproducible across machines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
