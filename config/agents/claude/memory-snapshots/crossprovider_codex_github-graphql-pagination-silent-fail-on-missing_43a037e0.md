---
name: crossprovider codex github-graphql-pagination-silent-fail-on-missing
description: GitHub GraphQL pagination silent-fail on missing pageInfo
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [graphql, pagination, error-handling, github-api]
---

Pagination guards checking `if page_info.get('hasNextPage'):` don't catch malformed responses where the `pageInfo` field is absent or missing entirely. Missing field is silently treated as terminal instead of raising. Nested label pagination under-triggers the same way. Pattern recurs across any pagination code consuming GraphQL.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
