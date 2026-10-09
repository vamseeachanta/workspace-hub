---
name: extract-skills-from-hermes-sessions
description: Automatically analyze Claude Code session transcripts to identify and extract reusable skills using LLM analysis via OpenRouter
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["automation", "skill-extraction", "hermes-integration", "hooks"]
---

# Extract Skills from Hermes Sessions

Use a PostToolUse hook to automatically analyze session transcripts after edits, identifying skill-worthy patterns. The extractor calls OpenRouter (via openai library) to evaluate conversation against skill criteria, parses JSON output, and writes skill files to disk. Key: strip JSON fence carefully, truncate prompts to prevent token limits, and use claude-haiku for speed/cost.