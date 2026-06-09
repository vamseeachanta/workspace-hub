"""Tests for scripts/cron/cron-audit.py (#2969, F2).

cron-audit.py carries a hyphen, so it is imported by file path. It in turn
imports the pure core cron_transaction.py (also by path). These tests exercise
the three required classifications end-to-end through the real loaders + the
real classify_line: a deckhand line -> preserved_external, a catalog line ->
cataloged, a random line -> uncataloged.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO_ROOT / "scripts" / "cron" / "cron-audit.py"
CRON_TX_PATH = REPO_ROOT / "scripts" / "cron" / "cron_transaction.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def audit():
    return _load_module("cron_audit_under_test", AUDIT_PATH)


@pytest.fixture(scope="module")
def ct():
    return _load_module("cron_transaction_under_test", CRON_TX_PATH)


# The 3 live deckhand cron lines on ace-linux-2 (from #2969 background).
DECKHAND_MEMBER_AUDIT = (
    "30 7 * * * PATH=/snap/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin; "
    "cd /mnt/local-analysis/deckhand && uv run --with telethon python3 "
    "scripts/deckhand/member-audit-cron.py >> $HOME/.hermes/logs/member-audit.log 2>&1"
)
DECKHAND_SWEEP = (
    "*/15 * * * * PATH=/home/linuxbrew/.linuxbrew/bin:/snap/bin:/usr/local/bin:/usr/bin:/bin; "
    "cd /mnt/local-analysis/.deckhand-sweep && git fetch -q origin main && "
    "git checkout -q --detach FETCH_HEAD && uv run --with pyyaml python3 "
    "scripts/deckhand/escalations.py sweep >> $HOME/.hermes/logs/escalation-sweep.log 2>&1"
)
DECKHAND_GUARD = (
    "17 * * * * PATH=/snap/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin; "
    "cd /mnt/local-analysis/.deckhand-guard && git fetch -q origin main && "
    "git checkout -q --detach FETCH_HEAD && uv run python3 "
    "scripts/deckhand/patch-health-check.py >> $HOME/.hermes/logs/patch-health.log 2>&1"
)


def test_deckhand_lines_are_preserved_external(audit, ct):
    fps = audit.load_external_fingerprints()
    assert fps, "preserved_external fingerprints must be loaded"
    for line in (DECKHAND_MEMBER_AUDIT, DECKHAND_SWEEP, DECKHAND_GUARD):
        assert ct.classify_line(line, [], fps) == "preserved_external", line


def test_deckhand_match_survives_path_log_and_wrapper_changes(audit, ct):
    """Fingerprints must match on stable bits only (cwd + basename)."""
    fps = audit.load_external_fingerprints()
    # Mutated: different PATH prefix, .venv python wrapper, different log target.
    mutated = (
        "30 7 * * * PATH=/totally/different/bin:/bin; "
        "cd /mnt/local-analysis/deckhand && .venv/bin/python "
        "scripts/deckhand/member-audit-cron.py >> /var/log/whatever.log 2>&1"
    )
    assert ct.classify_line(mutated, [], fps) == "preserved_external"


def test_catalog_line_is_cataloged(audit, ct):
    cmds = audit.load_catalog_commands()
    assert cmds, "catalog commands must be loaded"
    # A real live line invoking a catalogued script (with $WORKSPACE_HUB expanded).
    line = (
        "30 1 * * * PATH=/home/u/.local/bin:/bin; cd /home/u/workspace-hub && "
        "bash scripts/testing/run-benchmarks.sh >> /home/u/workspace-hub/logs/quality/benchmark.log 2>&1"
    )
    fps = audit.load_external_fingerprints()
    assert ct.classify_line(line, cmds, fps) == "cataloged"


def test_random_line_is_uncataloged(audit, ct):
    cmds = audit.load_catalog_commands()
    fps = audit.load_external_fingerprints()
    line = "0 3 * * * /usr/local/bin/some-rando-thing --do-stuff >> /tmp/x.log 2>&1"
    assert ct.classify_line(line, cmds, fps) == "uncataloged"


def test_audit_crontab_fails_closed_on_uncataloged(audit, ct):
    cmds = audit.load_catalog_commands()
    fps = audit.load_external_fingerprints()
    text = "\n".join(
        [
            "# a comment",
            "MAILTO=ops@example.com",
            DECKHAND_GUARD,
            "0 3 * * * /usr/local/bin/some-rando-thing >> /tmp/x.log 2>&1",
        ]
    )
    result = audit.audit_crontab(text, cmds, fps, ct.classify_line)
    assert result["counts"]["preserved_external"] == 1
    assert result["counts"]["uncataloged"] == 1
    assert result["counts"]["ignore"] == 2  # comment + MAILTO env line
    assert len(result["uncataloged"]) == 1


def test_stable_command_fragment_prefers_script_path(audit):
    cmd = (
        "PATH=$HOME/.local/bin:$PATH; cd $WORKSPACE_HUB && "
        "bash scripts/testing/run-benchmarks.sh >> $WORKSPACE_HUB/logs/x.log 2>&1"
    )
    assert audit.stable_command_fragment(cmd) == "scripts/testing/run-benchmarks.sh"


# ── #2988: preserved_local merges into the keep-verbatim bucket ──────────────
def test_preserved_local_merged_into_fingerprints(tmp_path):
    import importlib.util as _u, sys as _s
    spec = _u.spec_from_file_location("cron_audit_x", REPO_ROOT / "scripts" / "cron" / "cron-audit.py") \
        if "REPO_ROOT" in dir() else None
    # load module fresh by path
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[2]
    spec = _u.spec_from_file_location("cron_audit_x", root / "scripts" / "cron" / "cron-audit.py")
    m = _u.module_from_spec(spec); _s.modules["cron_audit_x"] = m; spec.loader.exec_module(m)
    classes = tmp_path / "hsc.yaml"
    classes.write_text(
        "preserved_external:\n  - fingerprint: {cwd_contains: /deckhand}\n"
        "preserved_local:\n  - fingerprint: {command_contains: scripts/maintenance/update-model-ids.sh}\n"
    )
    fps = m.load_external_fingerprints(classes)
    assert len(fps) == 2
    assert any(fp.get("command_contains") == "scripts/maintenance/update-model-ids.sh" for fp in fps)
