---
name: crossprovider codex plans-often-assert-things-don-t-exist-when-they-
description: Plans often assert things don't exist when they are already committed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, resource-intel, verification-hazard]
---

Plans frequently claim resource-intel facts (markers, imports, functions, config entries) that are actually present in the repo. Verification pattern: check committed code directly, don't trust plan resource-intel sections.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
