---
name: crossprovider hermes context-firewall-between-private-and-public-repo
description: Context firewall between private and public repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, oss, multi-repo]
---

Agents working across private workspace-hub and public llm-wiki must enforce strict boundaries: no private memory, vendor derivatives, local path-rich manifests, or credentials into commits/PRs/issues. Governance rules (CLAUDE.md, service-provider routing) are repo-local and override shared memory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
