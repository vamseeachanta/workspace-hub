"""Decision-table tests derived independently from the documented prerequisites.

No device or service is accessed. The Boolean examples are synthetic inputs,
not observations of a phone, account, destination or installed application.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/operations/phone_media_sync.py"
SPEC = importlib.util.spec_from_file_location("phone_media_sync", SCRIPT)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


USB = {"automation_required": False, "usb_access": True, "manual_accepted": True}
PHOTO = {
    "automation_required": True,
    "photosync_entitlement": True,
    "actual_size_confirmed": True,
    "webdav_verified": True,
    "autotransfer_tested": True,
}
CLOUD = {
    "automation_required": True,
    "icloud_photos_enabled": True,
    "icloud_web_access": True,
    "adp_enabled": False,
    "reauth_accepted": True,
}


def test_unknown_inputs_do_not_become_confirmation():
    """Hand table: no supplied facts means no candidate can be qualified."""
    result = sync.evaluate({})
    assert result["decision"] == "AWAITING_SELECTION"
    assert result["selected"] is None
    assert {c["status"] for c in result["candidates"].values()} == {"NOT_EVALUATED"}
    assert result["trial_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("name,facts", [("usb", USB), ("photosync", PHOTO), ("icloudpd", CLOUD)])
def test_each_option_can_be_explicitly_selected(name, facts):
    """Each fixture supplies every prerequisite in the guide's Boolean table."""
    result = sync.evaluate({**facts, "backup_capacity_verified": True}, name)
    assert result["candidates"][name] == {
        "status": "ELIGIBLE", "blockers": [], "missing": []
    }
    assert result["decision"] == "PROPOSED"
    assert result["trial_status"] == "READY_FOR_TRIAL"
    assert result["selected"] == name


def test_no_selection_is_inferred_from_eligible_option():
    assert sync.evaluate(USB)["decision"] == "AWAITING_SELECTION"


@pytest.mark.parametrize("name,facts,key", [
    ("usb", USB, "usb_access"),
    ("usb", USB, "manual_accepted"),
    ("photosync", PHOTO, "photosync_entitlement"),
    ("photosync", PHOTO, "actual_size_confirmed"),
    ("photosync", PHOTO, "webdav_verified"),
    ("photosync", PHOTO, "autotransfer_tested"),
    ("icloudpd", CLOUD, "icloud_photos_enabled"),
    ("icloudpd", CLOUD, "icloud_web_access"),
    ("icloudpd", CLOUD, "reauth_accepted"),
])
def test_failed_prerequisite_blocks_option(name, facts, key):
    """Hand table: one false required fact makes the conjunction false."""
    result = sync.evaluate({**facts, key: False}, name)
    assert result["candidates"][name]["status"] == "BLOCKED"
    assert key in result["candidates"][name]["blockers"]
    assert result["decision"] == "BLOCKED"


def test_automation_blocks_manual_usb():
    result = sync.evaluate({**USB, "automation_required": True}, "usb")
    assert result["candidates"]["usb"]["blockers"] == ["automation_required"]


def test_adp_blocks_cloud_without_recommending_security_change():
    """icloudpd README prerequisites exclude ADP; no setting is changed."""
    result = sync.evaluate({**CLOUD, "adp_enabled": True}, "icloudpd")
    assert result["candidates"]["icloudpd"]["blockers"] == ["adp_enabled"]
    assert result["trial_status"] == "BLOCKED"


@pytest.mark.parametrize("name,facts", [("usb", USB), ("photosync", PHOTO), ("icloudpd", CLOUD)])
def test_missing_prerequisite_is_not_evaluated(name, facts):
    partial = dict(facts)
    del partial[next(key for key in facts if key != "automation_required")]
    result = sync.evaluate(partial, name)
    assert result["decision"] == "NEEDS_INPUT"
    assert result["trial_status"] == "NOT_EVALUATED"


def test_known_blocker_takes_precedence_over_unknowns():
    result = sync.evaluate({"adp_enabled": True}, "icloudpd")
    assert result["candidates"]["icloudpd"]["status"] == "BLOCKED"
    assert result["candidates"]["icloudpd"]["missing"]


@pytest.mark.parametrize("capacity,expected", [(None, "NOT_EVALUATED"), (False, "BLOCKED"), (True, "READY_FOR_TRIAL")])
def test_capacity_is_an_independent_trial_gate(capacity, expected):
    result = sync.evaluate({**USB, "backup_capacity_verified": capacity}, "usb")
    assert result["decision"] == "PROPOSED"
    assert result["trial_status"] == expected


@pytest.mark.parametrize("facts", [[], None, {"usb_access": 1}, {"usb_access": "yes"}, {"extra": True}])
def test_invalid_inputs_are_rejected(facts):
    with pytest.raises((ValueError, TypeError)):
        sync.evaluate(facts)


def test_unknown_selection_is_rejected():
    with pytest.raises(ValueError):
        sync.evaluate(USB, "other")


def test_cli_worked_example_is_read_only(tmp_path):
    """USB facts satisfy its three conditions; capacity permits a trial only."""
    path = tmp_path / "facts.json"
    original = json.dumps({**USB, "backup_capacity_verified": True})
    path.write_text(original)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--select", "usb"],
        capture_output=True, text=True, check=True,
    )
    assert json.loads(result.stdout)["trial_status"] == "READY_FOR_TRIAL"
    assert path.read_text() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("raw", ['{"usb_access":true,"usb_access":false}', '{"usb_access":NaN}', '{', '[]'])
def test_cli_rejects_ambiguous_or_invalid_json(tmp_path, raw):
    path = tmp_path / "facts.json"
    path.write_text(raw)
    result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert not result.stdout
    assert "Traceback" not in result.stderr


def test_cli_missing_file_has_bounded_error(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "absent.json")],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_cloud_requires_web_data_access():
    """Upstream README prerequisites explicitly require web data access."""
    result = sync.evaluate({key: value for key, value in CLOUD.items() if key != "icloud_web_access"}, "icloudpd")
    assert result["candidates"]["icloudpd"]["status"] == "NOT_EVALUATED"
    assert "icloud_web_access" in result["candidates"]["icloudpd"]["missing"]


def test_documented_fixture_and_worked_answer_agree():
    """Independent conjunction: manual + USB + no automation + capacity = trial."""
    root = SCRIPT.parents[2]
    path = root / "docs/operations/examples/phone-media-usb-facts.json"
    facts = json.loads(path.read_text())
    result = sync.evaluate(facts, "usb")
    assert result["decision"] == "PROPOSED"
    assert result["trial_status"] == "READY_FOR_TRIAL"
    guide = (root / "docs/operations/phone-media-incremental-sync.html").read_text()
    assert path.name in guide
    assert "READY_FOR_TRIAL" in guide
    assert "PROPOSED" in guide
