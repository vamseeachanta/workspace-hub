# Cross-Review Package — WRK-1304

## Mission
Update pdf and pdf-text-extractor skills to recommend PyMuPDF4LLM as the default
single-doc PDF-to-Markdown tool, replacing OpenAI Codex as primary recommendation.

## Plan (specs/wrk/WRK-1304/plan.md)

### Changes
1. **pdf/SKILL.md** — Promote pymupdf4llm in Tool Selection table from "monitor only" to primary single-doc recommendation; remove "AGPL license blocks adoption"
2. **pdf-text-extractor/SKILL.md** — Replace Codex Quick Start with pymupdf4llm example
3. **pdf/why-convert-to-markdown-first/SKILL.md** — Reference PyMuPDF4LLM instead of Codex
4. **pdf/openai-codex-conversion/SKILL.md** — Downgrade to "optional for complex docs"

### Acceptance Criteria
1. pdf/SKILL.md Tool Selection table: PyMuPDF4LLM promoted to primary single-doc recommendation
2. pdf-text-extractor/SKILL.md: Quick Start updated to show pymupdf4llm workflow
3. pdf/why-convert-to-markdown-first/SKILL.md: Updated to reference PyMuPDF4LLM
4. pdf/openai-codex-conversion/SKILL.md: Downgraded to "optional for complex docs"
5. PyMuPDF4LLM install instructions and version pinning added

### Test Plan
| # | What | Type | Expected |
|---|------|------|----------|
| 1 | Tool Selection table has pymupdf4llm as primary | happy | Row recommends PyMuPDF4LLM |
| 2 | Quick Start shows pymupdf4llm code | happy | `import pymupdf4llm` present |
| 3 | Codex remains referenced as fallback | edge | "optional for complex docs" qualifier |
| 4 | YAML frontmatter valid after edits | happy | No parse errors |
| 5 | No broken markdown links | error | All links resolve |

## Review Questions
1. Are the 4 files the correct scope? Any other files referencing Codex as primary?
2. Is the AGPL license note removal appropriate, or should it be softened to a warning?
3. Are the acceptance criteria specific and testable?
4. Any risks with promoting pymupdf4llm given AGPL licensing?
