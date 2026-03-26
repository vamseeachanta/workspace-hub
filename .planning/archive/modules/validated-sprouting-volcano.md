# WRK-1156: Commissioning Validator — FAT/SAT/IST Test Sequence Generator

## Context

WRK-1156 is a child of feature WRK-1048, building the commissioning module under
`digitalmodel/src/digitalmodel/power/commissioning/`. The `power/` module does not
exist yet. WRK-1154 (sibling blocker) is archived. This module demonstrates
testability design and system verification methodology for FAT/SAT/IST phases.

## Files to Create

| File | Purpose |
|------|---------|
| `digitalmodel/src/digitalmodel/power/__init__.py` | Power package init |
| `digitalmodel/src/digitalmodel/power/commissioning/__init__.py` | Re-export public API with `__all__` |
| `digitalmodel/src/digitalmodel/power/commissioning/test_sequence_validator.py` | Core implementation |
| `digitalmodel/tests/power/__init__.py` | Test package init |
| `digitalmodel/tests/power/commissioning/__init__.py` | Test package init |
| `digitalmodel/tests/power/commissioning/test_commissioning_doc_verified.py` | All tests |

## Design

### Data Models (in `test_sequence_validator.py`)

```python
class CommissioningPhase(str, Enum):
    FAT = "fat"   # Factory Acceptance Test
    SAT = "sat"   # Site Acceptance Test
    IST = "ist"   # Integrated Systems Test

@dataclass
class TestStep:
    step_id: str
    phase: CommissioningPhase
    description: str
    preconditions: list[str]
    action: str
    acceptance_criteria: str
    dependencies: list[str]  # step_ids that must pass first

@dataclass
class TestResult:
    step_id: str
    status: str  # "pass" | "fail" | "not_run"
    actual_value: str
    notes: str
    timestamp: str

@dataclass
class PunchItem:
    step_id: str
    description: str
    phase: CommissioningPhase
    severity: str  # "critical" | "major" | "minor"
    action_required: str
```

### CommissioningSequenceGenerator

```python
class CommissioningSequenceGenerator:
    def __init__(self, system_config: dict):
        """system_config keys: system_name, subsystems, voltage_kv, phases"""

    def generate_sequence(self, phase: CommissioningPhase) -> list[TestStep]: ...
    def generate_all_phases(self) -> dict[CommissioningPhase, list[TestStep]]: ...
    def validate_dependencies(self, steps: list[TestStep]) -> list[str]: ...  # errors
```

Phase-specific step templates:
- **FAT**: insulation_resistance, hi_pot, relay_settings, breaker_trip, control_logic
- **SAT**: cable_megger, grounding_continuity, phase_rotation, protection_coordination, functional_interlock
- **IST**: load_test, failover, scada_integration, emergency_shutdown, performance_verification

### TestResultsValidator

```python
class TestResultsValidator:
    def __init__(self, sequence: list[TestStep]):
        """Initialize with expected sequence."""

    def load_results_csv(self, filepath: str) -> list[TestResult]: ...
    def validate(self, results: list[TestResult]) -> dict: ...
        # returns {passed: int, failed: int, not_run: int, errors: [...]}
    def generate_punch_list(self, results: list[TestResult]) -> list[PunchItem]: ...
    def export_punch_list_csv(self, punch_items: list[PunchItem], filepath: str) -> None: ...
    def export_punch_list_markdown(self, punch_items: list[PunchItem]) -> str: ...
```

## Test Plan (TDD — tests first)

| # | What | Type | Expected |
|---|------|------|----------|
| 1 | CommissioningPhase enum has 3 members | happy | FAT, SAT, IST |
| 2 | TestStep dataclass fields | happy | All 7 fields accessible |
| 3 | TestStep with empty dependencies | edge | dependencies=[] valid |
| 4 | Invalid phase string raises | error | ValueError |
| 5 | PunchItem severity validation | edge | Only critical/major/minor |
| 6 | generate_sequence(FAT) returns ≥5 steps | happy | Steps with correct phase |
| 7 | generate_sequence(SAT) returns ≥5 steps | happy | Steps with SAT phase |
| 8 | generate_sequence(IST) returns ≥5 steps | happy | Steps with IST phase |
| 9 | generate_all_phases returns 3 keys | happy | All phases present |
| 10 | Step IDs are unique within phase | happy | No duplicates |
| 11 | Dependencies reference valid step_ids | happy | No dangling refs |
| 12 | validate_dependencies catches bad ref | error | Returns error list |
| 13 | Empty system_config → minimal steps | edge | At least 1 step per phase |
| 14 | Custom subsystems add extra steps | happy | More steps than default |
| 15 | Steps are ordered respecting deps | happy | Dep appears before dependent |
| 16 | load_results_csv parses valid CSV | happy | Correct TestResult list |
| 17 | load_results_csv empty file | edge | Empty list |
| 18 | load_results_csv missing columns | error | ValueError |
| 19 | validate all pass | happy | passed=N, failed=0 |
| 20 | validate with failures | happy | failed count correct |
| 21 | validate unknown step_id | error | Error in result |
| 22 | generate_punch_list from failures | happy | PunchItem per failure |
| 23 | Punch list empty when all pass | edge | Empty list |
| 24 | export_punch_list_csv writes file | happy | Valid CSV output |
| 25 | export_punch_list_markdown format | happy | Markdown table string |
| 26 | export_punch_list_csv empty list | edge | Header-only CSV |

26 tests total: ≥5 data models, ≥10 generator, ≥8 validator, ≥3 export.

## Execution Sequence

1. Create package structure (`__init__.py` files)
2. Write all tests (RED)
3. Implement data models → tests pass (GREEN)
4. Implement CommissioningSequenceGenerator → tests pass
5. Implement TestResultsValidator → tests pass
6. Implement punch list export → tests pass
7. Wire `__init__.py` re-exports

## Verification

```bash
cd /mnt/local-analysis/workspace-hub/digitalmodel
PYTHONPATH=src uv run python -m pytest tests/power/commissioning/ -v
python -c "from digitalmodel.power.commissioning import CommissioningPhase, CommissioningSequenceGenerator, TestResultsValidator"
```
