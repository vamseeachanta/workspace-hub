# Module: Project Setup — Claude Code in Action

## Sample Project: uigen

A UI generation app (same as shown in course video). Uses Claude API to generate UI components;
falls back to static fake code if no API key provided.

Downloaded zip: `uigen.zip` → extract to `examples/claude-code-course/uigen/`

## Setup Steps

```bash
# 1. Ensure Node.js installed
node --version

# 2. Extract uigen.zip into examples/claude-code-course/uigen/

# 3. Install deps + set up local SQLite DB
cd examples/claude-code-course/uigen
npm run setup

# 4. (Optional) Set Anthropic API key for real UI generation
#    Get key at https://console.anthropic.com/
#    Add to .env:
#    ANTHROPIC_API_KEY=sk-ant-...

# 5. Start dev server
npm run dev
```

## Notes

- Node.js required (not Python) — check `node --version` on ace-linux-1
- API key optional; app works without it (static fake output)
- `.env` file — never commit; already in .gitignore (standard Node practice)
- Project is self-contained inside `examples/claude-code-course/uigen/`
