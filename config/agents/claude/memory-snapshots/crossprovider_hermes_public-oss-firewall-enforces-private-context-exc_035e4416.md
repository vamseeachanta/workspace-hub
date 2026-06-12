---
name: crossprovider hermes public-oss-firewall-enforces-private-context-exc
description: Public OSS firewall enforces private-context exclusion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [security, public-repo, governance]
---

vamseeachanta/llm-wiki uses strict CLAUDE.md gates to prevent workspace-hub private memory, recruiter notes, vendor-derivative content, local manifests, and credentials from leaking into public commits. Requires explicit per-repo context firewall and service-provider data routing logic. Spot-checks on all PRs/issues validate compliance.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
