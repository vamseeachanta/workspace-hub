---
name: crossprovider codex public-private-boundary-enforcement-requires-exp
description: Public/private boundary enforcement requires explicit removal in generated artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [public-safety, artifact-generation, boundary-enforcement]
---

Public OSS repos must filter private paths from generated link graphs and manifests. Private wiki paths (wikis/_audit/, wikis/engineering/CLAUDE.md) must be explicitly removed from public artifacts; metadata-only formats reduce exposure compared to raw content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
