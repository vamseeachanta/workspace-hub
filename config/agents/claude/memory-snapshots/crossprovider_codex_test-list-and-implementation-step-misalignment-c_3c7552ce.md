---
name: crossprovider codex test-list-and-implementation-step-misalignment-c
description: Test list and implementation step misalignment creates coverage gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, implementation, traceability]
---

Plans that list expected tests (e.g., `test_pipeline_line_sections_file_exists_for_ballymore_specs`) but don't explicitly connect them to numbered implementation steps allow tests to exist and pass without exercising the corresponding implementation. A path-existence check passes without proving the file was generated correctly or that the source key regression holds. Link each test to its implementation step and specify what each test must assert.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
