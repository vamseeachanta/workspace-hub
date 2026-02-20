---
provider: gemini
generated-from: AGENTS.md
contract-version: 1.0.0
generated-at: 2026-02-18T00:00:00Z
---

# Gemini Agent Adapter

> Adapter for Google Gemini / gemini CLI tooling.
> Canonical contract is in workspace-hub/AGENTS.md.

## Adapter Role

This file is a provider-specific adapter for Gemini-compatible tooling.
The canonical contract is in workspace-hub/AGENTS.md.

## Required Gates

1. Every non-trivial task must map to a WRK-* item in .claude/work-queue/.
2. Planning + explicit approval are required before implementation.
3. Route B/C work requires cross-review before completion.

## Plan and Spec Locality

1. Route A/B plan details can live in WRK body sections.
2. Route C execution specs: specs/wrk/WRK-<id>/.
3. Repository/domain specs: specs/repos/<repo>/.
4. Templates: specs/templates/.

## Provider Strengths

Research and content tasks: data analysis, summarization, documentation, reports.
Best for: research synthesis, content generation, large context analysis, and data review.

## Skills

`.gemini/skills/` → `.claude/skills/` (workspace-hub canonical)

All skills defined in `.claude/skills/` are available to Gemini via this symlink.
