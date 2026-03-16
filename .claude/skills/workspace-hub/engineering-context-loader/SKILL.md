---
name: engineering-context-loader
description: 'Auto-detects the active engineering domain from a WRK item''s tags and
  outputs a focused context: which skills to load, which design codes apply, and which
  memory/spec files to read. Prevents loading the full 350+ skill catalog when only
  ~20 domain-relevant skills are needed.

  '
version: 1.0.0
updated: 2026-02-24
category: workspace-hub
triggers:
- engineering context
- load engineering context
- context loader
- domain context
- engineering session start
- what skills do I need
- domain-aware session start
related_skills:
- session-start
- workstations
- save
capabilities:
- domain-detection
- skill-subset-selection
- design-code-surfacing
- memory-file-routing
- spec-file-discovery
requires: []
tags:
- session-lifecycle
- engineering
- context-optimization
- naval-architecture
invoke: engineering-context-loader
see_also:
- engineering-context-loader-domain-map
- engineering-context-loader-step-1-resolve-the-active-wrk-item
- engineering-context-loader-skills-to-load-read-these-skillmd-files
- engineering-context-loader-output-example
- engineering-context-loader-skills-to-load-read-these-skillmd-files
- engineering-context-loader-integration
- engineering-context-loader-error-cases
---

# Engineering Context Loader

## When to Use

- After `/session-start` when the top unblocked item has engineering tags
- When switching to a new WRK item mid-session
- Manually via `/engineering-context-loader` whenever domain context is stale

## Sub-Skills

- [Domain Map](domain-map/SKILL.md)
- [Step 1 — Resolve the Active WRK Item (+5)](step-1-resolve-the-active-wrk-item/SKILL.md)
- [Skills to Load (read these SKILL.md files) (+4)](skills-to-load-read-these-skillmd-files/SKILL.md)
- [Output Example](output-example/SKILL.md)
- [Skills to Load (read these SKILL.md files) (+4)](skills-to-load-read-these-skillmd-files/SKILL.md)
- [Integration](integration/SKILL.md)
- [Error Cases](error-cases/SKILL.md)
