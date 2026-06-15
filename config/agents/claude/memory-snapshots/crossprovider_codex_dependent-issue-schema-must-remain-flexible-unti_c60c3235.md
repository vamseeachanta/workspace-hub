---
name: crossprovider codex dependent-issue-schema-must-remain-flexible-unti
description: Dependent issue schema must remain flexible until upstream resolves
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [project-management, schema-design, dependency-coordination]
---

When downstream issue (e.g., #266 taxonomy) depends on unresolved upstream (e.g., #269 database capture), define schema with placeholder fields for upstream outputs but mark them optional/permissive in validators. Avoid freezing final vocabulary or slug patterns until upstream lands. Define citation versioning rules (e.g., `abs-db-<resource>-<snapshot-date>`) before implementation, not after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
