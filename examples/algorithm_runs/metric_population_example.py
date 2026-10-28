"""Offline record filtering, not numerical qualification or a production gate.

Fixture basis (including all numeric literals and version identifiers):
    docs/examples/algorithm-metric-populations.md, Synthetic record table.
Eligibility basis:
    docs/architecture/algorithm-run-dataset-contract.yaml, metrics.

Inputs are a synthetic, denormalized projection with previously resolved run and
metric-definition bindings. This example does not validate those bindings or
claim that a recorded status proves validation or reproducibility.
"""

from collections.abc import Iterable
from dataclasses import dataclass
import json


ELIGIBLE_RUN_STATUS = "succeeded_validated_reproducible"


@dataclass(frozen=True)
class PopulationKey:
    algorithm_id: str
    metric_id: str
    definition_version: str
    units: str


@dataclass(frozen=True)
class Observation:
    observation_id: str
    run_id: str
    key: PopulationKey
    run_status: str
    quality_state: str
    value: int | str | None


@dataclass(frozen=True)
class Selection:
    included: tuple[Observation, ...]
    excluded: dict[str, str]


def exclusion_reason(record: Observation, key: PopulationKey) -> str | None:
    """Return the first reason in a fixed precedence, without changing a record."""
    if record.run_status != ELIGIBLE_RUN_STATUS:
        return "run_not_eligible"
    if record.quality_state != "valid":
        return {
            "invalid": "observation_invalid",
            "missing": "observation_missing",
            "not_applicable": "observation_not_applicable",
        }.get(record.quality_state, "observation_quality_unknown")
    if record.value is None:
        return "value_missing"
    if record.value == "NA":
        return "value_not_applicable"
    for field, reason in (
        ("algorithm_id", "algorithm_mismatch"),
        ("metric_id", "metric_mismatch"),
        ("definition_version", "definition_version_mismatch"),
        ("units", "units_mismatch"),
    ):
        if getattr(record.key, field) != getattr(key, field):
            return reason
    return None


def select_population(records: Iterable[Observation], key: PopulationKey) -> Selection:
    """Filter one exact key; identifiers must be unique in this prepared input.

    No unit conversion, version substitution, aggregation or qualification occurs.
    Every excluded observation retains a stable reason; included objects are
    returned verbatim. Unknown run and quality statuses are excluded.
    """
    included = []
    excluded = {}
    for record in records:
        reason = exclusion_reason(record, key)
        if reason is None:
            included.append(record)
        else:
            excluded[record.observation_id] = reason
    return Selection(tuple(included), excluded)


# Synthetic record table in docs/examples/algorithm-metric-populations.md is the
# authored source for these identifiers, values, units and version constants.
DEFAULT_KEY = PopulationKey("alpha", "alpha/extent", "1.0.0", "m")
RECORDS = (
    Observation("zero", "run-zero", DEFAULT_KEY, ELIGIBLE_RUN_STATUS, "valid", 0),
    Observation("positive", "run-positive", DEFAULT_KEY, ELIGIBLE_RUN_STATUS, "valid", 2),
    Observation("invalid-success", "run-invalid-success", DEFAULT_KEY,
                "succeeded_invalid", "valid", 2),
    Observation("non-reproducible", "run-non-reproducible", DEFAULT_KEY,
                "succeeded_non_reproducible", "valid", 2),
    Observation("failed", "run-failed", DEFAULT_KEY,
                "failed_reproducible", "valid", 2),
    Observation("rejected", "run-rejected", DEFAULT_KEY, "rejected", "valid", 2),
    Observation("invalid-observation", "run-invalid-observation", DEFAULT_KEY,
                ELIGIBLE_RUN_STATUS, "invalid", 2),
    Observation("null", "run-null", DEFAULT_KEY, ELIGIBLE_RUN_STATUS, "missing", None),
    Observation("not-applicable", "run-not-applicable", DEFAULT_KEY,
                ELIGIBLE_RUN_STATUS, "not_applicable", "NA"),
    Observation("other-version", "run-other-version",
                PopulationKey("alpha", "alpha/extent", "2.0.0", "m"),
                ELIGIBLE_RUN_STATUS, "valid", 2),
    Observation("other-units", "run-other-units",
                PopulationKey("alpha", "alpha/extent", "1.0.0", "cm"),
                ELIGIBLE_RUN_STATUS, "valid", 2),
    Observation("other-metric", "run-other-metric",
                PopulationKey("alpha", "alpha/span", "1.0.0", "m"),
                ELIGIBLE_RUN_STATUS, "valid", 2),
    Observation("other-algorithm", "run-other-algorithm",
                PopulationKey("beta", "beta/extent", "1.0.0", "m"),
                ELIGIBLE_RUN_STATUS, "valid", 2),
)


def main() -> None:
    result = select_population(RECORDS, DEFAULT_KEY)
    print(json.dumps({
        "population": sorted(row.observation_id for row in result.included),
        "excluded": result.excluded,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
