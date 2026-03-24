# AC-Test Matrix — WRK-1304

| AC# | Acceptance Criteria | Result | Evidence |
|-----|---------------------|--------|----------|
| 1 | pdf/SKILL.md Tool Selection table: PyMuPDF4LLM promoted to primary | PASS | "Single-doc Markdown conversion" row recommends pymupdf4llm |
| 2 | pdf-text-extractor/SKILL.md: Quick Start updated with pymupdf4llm | PASS | `import pymupdf4llm` in Quick Start example |
| 3 | why-convert-to-markdown-first/SKILL.md: References PyMuPDF4LLM | PASS | Bullet added: "Fast local conversion — pymupdf4llm converts at 0.12s/doc" |
| 4 | Codex references downgraded to "optional for complex docs" | PASS | Note added to openai-codex-conversion/SKILL.md; tool selection shows "optional" |
| 5 | PyMuPDF4LLM install instructions and version pinning added | PASS | `pip install pymupdf4llm>=0.0.17` in pdf/SKILL.md and dependencies/SKILL.md |

**Additional scope (P2 cross-review):**

| File | Change | Result |
|------|--------|--------|
| pdf/dependencies/SKILL.md | Added pymupdf4llm install line | PASS |
| data/documents/INDEX.md | Updated pdf description | PASS |
