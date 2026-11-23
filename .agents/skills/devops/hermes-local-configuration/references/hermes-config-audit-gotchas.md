# Archived Skill: `hermes-config-audit-gotchas`

Original path: `/home/vamsee/.hermes/skills/devtools/hermes-config-audit-gotchas`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/devtools/hermes-config-audit-gotchas`
Consolidation date: 2026-04-29

---

---
name: hermes-config-audit-gotchas
description: Audit Hermes custom config keys and migrated skill settings safely, with verified command behavior and stale-path checks.
version: 1.0.1
author: Hermes Agent
license: MIT
---

# Hermes Config Audit Gotchas

Use when reviewing Hermes configuration after `hermes config migrate`, `hermes setup`, or when a prompt mentions new skill settings such as `wiki.path`.

## What this skill is for

Hermes can prompt for skill-defined config keys during migration, but the displayed logical key (for example `wiki.path`) is not always the exact stored path in config, and migrated defaults may point at directories that do not exist.

## Verified workflow

1. Load relevant config/documentation skills if available (`hermes-agent`, any skill declaring the config key).
2. Check live config with:
   - `hermes config show`
   - `hermes config check`
   - `hermes config path`
   - `hermes config env-path`
3. Do not assume `hermes config list` or `hermes config get` exist.
   - In the audited build, both are invalid subcommands.
4. Confirm the storage shape if needed by inspecting the config file with normal file tools.
5. Verify the configured filesystem path actually exists before recommending it.
6. If the prompted key is a skill key, remember Hermes stores it under `skills.config.*` even if the prompt shows only the logical key.

## Key findings

- `wiki.path` from `llm-wiki` is stored as `skills.config.wiki.path`.
- `hermes config show` is the authoritative read command in the audited build.
- `hermes config list` and `hermes config get` are not supported in the audited build.
- A migrated default like `~/wiki` can be stale. Verify the real wiki root before accepting it.
- On the audited machine, `/home/vamsee/wiki` was missing while `/mnt/local-analysis/workspace-hub/knowledge/wikis` existed and was the better candidate for the workspace-hub multi-wiki layout.

## Recommended review pattern

For each prompted config item:
1. Identify which skill declared it.
2. Confirm how Hermes stores it in config.
3. Check whether the current configured value exists and is meaningful.
4. Propose the corrected `hermes config set ...` command using the stored key path, not just the displayed logical key.

## Example

Prompted item:
- `wiki.path — Path to the LLM Wiki knowledge base directory`

Recommended command form:
```bash
hermes config set skills.config.wiki.path /mnt/local-analysis/workspace-hub/knowledge/wikis
```

## Pitfalls

- Do not trust migrated defaults without a filesystem existence check.
- Do not rely on unsupported subcommands like `list` or `get`.
- Do not confuse the displayed logical key with the stored YAML key path.
