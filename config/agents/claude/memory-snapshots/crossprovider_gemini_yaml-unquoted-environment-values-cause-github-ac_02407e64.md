---
name: crossprovider gemini yaml-unquoted-environment-values-cause-github-ac
description: YAML unquoted environment values cause GitHub Actions parse failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, yaml, github-actions]
---

Unquoted DATABASE_URL: sqlite:///:memory: fails YAML parsing; workflows never register jobs (0s duration). Quote all env values.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
