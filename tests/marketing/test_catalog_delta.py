"""Presence-sync expectations use the hand calculations stated below.

The synthetic catalog is a schema example, not measured capability evidence.
Policy basis: issue 3302 and its canonical-catalog follow-up, issue 3305.
"""

import importlib.util
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "scripts/marketing/deckhand-api-presence-sync"
SCRIPT = DIRECTORY / "catalog_delta.py"


@pytest.fixture
def helper():
    spec = importlib.util.spec_from_file_location("presence_delta", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(ref="screen", status="live_public", **extra):
    return {"ref": ref, "kind": "workflow", "domain": "analysis",
            "subdomains": ["screening"], "status": status, **extra}


def catalog(*records):
    return {"records": list(records), "private_internal_count": 0}


def test_public_projection(helper):
    """Hand count: one public + one roadmap + two hidden = four input rows."""
    result = helper.normalize_canonical(catalog(
        record(description="discard", scope="discard"), record("future", "roadmap"),
        record("hidden-a", "live_private"), record("hidden-b", "internal")))
    assert [p["ref"] for p in result["paths"]] == ["future", "screen"]
    assert result["private_internal_count"] == 2
    assert "discard" not in json.dumps(result)
    assert "hidden-" not in json.dumps(result)
    assert all(p["claimable_public"] is False for p in result["paths"])


def test_report_evidence_required(helper):
    result = helper.normalize_canonical(catalog(record(
        claimable_public=True, report_url_example="https://example.org/<run>/report.html")))
    assert result["paths"][0]["claim_check"] == "NOT_EVALUATED"
    result = helper.normalize_canonical(catalog(record()), {
        "screen": {"public_report_url": "https://example.org/report.html", "reviewed": True}})
    assert result["paths"][0]["claimable_public"] is True
    assert result["paths"][0]["public_report_url"] == "https://example.org/report.html"


@pytest.mark.parametrize("url", ["http://example.org/report.html", "file:report.html",
                                    "https://example.org/<run>/report.html",
                                    "https://example.org/report.html?token=redacted",
                                    "https://example.org/.../report.html"])
def test_unsafe_report_urls_not_claimable(helper, url):
    result = helper.normalize_canonical(catalog(record()), {
        "screen": {"public_report_url": url, "reviewed": True}})
    assert not result["paths"][0]["claimable_public"]
    assert url not in json.dumps(result)


def test_roadmap_cannot_be_claimed_with_evidence(helper):
    current = helper.normalize_canonical(catalog(record(status="roadmap")), {
        "screen": {"public_report_url": "https://example.org/report.html", "reviewed": True}})
    assert not current["paths"][0]["claimable_public"]


def test_inconsistent_roadmap_kind_rejected(helper):
    with pytest.raises(ValueError):
        helper.normalize_canonical(catalog(record(kind="roadmap")), {
            "screen": {"public_report_url": "https://example.org/report.html", "reviewed": True}})


def test_derive_private_data_never_leaves_projection(helper):
    """Hand count: two hidden rows; only one unbound domain becomes roadmap."""
    data = {
        "workflows": {
            "screen": {"artifact_residency": "public-sandbox",
                       "route": {"channel_domain": "analysis", "subdomains": ["screening"]}},
            "hidden-a": {"artifact_residency": "client-wiki",
                         "description": "hidden-value", "route": {"scope": "hidden-value"}},
            "hidden-b": {"artifact_residency": "none"}},
        "channel_domain_subdomains": {"analysis": ["screening"], "future": []}}
    result = helper.normalize_routing(data)
    assert {p["ref"] for p in result["paths"]} == {"screen", "roadmap:future"}
    assert result["private_internal_count"] == 2
    assert "hidden" not in json.dumps(result)


@pytest.mark.parametrize("data", [None, {}, {"records": {}},
                                    catalog(record(), record()),
                                    catalog(record(status="invented")),
                                    catalog(record(ref="../unsafe")),
                                    catalog(record(domain="unsafe text")),
                                    {"records": [], "private_internal_count": -1}])
def test_malformed_canonical_rejected(helper, data):
    with pytest.raises((ValueError, TypeError)):
        helper.normalize_canonical(data)


def test_delta_hand_calculation(helper):
    """C={kept, added}, P={kept, removed}; C-P={added}, P-C={removed}.

    kept changes roadmap -> live_public: exactly one status change. Evidence
    is absent, so neither live row is an eligible public addition.
    """
    previous = helper.normalize_canonical(catalog(record("kept", "roadmap"), record("removed")))
    current = helper.normalize_canonical(catalog(record("kept"), record("added")))
    delta = helper.compute_delta(current, previous)
    assert [p["ref"] for p in delta["new_paths"]] == ["added"]
    assert [p["ref"] for p in delta["removed_paths"]] == ["removed"]
    assert delta["status_changed"] == [{"ref": "kept", "from": "roadmap", "to": "live_public"}]
    assert delta["new_live_public"] == []
    assert delta["counts"]["current_live_public"] == 2
    assert delta["counts"]["claimable_public"] == 0


def test_promotion_and_demotion_without_new_ref(helper):
    """Same key, false -> true is one claim addition; inverse is one withdrawal."""
    raw = catalog(record())
    no_evidence = helper.normalize_canonical(raw)
    verified = helper.normalize_canonical(raw, {
        "screen": {"public_report_url": "https://example.org/report.html", "reviewed": True}})
    assert len(helper.compute_delta(verified, no_evidence)["new_live_public"]) == 1
    assert len(helper.compute_delta(no_evidence, verified)["withdrawn_public"]) == 1
    assert helper.compute_delta(verified, verified)["new_paths"] == []


def test_metadata_changes_need_review(helper):
    old = helper.normalize_canonical(catalog(record()))
    new = helper.normalize_canonical(catalog(record(subdomains=["another"])))
    assert helper.compute_delta(new, old)["metadata_changed"] == ["screen"]


def test_draft_packet_uses_only_claimable_rows(helper):
    current = helper.normalize_canonical(catalog(record(), record("future", "roadmap")))
    packet = helper.draft_packet(helper.compute_delta(current, {"paths": []}))
    assert packet["public_additions"] == []
    assert set(packet["surfaces"]) == {"resume", "linkedin", "website", "readme"}
    assert packet["publish_allowed"] is False


def run_cli(*args, evidence_env=None):
    environment = {k: v for k, v in os.environ.items() if k != "DECKHAND_API_EVIDENCE"}
    if evidence_env is not None:
        environment["DECKHAND_API_EVIDENCE"] = str(evidence_env)
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          check=False, capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
                          env=environment)


