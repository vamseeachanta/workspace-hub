---
name: crossprovider hermes local-pytest-noconftest-divergence-masks-ci-fail
description: Local pytest --noconftest divergence masks CI failures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, ci-divergence, validation-gap]
---

Local validation using `--noconftest -o addopts=` omits conftest/marker selection/coverage thresholds enforced in CI; local test passage does not guarantee CI passage. Affects cost/disclosure and CI-health issues where validator output directly gates approval decisions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
