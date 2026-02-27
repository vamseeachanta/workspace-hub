# Domain Notes: WRK-640

- Claude supports JSON schema validation in print mode.
- Gemini returns a JSON envelope whose `response` field may itself contain fenced JSON.
- Both providers can emit banner/debug lines before the real payload.
- Preserving raw provider output is necessary for debugging transport regressions.