def test_auto_prefers_canonical_and_missing_canonical_falls_back(tmp_path):
    canonical = tmp_path / "canonical.json"
    routing = tmp_path / "routing.yaml"
    snapshot = tmp_path / "snapshot.json"
    canonical.write_text(json.dumps(catalog(record("preferred"))), encoding="utf-8", newline="\n")
    routing.write_text(yaml.safe_dump({"workflows": {}, "channel_domain_subdomains": {}}), encoding="utf-8", newline="\n")
    result = run_cli("--canonical", canonical, "--catalog", routing, "--snapshot", snapshot)
    assert result.returncode == 0
    assert json.loads(result.stdout)["new_paths"][0]["ref"] == "preferred"
    assert not snapshot.exists()
    result = run_cli("--canonical", tmp_path / "absent.json", "--catalog", routing,
                     "--snapshot", snapshot, "--emit-current")
    assert result.returncode == 0
    assert json.loads(result.stdout)["source"] == "derive"


def test_corrupt_canonical_never_silently_falls_back(tmp_path):
    canonical = tmp_path / "canonical.json"
    canonical.write_text("not json", encoding="utf-8", newline="\n")
    result = run_cli("--canonical", canonical, "--snapshot", tmp_path / "snapshot.json")
    assert result.returncode != 0
    assert str(tmp_path) not in result.stderr
    assert "not json" not in result.stderr


def test_receipt_bound_to_catalog_and_snapshot(helper):
    current = helper.normalize_canonical(catalog(record()))
    previous = {"paths": [], "private_internal_count": 0}
    receipt = {
        "current_digest": helper.digest(current), "previous_digest": helper.digest(previous),
        "content_reviewed": True,
        "draft_prs": [{"url": "https://github.com/example/surfaces/pull/1", "isDraft": True,
                       "state": "OPEN", "surfaces": ["resume", "linkedin", "website", "readme"]}]}
    helper.validate_receipt(receipt, current, previous)
    for field, value in [("current_digest", "changed"), ("previous_digest", "changed"),
                         ("content_reviewed", False), ("draft_prs", [])]:
        bad = {**receipt, field: value}
        with pytest.raises(ValueError):
            helper.validate_receipt(bad, current, previous)
    for field, value in [("isDraft", False), ("state", "CLOSED"), ("surfaces", ["website"])]:
        bad = {**receipt, "draft_prs": [{**receipt["draft_prs"][0], field: value}]}
        with pytest.raises(ValueError):
            helper.validate_receipt(bad, current, previous)


