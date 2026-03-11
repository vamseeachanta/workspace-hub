### Verdict: APPROVE

### Summary
Simple, well-scoped 4-line bash guard that correctly filters periodic-review items from the whats-next list. Logic is sound, variable handling follows correct bash patterns (separate local declaration avoids exit-code suppression), and the two enumerated cases (WRK-235 excluded, WRK-234 retained) are handled as intended. The only concern is the absence of automated regression tests.

### Issues Found
- [P3] Minor: scripts/work-queue/whats-next.sh — No automated test added. The claim 'No regressions possible' overstates safety; a future change to get_field semantics or the YAML field names could silently break this guard without a test to catch it.
- [P3] Minor: scripts/work-queue/whats-next.sh — The behavior of get_field when the 'standing' or 'cadence' key is entirely absent from a file is not documented or verified beyond the two named WRK items. If get_field returns a non-empty default on missing keys, the guard could incorrectly exclude items.

### Suggestions
- Add at least one automated test (e.g., a fixture YAML with standing: true + cadence: monthly and assert it does not appear in whats-next output, and a counterpart with standing: true and no cadence that does appear). This would make the 'no regressions' claim verifiable.
- Add a brief inline comment or a reference to the test covering the get_field-missing-key behavior to document the assumed contract (empty string on missing key).

### Questions for Author
- What does get_field return when a key is completely absent from the YAML file — empty string, a literal 'null', or something else? The guard's correctness for non-periodic items depends on -n returning false for a missing cadence field.
- Are there any WRK items with cadence set but standing != true (or standing absent)? The guard is safe for that case (both conditions must be true), but worth confirming no existing items have an unexpected field combination that could be affected.
