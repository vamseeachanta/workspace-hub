"""Helper regressions; expected outcomes follow explicit byte comparisons.

SHA-256 is defined by FIPS 180-4 (2015), section 6.2. No digest literal is
treated as a semantic oracle: the fixture accepts only the original source.
Restoration follows the ``assert_semantic_rejection`` helper contract: restore
pins even on failure. Restoration digest literals were independently calculated
with sha256sum over the exact byte fixtures; restored mappings use pre-call values.
The unrelated sentinel hashes the ASCII word 'unrelated' followed by a newline.
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


@pytest.mark.parametrize("error_type", [AssertionError, RuntimeError])
def test_pin_restored_when_evaluator_raises(tmp_path, monkeypatch, error_type):
    """An evaluator failure propagates after restoring the entire literal mapping."""
    source = b"fixture.sh"
    original = b"allowed\n"
    mutated = b"bypass\n"
    # SHA-256 basis and independent digest calculation: module docstring above.
    before = {
        b"fixture.sh": "fda0c6dbbd27bb4682f2931877d6c3e6b408e65b07feb9b4c1e9cc29b1a2cda2",
        b"unrelated.sh": "f641f022503420433a082e885647810297b74db84e34a743976893e73e7e20cc",
    }
    refreshed = "d6b3d516f611c5f2000142c5305e48a80683c9cb6f82912b08b741b07a0b8b1a"
    pins = dict(before)
    error = error_type("mutated evaluator failure")

    def evaluate(records):
        if records[source] == original:
            assert pins == before
            return "accepted"
        assert records == {source: mutated}
        assert pins == {**before, source: refreshed}
        raise error

    with pytest.raises(error_type, match="mutated evaluator failure") as caught:
        assert_semantic_rejection(
            tmp_path, monkeypatch, source, original, lambda _body: mutated,
            pins, evaluate, "source-shape",
        )
    assert caught.value is error
    assert pins == before


@pytest.mark.parametrize("error_type", [AssertionError, RuntimeError])
def test_nested_repin_restores_outer_pin(tmp_path, monkeypatch, error_type):
    """Inner failure restores the active outer pin; outer failure restores all pins."""
    outer_source = b"outer.sh"
    inner_source = b"inner.sh"
    outer_original = b"allowed\n"
    outer_mutated = b"bypass\n"
    inner_original = b"inner allowed\n"
    inner_mutated = b"inner bypass\n"
    # SHA-256 basis and independent digest calculation: module docstring above.
    before = {
        b"outer.sh": "fda0c6dbbd27bb4682f2931877d6c3e6b408e65b07feb9b4c1e9cc29b1a2cda2",
        b"inner.sh": "1ef73706bb2e4f2cdd354b7858ae1d8cee39bff14a20b319ba517b2530bc0177",
        b"unrelated.sh": "f641f022503420433a082e885647810297b74db84e34a743976893e73e7e20cc",
    }
    outer_digest = "d6b3d516f611c5f2000142c5305e48a80683c9cb6f82912b08b741b07a0b8b1a"
    inner_digest = "b788d43988bf806372f01ff1639d161517faafe0716db4b02051d1c17a625f56"
    pins = dict(before)
    inner_error = error_type("inner evaluator failure")
    outer_error = error_type("outer evaluator failure")

    def evaluate_outer(records):
        if records[outer_source] == outer_original:
            assert pins == before
            return "accepted"
        assert records == {outer_source: outer_mutated}
        assert pins == {**before, outer_source: outer_digest}
        outer_refreshed = pins[outer_source]
        outer_pins = dict(pins)

        def evaluate_inner(inner_records):
            if inner_records[inner_source] == inner_original:
                assert pins == outer_pins
                return "accepted"
            assert inner_records == {inner_source: inner_mutated}
            assert pins == {**outer_pins, inner_source: inner_digest}
            raise inner_error

        with pytest.raises(error_type, match="inner evaluator failure") as caught_inner:
            assert_semantic_rejection(
                tmp_path, monkeypatch, inner_source, inner_original,
                lambda _body: inner_mutated, pins, evaluate_inner, "source-shape",
            )
        assert caught_inner.value is inner_error
        assert pins == outer_pins
        assert pins[outer_source] == outer_refreshed
        raise outer_error

    with pytest.raises(error_type, match="outer evaluator failure") as caught_outer:
        assert_semantic_rejection(
            tmp_path, monkeypatch, outer_source, outer_original,
            lambda _body: outer_mutated, pins, evaluate_outer, "source-shape",
        )
    assert caught_outer.value is outer_error
    assert pins == before


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
