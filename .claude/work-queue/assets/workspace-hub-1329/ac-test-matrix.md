# WRK-5139 AC Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| AC-1 | Empty stdout detection with exit 0 | classify_stderr + raw_size check in retry loop | PASS — code added, syntax verified |
| AC-2 | STDERR inspection for known errors | classify_stderr() handles CAPACITY_EXHAUSTED, AUTH_FAILURE, NETWORK_FAILURE | PASS — grep patterns match known Gemini errors |
| AC-3 | Valid output still works (no regression) | 45/45 existing tests + E2E with real Gemini CLI | PASS |
| AC-4 | Fallback when genuinely unavailable | Existing NO_OUTPUT classification in validate-review-output.sh unchanged | PASS |
