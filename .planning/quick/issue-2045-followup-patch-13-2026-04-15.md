Another focused #2045 patch wave landed locally after Codex rereview18:

- froze the provider scope to the enumerated set at plan approval time
- split repo-content completion from execution-time/live-GitHub validation more explicitly
- tightened the review-freshness gate so it keys off explicit inclusion in the authoritative artifact set rather than dates alone
- clarified Gemini as validation-only by default and Codex config as validation-only unless contradiction is found

Launching another focused Codex rerun now.
