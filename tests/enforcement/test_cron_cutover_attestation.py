"""Attest the corrected preservation and reconciliation source contracts.

Expected outcomes are independent safety predicates: complete classification
passes; removal of any section or failure branch fails; masking a child failure
fails even if an adjacent source pin is refreshed.
"""
import ast
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/enforcement"))
import scheduler_mutation_attestations as attest
import scheduler_mutation_wrapper_attestations as wrapper


def test_all_section_preservation_is_attested():
    source = (ROOT / "scripts/cron/cron_transaction.py").read_text()
    assert attest._preservation_shape(ast.parse(source))


@pytest.mark.parametrize("old,new", [
    ('("before", "managed", "after")', '("before", "after")'),
    ('if uncataloged:', 'if False:'),
    ('block[:1] + managed + block[1:]', 'block'),
])
def test_preservation_attestation_rejects_loss_and_failure_masking(old, new):
    source = (ROOT / "scripts/cron/cron_transaction.py").read_text()
    assert old in source
    assert not attest._preservation_shape(ast.parse(source.replace(old, new)))


def test_reconcile_status_is_attested():
    source = (ROOT / "scripts/cron/harness-update.sh").read_bytes()
    records = {wrapper.HARNESS: source}
    assert wrapper.evaluate_wrapper_attestation("harness-default-v1", records)
    assert wrapper.evaluate_wrapper_attestation("harness-dry-run-v1", records)


@pytest.mark.parametrize("old,new", [
    (b'exit "$cron_status"', b'exit 0'),
    (b'return "$status"', b'return 0'),
    (b'sync_crontab || cron_status=$?', b'sync_crontab || true'),
])
def test_reconcile_self_refreshed_pin_does_not_allow_masking(monkeypatch, old, new):
    source = (ROOT / "scripts/cron/harness-update.sh").read_bytes()
    assert old in source
    changed = source.replace(old, new)
    monkeypatch.setitem(wrapper.WRAPPER_SHA256, wrapper.HARNESS, hashlib.sha256(changed).hexdigest())
    assert not wrapper.evaluate_wrapper_attestation("harness-default-v1", {wrapper.HARNESS: changed})
