Provider status note for the current #2045 review-refresh wave:

- Gemini current-text rerun was attempted again but hit repeated `429 MODEL_CAPACITY_EXHAUSTED` capacity failures.
- Claude current-text rerun was attempted in print mode but did not produce a usable artifact before hanging, so that lane remains unreliable right now.
- Codex remains the reliable iterative rereview lane and continues to narrow the blocker set.

I am treating Gemini/Claude current-text reruns as opportunistic lanes and not waiting indefinitely on them.
