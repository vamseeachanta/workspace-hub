---
name: crossprovider hermes public-oss-repo-firewall-llm-wiki-blocks-workspa
description: Public OSS repo firewall: llm-wiki blocks workspace-hub private context
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance, public-repos, firewall]
---

The llm-wiki public repo has a CLAUDE.md agent-context firewall forbidding commits/PRs/docs from echoing workspace-hub private memory, recruiter notes, vendor derivatives, client/compliance data, or infrastructure details. Output boundaries: raw archives (/mnt/ace) are input-only. Enforced by per-repo LICENSE, .gitignore, and .claude/ constraints.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
