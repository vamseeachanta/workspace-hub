---
name: crossprovider hermes generated-artifact-path-hygiene-check-for-public
description: Generated artifact path hygiene check for public repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, public-artifacts, hygiene]
---

Generated HTML/Markdown artifacts destined for public repos must not leak absolute paths like `/tmp`, `/home`, `localhost`, mount paths, or session directories. Grep generated outputs for `^/`, `localhost`, or hostname before committing; substitute with relative paths or omit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
