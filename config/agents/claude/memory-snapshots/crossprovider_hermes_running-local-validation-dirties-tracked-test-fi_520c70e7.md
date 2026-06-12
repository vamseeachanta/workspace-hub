---
name: crossprovider hermes running-local-validation-dirties-tracked-test-fi
description: Running local validation dirties tracked test fixtures
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tests, validation, fixtures]
---

Executing pytest or mkdocs locally generates updates to tracked result/fixture files (YAML agent configs, test result snapshots, etc.). After validation passes, revert these generated changes with `git restore` to keep the repo clean; otherwise CI-ready state is broken by dirty tracked files.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
