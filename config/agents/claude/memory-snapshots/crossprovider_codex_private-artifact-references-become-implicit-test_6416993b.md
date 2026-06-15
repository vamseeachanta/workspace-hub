---
name: crossprovider codex private-artifact-references-become-implicit-test
description: Private artifact references become implicit test dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [artifact-lifecycle, testing, automation]
---

When a repo artifact (markdown, code comment) references a private JSONL file for validation, that path becomes a test-time requirement that must exist and be locatable. Document the capture root and ensure validation is runnable from the approved location.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
