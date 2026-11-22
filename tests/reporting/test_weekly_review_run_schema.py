"""Contract examples from docs/examples/weekly-review-run-format.md.

Literal versions, dates, counts and boundary values below are synthetic test
vectors defined in that document; they are not operational measurements.
"""

import copy
import json
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft7Validator, FormatChecker
from jsonschema.validators import validator_for
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "config/reporting/weekly-review-run.schema.json"
DOCUMENT = ROOT / "docs/examples/weekly-review-run-format.md"
DIALECT = "http://json-schema.org/draft-07/schema#"

# Independent literal oracle, matching the documentation's minimal JSON block.
MINIMAL = {
    "schema_version": "1.0.0",
    "metadata": {
        "run_id": "synthetic-weekly-review",
        "period_start": "2026-10-12T00:00:00Z",
        "period_end": "2026-10-19T00:00:00Z",
        "generated_at": "2026-10-19T00:00:00Z",
        "provenance": {
            "source_ref": "synthetic:review-input",
            "source_revision": "synthetic-revision",
            "producer": "synthetic-fixture",
        },
    },
    "readiness": {"status": "unknown"},
    "settings_routing": {
        "status": "unknown",
        "baseline_ref": "synthetic:settings-baseline",
    },
    "freshness": {"status": "unknown", "criteria_ref": "synthetic:freshness-policy"},
    "accessibility": {"status": "unknown"},
    "findings": [],
}

FINDING = {
    "id": "finding-alpha",
    "category": "accessibility",
    "severity": "warning",
    "summary": "Synthetic reference is unavailable.",
    "recommendation": "Inspect the synthetic reference.",
    "evidence_refs": ["synthetic:access-observation"],
}
FOLLOW_ON = {
    "finding_id": "finding-alpha",
    "kind": "issue",
    "ref": "synthetic:follow-on-issue",
}

# This literal domain table is the documentation's enum contract, not schema data.
ENUMS = [
    (("readiness", "status"), ("ready", "degraded", "blocked", "unknown")),
    (("settings_routing", "status"), ("consistent", "drifted", "unknown")),
    (("freshness", "status"), ("current", "stale", "unknown")),
    (("accessibility", "status"), ("accessible", "partial", "inaccessible", "unknown")),
    (("findings", 0, "category"),
     ("readiness", "settings_routing", "freshness", "accessibility")),
    (("findings", 0, "severity"), ("info", "warning", "critical")),
    (("follow_on_refs", 0, "kind"), ("issue", "artifact")),
]
REQUIRED = [
    ((), ("schema_version", "metadata", "readiness", "settings_routing", "freshness",
          "accessibility", "findings")),
    (("metadata",), ("run_id", "period_start", "period_end", "generated_at", "provenance")),
    (("metadata", "provenance"), ("source_ref", "source_revision", "producer")),
    (("readiness",), ("status",)),
    (("settings_routing",), ("status", "baseline_ref")),
    (("freshness",), ("status", "criteria_ref")),
    (("accessibility",), ("status",)),
    (("findings", 0), ("id", "category", "severity", "summary")),
    (("follow_on_refs", 0), ("finding_id", "kind", "ref")),
]
TEXT_PATHS = [
    ("metadata", "run_id"), ("metadata", "provenance", "source_ref"),
    ("metadata", "provenance", "source_revision"),
    ("metadata", "provenance", "producer"),
    ("settings_routing", "baseline_ref"), ("freshness", "criteria_ref"),
    ("findings", 0, "id"), ("findings", 0, "summary"),
    ("findings", 0, "recommendation"), ("follow_on_refs", 0, "finding_id"),
    ("follow_on_refs", 0, "ref"),
]
EVIDENCE_PATHS = [(section, "evidence_refs") for section in (
    "readiness", "settings_routing", "freshness", "accessibility"
)] + [("findings", 0, "evidence_refs")]
TIME_PATHS = [("metadata", field) for field in (
    "period_start", "period_end", "generated_at"
)]


@pytest.fixture
def validator():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["$schema"] == DIALECT
    cls = validator_for(schema)
    assert cls is Draft7Validator
    cls.check_schema(schema)
    checker = FormatChecker()
    assert "date-time" in checker.checkers, "Install jsonschema date-time format support"
    return cls(schema, format_checker=checker)


def complete():
    value = copy.deepcopy(MINIMAL)
    value["findings"] = [copy.deepcopy(FINDING)]
    value["follow_on_refs"] = [copy.deepcopy(FOLLOW_ON)]
    value["readiness"]["status"] = "degraded"
    value["settings_routing"]["status"] = "drifted"
    value["freshness"]["status"] = "stale"
    value["accessibility"]["status"] = "partial"
    for path in EVIDENCE_PATHS:
        at(value, path[:-1])[path[-1]] = ["synthetic:evidence"]
    return value


def at(value, path):
    for key in path:
        value = value[key]
    return value


