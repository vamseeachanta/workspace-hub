---
name: crossprovider codex registry-derived-skill-paths-pattern-for-sibling
description: Registry-derived skill paths pattern for sibling-repo SSoT
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, sibling-repos, hermes-config, workspace-hub]
---

Instead of hardcoding sibling repo paths in agent config templates, use a manifest (registry.yaml) with `tier1_repo_root` + `repo_layout: sibling` per machine; sync-agent-configs.sh then resolves and validates which sibling repos actually exist and contain SKILL.md before insertion. This makes the registry the source of truth without template edits on each repo addition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
