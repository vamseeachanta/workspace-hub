"""Independent scalar-envelope examples for the Demo 6 input contract.

All numerical fixtures are invented arithmetic examples, not measured responses
or standards limits. Each comparison is written out below; no expected result
is obtained from the implementation. Zero denotes absence of demand, not an
engineering allowance. No licensed solver or physical response model is used.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest
from gtm.demo_06_mooring_screening import screen_cases


@pytest.fixture
def case():
    """Assumed arithmetic inputs: tension 120 <= 150 kN; offset 6 <= 8 m.

    The limits and references are synthetic test data, not design criteria.
    """
    return {
        "case_id": "arithmetic-example",
        "response_source": "Synthetic envelope; see this test docstring",
        "max_tension_kn": 120,
        "allowable_tension_kn": 150,
        "tension_limit_source": "Synthetic tension limit for arithmetic only",
        "max_offset_m": 6,
        "allowable_offset_m": 8,
        "offset_limit_source": "Synthetic offset limit for arithmetic only",
    }


def test_independent_comparisons_preserve_evidence_and_inputs(case):
    """Hand comparison: 120 < 150 and 6 < 8, both within supplied limits."""
    before = copy.deepcopy(case)
    record = screen_cases([case])
    result = record["cases"][0]
    assert result["inputs"] == before
    assert case == before
    for name in ("tension", "offset"):
        assert result["checks"][name]["status"] == "WITHIN_SUPPLIED_LIMIT"
    for name in ("fatigue", "dnv_os_e301", "api_rp_2sk"):
        assert result["checks"][name]["status"] == "NOT_EVALUATED"
        assert result["checks"][name]["reason"]
    assert "design approval" in record["limitations"]
    json.dumps(record, allow_nan=False)


@pytest.mark.parametrize(
    ("tension", "offset", "expected"),
    [
        (150, 8, "WITHIN_SUPPLIED_LIMIT"),
        (151, 9, "EXCEEDS_SUPPLIED_LIMIT"),
        (0, 0, "WITHIN_SUPPLIED_LIMIT"),
    ],
)
def test_boundary_exceedance_and_zero_demand(case, tension, offset, expected):
    """Hand comparisons: 150=150, 8=8; 151>150, 9>8; 0<150, 0<8.

    Equality is explicitly included by the supplied-limit contract, with no
    numerical tolerance or engineering safety factor added.
    """
    case.update(max_tension_kn=tension, max_offset_m=offset)
    checks = screen_cases([case])["cases"][0]["checks"]
    assert checks["tension"]["status"] == expected
    assert checks["offset"]["status"] == expected


@pytest.mark.parametrize(
    "missing",
    [
        "response_source",
        "max_tension_kn",
        "allowable_tension_kn",
        "tension_limit_source",
        "max_offset_m",
        "allowable_offset_m",
        "offset_limit_source",
    ],
)
@pytest.mark.parametrize("absent", [None, "omitted"])
def test_missing_evidence_is_not_evaluated(case, missing, absent):
    """Missing response, limit or provenance cannot establish a comparison."""
    if absent is None:
        case[missing] = None
    else:
        del case[missing]
    checks = screen_cases([case])["cases"][0]["checks"]
    affected = (
        ("tension", "offset")
        if missing == "response_source"
        else ("tension" if "tension" in missing else "offset",)
    )
    for name in affected:
        assert checks[name]["status"] == "NOT_EVALUATED"
        assert missing in checks[name]["reason"]


@pytest.mark.parametrize(
    "field",
    [
        "max_tension_kn",
        "allowable_tension_kn",
        "max_offset_m",
        "allowable_offset_m",
    ],
)
@pytest.mark.parametrize(
    "invalid", [-1, float("nan"), float("inf"), float("-inf"), True, "120", [], {}]
)
def test_invalid_numbers_are_rejected(case, field, invalid):
    """Magnitudes must be real, finite and nonnegative; limits positive."""
    case[field] = invalid
    with pytest.raises(ValueError, match=field):
        screen_cases([case])


@pytest.mark.parametrize("field", ["allowable_tension_kn", "allowable_offset_m"])
def test_zero_limits_are_rejected(case, field):
    """A zero allowance cannot define this positive-limit input contract."""
    case[field] = 0
    with pytest.raises(ValueError, match=field):
        screen_cases([case])


@pytest.mark.parametrize(
    "field",
    [
        "response_source",
        "tension_limit_source",
        "offset_limit_source",
    ],
)
@pytest.mark.parametrize("invalid", ["", "  ", 42, []])
def test_malformed_references_are_rejected(case, field, invalid):
    case[field] = invalid
    with pytest.raises(ValueError, match=field):
        screen_cases([case])


@pytest.mark.parametrize(
    "cases", [[], {}, [None], [{"case_id": ""}], [{"case_id": " "}], [{"case_id": 42}]]
)
def test_malformed_cases_are_rejected(cases):
    with pytest.raises((ValueError, TypeError)):
        screen_cases(cases)


def test_missing_checks_and_unknown_fields(case):
    """An identity alone is a valid incomplete case; typos are rejected."""
    result = screen_cases([{"case_id": "incomplete"}])["cases"][0]
    assert all(c["status"] == "NOT_EVALUATED" for c in result["checks"].values())
    case["max_tension_n"] = case.pop("max_tension_kn")
    with pytest.raises(ValueError, match="unknown fields"):
        screen_cases([case])


def test_duplicate_case_identity_is_rejected(case):
    with pytest.raises(ValueError, match="duplicate case_id"):
        screen_cases([case, copy.deepcopy(case)])


def test_cases_are_independent_and_deterministic(case):
    """Second envelope has 151 > 150 kN; the first remains 120 < 150 kN."""
    second = {**case, "case_id": "exceedance", "max_tension_kn": 151}
    first_run = screen_cases([case, second])
    assert first_run == screen_cases([case, second])
    assert [c["checks"]["tension"]["status"] for c in first_run["cases"]] == [
        "WITHIN_SUPPLIED_LIMIT",
        "EXCEEDS_SUPPLIED_LIMIT",
    ]


SCRIPT = Path(__file__).resolve().parents[1] / "demo_06_mooring_screening.py"


def invoke(input_file):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(input_file)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_writes_reproducible_json(case, tmp_path):
    input_file = tmp_path / "envelopes.json"
    input_file.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
    first = invoke(input_file)
    second = invoke(input_file)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert json.loads(first.stdout) == screen_cases([case])
    assert first.stderr == ""


@pytest.mark.parametrize(
    "payload",
    [
        "{",
        "[]",
        "{}",
        '{"cases": []}',
        '{"cases": [], "unknown": true}',
        '{"cases": [], "cases": []}',
        '{"cases": [NaN]}',
    ],
)
def test_cli_rejects_malformed_json_and_contract(payload, tmp_path):
    input_file = tmp_path / "invalid.json"
    input_file.write_text(payload, encoding="utf-8")
    result = invoke(input_file)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_missing_input_does_not_print_local_path(tmp_path):
    result = invoke(tmp_path / "absent.json")
    assert result.returncode != 0
    assert result.stdout == ""
    assert "unable to read input" in result.stderr
    assert str(tmp_path) not in result.stderr
