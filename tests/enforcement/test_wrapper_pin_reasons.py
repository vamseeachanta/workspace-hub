"""Separate provenance failures from semantic rejection for pinned wrappers."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pin_helpers import assert_semantic_rejection

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/enforcement"))
import scheduler_mutation_wrapper_attestations as wrappers


def test_setup_committed_and_working_bytes_match_pin():
    """Digest equality is independently computed from committed source bytes.

    SHA-256: FIPS 180-4 (2015), section 6.2. The shape oracle is the reviewed
    wrapper contract; hashing alone does not qualify changed behaviour.
    """
    source = wrappers.SETUP
    committed = subprocess.run(
        ["git", "show", f"HEAD:{source.decode()}"], cwd=ROOT,
        capture_output=True, check=True,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
    ).stdout
    for body in (committed, (ROOT / source.decode()).read_bytes()):
        actual = hashlib.sha256(body).hexdigest()
        expected = wrappers.WRAPPER_SHA256[source]
        assert actual == expected, f"committed/working sha256={actual}; pinned sha256={expected}"
        for name in wrappers.SETUP_ATTESTATIONS:
            assert wrappers.evaluate_wrapper_attestation(name, {source: body})


@pytest.mark.parametrize("source,name", [
    (wrappers.SETUP, "setup-default-apply-v1"),
    (wrappers.NEW_MACHINE, "new-machine-default-v1"),
    (wrappers.HARNESS, "harness-default-v1"),
])
@pytest.mark.parametrize("failure", ["missing-pin", "stale-pin"])
def test_provenance_reasons_are_separate(monkeypatch, source, name, failure):
    body = (ROOT / source.decode()).read_bytes()
    if failure == "missing-pin":
        monkeypatch.delitem(wrappers.WRAPPER_SHA256, source)
    else:
        # Hash different bytes; no guessed digest or magic hexadecimal constant.
        monkeypatch.setitem(wrappers.WRAPPER_SHA256, source, hashlib.sha256(body + b"# drift").hexdigest())
    assert wrappers.wrapper_attestation_reason(name, {source: body}) == failure
    assert wrappers.evaluate_wrapper_attestation(name, {source: body}) is False


def test_refreshed_setup_mutation_has_semantic_reason(tmp_path, monkeypatch):
    source = wrappers.SETUP
    assert_semantic_rejection(
        tmp_path, monkeypatch, source, (ROOT / source.decode()).read_bytes(),
        lambda body: body.replace(b"DRY_RUN=false", b"DRY_RUN=true"),
        wrappers.WRAPPER_SHA256,
        lambda records: wrappers.wrapper_attestation_reason("setup-default-apply-v1", records),
        "source-shape",
    )
