---
name: crossprovider hermes ci-diagnosis-real-failures-vs-post-job-pipeline-
description: CI diagnosis: real failures vs. post-job pipeline noise
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [ci-debugging, pytest, log-inspection]
---

Distinguish pytest failures from post-job infrastructure failures (pip-cache, setup-python, build artifacts) by inspecting full CI logs and running local subset tests. Tool output often truncates; write diagnosis to files for inspection. Sibling repo dependencies may need mocking or fresh clones.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
