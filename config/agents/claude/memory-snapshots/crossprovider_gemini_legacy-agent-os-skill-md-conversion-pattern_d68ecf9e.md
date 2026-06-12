---
name: crossprovider gemini legacy-agent-os-skill-md-conversion-pattern
description: Legacy agent-os → SKILL.md conversion pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, modernization, skills, frameworks]
---

Modernize legacy agent-os domain agents by extracting markdown domain-knowledge files from agent.yaml into canonical `.claude/skills/<domain>/SKILL.md` format. Discard agent-os framework config (capability flags, RAG settings); preserve domain content (context, expertise, prompts). Enables skill portability and reduces framework lock-in.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
