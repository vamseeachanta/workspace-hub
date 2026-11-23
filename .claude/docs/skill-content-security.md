# Skill Content Security Scanning

## Overview
Skills loaded into agent system prompts are a prompt injection attack surface.
The `check-skill-content.sh` scanner detects threats before they enter the context
window, operating at two enforcement points:

1. **Pre-commit hook** (git) — blocks committing malicious skill files
2. **PreToolUse hook** (Claude Code) — warns when reading skill files with threats

## Threat Categories (120 patterns)
| Category | Count | Severity Range |
|---|---|---|
| Exfiltration | 22 | critical-high |
| Prompt injection | 19 | critical-medium |
| Destructive operations | 8 | critical-medium |
| Persistence | 12 | critical-medium |
| Network (reverse shells) | 9 | critical-medium |
| Obfuscation | 13 | critical-medium |
| Process execution | 6 | high-medium |
| Supply chain | 9 | critical-medium |
| Privilege escalation | 5 | critical-high |
| Credential exposure | 6 | critical |
| Path traversal | 5 | critical-medium |
| Crypto mining | 2 | critical-medium |
| Invisible unicode | 1 | high |

## Enforcement Points

### Pre-commit (blocks commit)
Already wired in `.git/hooks/pre-commit`. Scans staged files under `.claude/skills/`.
Critical and high findings block the commit (exit 1).

### Claude Code PreToolUse (advisory warning)
Wired in `.claude/settings.json` under `hooks.PreToolUse` for the `Read` tool.
When Claude reads a `.claude/skills/*.md` file, the scanner runs and emits a
warning if threats are found. Advisory only (does not block Read) to avoid
false-positive deadlocks.

### Manual / CLI
```bash
bash .claude/hooks/check-skill-content.sh --scan-file path/to/skill.md
```

## Source
Patterns ported from Hermes Agent's `~/.hermes/hermes-agent/tools/skills_guard.py`
and `agent/prompt_builder.py` `_CONTEXT_THREAT_PATTERNS`.

## Files
- `.claude/hooks/check-skill-content.sh` — scanner (pre-commit + CLI)
- `.claude/hooks/skill-content-pretooluse.sh` — PreToolUse hook wrapper
- `.claude/settings.json` — hook wiring
- `.git/hooks/pre-commit` — git hook entry point
