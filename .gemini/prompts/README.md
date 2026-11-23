# Gemini Prompt Templates

Prompt templates for Google Gemini CLI when a `.claude/skills/` equivalent
is not available or not applicable.

## Purpose

Claude Code has a skills marketplace (`.claude/skills/`). Gemini CLI does not
have an equivalent plugin system, so structured prompt templates live here
instead. Each template is a plain Markdown file containing instructions that
can be piped to `gemini` via the `-p` flag.

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
# Pipe a prompt template to gemini
cat .gemini/prompts/<template>.md | gemini -p "Apply this to <target>" -y

# Or reference inline
echo "$(cat .gemini/prompts/<template>.md) Apply to src/foo.py" | gemini -y
```

## Relationship to Skills

- Canonical skills live in `.claude/skills/` (workspace-hub root).
- `.gemini/skills/` symlinks to `.claude/skills/` for shared skill access.
- This `prompts/` directory is for Gemini-specific prompt templates that
  have no skills equivalent.
