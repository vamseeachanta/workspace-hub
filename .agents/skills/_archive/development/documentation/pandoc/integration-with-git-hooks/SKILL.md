---
name: pandoc-integration-with-git-hooks
description: 'Sub-skill of pandoc: Integration with Git Hooks (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Integration with Git Hooks (+1)

## Integration with Git Hooks


```bash
#!/bin/bash
# .git/hooks/pre-commit
# Rebuild PDFs before commit

set -e

# Check if any markdown files changed
changed_md=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' || true)

if [[ -n "$changed_md" ]]; then
    echo "Rebuilding PDF documents..."

    for file in $changed_md; do
        if [[ -f "$file" ]]; then
            output="${file%.md}.pdf"
            echo "  Converting: $file -> $output"
            pandoc "$file" -o "$output" --pdf-engine=xelatex --toc
            git add "$output"
        fi
    done
fi
```


## Integration with VS Code Tasks


```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Pandoc: Build PDF",
            "type": "shell",
            "command": "pandoc",
            "args": [
                "${file}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}.pdf",
                "--pdf-engine=xelatex",
                "--toc",
                "--number-sections"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always"
            }
        },
        {
            "label": "Pandoc: Build DOCX",
            "type": "shell",
            "command": "pandoc",
            "args": [
                "${file}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}.docx",
                "--toc"
            ]
        },
        {
            "label": "Pandoc: Watch and Build",
            "type": "shell",
            "command": "find . -name '*.md' | entr -c pandoc ${file} -o ${fileDirname}/${fileBasenameNoExtension}.pdf --pdf-engine=xelatex",
            "isBackground": true,
            "problemMatcher": []
        }
    ]
}
```
