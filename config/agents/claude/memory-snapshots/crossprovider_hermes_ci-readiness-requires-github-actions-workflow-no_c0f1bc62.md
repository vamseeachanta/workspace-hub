---
name: crossprovider hermes ci-readiness-requires-github-actions-workflow-no
description: CI-readiness requires GitHub Actions workflow, not just passing tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci, github-actions, workflows]
---

A repo with all local tests passing can still fail CI-readiness checks if it lacks `.github/workflows/ci.yml`. The workflow file is the gating artifact; if absent, the repo cannot run checks on PR/push regardless of local test status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
