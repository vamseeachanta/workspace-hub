---
name: extract-skills-from-claude-code-sessions
description: Automatically extract reusable skills from Claude Code session transcripts using LLM analysis and wire them into a Stop hook
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["claude-code", "skills", "automation", "self-improvement", "hooks"]
---

# Extract Skills from Claude Code Sessions

Wire a Stop hook that fires when Claude Code ends a session. The hook runs `skill-extractor.py`, which reads the transcript, calls an LLM (via OpenRouter) to identify skill-worthy patterns, and writes a SKILL.md file if extraction succeeds. Use `openai` library for API calls, strip JSON fence artifacts with `.strip()`, and request concise content (<1500 tokens) to avoid truncation. Test end-to-end with synthetic skill-worthy conversations before deploying.