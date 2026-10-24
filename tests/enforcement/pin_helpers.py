"""Exercise semantics after refreshing a source pin in memory only."""
from __future__ import annotations

import hashlib

SEMANTIC_REASONS = frozenset({"source-shape", "unreachable"})


def checked_rejection(actual, expected):
    """A false boolean or provenance failure cannot establish semantic rejection."""
    assert expected in SEMANTIC_REASONS, f"unknown semantic reason: {expected!r}"
    assert actual == expected, f"expected semantic {expected!r}, received {actual!r}"


def assert_semantic_rejection(
    tmp_path, monkeypatch, source, original, mutate, pins, evaluate, expected,
    *, records=None,
):
    """Copy source, mutate, re-pin, evaluate, and restore pins even on failure.

    The evaluator receives an isolated record mapping containing the bytes read
    back from the temporary file. SHA-256: FIPS 180-4 (2015), section 6.2.
    An identity mutation is a fixture error rather than a semantic test.
    """
    target = tmp_path / source.decode()
    assert target.resolve().is_relative_to(tmp_path.resolve()), "source escapes temporary directory"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(original)
    mutated = mutate(target.read_bytes())
    assert mutated != original, "mutation left source unchanged"
    target.write_bytes(mutated)
    changed = dict(records or {})
    changed[source] = original
    assert pins.get(source) == hashlib.sha256(original).hexdigest(), "baseline pin differs"
    assert evaluate(changed) == "accepted", "baseline semantic evaluation must accept"
    changed[source] = target.read_bytes()
    digest = hashlib.sha256(changed[source]).hexdigest()
    with monkeypatch.context() as patch:
        patch.setitem(pins, source, digest)
        checked_rejection(evaluate(changed), expected)
