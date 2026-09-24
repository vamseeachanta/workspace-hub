---
name: crossprovider codex prefer-apis-over-clis-for-agent-integration
description: Prefer APIs over CLIs for agent integration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [agent-design, integration-pattern, api-vs-cli]
---

When exposing domain data or services to agents, prefer structured Python APIs and catalogs over CLI scraping. APIs are safer (no shell injection risk), more structured (typed returns), agent-callable without parsing, and maintainable. Reserve CLI-only commands for coarse, safe operations with clear scope boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
