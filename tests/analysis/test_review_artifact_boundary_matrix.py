"""Synthetic artifact combinations for the review-summary boundary.

Digest expectations use hashlib on literal fixture bytes, independently of the
pipeline's hashing helper. No provider commands or external evidence are used.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest


# Repository layout: this module is in tests/analysis, below the repository root.
MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "continuous-planning-pipeline.py"
spec = importlib.util.spec_from_file_location("review_artifact_boundary_pipeline", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

# Synthetic first issue; only the artifact filename and summary lookup use it.
ISSUE_NUMBER = 1
REQUIRED_PROVIDERS = ("alpha", "beta", "gamma")
PLAN_BYTES = b"# Synthetic plan\n\nCheck artifact evidence.\n"
CRLF_PLAN_BYTES = PLAN_BYTES.replace(b"\n", b"\r\n")


@pytest.fixture
def plan_path(tmp_path: Path) -> Path:
    path = tmp_path / "plan.md"
    path.write_bytes(PLAN_BYTES)
    return path


def write_artifact(root: Path, provider: str, text: str) -> Path:
    path = root / "scripts" / "review" / "results" / f"fixture-plan-{ISSUE_NUMBER}-{provider}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def matching_reviews(root: Path, sha: str) -> None:
    for provider in REQUIRED_PROVIDERS:
        write_artifact(root, provider, f"Plan-SHA256: {sha}\nVerdict: MINOR\n")


def summarize(root: Path, plan_path: Path, *, allow_legacy: bool = False):
    reviews = module.discover_reviews(root, REQUIRED_PROVIDERS)
    return module.review_summary(
        ISSUE_NUMBER, plan_path, reviews, REQUIRED_PROVIDERS,
        allow_legacy_review_artifacts=allow_legacy,
    )


@pytest.mark.parametrize("stale_provider", REQUIRED_PROVIDERS)
@pytest.mark.parametrize("allow_legacy", (False, True), ids=("strict", "legacy-opt-in"))
def test_stale_required_review_cannot_be_outvoted(
    tmp_path: Path, plan_path: Path, stale_provider: str, allow_legacy: bool,
) -> None:
    current_sha = hashlib.sha256(PLAN_BYTES).hexdigest()
    stale_sha = hashlib.sha256(b"# Synthetic plan\n\nPrevious content.\n").hexdigest()
    assert stale_sha != current_sha
    matching_reviews(tmp_path, current_sha)
    write_artifact(
        tmp_path, stale_provider,
        f"Reviewed-Plan-SHA256: {current_sha}\nPlan-SHA256: {stale_sha}\nVerdict: APPROVE\n",
    )

    clean, warnings, evidence = summarize(tmp_path, plan_path, allow_legacy=allow_legacy)

    assert clean is False
    assert warnings == ["sha_mismatch_review"]
    assert evidence["plan_sha256"] == current_sha
    assert evidence["required_providers"] == list(REQUIRED_PROVIDERS)
    for provider in REQUIRED_PROVIDERS:
        expected_sha = stale_sha if provider == stale_provider else current_sha
        assert evidence["providers"][provider]["plan_sha256"] == expected_sha


@pytest.mark.parametrize(
    ("original_bytes", "changed_bytes"),
    (
        pytest.param(PLAN_BYTES, PLAN_BYTES + b"Additional requirement.\n", id="content-edit"),
        pytest.param(PLAN_BYTES, CRLF_PLAN_BYTES, id="lf-to-crlf"),
        pytest.param(CRLF_PLAN_BYTES, PLAN_BYTES, id="crlf-to-lf"),
    ),
)
def test_plan_byte_change_invalidates_review(
    tmp_path: Path, plan_path: Path, original_bytes: bytes, changed_bytes: bytes,
) -> None:
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    changed_sha = hashlib.sha256(changed_bytes).hexdigest()
    assert original_sha != changed_sha
    plan_path.write_bytes(original_bytes)
    matching_reviews(tmp_path, original_sha)
    clean, warnings, evidence = summarize(tmp_path, plan_path)
    assert clean is True
    assert warnings == []
    assert evidence["plan_sha256"] == original_sha

    plan_path.write_bytes(changed_bytes)
    clean, warnings, evidence = summarize(tmp_path, plan_path)

    assert plan_path.read_bytes() == changed_bytes
    assert clean is False
    assert warnings == ["sha_mismatch_review"]
    assert evidence["plan_sha256"] == changed_sha
    for provider in REQUIRED_PROVIDERS:
        assert evidence["providers"][provider]["plan_sha256"] == original_sha


@pytest.mark.parametrize(
    ("case", "expected_warnings"),
    (
        ("missing-canonical-sha", ["legacy_review_no_sha"]),
        ("whitespace-only", ["empty_review"]),
        ("disagreement-only", ["missing_review"]),
        ("combined", ["empty_review", "legacy_review_no_sha", "missing_review"]),
    ),
)
@pytest.mark.parametrize("allow_legacy", (False, True), ids=("strict", "legacy-opt-in"))
def test_missing_sha_empty_and_disagreement_are_distinct(
    tmp_path: Path, plan_path: Path, case: str,
    expected_warnings: list[str], allow_legacy: bool,
) -> None:
    sha = hashlib.sha256(PLAN_BYTES).hexdigest()
    if case in {"missing-canonical-sha", "whitespace-only"}:
        matching_reviews(tmp_path, sha)
    if case in {"missing-canonical-sha", "combined"}:
        write_artifact(tmp_path, "alpha", f"Reviewed-Plan-SHA256: {sha}\nVerdict: MINOR\n")
    if case in {"whitespace-only", "combined"}:
        write_artifact(tmp_path, "beta", " \t\r\n \n")
    # A matching summary cannot supply any missing required provider's review.
    write_artifact(tmp_path, "disagreement", f"Plan-SHA256: {sha}\nVerdict: APPROVE\n")

    clean, warnings, evidence = summarize(tmp_path, plan_path, allow_legacy=allow_legacy)

    assert clean is (allow_legacy and case == "missing-canonical-sha")
    assert warnings == expected_warnings
    assert evidence["plan_sha256"] == sha
    providers = evidence["providers"]
    assert set(providers) == set(REQUIRED_PROVIDERS)
    if case in {"missing-canonical-sha", "combined"}:
        assert providers["alpha"]["plan_sha256"] is None
        assert providers["alpha"]["verdict"] == "MINOR"
        assert providers["alpha"]["empty"] is False
    if case in {"whitespace-only", "combined"}:
        assert providers["beta"]["empty"] is True
        assert providers["beta"]["verdict"] == "EMPTY"
        assert providers["beta"]["plan_sha256"] is None
    if case == "disagreement-only":
        assert providers == {provider: {"status": "missing"} for provider in REQUIRED_PROVIDERS}
    elif case == "combined":
        assert providers["gamma"] == {"status": "missing"}


@pytest.mark.parametrize("plan_bytes", (PLAN_BYTES, CRLF_PLAN_BYTES), ids=("lf", "crlf"))
def test_matching_required_reviews_control(tmp_path: Path, plan_path: Path, plan_bytes: bytes) -> None:
    plan_path.write_bytes(plan_bytes)
    sha = hashlib.sha256(plan_bytes).hexdigest()
    matching_reviews(tmp_path, sha)
    write_artifact(tmp_path, "alpha", f"Plan-SHA256: {sha}\nVerdict: APPROVE\n")
    # A summary is outside the required evidence set, even with a negative verdict.
    write_artifact(tmp_path, "disagreement", f"Plan-SHA256: {sha}\nVerdict: MAJOR\n")

    clean, warnings, evidence = summarize(tmp_path, plan_path)

    assert clean is True
    assert warnings == []
    assert evidence["plan_sha256"] == sha
    assert evidence["required_providers"] == list(REQUIRED_PROVIDERS)
    assert set(evidence["providers"]) == set(REQUIRED_PROVIDERS)
    for provider in REQUIRED_PROVIDERS:
        assert evidence["providers"][provider]["plan_sha256"] == sha
        assert evidence["providers"][provider]["empty"] is False
        assert evidence["providers"][provider]["verdict"] == (
            "APPROVE" if provider == "alpha" else "MINOR"
        )
