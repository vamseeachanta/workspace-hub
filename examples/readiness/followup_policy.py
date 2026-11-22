"""Pure draft proposal example; see docs/examples/readiness-followup-policy.md.

The literal fixture table is illustrative, not approved readiness policy.
No network, persistence, model execution or publication is implemented.
"""

from collections.abc import Iterable, Mapping
import json


# Ordered labels and literal inputs: documentation sections "Fixture policy"
# and "Fixture gaps". They are not normative readiness thresholds.
SEVERITIES = ("low", "medium", "high", "critical")
FIXTURE_POLICY = {"context-budget": "high", "truncation-safety": "medium"}
FIXTURE_GAP = {
    "repository": "example-repository",
    "release": "example-release",
    "dimension": "context-budget",
    "surface": "adapter-guide",
    "gap_id": "missing-budget",
    "severity": "medium",
    "summary": "Read budget is absent",
    "evidence": "fixture:missing-budget",
    "responsible_role": "documentation-maintainer",
    "accountable_role": "release-maintainer",
    "action": "Document the intended read budget",
    "acceptance": "The guide states its intended read budget",
}
IDENTITY_FIELDS = ("repository", "release", "dimension", "surface", "gap_id")
TEXT_FIELDS = (
    *IDENTITY_FIELDS, "severity", "summary", "evidence", "responsible_role",
    "accountable_role", "action", "acceptance",
)


def _text(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or any(character in value for character in ("\n", "\r"))
    ):
        raise ValueError(f"{field} requires nonempty, trimmed, single-line text")
    return value


def _validate_gap(gap: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(gap, Mapping):
        raise ValueError("gap requires a mapping")
    missing = set(TEXT_FIELDS) - gap.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if gap.keys() - set(TEXT_FIELDS):
        raise ValueError("unknown gap fields")
    result = {field: _text(gap[field], field) for field in TEXT_FIELDS}
    if result["severity"] not in SEVERITIES:
        raise ValueError("unknown severity")
    return result


def _render(gap: Mapping[str, str], policy: Mapping[str, str]) -> dict:
    gap = _validate_gap(gap)
    if gap["dimension"] not in policy:
        raise ValueError("policy has no threshold for dimension")
    key = json.dumps(
        ["readiness-followup", *(gap[field] for field in IDENTITY_FIELDS)],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return {
        "duplicate_key": key,
        "status": "draft",
        "threshold_met": (
            SEVERITIES.index(gap["severity"]) >= SEVERITIES.index(policy[gap["dimension"]])
        ),
        "title": f"Readiness follow-up: {gap['summary']}",
        "body": "\n".join(
            f"{label}: {gap[field]}"
            for label, field in (
                ("Dimension", "dimension"),
                ("Surface", "surface"),
                ("Evidence", "evidence"),
                ("Responsible role", "responsible_role"),
                ("Accountable role", "accountable_role"),
                ("Action", "action"),
                ("Acceptance", "acceptance"),
            )
        ),
        "gap": gap,
    }


def propose(
    gaps: Iterable[Mapping[str, str]],
    policy: Mapping[str, str],
    existing: Iterable[Mapping],
) -> list[dict]:
    """Return sorted new drafts without modifying inputs or publishing anything.

    Policy is always explicit. Identical existing drafts suppress output.
    Changed content under an existing identity is rejected, never updated.
    All validation completes before any result is returned.
    """
    if not isinstance(policy, Mapping):
        raise ValueError("policy requires a mapping")
    for dimension, threshold in policy.items():
        _text(dimension, "policy dimension")
        if threshold not in SEVERITIES:
            raise ValueError("policy requires a known severity threshold")

    known = {}
    for draft in existing:
        if not isinstance(draft, Mapping) or "gap" not in draft:
            raise ValueError("existing proposal requires gap metadata")
        expected = _render(draft["gap"], policy)
        if not isinstance(draft.get("threshold_met"), bool) or draft != expected:
            raise ValueError("existing proposal does not match its draft metadata")
        key = expected["duplicate_key"]
        if key in known and known[key] != expected:
            raise ValueError("conflicting existing proposals")
        known[key] = expected

    pending = {}
    for gap in gaps:
        draft = _render(gap, policy)
        key = draft["duplicate_key"]
        previous = known.get(key, pending.get(key))
        if previous is not None and previous != draft:
            raise ValueError("conflicting proposals for duplicate key")
        if key not in known:
            pending[key] = draft
    return [pending[key] for key in sorted(pending)]


def main() -> None:
    """Print the documentation's fixture drafts as deterministic JSON."""
    fixture_gaps = [
        FIXTURE_GAP,
        dict(FIXTURE_GAP),
        {**FIXTURE_GAP, "gap_id": "missing-budget-note", "severity": "high"},
    ]
    print(json.dumps(propose(fixture_gaps, FIXTURE_POLICY, []), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
