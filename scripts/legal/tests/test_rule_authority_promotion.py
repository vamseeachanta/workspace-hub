from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, promotion  # noqa: E402


def canonical(value):
    return codec.canonical_bytes(value)


def test_owner_promotion_preconditions_are_compare_and_swap_bound(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("CURRENT", "current-envelope")
    monkeypatch.setenv("PENDING", "pending-envelope")
    head, tree = "a" * 40, "b" * 40
    preview = {
        "current_envelope_sha256": hashlib.sha256(b"current-envelope").hexdigest(),
        "expected_head_oid": head,
        "expected_tree_oid": tree,
        "pending_envelope_sha256": hashlib.sha256(b"pending-envelope").hexdigest(),
        "schema_id": "legal-rule-promotion-preview-v1",
    }
    assert (
        promotion.validate("CURRENT", "PENDING", head, tree, canonical(preview))
        == preview
    )
    monkeypatch.setenv("PENDING", "changed")
    with pytest.raises(codec.AuthorityError, match="integrity"):
        promotion.validate("CURRENT", "PENDING", head, tree, canonical(preview))


def test_promotion_is_unavailable_in_actions_and_without_owner_gate(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(codec.AuthorityError, match="config"):
        promotion.validate("CURRENT", "PENDING", "a" * 40, "b" * 40, b"{}\n")
    monkeypatch.delenv("GITHUB_ACTIONS")
    monkeypatch.delenv("LEGAL_RULE_OWNER_PROMOTE")
    with pytest.raises(codec.AuthorityError, match="config"):
        promotion.validate("CURRENT", "PENDING", "a" * 40, "b" * 40, b"{}\n")
