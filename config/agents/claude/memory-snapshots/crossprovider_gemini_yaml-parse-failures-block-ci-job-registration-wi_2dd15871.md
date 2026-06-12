---
name: crossprovider gemini yaml-parse-failures-block-ci-job-registration-wi
description: YAML parse failures block CI job registration with 0s duration symptom
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci-health, yaml-parsing, debugging-pattern]
---

Unquoted YAML values like `DATABASE_URL: sqlite:///:memory:` (without quotes) cause GitHub Actions YAML parser rejection at startup, resulting in 0 jobs registered and 0s execution time. This prevents any job logic from running. Fix YAML syntax before attempting to debug job logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
