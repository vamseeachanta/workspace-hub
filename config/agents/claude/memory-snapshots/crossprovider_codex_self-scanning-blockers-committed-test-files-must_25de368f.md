---
name: crossprovider codex self-scanning-blockers-committed-test-files-must
description: Self-scanning blockers: committed test files must not contain literal prohibited values
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [security-scanner, test-design, ci-gates]
---

When implementing security scanners, test files that hold negative examples (emails, paths, secrets) cause CI to fail once tracked if those literals are in the scanner's deny list. Move all prohibited test values to runtime-generated temp fixtures or synthetic placeholders—never commit literal examples that would trigger the scanner itself.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
