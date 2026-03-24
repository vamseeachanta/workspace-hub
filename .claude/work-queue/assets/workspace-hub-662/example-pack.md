# Example Pack: WRK-640

1. Claude trivial prompt from repo root times out.
2. Claude trivial prompt from isolated temp directory returns immediately.
3. Claude JSON-schema output contains `structured_output` and can be rendered to markdown.
4. Gemini repo-root prompt times out or drifts.
5. Gemini isolated temp-directory prompt returns a JSON envelope with a `response` string.
6. Gemini `response` string may wrap the review JSON in fenced code blocks.
