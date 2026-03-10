# WRK-1092 Plan — Codex Review Input

## Task
Implement mypy error count ratchet for 5 Python repos.

## Files to create
- `config/quality/mypy-baseline.yaml`
- `scripts/quality/check_mypy_ratchet.py`
- `tests/quality/test_check_mypy_ratchet.py`

## Files to modify
- `scripts/quality/check-all.sh` (add `--mypy-ratchet` flag)
- `scripts/hooks/pre-push.sh` (add mypy ratchet step)

## Logic
```
baseline = load yaml
for repo in repos:
    count = run_mypy(repo) -> parse int error count
    if count > baseline[repo]: FAIL
    if count < baseline[repo]: PASS + update baseline
    if count == baseline[repo]: PASS
```

## Tests (TDD — write first)
1. schema validation
2. parse "Found N errors in M files" → N
3. parse "Success: no issues found" → 0
4. ratchet fail
5. ratchet pass + auto-update
6. SKIP_MYPY_REASON bypass
