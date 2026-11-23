---
description: Convert Markdown to styled PDF via Chrome headless
allowed-tools: Bash, Read, Write, Edit, Glob
---

# md-to-pdf

Convert a Markdown document with YAML frontmatter into a professional, styled PDF using Chrome headless rendering.

## Usage

```
/md-to-pdf <input.md> [output.pdf]
```

## Examples

```bash
# Basic conversion
python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py report.md -o report.pdf

# With screenshot for QA
python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py report.md -o report.pdf --screenshot

# Keep HTML intermediate for debugging
python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py report.md -o report.pdf --keep-html

# No cover page
python3 .claude/skills/data/documents/md-to-pdf/md_to_pdf.py report.md -o report.pdf --no-cover
```

## Skill Reference

@.claude/skills/data/documents/md-to-pdf/SKILL.md
