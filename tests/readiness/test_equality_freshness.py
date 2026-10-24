"""Synthetic UTC examples, independently calculated by timestamp subtraction.

Clock 2026-10-22 12:00 UTC, policy TTL 24 hours: noon yesterday is exactly
24 hours old; one second later/earlier is inside/outside. A timestamp one
second ahead of the clock is skewed and cannot establish freshness.
"""
import importlib.util
from datetime import datetime
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "freshness_matrix", Path(__file__).resolve().parents[2]
    / "scripts/readiness/build-equality-matrix.py")
matrix = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(matrix)
NOW = datetime.fromisoformat("2026-10-22T12:00:00+00:00")


@pytest.mark.parametrize("stamp,verdict", [
    ("2026-10-22T12:00:00Z", "FRESH"),
    ("2026-10-21T12:00:01Z", "FRESH"),
    ("2026-10-21T12:00:00Z", "FRESH"),
    ("2026-10-21T11:59:59Z", "STALE"),
    (None, "STALE"), ("invalid", "STALE"),
    ("2026-10-22T12:00:01Z", "STALE"),
    ("2026-10-22T12:00:00", "STALE"),
    ("2026-10-22T14:00:00+02:00", "FRESH"),
])
def test_age_boundary(stamp, verdict):
    assert matrix.evidence_age({"generated_at": stamp}, now=NOW, ttl_hours=24)[1] == verdict


@pytest.mark.parametrize("ttl", [0, -1, float("nan"), float("inf")])
def test_ttl_must_be_positive_finite(ttl):
    with pytest.raises(ValueError):
        matrix.evidence_age({}, now=NOW, ttl_hours=ttl)


def test_stale_rows_do_not_vote_or_conform():
    """Two current identical values outvote nobody: the stale differing peer is excluded."""
    roster = {name: {"status": "active"} for name in ("current", "peer", "old")}
    reports = {name: {"generated_at": stamp, "provenance": {
        "dirty": False, "behind_main": 0, "ahead_main": 0, "origin_ref_age_h": 0},
        "dimensions": {"kanban": {"dispatch_queues": value}}}
        for name, stamp, value in (
            ("current", "2026-10-22T12:00:00Z", "same"),
            ("peer", "2026-10-22T11:00:00Z", "same"),
            ("old", "2026-10-20T12:00:00Z", "different"))}
    verdicts = matrix.matrix_verdicts(reports, {}, roster, [], now=NOW, ttl_hours=24)
    assert verdicts[("kanban", "current")] == "EQUAL"
    assert verdicts[("kanban", "old")] == "STALE"
    assert matrix.rollup_verdict(["STALE"])[0] == "STALE"
    rendered = matrix.freshness_table(reports, roster, now=NOW, ttl_hours=24)
    assert '<th>Age (hours)</th>' in rendered
    assert 'class="stale"' in rendered
    assert "2/3 fresh" in rendered
    assert "all conform" not in rendered.lower()


def test_unreadable_is_not_conformance():
    roster = {'broken': {'status': 'active'}}
    reports = {'broken': {'_error': 'unreadable'}}
    verdicts = matrix.matrix_verdicts(reports, {}, roster, [], now=NOW, ttl_hours=24)
    assert verdicts[('compute', 'broken')] == 'MISSING-EVIDENCE'
    assert 'UNREADABLE' in matrix.freshness_table(reports, roster, now=NOW, ttl_hours=24)


def test_cli_renders_five_row_example(tmp_path, monkeypatch, capsys):
    """The documentation example has two current timestamps and three stale ones."""
    import yaml

    state = tmp_path / 'input'
    state.mkdir()
    output = tmp_path / 'render'
    config = tmp_path / 'config.yaml'
    stamps = {'alpha': '2026-10-22T12:00:00Z', 'beta': '2026-10-21T12:00:01Z',
              'gamma': '2026-10-21T11:59:59Z', 'delta': None, 'epsilon': '2026-10-22T12:00:01Z'}
    config.write_text(yaml.safe_dump({'workstations': {m: {'status': 'active'} for m in stamps}}))
    for name, stamp in stamps.items():
        (state / f'equality-{name}.yaml').write_text(yaml.safe_dump(
            {'generated_at': stamp, 'dimensions': {}}))
    monkeypatch.setattr(matrix, 'CONFIG', config)
    monkeypatch.setattr(matrix, 'STATE', tmp_path / 'unused')
    monkeypatch.setattr(matrix, 'REPORTS', tmp_path / 'unused-render')
    monkeypatch.setattr(matrix.sys, 'argv', ['matrix', '--state-dir', str(state),
                        '--out-dir', str(output), '--now', NOW.isoformat(), '--ttl-hours', '24'])
    matrix.main()
    rendered = (output / 'machine-equality-matrix.html').read_text()
    assert '2/5 fresh active reports' in rendered
    assert rendered.count('<tr class="stale"><th>') == 3
    assert rendered.count('<tr class="fresh"><th>') == 2
    assert 'class="stale">STALE' in rendered

    capsys.readouterr()
    monkeypatch.setattr(matrix.sys, 'argv', ['matrix', '--json', '--machine=alpha',
                        '--now=' + NOW.isoformat(), '--state-dir=' + str(state)])
    matrix.main()
    import json
    assert set(json.loads(capsys.readouterr().out)) == {'alpha'}