def test_cli_update_requires_receipt_and_is_atomic(tmp_path, helper):
    canonical = tmp_path / "catalog.json"
    canonical.write_text(json.dumps(catalog(record())), encoding="utf-8", newline="\n")
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text('{"paths": [], "private_internal_count": 0}', encoding="utf-8", newline="\n")
    before = snapshot.read_bytes()
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}", encoding="utf-8", newline="\n")
    args = ["--source", "canonical", "--canonical", canonical, "--snapshot", snapshot,
            "--evidence", evidence]
    result = run_cli(*args, "--update-snapshot")
    assert result.returncode != 0
    assert snapshot.read_bytes() == before
    current = helper.normalize_canonical(catalog(record()))
    current["source"] = "canonical"
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "current_digest": helper.digest(current),
        "previous_digest": helper.digest(json.loads(before)), "content_reviewed": True,
        "draft_prs": [{"url": "https://github.com/example/surfaces/pull/1", "isDraft": True,
                       "state": "OPEN", "surfaces": ["resume", "linkedin", "website", "readme"]}]}), encoding="utf-8", newline="\n")
    result = run_cli(*args, "--update-snapshot", "--review-receipt", receipt)
    assert result.returncode == 0
    assert json.loads(snapshot.read_text(encoding="utf-8")) == current


def test_duplicate_yaml_keys_fail_closed(tmp_path):
    routing = tmp_path / "routing.yaml"
    routing.write_text("workflows: {}\nworkflows: {}\nchannel_domain_subdomains: {}\n", encoding="utf-8", newline="\n")
    result = run_cli("--source", "derive", "--catalog", routing,
                     "--snapshot", tmp_path / "snapshot.json")
    assert result.returncode != 0
    assert str(tmp_path) not in result.stderr


def test_duplicate_json_keys_fail_closed(tmp_path):
    canonical = tmp_path / "catalog.json"
    canonical.write_text('{"records": [], "records": []}', encoding="utf-8", newline="\n")
    assert run_cli("--source", "canonical", "--canonical", canonical).returncode != 0


def test_worked_example(helper):
    """Hand sets: P={old,screen}, C={future,screen}; C-P={future}, P-C={old}.

    Public sets change {old}->{screen}: one addition, one withdrawal, count one.
    This is the complete example in SKILL.md, independent of helper output.
    """
    proof = {ref: {"public_report_url": "https://example.org/report.html", "reviewed": True}
             for ref in ["old", "screen"]}
    previous = helper.normalize_canonical(catalog(record("old"), record("screen", "roadmap")), proof)
    current = helper.normalize_canonical(catalog(record("screen"), record("future", "roadmap")), proof)
    delta = helper.compute_delta(current, previous)
    assert [p["ref"] for p in delta["new_paths"]] == ["future"]
    assert [p["ref"] for p in delta["removed_paths"]] == ["old"]
    assert [p["ref"] for p in delta["new_live_public"]] == ["screen"]
    assert [p["ref"] for p in delta["withdrawn_public"]] == ["old"]
    assert delta["counts"]["claimable_public"] == 1


def test_schedule_targets_existing_read_only_helper():
    tasks = yaml.safe_load((ROOT / "config/scheduled-tasks/schedule-tasks.yaml").read_text(encoding="utf-8"))["tasks"]
    task = next(t for t in tasks if t["id"] == "deckhand-api-presence-sync")
    # Issue 3302 specifies Sunday at 05:00 UTC; the existing scheduler owns installation.
    assert task["schedule"] == "0 5 * * 0"
    assert "scripts/marketing/deckhand-api-presence-sync/catalog_delta.py" in task["command"]
    assert "--update-snapshot" not in task["command"]
    assert SCRIPT.is_file()


def test_seed_and_skill_are_public_safe():
    seed = json.loads((DIRECTORY / "state/api-catalog-snapshot.json").read_text(encoding="utf-8"))
    assert seed["paths"] == []
    skill = (DIRECTORY / "SKILL.md").read_text(encoding="utf-8")
    assert "../../" not in skill
    assert "DRAFT" in skill


def scheduled_args():
    tasks = yaml.safe_load((ROOT / "config/scheduled-tasks/schedule-tasks.yaml")
                           .read_text(encoding="utf-8"))["tasks"]
    command = next(t["command"] for t in tasks if t["id"] == "deckhand-api-presence-sync")
    return shlex.split(command.split("catalog_delta.py", 1)[1].split(">>", 1)[0])


