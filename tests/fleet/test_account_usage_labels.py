"""The account-usage collector keeps physical host names out of the public tree (owner decision H01).

config/ai-tools/ai-accounts.yaml is PUBLIC. A host's ``ssh`` argv names hosts by
logical fleet label only (``user@ace-win-2``); the collector resolves each label
to its physical name at run time from the same private map the fleet snapshot
labeller reads (scripts/fleet/fleet_snapshot_labels.py), and never writes the
resolved argv anywhere. The published aggregate is checked against that map
before it is written. Every failure is closed: nothing is probed, or nothing is
written.

The physical names below are synthetic and chosen so they do not match the
identifier gate's hostname pattern.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
FLEET = REPO / "scripts/fleet/collect_account_usage_fleet.py"
CONFIG = REPO / "config/ai-tools/ai-accounts.yaml"

spec = importlib.util.spec_from_file_location("fleet_usage_labels", FLEET)
fleet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fleet)
fsl = fleet.fsl

MAP_TEXT = """\
# physical-name  logical-label
phys-box-a   ace-win-1
phys-box-b   ace-win-2
ace-linux-1  ace-linux-1
"""


@pytest.fixture()
def table(tmp_path: Path) -> dict:
    m = tmp_path / "fleet-label-map.txt"
    m.write_text(MAP_TEXT, encoding="utf-8")
    return fsl.load_map(m)


DOUBLE_HOP = ["/opt/bin/ts-ssh", "op@ace-win-2", "ssh", "-o", "BatchMode=yes", "op@ace-win-1"]


def test_ssh_argv_labels_resolve_to_physical_names(table):
    out = fleet.resolve_ssh_argv(DOUBLE_HOP, table)
    assert out == ["/opt/bin/ts-ssh", "op@phys-box-b", "ssh", "-o", "BatchMode=yes", "op@phys-box-a"]


def test_identity_label_resolves_to_itself(table):
    assert fleet.resolve_ssh_argv(["ssh", "ace-linux-1"], table) == ["ssh", "ace-linux-1"]


def test_label_missing_from_map_fails_closed(table):
    with pytest.raises(fsl.LabelError):
        fleet.resolve_ssh_argv(["ssh", "op@gpu-claw"], table)


def test_physical_name_in_config_argv_is_refused(table):
    with pytest.raises(fsl.LabelError) as exc:
        fleet.resolve_ssh_argv(["ssh", "op@phys-box-a"], table)
    assert "phys-box-a" not in str(exc.value)


def test_label_shared_by_two_physical_names_is_ambiguous(tmp_path):
    m = tmp_path / "map.txt"
    m.write_text("phys-one ace-win-1\nphys-two ace-win-1\n", encoding="utf-8")
    with pytest.raises(fsl.LabelError):
        fleet.resolve_ssh_argv(["op@ace-win-1"], fsl.load_map(m))


def test_run_probe_uses_resolved_argv_and_reports_label_only(table, monkeypatch):
    seen = {}

    class Done:
        returncode = 0
        stdout = b'{"captured_at": "2026-09-27T00:00:00+00:00", "providers": {}}'
        stderr = b""

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        return Done()

    monkeypatch.setattr(fleet.subprocess, "run", fake_run)
    host = {"ssh": DOUBLE_HOP, "remote_wrap": "powershell"}
    rec = fleet.run_probe("ace-win-1", host, 15, b"", table)
    assert rec["reachable"] is True and rec["host"] == "ace-win-1"
    assert seen["cmd"][1] == "op@phys-box-b" and seen["cmd"][5] == "op@phys-box-a"
    assert "phys-box" not in json.dumps(rec)


def test_run_probe_without_map_does_not_probe_a_list_argv(monkeypatch):
    monkeypatch.setattr(fleet.subprocess, "run", lambda *a, **k: pytest.fail("probed without a map"))
    rec = fleet.run_probe("ace-win-1", {"ssh": DOUBLE_HOP}, 15, b"", None)
    assert rec["reachable"] is False
    assert "label" in rec["note"]


def test_published_text_guard_rejects_physical_names_and_hostname_shapes(table):
    fleet.assert_publishable('{"hosts": {"ace-win-1": {"reachable": true}}}', table)
    with pytest.raises(fsl.LabelError):
        fleet.assert_publishable('{"note": "cannot reach phys-box-a"}', table)
    with pytest.raises(fsl.LabelError):
        fleet.assert_publishable('{"note": "cannot reach ws' + '123"}', table)


def _write_cfg(path: Path) -> Path:
    cfg = {
        "accounts": {"claude-owner": {"provider": "claude", "holder": "owner"}},
        "hosts": {"ace-win-1": {"claude": "claude-owner", "ssh": DOUBLE_HOP}},
    }
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def test_main_writes_nothing_when_output_carries_a_physical_name(tmp_path, monkeypatch):
    m = tmp_path / "map.txt"
    m.write_text(MAP_TEXT, encoding="utf-8")
    cfg = _write_cfg(tmp_path / "accounts.yaml")
    out, md = tmp_path / "out.json", tmp_path / "out.md"

    def leaky(label, host, timeout, src, table):
        return {"host": label, "reachable": True, "captured_at": "2026-09-27T00:00:00+00:00",
                "providers": {"claude": {"source": "unavailable", "error": "phys-box-a refused"}}}

    monkeypatch.setattr(fleet, "run_probe", leaky)
    rc = fleet.main(["--config", str(cfg), "--out", str(out), "--md", str(md), "--label-map", str(m)])
    assert rc == 2
    assert not out.exists() and not md.exists()


def test_main_refuses_to_publish_without_the_label_map(tmp_path, monkeypatch):
    cfg = _write_cfg(tmp_path / "accounts.yaml")
    out, md = tmp_path / "out.json", tmp_path / "out.md"
    monkeypatch.setattr(fleet, "run_probe", lambda *a: pytest.fail("probed without a map"))
    rc = fleet.main(["--config", str(cfg), "--out", str(out), "--md", str(md),
                     "--label-map", str(tmp_path / "absent.txt")])
    assert rc == 2
    assert not out.exists() and not md.exists()


def test_main_publishes_labels_when_clean(tmp_path, monkeypatch):
    m = tmp_path / "map.txt"
    m.write_text(MAP_TEXT, encoding="utf-8")
    cfg = _write_cfg(tmp_path / "accounts.yaml")
    out, md = tmp_path / "out.json", tmp_path / "out.md"

    def clean(label, host, timeout, src, table):
        assert table is not None
        return {"host": label, "reachable": True, "captured_at": "2026-09-27T00:00:00+00:00", "providers": {}}

    monkeypatch.setattr(fleet, "run_probe", clean)
    rc = fleet.main(["--config", str(cfg), "--out", str(out), "--md", str(md), "--label-map", str(m)])
    assert rc == 0
    assert "ace-win-1" in out.read_text(encoding="utf-8")
    assert "phys-box" not in out.read_text(encoding="utf-8") + md.read_text(encoding="utf-8")


def test_load_config_refuses_a_hostname_shaped_value(tmp_path):
    p = tmp_path / "accounts.yaml"
    p.write_text(yaml.safe_dump({
        "accounts": {"claude-owner": {"provider": "claude"}},
        "hosts": {"ace-win-1": {"claude": "claude-owner", "ssh": ["ssh", "op@ws" + "123"]}},
    }), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        fleet.load_config(p)
    assert exc.value.code == 2


def test_load_config_refuses_a_host_key_that_is_not_a_label(tmp_path):
    p = tmp_path / "accounts.yaml"
    p.write_text(yaml.safe_dump({
        "accounts": {"claude-owner": {"provider": "claude"}},
        "hosts": {"phys-box-a": {"claude": "claude-owner"}},
    }), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        fleet.load_config(p)
    assert exc.value.code == 2


def test_committed_account_map_names_hosts_by_label_only():
    text = CONFIG.read_text(encoding="utf-8")
    assert not fsl.HOSTNAME_SHAPE_RE.search(text), "hostname-shaped token in ai-accounts.yaml"
    cfg = yaml.safe_load(text)
    for label, host in cfg["hosts"].items():
        assert fsl.is_public_label(label)
        ssh = (host or {}).get("ssh")
        if isinstance(ssh, list):
            hosts = [a.split("@", 1)[1] for a in map(str, ssh) if "@" in a]
            assert hosts and all(fsl.is_public_label(h) for h in hosts), label
        elif ssh is not None:
            assert fsl.is_public_label(ssh), label
    # The committed file loads under the collector's own validation.
    fleet.load_config(CONFIG)
