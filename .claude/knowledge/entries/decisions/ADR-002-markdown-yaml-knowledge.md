---
id: ADR-002
type: decision
title: "Use Markdown with YAML frontmatter for knowledge entries"
category: architecture
tags: [knowledge-management, storage, markdown, yaml]
repos: [workspace-hub]
confidence: 0.9
created: "2026-01-30"
last_validated: "2026-01-30"
source_type: manual
related: [ADR-001]
status: active
access_count: 0
---

# Use Markdown with YAML Frontmatter for Knowledge Entries

## Context

The workspace-hub needed a storage format for institutional knowledge that is human-readable, machine-parseable, version-controllable, and consistent with existing patterns (WRK-*.md work items, SKILL.md files, spec templates).

## Decision

Each knowledge entry is a markdown file with YAML frontmatter containing structured metadata. A companion index.json provides fast machine-readable search without parsing every file. Entry types (ADR, PAT, GOT, COR, TIP) each have their own prefix and subdirectory.

## Rationale

- Markdown is the lingua franca of the workspace-hub (CLAUDE.md, specs, skills all use it)
- YAML frontmatter is already used in work queue items and spec files
- Git tracks changes naturally - no database needed
- JSON index enables fast search by type, tag, category, repo without full-text scan
- Progressive disclosure: index metadata (~100 tokens) -> full entry (<5K tokens)

## Consequences

- Index must be rebuilt when entries change (knowledge-index.sh handles this)
- No real-time search - index is a snapshot (acceptable for institutional knowledge)
- Deduplication requires title similarity check against existing index
