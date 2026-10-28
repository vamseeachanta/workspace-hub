"""Offline refresh examples; epoch and freshness arithmetic are hand-derived."""

import importlib.util
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ai/quota_snapshot.py"


def load():
    spec = importlib.util.spec_from_file_location("quota_snapshot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_at_and_source_age(tmp_path):
    """Unix epoch + one day = 86400 s; copied observations keep their old age."""
    module = load()
    out = tmp_path / "quota.json"
    module.write_snapshot({"agents": [
        {"provider": "codex", "source": "app-server-live", "pct_remaining": 79},
        {"provider": "claude", "source": "copied", "as_of": "1970-01-01T00:00:00Z"},
        {"provider": "gemini"},
    ]}, out, datetime(1970, 1, 2, tzinfo=UTC))
    result = json.loads(out.read_text())
    assert result["generated_at"] == {"iso8601": "1970-01-02T00:00:00Z", "epoch": 86400}
    assert result["timestamp"] == "1970-01-02T00:00:00Z"
    assert result["agents"][1]["as_of"] == "1970-01-01T00:00:00Z"
    assert result["agents"][2]["source"] == "unavailable"
    assert result["agents"][2]["as_of"] is None


def test_failed_write_preserves_previous(tmp_path, monkeypatch):
    module = load()
    out = tmp_path / "quota.json"
    out.write_text('previous bytes')

    def fail(*args):
        raise OSError("fixture rename denied")

    monkeypatch.setattr(module.os, "replace", fail)
    with pytest.raises(OSError):
        module.write_snapshot({"agents": []}, out, datetime.now(UTC))
    assert out.read_text() == 'previous bytes'


def test_malformed_input_preserves_previous(tmp_path):
    out = tmp_path / "quota.json"
    out.write_text("previous bytes")
    result = subprocess.run(["python3", str(SCRIPT), str(out)], input="bad JSON",
                            capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert out.read_text() == "previous bytes"


def test_query_writer_uses_snapshot_helper(tmp_path):
    """Real writer function, synthetic query result; no provider functions execute."""
    text = (ROOT / "scripts/ai/assessment/query-quota.sh").read_text()
    start = text.index("write_repo_quota()")
    function = text[start:text.index("\n}", start) + 2]
    out = tmp_path / "quota.json"
    env = dict(os.environ, REPO_ROOT=str(ROOT), REPO_QUOTA_FILE=str(out))
    subprocess.run(["bash", "-c", function + '\nwrite_repo_quota \'{"agents":[]}\''],
                   env=env, check=True, capture_output=True)
    assert "generated_at" in json.loads(out.read_text())


@pytest.mark.parametrize("broken", [False, True, "query_failure"])
def test_fixture_refresh_preserves_previous_on_query_failure(tmp_path, broken):
    """The shipped query orchestration runs with local stub provider functions."""
    import shutil

    root = tmp_path / "fixture"
    target = root / "scripts/ai/assessment"
    lib = target / "lib"
    lib.mkdir(parents=True)
    shutil.copy(ROOT / "scripts/ai/assessment/query-quota.sh", target / "query-quota.sh")
    shutil.copy(SCRIPT, target.parent / "quota_snapshot.py")
    (lib / "utils.sh").write_text("")
    (lib / "display.sh").write_text("")
    value = "invalid JSON" if broken is True else '{"provider":"codex","source":"fixture-cache","as_of":"1970-01-01T00:00:00Z"}'
    command = "return 1" if broken == "query_failure" else f"printf '%s' '{value}'"
    (lib / "providers.sh").write_text(
        "\n".join(f"query_{p}() {{ {command}; }}" for p in ["claude", "codex", "gemini"])
    )
    bin_dir = root / "bin"
    bin_dir.mkdir()
    git = bin_dir / "git"
    git.write_text('#!/bin/sh\nprintf "%s\\n" "$FIXTURE_ROOT"\n')
    git.chmod(0o755)
    out = root / "config/ai-tools/agent-quota-latest.json"
    out.parent.mkdir(parents=True)
    out.write_text("previous bytes")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(HOME=str(root / "user"), FIXTURE_ROOT=str(root), CLAUDE_SUBAGENT="0",
               PATH=str(bin_dir) + os.pathsep + env["PATH"])
    proc = subprocess.run(["bash", str(target / "query-quota.sh"), "--refresh", "--json"],
                          env=env, cwd=root, capture_output=True, text=True, check=False)
    if broken:
        assert proc.returncode != 0
        assert out.read_text() == "previous bytes"
    else:
        assert proc.returncode == 0, proc.stderr
        data = json.loads(out.read_text())
        assert data["generated_at"]["iso8601"].endswith("Z")
        assert isinstance(data["generated_at"]["epoch"], int)
        assert all(a["source"] == "fixture-cache" and a["as_of"] == "1970-01-01T00:00:00Z"
                   for a in data["agents"])


@pytest.mark.parametrize("failed", [False, True])
def test_cron_refresh_with_fake_query(tmp_path, failed):
    """The real cron wrapper uses a fake collector and fake report generators."""
    import shutil

    cron = tmp_path / "scripts/cron/provider-utilization-refresh.sh"
    cron.parent.mkdir(parents=True)
    shutil.copy(ROOT / "scripts/cron/provider-utilization-refresh.sh", cron)
    assess = tmp_path / "scripts/ai/assessment"
    assess.mkdir(parents=True)
    shutil.copy(SCRIPT, assess.parent / "quota_snapshot.py")
    collector = ("exit 1\n" if failed else
                 "printf '%s' '{\"agents\":[{\"provider\":\"codex\",\"source\":\"fixture\"}]}' | "
                 "python3 scripts/ai/quota_snapshot.py config/ai-tools/agent-quota-latest.json\n")
    (assess / "query-quota.sh").write_text(collector)
    quota = tmp_path / "config/ai-tools/agent-quota-latest.json"
    quota.parent.mkdir(parents=True)
    quota.write_text("previous bytes")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_uv = bin_dir / "uv"
    fake_uv.write_text(
        '#!/bin/sh\nmkdir -p docs/reports config/ai-tools\n'
        'for name in provider-utilization-weekly provider-routing-scorecard provider-work-queue '
        'provider-autolabel-candidates provider-kanban; do\n'
        '  printf "{}" > "config/ai-tools/$name.json"\n'
        '  printf "fixture" > "docs/reports/$name.md"\ndone\n'
        'printf "fixture" > docs/reports/provider-kanban-dashboard.md\n'
        'printf "fixture" > docs/reports/provider-kanban-dashboard.html\n'
    )
    fake_uv.chmod(0o755)
    env = dict(os.environ, HOME=str(tmp_path / "user"),
               PATH=str(bin_dir) + os.pathsep + os.environ["PATH"])
    proc = subprocess.run(["bash", str(cron)], env=env, capture_output=True, check=False)
    if failed:
        assert proc.returncode != 0
        assert quota.read_text() == "previous bytes"
    else:
        assert proc.returncode == 0, proc.stderr
        data = json.loads(quota.read_text())
        assert data["generated_at"]["iso8601"].endswith("Z")
        assert data["agents"][0]["source"] == "fixture"
        assert data["agents"][0]["as_of"] is None


@pytest.mark.parametrize("age,marker", [(21599, False), (21601, True), (None, True)])
def test_existing_statusline_age_gate(tmp_path, age, marker):
    """Policy 6 h = 6*60*60 = 21600 s; 21599 inside, 21601 outside.

    Missing legacy timestamp is undatable. A generated_at-only producer therefore
    cannot be consumed without retaining the existing timestamp compatibility key.
    """
    quota = tmp_path / "quota.json"
    data = {"agents": [{"provider": "codex", "week_pct": 21}]}
    now = 86400  # Hand calculation: one day after Unix epoch.
    if age is not None:
        data["timestamp"] = datetime.fromtimestamp(now - age, UTC).isoformat()
    quota.write_text(json.dumps(data))
    text = (ROOT / ".claude/statusline-command.sh").read_text()
    functions = text[text.index("iso_epoch() {"):text.index("primary_state=$(quota_file_state")]
    env = dict(os.environ, STATUSLINE_QUOTA_MAX_AGE_HOURS="6")
    proc = subprocess.run(["bash", "-c", functions + '\ndate() { echo 86400; }\nquota_file_state "$1"',
                           "fixture", str(quota)], env=env, capture_output=True, text=True, check=True)
    assert proc.stdout.strip() == ("stale" if marker else "fresh")
