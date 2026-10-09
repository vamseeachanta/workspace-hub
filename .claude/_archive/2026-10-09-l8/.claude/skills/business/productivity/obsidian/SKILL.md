---
name: obsidian
version: 1.1.0
description: Local-first knowledge management with markdown vaults, bidirectional linking, plugin ecosystem, and practical vault file operations.
author: workspace-hub
category: business
type: skill
capabilities:
- markdown_knowledge_base
- bidirectional_linking
- graph_visualization
- plugin_ecosystem
- templating_automation
- dataview_queries
- sync_strategies
- backup_workflows
tools:
- obsidian
- obsidian-cli
- dataview
- templater
- git
tags:
- obsidian
- knowledge-management
- markdown
- zettelkasten
- pkm
- productivity
platforms:
- desktop
- mobile
- linux
- macos
- windows
- ios
- android
related_skills:
- yaml-configuration
- git-sync-manager
requires: []
scripts_exempt: true
---

# Obsidian

## When to Use

Use Obsidian when you want a local-first markdown vault with links, durable files, and flexible automation. It fits personal knowledge management, project notes, research notes, journals, and operational runbooks.

Do not use it when you need live multi-user collaboration, database-style workflows, or permission-heavy enterprise knowledge bases.

## Basic Vault Operations

Typical vault path handling:

```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault"
ls "$OBSIDIAN_VAULT_PATH"
find "$OBSIDIAN_VAULT_PATH" -name '*.md' | head
```

Always quote vault paths because spaces are common.

Read a note:

```bash
cat "$OBSIDIAN_VAULT_PATH/Projects/My Project.md"
```

Create a note:

```bash
cat > "$OBSIDIAN_VAULT_PATH/Inbox/New Note.md" <<'EOF'
# New Note

- idea
- follow-up
EOF
```

Append to a note:

```bash
echo "- next action" >> "$OBSIDIAN_VAULT_PATH/Projects/My Project.md"
```

Search by filename/content:

```bash
find "$OBSIDIAN_VAULT_PATH" -iname '*project*'
grep -R "cathodic protection" "$OBSIDIAN_VAULT_PATH"
```

## Vault Structure

A practical starting layout:

```bash
mkdir -p "$OBSIDIAN_VAULT_PATH"/{Inbox,Projects,Areas,Resources,Archive,Templates,"Daily Notes"}
```

## Linking Conventions

Use wikilinks for concept connections:
- `[[Project X]]`
- `[[API 579]]`
- `[[Meeting Notes 2026-04-03]]`

Prefer stable note names over constantly-renamed files.

## Plugins and Automation

Common useful plugins:
- Dataview for note queries
- Templater for standardized note creation
- Git for sync/versioning

## Sync and Backups

Recommended patterns:
- Git for text-first technical vaults
- cloud sync for personal/mobile access
- periodic filesystem backup regardless of sync strategy

## Practical Use Cases

- project dashboards and action tracking
- reading notes and literature synthesis
- engineering reference capture
- daily/weekly review notes
- meeting notes linked to decisions and follow-ups

## Resources

- https://obsidian.md/
- https://help.obsidian.md/
- https://blacksmithgu.github.io/obsidian-dataview/
- https://silentvoid13.github.io/Templater/

## Sub-Skills

- [1. Vault Structure and Organization (+1)](1-vault-structure-and-organization/SKILL.md)
- [Integration with Git Repositories](integration-with-git-repositories/SKILL.md)
- [1. Note Naming and Organization (+3)](1-note-naming-and-organization/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
- [Summary](summary/SKILL.md)
- [Related Concepts](related-concepts/SKILL.md)
- [Sources](sources/SKILL.md)
- [Applications](applications/SKILL.md)
