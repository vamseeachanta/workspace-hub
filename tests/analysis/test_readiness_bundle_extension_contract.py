"""Additive checks under the current readiness contract, without live probes.

Basis: docs/modules/ai/readiness-evidence-bundle.schema.yaml, checks.items and
checks.allOf; docs/modules/ai/readiness-evidence-validation.html, Method and
acceptance criteria and Worked example: synthetic inputs. Generic evidence is
an object without a canonical payload contract; it cannot replace required checks.
"""

from __future__ import annotations

import copy
from html import unescape
from pathlib import Path

import pytest
import yaml

from analysis.readiness_bundle_schema import validate_bundle

# This module is under tests/analysis, two directories below the repository root.
REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_IDS = ("access-mode", "workspace-root", "ai-cli", "licensed-tools")


def _fixture_counts(checks: list[dict]) -> dict[str, int]:
    """Enumerate fixture rows independently of the validator's counting helper."""
    return {
        "total": len(checks),
        **{
            status: sum(check["status"] == status for check in checks)
            for status in ("pass", "warn", "fail", "error", "skip")
        },
    }


@pytest.fixture
def extension_bundle() -> dict:
    """Extend the documented synthetic example; retain its canonical payloads."""
    document = (
        REPO_ROOT / "docs/modules/ai/readiness-evidence-validation.html"
    ).read_text(encoding="utf-8")
    _, _, example = document.partition('<pre id="worked-example">')
    example, _, _ = example.partition("</pre>")
    bundle = yaml.safe_load(unescape(example))
    bundle["checks"].append(
        {
            "id": "synthetic-extension",
            "name": "Synthetic extension",
            "status": "warn",
            "summary": "Additional synthetic evidence requires attention",
            "evidence": {"detail": {"observed": False, "tags": ["synthetic"]}},
        }
    )
    bundle["overall"]["verdict"] = "degraded"
    bundle["overall"]["summary"] = "Synthetic extension contains a warning"
    # Hand calculation from the documented rows plus the added warning:
    # access + workspace + command = 1 + 1 + 1 = 3 passes; tools = 1 skip;
    # extension = 1 warning; total = 3 + 1 + 1 = 5; all other outcomes = 0.
    bundle["overall"]["counts"] = {
        "total": 5, "pass": 3, "warn": 1, "fail": 0, "error": 0, "skip": 1
    }
    return bundle


@pytest.mark.parametrize("canonical_id", CANONICAL_IDS)
def test_generic_extension_preserves_required_canonical_checks(
    extension_bundle, canonical_id
):
    assert {check["id"] for check in extension_bundle["checks"]} == {
        *CANONICAL_IDS, "synthetic-extension"
    }
    assert validate_bundle(extension_bundle) == []

    # Keep the generic row and consistent counts: it cannot substitute for any
    # required canonical row. The schema's contains rule must reject the omission.
    missing_canonical = copy.deepcopy(extension_bundle)
    missing_canonical["checks"] = [
        check for check in missing_canonical["checks"] if check["id"] != canonical_id
    ]
    missing_canonical["overall"]["counts"] = _fixture_counts(
        missing_canonical["checks"]
    )
    # A missing canonical row produces a contains diagnostic for the check array;
    # the library message does not include the missing identifier.
    (error,) = validate_bundle(missing_canonical)
    assert error.startswith("checks: None of ")
    assert error.endswith(" are valid under the given schema")


@pytest.mark.parametrize(
    "canonical_id,field,diagnostic",
    [
        ("access-mode", "transport", "'transport' is a required property"),
        ("workspace-root", "path", "'path' is a required property"),
        ("ai-cli", "codex", "'codex' is a required property"),
        ("licensed-tools", "required", "{} is not valid under any of the given schemas"),
    ],
)
def test_generic_extension_cannot_hide_invalid_canonical_payload(
    extension_bundle, canonical_id, field, diagnostic
):
    # Establish validity before removing only the required canonical evidence field.
    assert validate_bundle(extension_bundle) == []
    index = next(
        index for index, check in enumerate(extension_bundle["checks"])
        if check["id"] == canonical_id
    )
    del extension_bundle["checks"][index]["evidence"][field]

    assert validate_bundle(extension_bundle) == [
        f"checks/{index}/evidence: {diagnostic}"
    ]


def test_duplicate_extension_identifier_is_rejected(extension_bundle):
    assert validate_bundle(extension_bundle) == []
    generic = next(
        check for check in extension_bundle["checks"]
        if check["id"] == "synthetic-extension"
    )
    duplicate = copy.deepcopy(generic)
    duplicate["summary"] = "Distinct row with the same synthetic identifier"
    extension_bundle["checks"].append(duplicate)
    # Include both warning rows in the counts so only identifier uniqueness fails.
    extension_bundle["overall"]["counts"] = _fixture_counts(extension_bundle["checks"])

    assert validate_bundle(extension_bundle) == ["checks: duplicate check id"]


@pytest.mark.parametrize("field", ("total", "pass", "warn", "fail", "error", "skip"))
def test_extension_counts_match_fixture_arithmetic(extension_bundle, field):
    expected = _fixture_counts(extension_bundle["checks"])
    assert extension_bundle["overall"]["counts"] == expected
    assert validate_bundle(extension_bundle) == []

    # Adding one to a correct supplied count is inconsistent by direct arithmetic.
    extension_bundle["overall"]["counts"][field] = expected[field] + 1
    assert validate_bundle(extension_bundle) == [
        f"overall/counts/{field}: count mismatch"
    ]
