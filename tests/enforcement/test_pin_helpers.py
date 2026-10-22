"""Helper regressions; expected outcomes follow explicit byte comparisons.

SHA-256 is defined by FIPS 180-4 (2015), section 6.2. No digest literal is
treated as a semantic oracle: the fixture accepts only the original source.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from pin_helpers import assert_semantic_rejection, checked_rejection


@pytest.fixture
def vacuous_evaluator():
    """Reject stale bytes, then accept every behaviour: intentionally defective."""
    def evaluate(body, expected):
        if hashlib.sha256(body).hexdigest() != expected:
            return "stale-pin"
        return "accepted"
    return evaluate


def test_vacuous_fixture_is_rejected(tmp_path, monkeypatch, vacuous_evaluator):
    original = b"allowed\n"
    pins = {b"fixture.sh": hashlib.sha256(original).hexdigest()}
    before = dict(pins)
    with pytest.raises(AssertionError, match="semantic"):
        assert_semantic_rejection(
            tmp_path, monkeypatch, b"fixture.sh", original,
            lambda body: body.replace(b"allowed", b"bypass"), pins,
            lambda records: vacuous_evaluator(records[b"fixture.sh"], pins[b"fixture.sh"]),
            "source-shape",
        )
    assert pins == before


@pytest.mark.parametrize("reason", ["stale-pin", "missing-pin", "accepted", None, False])
def test_self_check_rejects_provenance_and_boolean_results(reason):
    with pytest.raises(AssertionError, match="semantic"):
        checked_rejection(reason, "source-shape")


def test_helper_repins_restores_and_uses_mutated_bytes(tmp_path, monkeypatch):
    original = b"allowed\n"
    pins = {b"fixture.sh": hashlib.sha256(original).hexdigest()}
    before = dict(pins)

    def evaluate(records):
        body = records[b"fixture.sh"]
        assert hashlib.sha256(body).hexdigest() == pins[b"fixture.sh"]
        return "accepted" if body == original else "source-shape"

    assert_semantic_rejection(
        tmp_path, monkeypatch, b"fixture.sh", original,
        lambda body: body.replace(b"allowed", b"bypass"), pins, evaluate, "source-shape",
    )
    assert pins == before
    assert (tmp_path / "fixture.sh").read_bytes() == b"bypass\n"


def test_noop_mutation_is_rejected(tmp_path, monkeypatch):
    with pytest.raises(AssertionError, match="unchanged"):
        assert_semantic_rejection(
            tmp_path, monkeypatch, b"fixture.sh", b"allowed\n",
            lambda body: body, {}, lambda _records: "source-shape", "source-shape",
        )


def test_always_rejecting_evaluator_is_not_semantic_evidence(tmp_path, monkeypatch):
    original = b"allowed\n"
    pins = {b"fixture.sh": hashlib.sha256(original).hexdigest()}
    with pytest.raises(AssertionError, match="baseline"):
        assert_semantic_rejection(
            tmp_path, monkeypatch, b"fixture.sh", original,
            lambda body: body.replace(b"allowed", b"bypass"), pins,
            lambda _records: "source-shape", "source-shape",
        )


def test_worked_example(tmp_path, monkeypatch):
    """Manual oracle: line 'mode=preview' permits preview; 'mode=apply' rejects.

    The fixture has ten lines, counted directly, and no command is executed.
    Digest literals were independently read from sha256sum of the exact fixture
    and its one-line substitution. SHA-256: FIPS 180-4 (2015), section 6.2.
    """
    original = (Path(__file__).parent / "fixtures/pinned-preview.sh").read_bytes()
    assert len(original.splitlines()) == 10  # Hand count of the fixture above.
    pin = "605183fcd3b4f413a2c91c3849caec5bf0faa0cffed79dec632d29ba02fdc19b"
    refreshed = "646156d0b7abbcece69a10f424fade9d0c1322ab8e4eae56e9775555aa36a2c9"
    assert hashlib.sha256(original).hexdigest() == pin
    mutated = original.replace(b"mode=preview", b"mode=apply")
    assert hashlib.sha256(mutated).hexdigest() == refreshed

    def evaluate(records):
        body = records[b"fixture.sh"]
        if hashlib.sha256(body).hexdigest() != pins[b"fixture.sh"]:
            return "stale-pin"
        return "accepted" if b"mode=preview" in body.splitlines() else "source-shape"

    pins = {b"fixture.sh": pin}
    assert evaluate({b"fixture.sh": mutated}) == "stale-pin"
    assert_semantic_rejection(
        tmp_path, monkeypatch, b"fixture.sh", original,
        lambda _body: mutated, pins, evaluate, "source-shape",
    )
    assert pins == {b"fixture.sh": pin}


@pytest.mark.parametrize("kind", ["parent", "absolute"])
def test_helper_refuses_source_outside_temporary_root(tmp_path, monkeypatch, kind):
    source = b"../escape.sh" if kind == "parent" else str(tmp_path.parent / "escape.sh").encode()
    with pytest.raises(AssertionError, match="temporary"):
        assert_semantic_rejection(
            tmp_path, monkeypatch, source, b"original", lambda _body: b"mutated",
            {}, lambda _records: "accepted", "source-shape",
        )
