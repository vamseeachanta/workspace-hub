# WRK-1086 AC Test Matrix

| AC | Test | Result |
|----|------|--------|
| new-module.sh assetutilities creates 4 artefacts | Case 1: `bash tests/test_new_module.sh` | PASS |
| Generated test file has 1 failing test (TDD-RED) | All 5 cases assert `pytest.fail` / NotImplementedError marker | PASS |
| `--domain` flag pre-fills stubs | Cases 2-4 grep for domain string in module.py | PASS |
| All 5 repos supported, correct src/ path | Cases 1-5 cover all repos | PASS |
| Generated code passes ruff | ruff check on assetutilities output | PASS |
| Cross-review passes | Route A single-pass Claude APPROVE | PASS |

Total: 6/6 PASS, 0 FAIL
