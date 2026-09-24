---
name: crossprovider codex independent-cross-validation-of-automated-detect
description: Independent cross-validation of automated detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification-method, automated-detection, independent-cross-check]
---

Automated sweeps or enumeration (e.g., script-based PDF detection) should be independently verified using orthogonal methods (e.g., filesystem `find`) to catch edge cases like case-sensitivity or skip-directory coverage gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
