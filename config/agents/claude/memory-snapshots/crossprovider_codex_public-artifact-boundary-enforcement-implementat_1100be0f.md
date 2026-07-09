---
name: crossprovider codex public-artifact-boundary-enforcement-implementat
description: Public artifact boundary enforcement: implementation docs must not include private wiki paths or data-source titles
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [security, boundary-enforcement, public-private-separation]
---

Plans and public PRs that name private wiki source paths, drive-query titles, or provenance identifiers violate the public/private boundary even if they're 'just documentation.' Move source detail and wiki paths to private artifacts only; public artifacts should reference only RSU handles, bands, and generic component names. Discovered in digitalmodel #1470 where plan text included private wiki paths despite stated policy forbidding them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