@pytest.fixture
def reviewed_inputs(tmp_path, helper):
    canonical = tmp_path / "catalog.json"
    evidence = tmp_path / "evidence.json"
    snapshot = tmp_path / "snapshot.json"
    proof = {"screen": {"public_report_url": "https://example.org/report.html", "reviewed": True}}
    canonical.write_text(json.dumps(catalog(record())), encoding="utf-8", newline="\n")
    evidence.write_text(json.dumps(proof), encoding="utf-8", newline="\n")
    previous = helper.normalize_canonical(catalog(record()), proof)
    previous["source"] = "canonical"
    snapshot.write_text(json.dumps(previous), encoding="utf-8", newline="\n")
    return canonical, evidence, snapshot


def test_scheduled_comparison_uses_advancement_evidence(reviewed_inputs):
    canonical, evidence, snapshot = reviewed_inputs
    args = scheduled_args()
    assert args == ["--evidence", "${DECKHAND_API_EVIDENCE:-}"]
    # Execute the scheduled arguments with the same private configuration as advancement.
    args = [str(evidence) if a == "${DECKHAND_API_EVIDENCE:-}" else a for a in args]
    result = run_cli(*args, "--canonical", canonical, "--snapshot", snapshot)
    assert result.returncode == 0
    delta = json.loads(result.stdout)
    # Hand count: one unchanged reviewed row; one claim, zero withdrawals or changes.
    assert delta["counts"]["claimable_public"] == 1
    assert delta["withdrawn_public"] == []
    assert delta["metadata_changed"] == []
    assert delta["claim_check"] == "EVALUATED"


@pytest.mark.parametrize("evidence_mode", ["omitted", "absent", "empty-path", "directory"])
def test_unavailable_evidence_does_not_withdraw_reviewed_claims(reviewed_inputs, evidence_mode):
    canonical, evidence, snapshot = reviewed_inputs
    arguments = {"omitted": [], "absent": ["--evidence", evidence.with_name("absent.json")],
                 "empty-path": ["--evidence", ""], "directory": ["--evidence", evidence.parent]}
    before = snapshot.read_bytes()
    for mode in ([], ["--draft-packet"]):
        result = run_cli("--canonical", canonical, "--snapshot", snapshot,
                         *arguments[evidence_mode], *mode)
        assert result.returncode == 0
        delta = json.loads(result.stdout)
        assert delta["claim_check"] == "NOT_EVALUATED"
        assert delta["claim_reason"] == "Reviewed report evidence is unavailable."
        if mode:
            assert delta["withdrawals"] == []
            assert delta["public_count"] is None
        else:
            assert delta["withdrawn_public"] == []
            assert delta["metadata_changed"] == []
            assert delta["counts"]["claimable_public"] is None
    assert snapshot.read_bytes() == before


def test_explicit_empty_evidence_still_withdraws(reviewed_inputs):
    canonical, evidence, snapshot = reviewed_inputs
    evidence.write_text("{}", encoding="utf-8", newline="\n")
    result = run_cli("--canonical", canonical, "--snapshot", snapshot, "--evidence", evidence)
    assert result.returncode == 0
    delta = json.loads(result.stdout)
    assert delta["claim_check"] == "EVALUATED"
    assert [row["ref"] for row in delta["withdrawn_public"]] == ["screen"]


def test_missing_evidence_cannot_advance_with_matching_receipt(reviewed_inputs, helper, tmp_path):
    canonical, _evidence, snapshot = reviewed_inputs
    current = helper.normalize_canonical(catalog(record()))
    current["source"] = "canonical"
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "current_digest": helper.digest(current),
        "previous_digest": helper.digest(json.loads(snapshot.read_text(encoding="utf-8"))),
        "content_reviewed": True,
        "draft_prs": [{"url": "https://github.com/example/surfaces/pull/1", "isDraft": True,
                       "state": "OPEN", "surfaces": ["resume", "linkedin", "website", "readme"]}]}),
        encoding="utf-8", newline="\n")
    before = snapshot.read_bytes()
    result = run_cli("--canonical", canonical, "--snapshot", snapshot,
                     "--update-snapshot", "--review-receipt", receipt)
    assert result.returncode != 0
    assert snapshot.read_bytes() == before


def test_unavailable_evidence_preserves_catalog_metadata_changes(reviewed_inputs):
    canonical, _evidence, snapshot = reviewed_inputs
    canonical.write_text(json.dumps(catalog(record(subdomains=["updated"]))),
                         encoding="utf-8", newline="\n")
    result = run_cli("--canonical", canonical, "--snapshot", snapshot)
    delta = json.loads(result.stdout)
    assert delta["claim_check"] == "NOT_EVALUATED"
    assert delta["metadata_changed"] == ["screen"]
    assert delta["withdrawn_public"] == []


