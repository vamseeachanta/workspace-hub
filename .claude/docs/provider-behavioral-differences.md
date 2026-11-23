# Provider Behavioral Differences — Top 3
> WRK-1405 Phase 4 | Updated: 2026-03-25

## 1. Context Window & Tool Usage
| Aspect | Claude Code | Codex CLI | Gemini CLI |
|--------|------------|-----------|------------|
| Context | 1M tokens | 200K tokens | 1M tokens |
| File editing | Edit tool (targeted) | apply_patch | Edit via file writes |
| Parallel tools | Yes (multi-tool) | Sequential only | Sequential only |
| **Implication** | Can handle large specs in single context | Needs chunked context for large WRK items | JIT context loading compensates |

## 2. Permission Models & Autonomy
| Aspect | Claude Code | Codex CLI | Gemini CLI |
|--------|------------|-----------|------------|
| Modes | default/plan/auto/bypassPermissions | suggest/auto-edit/full-auto | allowlist-based |
| Sandbox | Bash sandboxing | Network-isolated Docker | No sandbox |
| Hooks | PreToolUse/PostToolUse/Stop | None | None |
| **Implication** | Hooks-based enforcement works only in Claude; Codex/Gemini need AGENTS.md rules instead |

## 3. Cross-Review Routing
| Aspect | Claude Code | Codex CLI | Gemini CLI |
|--------|------------|-----------|------------|
| Strength | Plan review, architecture | Implementation review, CLI patterns | Research, alternative approaches |
| Weakness | Can over-engineer | Terse outputs, misses context | Verbose, may diverge from task |
| Best for | Stage 6 plan cross-review lead | Stage 13 implementation review | Stage 4 research/resource-intel |
| **Implication** | Route cross-review roles by provider strength, not round-robin |

## Usage Notes
- All three providers share CLAUDE.md/AGENTS.md/GEMINI.md for instruction alignment
- Correction capture hook only fires in Claude Code sessions (Codex/Gemini corrections not tracked)
- Skill invocation works in Claude/Gemini but not in Codex (uses AGENTS.md sections instead)
