> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/data_format_guidelines.md

---
name: data-format-guidelines
description: When to use YAML vs JSON vs Markdown for AI agent-readable/writable files — token cost, corruption patterns, and format decision rules
type: feedback
---

## Format Decision Rule

**Default to YAML for all agent-facing structured data** — with schema validation to eliminate YAML's silent corruption weakness.

| Who writes | Format | Why |
|-----------|--------|-----|
| Human curates | YAML | Comments, readability, diff-friendly |
| Agent writes structured data | YAML + schema validation | Fewer tokens = better instruction-following; comments as inline instructions |
| Agent writes evidence/state | YAML | Ecosystem consistency; 30-40% fewer tokens than JSON |
| Script generates deterministic output | JSON | Schema-enforceable, no ambiguity |
| Prose content (plans, reviews, narratives) | Markdown | Rendering matters; human review at gates |
| External API interchange | JSON | Industry standard for APIs |

## YAML vs JSON — Agent Instruction-Following

Both parse to identical Python objects — semantically equivalent. But YAML is superior for agent instruction-following when schema validation is in place:

- **Token density**: YAML uses ~30-40% fewer tokens → more instructions fit per context window → instruction-following degrades later as context fills
- **Comments as co-located instructions**: YAML allows `# HARD RULE: never change this` next to the field — agents follow rules better when rationale is adjacent to data
- **Multiline instructions**: YAML `|` blocks preserve formatting; JSON `\n` escaping degrades instruction parsing
- **Visual hierarchy**: indentation-based nesting costs fewer attention tokens to parse than brace-matching
- **Anthropic's JSON recommendation**: was specifically about corruption detection (strict parser), NOT about comprehension. With schema validation on YAML, that advantage disappears
- **JSON only wins** for: external API interchange, script-generated output, and cases where no schema validation exists

## Corruption Patterns by Format

| Format | Common LLM corruption | Detection |
|--------|----------------------|-----------|
| Markdown tables | Rows deleted, columns misaligned, reformatted | Silent — no parser |
| YAML | Indentation drift, block/flow confusion | Silent — valid YAML, wrong data |
| JSON | Trailing commas, missing braces, added comments | Loud — parser rejects immediately |

**How to apply:** When creating new agent-writable structured files, use JSON if the agent edits specific fields (checklists, status flags), YAML if the agent appends records (evidence, logs). Never use markdown tables for structured data agents write.
