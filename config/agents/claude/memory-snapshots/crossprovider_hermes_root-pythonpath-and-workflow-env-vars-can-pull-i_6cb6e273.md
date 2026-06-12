---
name: crossprovider hermes root-pythonpath-and-workflow-env-vars-can-pull-i
description: Root PYTHONPATH and workflow env vars can pull in unintended parent-workspace tests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-config, pythonpath, test-discovery]
---

When fixing CI, check root `pyproject.toml` and `.github/workflows/` for PYTHONPATH that includes parent directories. These can inadvertently expose parent-workspace test files to child-repo test discovery. Update workflows per-repo to use minimal isolated pythonpath (e.g., `src` or `src:../sibling/src`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
