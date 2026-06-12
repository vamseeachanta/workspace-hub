---
name: crossprovider hermes path-based-repo-routing-requires-live-signal-sou
description: Path-based repo routing requires live signal source
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-structure, fanout-routing, repo-coupling]
---

File-path classification for repo-subset fanout (e.g., grep '^${repo}/' in pre-push) only works if the signal actually exists in tracked commits. Plans assuming such signals must first verify the repo structure contains the path prefixes being classified.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
