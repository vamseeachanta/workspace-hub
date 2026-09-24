---
name: crossprovider codex interdependent-issue-chains-need-explicit-blocki
description: Interdependent issue chains need explicit blocking and sequencing markers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning-discipline, dependency-management, multi-issue-coordination]
---

Issues #605–#613 form a dependency graph where downstream plans reference modules and data contracts from upstream issues that don't yet exist (e.g., orcawave_asset_resolver.py). Plans must mark §Blockers with explicit "blocked on <issue> until <contract> is available" and explain why, or split scope to decouple.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
