---
name: crossprovider gemini provider-specific-prompt-directories-for-systems
description: Provider-specific prompt directories for systems without unified plugin markets
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tooling, cross-provider, architecture]
---

Codex and Gemini CLIs lack centralized skill/plugin systems equivalent to Claude's `.claude/skills/`, so workspace-hub maintains provider-specific prompt directories (`.codex/prompts/`, `.gemini/prompts/`) alongside centralized skills. Provider-specific templates coexist with shared skills via symlinks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