@pytest.mark.parametrize("contents", ["not json", "null", "[]"])
def test_invalid_evidence_fails_closed(reviewed_inputs, contents):
    canonical, evidence, snapshot = reviewed_inputs
    evidence.write_text(contents, encoding="utf-8", newline="\n")
    before = snapshot.read_bytes()
    result = run_cli("--canonical", canonical, "--snapshot", snapshot, "--evidence", evidence)
    assert result.returncode != 0
    assert result.stdout == ""
    assert snapshot.read_bytes() == before


def test_snapshot_update_rejects_junction_parent(tmp_path, helper, monkeypatch):
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text("{}", encoding="utf-8", newline="\n")
    monkeypatch.setattr(Path, "is_junction", lambda p: p == tmp_path, raising=False)
    with pytest.raises(ValueError):
        helper.atomic_snapshot(snapshot, {"paths": []})
    assert snapshot.read_text(encoding="utf-8") == "{}"


def test_snapshot_update_rejects_reparse_parent(tmp_path, helper, monkeypatch):
    from stat import FILE_ATTRIBUTE_REPARSE_POINT
    from types import SimpleNamespace

    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text("{}", encoding="utf-8", newline="\n")
    original = Path.lstat

    def observed_stat(path):
        observed = original(path)
        if path == tmp_path:
            return SimpleNamespace(st_mode=observed.st_mode,
                                   st_file_attributes=FILE_ATTRIBUTE_REPARSE_POINT)
        return observed

    monkeypatch.setattr(Path, "lstat", observed_stat)
    with pytest.raises(ValueError):
        helper.atomic_snapshot(snapshot, {"paths": []})
    assert snapshot.read_text(encoding="utf-8") == "{}"


@pytest.mark.parametrize("new_status", ["removed", "roadmap", "internal"])
@pytest.mark.parametrize("evidence_mode", ["omitted", "absent", "empty-path"])
def test_unavailable_evidence_preserves_catalog_withdrawals(reviewed_inputs, new_status, evidence_mode):
    canonical, evidence, snapshot = reviewed_inputs
    updated = catalog() if new_status == "removed" else catalog(record(status=new_status))
    canonical.write_text(json.dumps(updated), encoding="utf-8", newline="\n")
    arguments = {"omitted": [], "absent": ["--evidence", evidence.with_name("absent.json")],
                 "empty-path": ["--evidence", ""]}
    for mode in ([], ["--draft-packet"]):
        result = run_cli("--canonical", canonical, "--snapshot", snapshot,
                         *arguments[evidence_mode], *mode)
        assert result.returncode == 0
        delta = json.loads(result.stdout)
        assert delta["claim_check"] == "NOT_EVALUATED"
        if mode:
            assert delta["withdrawals"] == ["screen"]
            assert delta["removed_paths"] or delta["status_changed"]
        else:
            assert [row["ref"] for row in delta["withdrawn_public"]] == ["screen"]


def test_environment_evidence_is_shared_with_advancement(reviewed_inputs, helper, tmp_path):
    canonical, evidence, snapshot = reviewed_inputs
    result = run_cli("--canonical", canonical, "--snapshot", snapshot, evidence_env=evidence)
    assert result.returncode == 0
    delta = json.loads(result.stdout)
    assert delta["counts"]["claimable_public"] == 1
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({
        "current_digest": delta["current_digest"], "previous_digest": delta["previous_digest"],
        "content_reviewed": True,
        "draft_prs": [{"url": "https://github.com/example/surfaces/pull/1", "isDraft": True,
                       "state": "OPEN", "surfaces": ["resume", "linkedin", "website", "readme"]}]}),
        encoding="utf-8", newline="\n")
    result = run_cli("--canonical", canonical, "--snapshot", snapshot,
                     "--update-snapshot", "--review-receipt", receipt, evidence_env=evidence)
    assert result.returncode == 0
    saved = json.loads(snapshot.read_text(encoding="utf-8"))
    assert helper.digest(saved) == delta["current_digest"]


def test_draft_packet_exposes_unreviewed_catalog_additions(helper):
    current = helper.normalize_canonical(catalog(record(), record("future", "roadmap")))
    packet = helper.draft_packet(helper.compute_delta(current, {"paths": []}, evidence_available=False))
    assert {row["ref"] for row in packet["new_paths"]} == {"screen", "future"}
    assert packet["public_additions"] == []
    assert packet["public_count"] is None


def test_evaluated_reason_does_not_assert_reviewed_claims(helper):
    current = helper.normalize_canonical(catalog(record()))
    delta = helper.compute_delta(current, {"paths": []})
    assert delta["claim_reason"] == "The evidence mapping was read."
    assert delta["counts"]["claimable_public"] == 0
