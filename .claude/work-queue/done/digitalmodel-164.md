---
id: digitalmodel#164
title: "Update pdf skill to recommend PyMuPDF4LLM over Codex for single-doc Markdown conversion"
status: done
completed_at: "2026-03-24T08:20:00Z"
activated_at: "2026-03-24T08:02:00Z"
priority: medium
complexity: simple
route: A
created_at: "2026-03-17"
target_repos:
  - workspace-hub
category: engineering
subcategory: skills-maintenance
computer: dev-primary
plan_workstations:
  - dev-primary
execution_workstations:
  - dev-primary
blocked_by: []
tags: [pdf, skills, pymupdf4llm]
github_issue_ref: https://github.com/vamseeachanta/digitalmodel/issues/164
stage_evidence_ref: .claude/work-queue/assets/WRK-1304/evidence/stage-evidence.yaml
plan_ref: specs/wrk/WRK-1304/plan.md
plan_reviewed: true
plan_approved: true
---

## Mission

After WRK-1302 benchmarking confirms PyMuPDF4LLM viability, update pdf and
pdf-text-extractor skills to recommend PyMuPDF4LLM as the default single-doc
PDF-to-Markdown tool (replacing Codex recommendation). Codex remains an option
for cases requiring deeper understanding.

## Acceptance Criteria

1. [ ] Update pdf/SKILL.md Tool Selection table
2. [ ] Update pdf-text-extractor/SKILL.md Quick Start code examples
3. [ ] Update pdf/why-convert-to-markdown-first sub-skill
4. [ ] Remove or downgrade Codex references to "optional for complex docs"
5. [ ] Add PyMuPDF4LLM install instructions and version pinning
