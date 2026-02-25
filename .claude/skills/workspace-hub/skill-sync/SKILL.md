---
name: skill-sync
description: "Synchronize skills from anthropics/knowledge-work-plugins into workspace-hub skill system"
version: 1.0.0
category: workspace-hub
last_updated: 2026-02-03
source: internal
related_skills:
  - compliance-check
  - repo-sync
capabilities: []
requires: []
see_also: []
---

# Skill Sync

Synchronize skills from the `anthropics/knowledge-work-plugins` repository into the workspace-hub local skill system. This process fetches upstream SKILL.md files, converts them to the local format, and places them under `.claude/skills/` in the correct category directory.

## Overview

The sync mechanism bridges the upstream knowledge-work-plugins repository with the workspace-hub skill tree. Each upstream "plugin" maps to a local category directory, and each skill within a plugin gets its own subdirectory containing a `SKILL.md` file.

The sync script lives at `scripts/skills/sync-knowledge-work-plugins.sh`.

## Plugin-to-Directory Mapping

| Plugin                   | Local Directory                       |
|--------------------------|---------------------------------------|
| sales                    | business/sales                        |
| customer-support         | business/customer-support             |
| product-management       | business/product                      |
| marketing                | business/marketing                    |
| legal                    | business/legal                        |
| finance                  | business/finance                      |
| data                     | data/analytics                        |
| enterprise-search        | business/enterprise-search            |
| productivity             | business/productivity                 |
| bio-research             | science/bio-research                  |
| cowork-plugin-management | development/plugin-management         |

All paths are relative to `.claude/skills/`.

## Usage

### Check status of all plugins

```bash
./scripts/skills/sync-knowledge-work-plugins.sh
```

Reports each skill as OK, MISSING, or OUTDATED. Exits non-zero if any skills are missing or outdated (useful as a CI gate).

### Dry run

```bash
./scripts/skills/sync-knowledge-work-plugins.sh --dry-run
```

Shows what files would be created or updated without writing anything to disk.

### Show diffs

```bash
./scripts/skills/sync-knowledge-work-plugins.sh --diff
```

Displays a unified diff for each skill whose local copy differs from the upstream version. Combine with `--dry-run` for a preview:

```bash
./scripts/skills/sync-knowledge-work-plugins.sh --dry-run --diff
```

### Sync a single plugin

```bash
./scripts/skills/sync-knowledge-work-plugins.sh --sync --plugin=sales
```

Fetches and writes only the skills belonging to the specified plugin.

### Full sync

```bash
./scripts/skills/sync-knowledge-work-plugins.sh --sync
```

Fetches all plugins and writes every missing or outdated skill file.

## Adding a New Plugin

1. Add the plugin name and its local directory to the `PLUGIN_MAP` associative array in the sync script.
2. Add the plugin name and its space-separated skill slugs to the `PLUGIN_SKILLS` associative array.
3. Run `--dry-run` to verify the mapping is correct.
4. Run `--sync` to pull the new skills.

Example addition:

```bash
PLUGIN_MAP["new-plugin"]="category/new-plugin"
PLUGIN_SKILLS["new-plugin"]="skill-a skill-b skill-c"
```

## Format Conversion Rules

The sync script applies the following transformations when converting upstream content to the local format:

1. **Strip source-table frontmatter**: Removes content between `<!-- source-table -->` and `<!-- /source-table -->` comment markers, as well as leading HTML `<table>...</table>` blocks used by some plugins.
2. **Strip upstream YAML frontmatter**: If the upstream file already contains a YAML frontmatter block (delimited by `---`), it is removed.
3. **Add local YAML frontmatter**: A new YAML frontmatter block is prepended with the following fields:
   - `name`: the skill slug
   - `description`: auto-generated reference to the source plugin
   - `version`: set to `1.0.0`
   - `category`: the local directory path from `PLUGIN_MAP`
   - `last_updated`: the date the sync was performed
   - `source`: `anthropics/knowledge-work-plugins`
   - `source_plugin`: the upstream plugin name
4. **Trim leading blank lines**: Any blank lines between the stripped frontmatter and the body content are removed.

## Merge Strategy for Overlapping Skills

When a skill slug exists in multiple plugins (for example, `competitive-analysis` appears in both `product-management` and `marketing`), each instance is stored in its respective category directory. There is no deduplication -- both copies are maintained independently because the skill content differs by domain context.

If a local skill file has been manually customized:

- The `--diff` flag will show the divergence from upstream.
- The `--sync` flag will overwrite local changes with the upstream version.
- To preserve local customizations, either skip that plugin during sync (`--plugin` flag to sync others) or back up the file before syncing.

For skills that need permanent local modifications, consider removing them from the `PLUGIN_SKILLS` list in the sync script so they are no longer tracked against upstream.

## CI Integration

The script exits with code 1 when missing or outdated skills are detected (unless `--sync` is active). This makes it suitable as a CI check:

```yaml
- name: Check skill sync status
  run: ./scripts/skills/sync-knowledge-work-plugins.sh
```
