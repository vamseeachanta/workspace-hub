# Codex Prompt Templates

Prompt templates for OpenAI Codex CLI when a `.claude/skills/` equivalent
is not available or not applicable.

## Purpose

Claude Code has a skills marketplace (`.claude/skills/`). Codex CLI does not
have an equivalent plugin system, so structured prompt templates live here
instead. Each template is a plain Markdown file containing instructions that
can be fed to `codex` via stdin or the `-p` flag.

## Format

Each prompt file should follow this structure:

```markdown
# <Prompt Name>

## Context
One-line description of when to use this prompt.

## Instructions
Step-by-step instructions for the task.

## Output Format
Expected output structure (code, YAML, prose, etc.).
```

## Usage

```bash
# Pipe a prompt template to codex
cat .codex/prompts/<template>.md | codex -p "Apply this to <target>"

# Or reference inline
codex -p "$(cat .codex/prompts/<template>.md) Apply to src/foo.py"
```

## Relationship to Skills

- Canonical skills live in `.claude/skills/` (workspace-hub root).
- `.codex/skills/` symlinks to `.claude/skills/` for shared skill access.
- This `prompts/` directory is for Codex-specific prompt templates that
  have no skills equivalent.
