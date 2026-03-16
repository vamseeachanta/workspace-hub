---
name: interoperability-editor-settings-recommended
description: 'Sub-skill of interoperability: Editor Settings (recommended).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Editor Settings (recommended)

## Editor Settings (recommended)


| Editor | Setting | Value |
|--------|---------|-------|
| VSCode | `files.encoding` | `utf8` |
| VSCode | `files.eol` | `\n` |
| VSCode | `files.autoGuessEncoding` | `false` |
| Notepad++ | Encoding menu | UTF-8 (not UTF-8 BOM) |
| Windows Notepad | — | Avoid for repo files |

VSCode `.vscode/settings.json` (already recommended in workspace):
```json
{
  "files.encoding": "utf8",
  "files.eol": "\n"
}
```
