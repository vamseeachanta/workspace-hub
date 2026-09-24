---
name: crossprovider codex canonical-identity-needs-rename-history-alias-po
description: Canonical identity needs rename history, alias policy, and wrapper handling beyond frontmatter
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [identity, versioning, system-design]
---

Using only frontmatter `name` as canonical identity fails when skills are renamed, wrapped, superseded, or have aliases across specializations. Stable keys must account for historical renames and parent/child relationships. Define explicit identity/alias/wrapper policy before building detection automation on it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
