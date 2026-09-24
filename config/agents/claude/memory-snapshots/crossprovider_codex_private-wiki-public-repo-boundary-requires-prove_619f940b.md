---
name: crossprovider codex private-wiki-public-repo-boundary-requires-prove
description: Private-wiki/public-repo boundary requires provenance tripwire
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, repo-boundaries, automation]
---

Projects maintaining both public and private repos (e.g., public digitalmodel repo with paired private wiki containing criteria values) need automated provenance checks to prevent private identifiers leaking into commits. The provenance tripwire is slow but necessary; run it separately from fast resolver tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
