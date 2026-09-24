---
name: crossprovider gemini bandit-security-baseline-using-native-feature
description: Bandit security baseline using native feature
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [bandit, static-analysis, ci-integration]
---

Use Bandit's native baseline mechanism (`bandit -f json -o bandit-baseline.json` for initial capture, then `bandit -b bandit-baseline.json` for checks) instead of custom YAML parsing. This is more robust than parsing text output and integrates with the tool's intended workflow.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
