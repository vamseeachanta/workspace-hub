"""Literal population oracles: docs/examples/algorithm-metric-populations.md.

All identifiers, versions, units and values below cite the synthetic record table
in that document; no expected population is calculated by the example.
"""

from copy import deepcopy
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples/algorithm_runs/metric_population_example.py"
SPEC = importlib.util.spec_from_file_location("metric_population_example", EXAMPLE)
example = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = example
SPEC.loader.exec_module(example)

# Independently enumerated from the documented synthetic record table.
EXPECTED_EXCLUSIONS = {
    "invalid-success": "run_not_eligible",
    "non-reproducible": "run_not_eligible",
    "failed": "run_not_eligible",
    "rejected": "run_not_eligible",
    "invalid-observation": "observation_invalid",
    "null": "observation_missing",
    "not-applicable": "observation_not_applicable",
    "other-version": "definition_version_mismatch",
    "other-units": "units_mismatch",
    "other-metric": "metric_mismatch",
    "other-algorithm": "algorithm_mismatch",
}


def test_only_validated_reproducible_successes_enter_population():
    result = example.select_population(example.RECORDS, example.DEFAULT_KEY)
    assert {row.observation_id for row in result.included} == {"zero", "positive"}
    assert result.excluded == EXPECTED_EXCLUSIONS


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        (example.PopulationKey("alpha", "alpha/extent", "1.0.0", "m"),
         {"zero", "positive"}),
        (example.PopulationKey("alpha", "alpha/extent", "2.0.0", "m"),
         {"other-version"}),
        (example.PopulationKey("alpha", "alpha/extent", "1.0.0", "cm"),
         {"other-units"}),
        (example.PopulationKey("alpha", "alpha/span", "1.0.0", "m"),
         {"other-metric"}),
        (example.PopulationKey("beta", "beta/extent", "1.0.0", "m"),
         {"other-algorithm"}),
    ],
)
def test_definition_version_and_units_partition_populations(key, expected):
    result = example.select_population(example.RECORDS, key)
    assert {row.observation_id for row in result.included} == expected
    assert {row.key for row in result.included} == {key}


def test_null_and_not_applicable_remain_distinct():
    by_id = {row.observation_id: row for row in example.RECORDS}
    assert by_id["null"].quality_state == "missing"
    assert by_id["null"].value is None
    assert by_id["not-applicable"].quality_state == "not_applicable"
    assert by_id["not-applicable"].value == "NA"
    assert by_id["zero"].value == 0
    result = example.select_population(example.RECORDS, example.DEFAULT_KEY)
    assert result.excluded["null"] == "observation_missing"
    assert result.excluded["not-applicable"] == "observation_not_applicable"
    assert {row.observation_id for row in result.included} == {"zero", "positive"}


def test_filter_is_pure_and_exclusions_are_order_independent():
    before = deepcopy(example.RECORDS)
    result = example.select_population(iter(example.RECORDS), example.DEFAULT_KEY)
    reversed_result = example.select_population(reversed(example.RECORDS), example.DEFAULT_KEY)
    assert example.RECORDS == before
    assert reversed_result.excluded == result.excluded
    assert set(reversed_result.included) == set(result.included)
    # Values and pinned keys are retained verbatim, including zero.
    assert {(row.observation_id, row.value) for row in result.included} == {
        ("zero", 0), ("positive", 2),
    }


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"run_status": "unknown"}, "run_not_eligible"),
        ({"quality_state": "unknown"}, "observation_quality_unknown"),
        ({"value": None}, "value_missing"),
        ({"value": "NA"}, "value_not_applicable"),
    ],
)
def test_unknown_or_inconsistent_states_do_not_enter_population(changes, reason):
    # The zero row is the documented valid control; only its named field changes.
    control = next(row for row in example.RECORDS if row.observation_id == "zero")
    result = example.select_population([replace(control, **changes)], example.DEFAULT_KEY)
    assert result.included == ()
    assert result.excluded == {"zero": reason}



@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"run_status": "rejected", "quality_state": "invalid", "value": None},
         "run_not_eligible"),
        ({"quality_state": "invalid", "value": None}, "observation_invalid"),
        ({"value": None}, "value_missing"),
        ({}, "algorithm_mismatch"),
    ],
)
def test_first_exclusion_reason_has_fixed_precedence(changes, reason):
    # Each key field differs from the documented default; the failed run probe
    # also has invalid quality and a null value, so all earlier checks compete.
    control = next(row for row in example.RECORDS if row.observation_id == "zero")
    unlike = example.PopulationKey("beta", "beta/extent", "2.0.0", "cm")
    record = replace(control, key=unlike, **changes)
    result = example.select_population([record], example.DEFAULT_KEY)
    assert result.included == ()
    assert result.excluded == {"zero": reason}


def test_admitted_status_matches_existing_contract():
    contract = yaml.safe_load(
        (ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml").read_text()
    )
    assert contract["metrics"]["eligible_run_statuses"] == [example.ELIGIBLE_RUN_STATUS]


def test_example_runs_offline_from_an_unrelated_directory(tmp_path):
    completed = subprocess.run(
        [sys.executable, "-I", str(EXAMPLE)], cwd=tmp_path,
        check=True, capture_output=True, text=True,
    )
    assert json.loads(completed.stdout) == {
        "population": ["positive", "zero"],
        "excluded": EXPECTED_EXCLUSIONS,
    }
    assert completed.stderr == ""
