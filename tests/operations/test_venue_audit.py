"""TDD tests for venue_audit.py — Telegram venue parity verifier (#2971, F4)."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "operations" / "venue_audit.py"
spec = importlib.util.spec_from_file_location("venue_audit", MODULE_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
sys.modules["venue_audit"] = module
assert spec.loader is not None
spec.loader.exec_module(module)

CURRENT = module.CURRENT_CONTRACT_VERSION


def _conformant_config(contract_version: int | None = None) -> dict:
    """A deckhand venue config that fully satisfies the contract."""
    return {
        "venue_contract": {
            "contract_version": CURRENT if contract_version is None else contract_version,
            "idempotency": {"scheme": "client-ref+message-type+monotonic-seq"},
            "dead_letter": {"target": "deckhand-dead-letter-queue"},
            "audit": {"pii_safe": True},
            "escalation": {"label_swap": "needs-mirror->mirrored"},
        }
    }


# --- conformant ----------------------------------------------------------------


def test_conformant_config_returns_no_gaps():
    gaps = module.verify(_conformant_config(), CURRENT)
    assert gaps == []


def test_conformant_with_newer_declared_version_is_ok():
    # declared >= current is fine (fail-closed only triggers on older)
    gaps = module.verify(_conformant_config(CURRENT + 5), CURRENT)
    assert gaps == []


# --- missing field -------------------------------------------------------------


def test_missing_required_field_returns_gap():
    cfg = _conformant_config()
    del cfg["venue_contract"]["dead_letter"]
    gaps = module.verify(cfg, CURRENT)
    fields = {g["field"] for g in gaps}
    assert "venue_contract.dead_letter.target" in fields
    # every gap carries field + detail
    for g in gaps:
        assert set(g) == {"field", "detail"}


def test_empty_config_returns_all_gaps():
    gaps = module.verify({}, CURRENT)
    assert len(gaps) == len(module.required_contract_fields())


# --- older contract version (fail closed) -------------------------------------


def test_older_declared_contract_version_returns_gap():
    cfg = _conformant_config(CURRENT - 1)
    gaps = module.verify(cfg, CURRENT)
    fields = {g["field"] for g in gaps}
    assert "venue_contract.contract_version" in fields
    detail = next(g["detail"] for g in gaps if g["field"] == "venue_contract.contract_version")
    assert "older" in detail.lower()


def test_missing_contract_version_returns_gap():
    cfg = _conformant_config()
    del cfg["venue_contract"]["contract_version"]
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.contract_version" in {g["field"] for g in gaps}


def test_non_integer_contract_version_returns_gap():
    cfg = _conformant_config()
    cfg["venue_contract"]["contract_version"] = "1"  # string, not int
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.contract_version" in {g["field"] for g in gaps}


# --- PII-safe audit ------------------------------------------------------------


def test_audit_without_pii_safe_true_returns_gap():
    cfg = _conformant_config()
    cfg["venue_contract"]["audit"] = {"pii_safe": False}
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.audit.pii_safe" in {g["field"] for g in gaps}


def test_audit_missing_pii_safe_returns_gap():
    cfg = _conformant_config()
    cfg["venue_contract"]["audit"] = {}  # present but no pii_safe key
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.audit.pii_safe" in {g["field"] for g in gaps}


# --- idempotency scheme (no content-hash) -------------------------------------


def test_content_hash_idempotency_scheme_returns_gap():
    cfg = _conformant_config()
    cfg["venue_contract"]["idempotency"]["scheme"] = "content-hash"
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.idempotency.scheme" in {g["field"] for g in gaps}


def test_wrong_label_swap_returns_gap():
    cfg = _conformant_config()
    cfg["venue_contract"]["escalation"]["label_swap"] = "open->closed"
    gaps = module.verify(cfg, CURRENT)
    assert "venue_contract.escalation.label_swap" in {g["field"] for g in gaps}


# --- purity / robustness -------------------------------------------------------


def test_verify_does_not_mutate_input():
    cfg = _conformant_config()
    snapshot = copy.deepcopy(cfg)
    module.verify(cfg, CURRENT)
    assert cfg == snapshot


def test_non_dict_config_fails_closed():
    gaps = module.verify("not-a-dict", CURRENT)
    assert len(gaps) == 1
    assert gaps[0]["field"] == "<root>"


# --- schema shape --------------------------------------------------------------


def test_required_contract_fields_schema_shape():
    schema = module.required_contract_fields()
    assert "venue_contract.contract_version" in schema
    assert "venue_contract.idempotency.scheme" in schema
    assert "venue_contract.dead_letter.target" in schema
    assert "venue_contract.audit.pii_safe" in schema
    assert "venue_contract.escalation.label_swap" in schema
    for spec in schema.values():
        assert "detail" in spec
