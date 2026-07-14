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


class FakeOwnerApi:
    def __init__(self, head, tree):
        self.slots = {"CURRENT": "current-envelope", "PENDING": "pending-envelope"}
        self.head = head
        self.tree = tree
        self.calls = []

    def read_slot(self, name):
        self.calls.append(("read_slot", name))
        return self.slots.get(name)

    def read_main(self):
        self.calls.append(("read_main",))
        return {"head_oid": self.head, "tree_oid": self.tree}

    def write_slot(self, name, value):
        self.calls.append(("write_slot", name))
        self.slots[name] = value

    def delete_slot(self, name):
        self.calls.append(("delete_slot", name))
        del self.slots[name]


def _preview(head, tree):
    return canonical(
        {
            "current_envelope_sha256": hashlib.sha256(b"current-envelope").hexdigest(),
            "expected_head_oid": head,
            "expected_tree_oid": tree,
            "pending_envelope_sha256": hashlib.sha256(b"pending-envelope").hexdigest(),
            "schema_id": "legal-rule-promotion-preview-v1",
        }
    )


def test_owner_promote_performs_verified_compare_and_swap(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    head, tree = "a" * 40, "b" * 40
    api = FakeOwnerApi(head, tree)

    assert promotion.promote(
        api, "CURRENT", "PENDING", head, tree, _preview(head, tree)
    )
    assert api.slots == {"CURRENT": "pending-envelope"}
    assert api.calls == [
        ("read_slot", "CURRENT"),
        ("read_slot", "PENDING"),
        ("read_main",),
        ("read_slot", "CURRENT"),
        ("read_slot", "PENDING"),
        ("write_slot", "CURRENT"),
        ("read_slot", "CURRENT"),
        ("read_main",),
        ("read_slot", "PENDING"),
        ("delete_slot", "PENDING"),
    ]


@pytest.mark.parametrize("drift", ["head", "tree", "current", "pending"])
def test_owner_promote_aborts_before_write_on_compare_and_swap_drift(
    monkeypatch, drift
):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    head, tree = "a" * 40, "b" * 40
    api = FakeOwnerApi(head, tree)
    original_read_slot = api.read_slot
    reads = {"CURRENT": 0, "PENDING": 0}

    def read_slot(name):
        value = original_read_slot(name)
        reads[name] += 1
        if drift == name.lower() and reads[name] == 2:
            return "drifted"
        return value

    api.read_slot = read_slot
    if drift == "head":
        api.head = "c" * 40
    if drift == "tree":
        api.tree = "d" * 40

    with pytest.raises(codec.AuthorityError, match="integrity"):
        promotion.promote(api, "CURRENT", "PENDING", head, tree, _preview(head, tree))
    assert not any(call[0] in {"write_slot", "delete_slot"} for call in api.calls)


def test_owner_promote_retains_pending_when_current_readback_fails(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    head, tree = "a" * 40, "b" * 40
    api = FakeOwnerApi(head, tree)
    original_read_slot = api.read_slot
    current_reads = 0

    def read_slot(name):
        nonlocal current_reads
        value = original_read_slot(name)
        if name == "CURRENT":
            current_reads += 1
            if current_reads == 3:
                return "failed-readback"
        return value

    api.read_slot = read_slot
    with pytest.raises(codec.AuthorityError, match="integrity"):
        promotion.promote(api, "CURRENT", "PENDING", head, tree, _preview(head, tree))
    assert api.slots["PENDING"] == "pending-envelope"
    assert not any(call[0] == "delete_slot" for call in api.calls)
