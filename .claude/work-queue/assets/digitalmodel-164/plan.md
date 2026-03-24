# WRK-1304: Update pdf skill to recommend PyMuPDF4LLM over Codex

## Summary
Update pdf and pdf-text-extractor skills to recommend PyMuPDF4LLM as the default
single-doc PDF-to-Markdown tool, replacing OpenAI Codex as primary recommendation.
Codex remains an option for complex documents requiring deeper understanding.

## Acceptance Criteria
1. pdf/SKILL.md Tool Selection table: PyMuPDF4LLM promoted to primary single-doc recommendation
2. pdf-text-extractor/SKILL.md: Quick Start updated to show pymupdf4llm workflow
3. pdf/why-convert-to-markdown-first/SKILL.md: Updated to reference PyMuPDF4LLM
4. pdf/openai-codex-conversion/SKILL.md: Downgraded to "optional for complex docs"
5. PyMuPDF4LLM install instructions and version pinning added

## Changes

### 1. pdf/SKILL.md
- Description: change "OpenAI Codex PDF-to-Markdown" → "PyMuPDF4LLM"
- Tool Selection table: promote pymupdf4llm from "monitor only" to primary single-doc
- "Single-doc understanding" row: change from Codex to PyMuPDF4LLM
- Remove "AGPL license blocks adoption" note (user has accepted AGPL)
- When to Use: update Codex reference

### 2. pdf-text-extractor/SKILL.md
- Description: replace Codex with PyMuPDF4LLM for single-doc quality
- Quick Start: replace Codex workflow with pymupdf4llm example
- Tool selection summary: update

### 3. pdf/why-convert-to-markdown-first/SKILL.md
- Replace Codex reference with PyMuPDF4LLM
- Update bullet about "AI understanding"

### 4. pdf/openai-codex-conversion/SKILL.md
- Add note: "For most single-doc conversions, prefer pymupdf4llm (faster, no API cost).
  Use Codex when you need deeper understanding of complex documents."

## Pseudocode
N/A — pure documentation/skill updates, no executable code changes.

## Test Plan

| # | What | Type | Expected |
|---|------|------|----------|
| 1 | pdf/SKILL.md Tool Selection table has pymupdf4llm as primary single-doc tool | happy | "Single-doc understanding" row recommends PyMuPDF4LLM |
| 2 | pdf-text-extractor/SKILL.md Quick Start shows pymupdf4llm code | happy | `import pymupdf4llm` in Quick Start example |
| 3 | Codex remains referenced as fallback for complex docs | edge | Codex mentioned with "optional for complex docs" qualifier |
| 4 | YAML frontmatter still valid after edits | happy | No YAML parse errors in skill frontmatter |
| 5 | No broken markdown links in edited files | error | All sub-skill links resolve to existing files |

## Scripts to Create
None — no recurring operations.

## Confirmation
confirmed_by: user
confirmed_at: 2026-03-24T02:00:00-05:00
decision: passed
