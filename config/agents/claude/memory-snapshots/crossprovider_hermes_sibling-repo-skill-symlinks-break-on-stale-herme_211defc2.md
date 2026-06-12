---
name: crossprovider hermes sibling-repo-skill-symlinks-break-on-stale-herme
description: Sibling-repo skill symlinks break on stale Hermes template
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [symlinks, provider-config, template-drift]
---

Sibling repos have `.codex/skills` → `../../.claude/skills` (missing parent); root cause is Hermes template still using `__WS_HUB_PATH__/<repo>/.claude/skills` nested form. Template mutation and symlink harmonization must occur in tandem or cascade breakage spreads to all providers. Verify both in PR review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
