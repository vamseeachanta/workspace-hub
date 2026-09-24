---
name: crossprovider gemini test-scaffolding-pattern-for-agent-routing-mock-
description: Test scaffolding pattern for agent routing: mock work queue + phase-based provider resolution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [testing, agent-routing, patterns]
---

Agent routing tests use mock work queue directory structure with frontmatter-based WRK items, assertion helpers (assert_eq), and phase-based provider resolution with fallback chains: task_agents[phase] → provider field → CLI fallback. This pattern supports testing provider dispatch logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
