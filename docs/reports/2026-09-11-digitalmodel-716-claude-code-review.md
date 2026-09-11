# Digitalmodel716 — Claude code review

Model: haiku; effort low; existing auth; empty setting sources; no session persistence; tools disabled; packet-only prompt.
Verdict: MAJOR
Deadline120s. Exit: 0. Elapsed: 62.77s. Timed out: False.
Private temporary directory removed: True.
Raw stdout SHA256: 81695c947f989fe7b3f3a83f7bce10e9835847a024b1bbdac992329429017d29
Packet: candidate tracked diff, full new helper/test module, full integrating validator.
Private context redacted if present; otherwise exact output.

## Reviewed file hashes

{
  "src/digitalmodel/solvers/orcaflex/yaml_validator.py": "c25c5170ccd61685aeec6a82e2730c98715b9b8ff5e211d32aa831e80fca25be",
  "src/digitalmodel/solvers/orcaflex/yaml_timestep_validation.py": "617dadf1b0872972a37308889a3733ac49c27875b6ca4f41abb0cbd3077d85e6",
  "tests/solvers/orcaflex/test_yaml_validator_timestep.py": "82b72b29578991ce66bee809b1797a9ba56718972d98ead680b2cd8e8d09e190"
}

## Actual stdout

**VERDICT: MAJOR**

---

## Material Defects Found

### 1. **Deduplication Logic Ignores Line Numbers (Line 216–217)**

**Location:** `yaml_validator.py`, `validate_file()` method, final merge loop

**Bug:** The dedup check compares only `property` and `message`:
```python
if not any(i.property == prop and i.message == message for i in result.issues):
```

This silently drops duplicate errors **with identical message text but different line numbers**. The same invalid property on lines 5 and 10 reports only once.

**Reproduction:**
```yaml
General:
  ImplicitVariableMaxTimeStep: 0.125  # Line 3
  StageDuration: 1.0
  ImplicitVariableMaxTimeStep: 0.250  # Line 5 (duplicate key)
```

When YAML allows duplicate keys, `inspect_source()` detects the same issue twice. Result: second occurrence (line 5) is deduplicated and lost.

**Fix:** Include line number in dedup key:
```python
seen = set()
for severity, message, prop, line in source_issues:
    key = (prop, message, line)
    if key not in seen:
        seen.add(key)
        result.add(Severity(severity), message, file=filename, prop=prop, line=line)
```

---

### 2. **Source Issues Lost If YAML Parsing Fails (Line 189–194)**

**Location:** `yaml_validator.py`, exception handler in `validate_file()`

**Bug:** If `yaml.safe_load()` raises, the exception handler returns without reporting `source_issues`:
```python
try:
    source_issues, halt = inspect_source(raw_text, VALID_TOP_LEVEL_SECTIONS, INVALID_PROPERTIES)
    if halt:
        for severity, message, prop, line in source_issues:
            result.add(Severity(severity), message, file=filename, prop=prop, line=line)
        return result
    data = yaml.safe_load(raw_text)
except (yaml.YAMLError, RecursionError) as exc:
    result.add(Severity.ERROR, f"YAML parse error: {exc}", file=filename)
    return result  # <-- source_issues never used here
```

**Reproduction:**
```yaml
General:
  ImplicitVariableMaxTimeStep: 0.125  # Valid property, correct context
  BadYaml: [unclosed
```

`inspect_source()` validates the timestep logic (no issues). But YAML parse error prevents any validation. User sees only "YAML parse error" and misses structural validation already done.

**Fix:** Capture and report source issues even on parse failure:
```python
source_issues, halt = inspect_source(raw_text, VALID_TOP_LEVEL_SECTIONS, INVALID_PROPERTIES)
if halt:
    for severity, message, prop, line in source_issues:
        result.add(Severity(severity), message, file=filename, prop=prop, line=line)
    return result

try:
    data = yaml.safe_load(raw_text)
except (yaml.YAMLError, RecursionError) as exc:
    result.add(Severity.ERROR, f"YAML parse error: {exc}", file=filename)
    # Report non-critical source issues even if parse fails
    for severity, message, prop, line in source_issues:
        if severity != "error":  # Don't duplicate halt-level errors
            result.add(Severity(severity), message, file=filename, prop=prop, line=line)
    return result
```

---

## Secondary Issue

**RecursionError Handler Unclear (Line 191):** Why add `RecursionError` to except clause if `inspect_source()` halts on cyclic aliases (line 38–39 in `yaml_timestep_validation.py`)? If it's reachable, `inspect_source()` is missing cyclic patterns. If unreachable, it's dead code. **Requires clarification or test demonstrating the catch.**

---

## Test Gap
No test in `test_yaml_validator_timestep.py` verifies that duplicate property errors on different lines are both reported. Add:
```python
def test_duplicate_property_different_lines_both_reported(tmp_path):
    # Lines 3 and 5 both define ImplicitVariableMaxTimeStep → two errors
    result = check(tmp_path, "General:\n  X: 1\n  ImplicitVariableMaxTimeStep: 0.125\n  Y: 2\n  ImplicitVariableMaxTimeStep: 0.25\n")
    max_errors = [i for i in result.errors if "ImplicitVariableMaxTimeStep" in i.message]
    assert len(max_errors) == 2, f"Expected 2 errors, got {len(max_errors)}"
```


## Actual stderr
