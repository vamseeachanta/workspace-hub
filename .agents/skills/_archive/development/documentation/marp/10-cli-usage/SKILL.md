---
name: marp-10-cli-usage
description: 'Sub-skill of marp: 10. CLI Usage (+5).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 10. CLI Usage (+5)

## 10. CLI Usage


```bash
# Convert to HTML
marp slides.md -o slides.html

# Convert to PDF
marp slides.md -o slides.pdf

# Convert to PPTX
marp slides.md -o slides.pptx


*See sub-skills for full details.*

## 11. Configuration File


```yaml
# .marprc.yml
html: true
allowLocalFiles: true
output: "./dist"
theme: "./themes/corporate.css"

pdf: true
pdfNotes: true

watch: false
server: false
serverPort: 8080
```

## 12. VS Code Settings


```json
// .vscode/settings.json
{
  "markdown.marp.enableHtml": true,
  "markdown.marp.themes": [
    "./themes/custom.css"
  ],
  "markdown.marp.mathTypesetting": "katex",
  "markdown.marp.exportType": "pdf"
}
```

## 13. GitHub Actions Workflow


```yaml
# .github/workflows/presentations.yml
name: Build Presentations

on:
  push:
    branches: [main]
    paths: ['presentations/**']

jobs:

*See sub-skills for full details.*

## 14. Docker Usage


```bash
# Build with Docker
docker run --rm -v $(pwd):/app marpteam/marp-cli \
  /app/slides.md -o /app/slides.pdf

# Run server
docker run --rm -p 8080:8080 -v $(pwd):/app marpteam/marp-cli \
  -s /app/slides.md
```

## 15. Advanced Layouts


```markdown
---
marp: true
---

<style>
.columns { display: grid; grid-template-columns: 1fr 1fr; gap: 2em; }
.centered { display: flex; flex-direction: column; justify-content: center; align-items: center; }
</style>


*See sub-skills for full details.*
