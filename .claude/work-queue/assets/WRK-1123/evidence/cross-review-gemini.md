### Verdict: REQUEST_CHANGES

### Summary
The script provides a functional orchestration layer but contains a potential path traversal vulnerability and relies on brittle custom YAML parsing logic.

### Issues Found
- [P1] Critical: [start_stage.py:244] Path traversal vulnerability. The `wrk_id` argument from `sys.argv[1]` is used directly in path construction without validation, which could allow arbitrary file reads/writes.
- [P2] Important: [start_stage.py:35] The fallback `_load_yaml` function's naive parsing (`line.partition(':')`) will break for any values containing colons, such as URLs or timestamps.
- [P2] Important: [start_stage.py:105] The custom checkpoint parser in `_read_checkpoint` is similarly brittle and prone to breaking on standard YAML constructs.
- [P3] Minor: [start_stage.py:60] Broad `except Exception:` block in `_extract_sections` can hide unexpected errors during regex execution.

### Suggestions
- Validate `wrk_id` against a strict regex (e.g., `^WRK-\d+$`) before using it to construct file paths.
- Make `PyYAML` a strict dependency for the project to eliminate the need for error-prone fallback parsing.
- Replace broad `except Exception:` blocks with more specific exception handling (e.g., `re.error`).
- Move inline imports (e.g., `import re`, `import subprocess`) to the top of the file unless lazy loading is strictly necessary for startup performance.

### Questions for Author
- Can we ensure `PyYAML` is available in the target environment to safely remove the custom YAML parsing fallbacks?
- Is there a reason `wrk_id` cannot be strictly validated against a known pattern to prevent directory traversal?
