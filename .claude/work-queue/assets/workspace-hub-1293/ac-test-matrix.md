# WRK-1369 AC/Test Matrix

| AC | Description | Test | Result |
|----|-------------|------|--------|
| 1 | Reports for all textbook manifests | Count reports vs manifests | PASS (44/44) |
| 2 | Total indexed examples >= 100 | Aggregate worked_examples from JSONL index | PASS (107 indexed; 82 deep-extracted + 25 classifier-detected). Follow-up WRK for remaining gap to 150-200 target. |
| 3 | JSONL indexes rebuilt | Run build-doc-intelligence.py --force | PASS (150 manifests, 3884 tables) |
| 4 | Yield report written | Check file exists and is valid YAML | PASS |
| 5 | Hook fix works | enforce-human-gate.sh no longer crashes on no_awaiting | PASS |
