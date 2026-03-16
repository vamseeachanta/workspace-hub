---
name: ecosystem-health
description: "Parallel health check agent for workspace-hub \u2014 verifies encoding\
  \ guard, hook wiring, uv availability, skill frontmatter, and work queue integrity\
  \ at session end or after repo-sync"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-02-19
wrk_ref: WRK-211
trigger: session-exit, post-repo-sync
auto_execute: false
related_skills:
- repo-sync
- improve
- interoperability
- claude-reflect
tags:
- ecosystem
- health-checks
- agent-teams
- automation
- parallel-agent
platforms:
- all
capabilities: []
requires: []
see_also:
- ecosystem-health-usage
- ecosystem-health-when-to-run
- ecosystem-health-group-1-cross-platform-guard
- ecosystem-health-output-format
- ecosystem-health-json-signal-for-improve
- ecosystem-health-step-1-group-1-checks-bash-fast
- ecosystem-health-integration-with-repo-sync
- ecosystem-health-related
---

# Ecosystem Health

## Sub-Skills

- [Usage](usage/SKILL.md)
- [When to Run](when-to-run/SKILL.md)
- [Group 1: Cross-Platform Guard (+3)](group-1-cross-platform-guard/SKILL.md)
- [Output Format](output-format/SKILL.md)
- [JSON Signal (for /improve)](json-signal-for-improve/SKILL.md)
- [Step 1: Group 1 checks (bash, fast) (+3)](step-1-group-1-checks-bash-fast/SKILL.md)
- [Integration with /repo-sync](integration-with-repo-sync/SKILL.md)
- [Related](related/SKILL.md)
