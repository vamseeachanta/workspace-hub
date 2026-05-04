---
name: mcp-builder-do
description: 'Sub-skill of mcp-builder: Do (+1).'
version: 1.2.0
category: development
type: reference
scripts_exempt: true
---

# Do (+1)

## Do


1. Use TypeScript for type safety
2. Validate all inputs with Zod
3. Provide clear, actionable error messages
4. Use environment variables for secrets
5. Implement rate limiting for external APIs
6. Add tool annotations for destructive operations


## Don't


1. Hardcode API keys or secrets
2. Skip input validation
3. Return raw error stack traces
4. Create overly complex tool schemas
5. Ignore rate limits on external services
