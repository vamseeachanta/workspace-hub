---
name: crossprovider gemini yaml-parse-errors-manifest-as-zero-jobs-zero-dur
description: YAML parse errors manifest as zero jobs / zero duration in CI
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [github-actions, yaml-syntax, ci-health, debugging]
---

GitHub Actions workflows that fail YAML parsing show 0 registered jobs and 0 seconds duration at startup. #2442 had unquoted YAML value `DATABASE_URL: sqlite:///:memory:` (colons require quotes in YAML mappings), causing immediate rejection before any job registered. When diagnosing workflows that won't run, check YAML syntax first—especially unquoted special characters—before investigating more complex API or trigger issues.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
