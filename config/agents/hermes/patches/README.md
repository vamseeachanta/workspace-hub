# Hermes Local Patches

Patches applied by harness-update.sh after each hermes update.
Replaces the need to fork NousResearch/hermes-agent.

## Creating a patch
cd ~/.hermes/hermes-agent
git diff > ~/workspace-hub/config/agents/hermes/patches/my-fix.patch

## Current patches

### exclude-archive-skill-dirs.patch
Added 2026-04-02. Extends `EXCLUDED_SKILL_DIRS` in `agent/skill_utils.py`
to skip `_archive`, `_internal`, `_runtime`, `_core`, and `session-logs`
directories when scanning external skill directories. This prevents
2,166 archived workspace-hub skills from bloating the system prompt —
only the 387 active skills are indexed.