def replaced(path, replacement):
    value = complete()
    at(value, path[:-1])[path[-1]] = replacement
    return value


def test_minimal_weekly_run_is_valid(validator):
    validator.validate(MINIMAL)


@pytest.mark.parametrize("path,fields", REQUIRED)
def test_required_sections_and_enums_reject_invalid_inputs(validator, path, fields):
    for field in fields:
        value = complete()
        del at(value, path)[field]
        errors = list(validator.iter_errors(value))
        assert any(error.validator == "required" and tuple(error.path) == path
                   for error in errors), (path, field)
    for enum_path, _ in ENUMS:
        errors = list(validator.iter_errors(replaced(enum_path, "unsupported")))
        assert any(error.validator == "enum" and tuple(error.path) == enum_path
                   for error in errors), enum_path


@pytest.mark.parametrize("path,values", ENUMS)
def test_all_documented_enum_members_are_valid(validator, path, values):
    for value in values:
        validator.validate(replaced(path, value))
    for value in (None, False, 0, [], {}):
        assert not validator.is_valid(replaced(path, value))


@pytest.mark.parametrize("version", ["2.0.0", "1.0.1", "1.0", 1, None])
def test_version_mismatch_is_rejected(validator, version):
    assert not validator.is_valid(replaced(("schema_version",), version))


def test_optional_section_omission_is_valid(validator):
    value = complete()
    del value["follow_on_refs"]
    validator.validate(value)
    validator.validate(MINIMAL)
    value = complete()
    del value["findings"][0]["recommendation"]
    validator.validate(value)


@pytest.mark.parametrize("path,_fields", REQUIRED)
def test_objects_are_typed_and_closed(validator, path, _fields):
    for invalid in (None, [], "invalid", True, 0):
        value = replaced(path, invalid) if path else invalid
        assert not validator.is_valid(value), path
    value = complete()
    at(value, path)["undeclared"] = "synthetic"
    assert not validator.is_valid(value), path


@pytest.mark.parametrize("path", TEXT_PATHS)
@pytest.mark.parametrize("invalid", ["", " \t\n", None, False, 0, [], {}])
def test_text_requires_nonblank_strings(validator, path, invalid):
    assert not validator.is_valid(replaced(path, invalid))


@pytest.mark.parametrize("path", TIME_PATHS)
@pytest.mark.parametrize("invalid", [
    "", "2026-02-30T00:00:00Z", "2026-10-19", "2026-10-19T25:00:00Z",
    "2026-10-19T00:00:00", None, 0, False, [], {},
])
def test_timestamps_require_rfc3339_instants(validator, path, invalid):
    assert not validator.is_valid(replaced(path, invalid))


@pytest.mark.parametrize("path", TIME_PATHS)
def test_fractional_seconds_and_offsets_are_valid(validator, path):
    validator.validate(replaced(path, "2026-10-19T01:00:00.123+01:00"))


@pytest.mark.parametrize("path", EVIDENCE_PATHS)
def test_evidence_lists_are_optional_unique_text_arrays(validator, path):
    value = complete()
    del at(value, path[:-1])[path[-1]]
    validator.validate(value)
    validator.validate(replaced(path, []))
    for invalid in (None, "synthetic:evidence", {}, [""], [" "], [None], [0],
                    [False], [[]], [{}], ["synthetic:ref", "synthetic:ref"]):
        assert not validator.is_valid(replaced(path, invalid)), path


@pytest.mark.parametrize("path", [("findings",), ("follow_on_refs",)])
def test_record_arrays_reject_wrong_types_and_duplicate_records(validator, path):
    validator.validate(replaced(path, []))
    for invalid in (None, {}, "invalid", 0, [None], [False], [0], ["invalid"], [[]]):
        assert not validator.is_valid(replaced(path, invalid))
    record = FINDING if path == ("findings",) else FOLLOW_ON
    assert not validator.is_valid(replaced(path, [record, record]))


def test_documented_examples_match_literal_oracles(validator):
    blocks = re.findall(r"```json\n(.*?)\n```", DOCUMENT.read_text(encoding="utf-8"), re.S)
    minimal, degraded, invalid_version, invalid_status = map(json.loads, blocks)
    assert minimal == MINIMAL
    assert degraded == complete()
    validator.validate(minimal)
    validator.validate(degraded)
    assert invalid_version == dict(MINIMAL, schema_version="2.0.0")
    assert invalid_status == dict(MINIMAL, readiness={"status": "unsupported"})
    assert not validator.is_valid(invalid_version)
    assert not validator.is_valid(invalid_status)


def test_documentation_command_validates_offline():
    text = DOCUMENT.read_text(encoding="utf-8")
    command = re.search(r"```bash\n.*?python - <<'PY'\n(.*?)\nPY\n```", text, re.S)
    assert command is not None
    result = subprocess.run([sys.executable, "-c", command.group(1)], cwd=ROOT,
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Synthetic examples: valid and invalid cases verified."
