from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import codec, gh_owner, promotion  # noqa: E402


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


class Result:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def test_gh_transport_uses_stdin_and_remote_metadata_for_cas(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("CURRENT", "current-envelope")
    monkeypatch.setenv("PENDING", "pending-envelope")
    metadata = {
        "CURRENT": "2026-07-13T00:00:00Z",
        "PENDING": "2026-07-13T00:00:00Z",
    }
    calls = []

    def runner(argv, **kwargs):
        calls.append((argv, kwargs.get("input")))
        assert "current-envelope" not in argv
        assert "pending-envelope" not in argv
        assert "CURRENT" not in kwargs["env"]
        assert "PENDING" not in kwargs["env"]
        if argv[1:3] == ["secret", "list"]:
            return Result(
                codec.canonical_bytes(
                    [
                        {"name": name, "updatedAt": updated}
                        for name, updated in metadata.items()
                    ]
                ).decode()
            )
        if argv[1:3] == ["secret", "set"]:
            assert argv[3] == "CURRENT"
            assert kwargs["input"] == "pending-envelope"
            metadata["CURRENT"] = "2026-07-14T00:00:00Z"
            return Result()
        if argv[1:3] == ["secret", "delete"]:
            assert argv[3] == "PENDING"
            del metadata["PENDING"]
            return Result()
        if argv[1:3] == ["api", "repos/o/r/git/ref/heads/main"]:
            return Result("a" * 40 + "\n")
        if argv[1:3] == ["api", "repos/o/r/git/commits/" + "a" * 40]:
            return Result("b" * 40 + "\n")
        raise AssertionError(argv)

    api = gh_owner.GhOwnerTransport("CURRENT", "PENDING", "o/r", runner=runner)
    head, tree = "a" * 40, "b" * 40
    promotion.promote(api, "CURRENT", "PENDING", head, tree, _preview(head, tree))

    assert "PENDING" not in metadata
    assert any(call[0][1:3] == ["secret", "set"] for call in calls)
    assert any(call[0][1:3] == ["secret", "delete"] for call in calls)


def test_gh_transport_fails_closed_on_remote_drift_and_redacts_errors(monkeypatch):
    monkeypatch.setenv("LEGAL_RULE_OWNER_PROMOTE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("CURRENT", "current-envelope")
    monkeypatch.setenv("PENDING", "pending-envelope")
    responses = iter(
        [
            Result(
                '[{"name":"CURRENT","updatedAt":"one"},{"name":"PENDING","updatedAt":"one"}]'
            ),
            Result(
                '[{"name":"CURRENT","updatedAt":"drift"},{"name":"PENDING","updatedAt":"one"}]'
            ),
        ]
    )

    def runner(_argv, **_kwargs):
        return next(responses)

    api = gh_owner.GhOwnerTransport("CURRENT", "PENDING", "o/r", runner=runner)
    assert api.read_slot("CURRENT") == "current-envelope"
    with pytest.raises(codec.AuthorityError, match="integrity") as caught:
        api.read_slot("CURRENT")
    assert "current-envelope" not in str(caught.value)


def test_gh_transport_rejects_ci_and_invalid_names_before_subprocess(monkeypatch):
    calls = []
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(codec.AuthorityError, match="config"):
        gh_owner.GhOwnerTransport("CURRENT;bad", "PENDING", "o/r", runner=calls.append)
    assert calls == []
