---
name: crossprovider hermes graphql-rate-limit-fallback-use-rest-api-when-gh
description: GraphQL rate limit fallback: use REST API when gh issue view fails
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-api, rate-limiting, tool-fallback]
---

When `gh issue view` (GraphQL) hits rate limit, fall back to REST endpoints like `gh api /repos/<owner>/<repo>/issues/<num>` or curl equivalents. Verified working in session_20260512_182557 during high API usage periods.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
