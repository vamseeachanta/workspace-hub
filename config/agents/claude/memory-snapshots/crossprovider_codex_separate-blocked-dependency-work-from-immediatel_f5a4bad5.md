---
name: crossprovider codex separate-blocked-dependency-work-from-immediatel
description: Separate blocked-dependency work from immediately executable work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, planning, executability, plan-review]
---

Plans that state implementation waits for dependency `#XXXX` but then specify concrete code/tests `now` create executability ambiguity. Explicitly partition work: what can start immediately, what is blocked by each dependency, and when the dependency unblocks which files. If a dependency is truly blocking all work, defer all concrete file/test specs until after the dependency is resolved.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
