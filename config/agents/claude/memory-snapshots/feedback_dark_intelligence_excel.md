---
name: Dark intelligence for Excel calculation extraction
description: Use dark intelligence archive to extract calculation logic from legacy Excel files — strips client context, preserves engineering methodology, avoids legal issues
type: feedback
---

Dark intelligence (`knowledge/dark-intelligence/`) serves a critical legal compliance purpose:
extract calculation methodology from legacy Excel spreadsheets and archive ONLY the generic
engineering logic (formulas, validation data, worked examples) — never client identifiers,
project names, or proprietary data.

**Why:** Legacy Excel files contain verified calculations but also client-specific data that
creates legal/IP risk if carried forward. Extracting the methodology into dark intelligence
completely avoids legacy legal issues while preserving the engineering value.

**How to apply:**
- When encountering Excel calculations from past work, use the research-literature skill
  to extract: equations, input ranges, expected outputs, validation cases
- Archive as YAML in `knowledge/dark-intelligence/<category>/<subcategory>/`
- Run legal-sanity-scan on extracted content before archiving
- Use extracted worked examples as TDD test data for new implementations
- Never copy raw Excel files — only the distilled methodology
- This is the preferred path for porting any legacy calculation to the 4 public repos
