---
name: crossprovider hermes search-files-times-out-on-broad-repo-globs-refin
description: Search-files times out on broad repo globs; refine iteratively instead
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tooling, search-files, repo-size-performance]
---

Patterns like `*maneuver*|*curve*|*nomoto*` on large repos timeout after 120 seconds. Terminal `find` is explicitly discouraged. Instead: start narrow (e.g., `*maneuverability*` or `*yaw*`), inspect results, then refine. The search_files tool is slower than find but respects permission boundaries; accept narrower queries as the tradeoff.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
