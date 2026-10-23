"""Synthetic examples use integer bytes and independent arithmetic, not measurements."""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/phone_media/backup.py"


@pytest.fixture
def backup():
    spec = importlib.util.spec_from_file_location("phone_backup", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("free,expected", [(150, "READY"), (149, "BLOCKED"), (151, "READY")])
def test_capacity_boundary(backup, free, expected):
    """Hand calculation: next 100 + growth 10/month * 3 months + reserve 20 = 150 B."""
    result = backup.capacity_plan(free, 100, 10, 3, 20)
    assert result == {"required_bytes": 150, "headroom_bytes": free - 150,
                      "status": expected}


def test_zero_growth_and_empty_projection(backup):
    """Hand calculation: 0 + 0*0 + 0 = 0 B, so zero free space meets this projection."""
    assert backup.capacity_plan(0, 0, 0, 0, 0)["status"] == "READY"


@pytest.mark.parametrize("value", [-1, 1.5, True, float("nan"), "10"])
@pytest.mark.parametrize("position", range(5))
def test_capacity_rejects_invalid_input(backup, value, position):
    args = [100, 10, 1, 1, 0]
    args[position] = value
    with pytest.raises(ValueError):
        backup.capacity_plan(*args)


def test_large_integer_precision(backup):
    """Hand calculation: (2**60 + 1) - 2**60 = 1 B; float conversion loses it."""
    assert backup.capacity_plan(2**60 + 1, 2**60, 0, 0, 0)["headroom_bytes"] == 1


@pytest.fixture
def archive(tmp_path):
    source = tmp_path / "archive with spaces"
    source.mkdir()
    (source / "photo.bin").write_bytes(b"synthetic media")
    return source


def mock_tools(backup, monkeypatch, run):
    """Execute inspection locally in unit tests; replace only child transport.

    The integration tests below use the actual inspection subprocess.
    """
    def bounded(argv, **kwargs):
        if len(argv) == 4 and argv[2] == "_preflight":
            backup._validate_source(argv[3])
            return subprocess.CompletedProcess(argv, 0)
        return run(argv, **kwargs)

    monkeypatch.setattr(backup, "_run_bounded", bounded)


@pytest.fixture
def commands(backup, monkeypatch):
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0)

    mock_tools(backup, monkeypatch, run)
    return calls


def test_full_comparison_is_read_only(backup, archive, commands):
    assert backup.verify(archive, "archive:phone-media", 60, "notify") == 0
    argv, kwargs = commands[0]
    assert argv == ["rclone", "check", str(archive.resolve()), "archive:phone-media",
                    "--download", "--checkers", "1", "--transfers", "1"]
    assert 0 < kwargs["timeout"] <= 60
    assert len(commands) == 1
    assert (archive / "photo.bin").read_bytes() == b"synthetic media"


@pytest.mark.parametrize("kind", ["missing", "empty", "symlink", "file"])
def test_invalid_source_alerts_without_rclone(backup, tmp_path, commands, kind):
    source = tmp_path / "source"
    if kind == "empty":
        source.mkdir()
    elif kind == "symlink":
        source.symlink_to(tmp_path, target_is_directory=True)
    elif kind == "file":
        source.write_bytes(b"not a directory")
    assert backup.verify(source, "archive:phone-media", 60, "notify") != 0
    assert len(commands) == 1
    assert commands[0][0][0] == "notify"


@pytest.mark.parametrize("remote", ["", "local-directory", "-bad:path", "archive:",
                                    "archive:/", "archive:path\nother", "archive:.",
                                    "archive:./", "archive:..", "archive:../media",
                                    "archive:/./", "archive:media/../", "archive:media/./photo"])
def test_bad_remote_alerts(backup, archive, commands, remote):
    assert backup.verify(archive, remote, 60, "notify") != 0
    assert commands[0][0][0] == "notify"


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_bad_timeout_fails_without_unbounded_notification(backup, archive, commands, timeout):
    assert backup.verify(archive, "archive:media", timeout, "notify") != 0
    assert commands == []


@pytest.mark.parametrize("failure", [3, 7, "timeout", "missing"])
def test_failed_check_alerts(backup, archive, monkeypatch, failure):
    calls = []

    def run(argv, **kwargs):
        calls.append(argv)
        if argv[0] == "rclone":
            if failure == "timeout":
                raise subprocess.TimeoutExpired(argv, kwargs["timeout"])
            if failure == "missing":
                raise FileNotFoundError("unavailable")
            return subprocess.CompletedProcess(argv, failure)
        return subprocess.CompletedProcess(argv, 0)

    mock_tools(backup, monkeypatch, run)
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert [call[0] for call in calls] == ["rclone", "notify"]


def test_notification_failure_remains_failure(backup, archive, monkeypatch, capsys):
    def run(argv, **kwargs):
        raise FileNotFoundError("unavailable")

    mock_tools(backup, monkeypatch, run)
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert "notification failed" in capsys.readouterr().err


def test_cli_capacity(backup, capsys):
    assert backup.main(["plan", "--free-bytes", "150", "--next-bytes", "100",
                        "--growth-bytes-per-month", "10", "--months", "3",
                        "--reserve-bytes", "20"]) == 0
    assert json.loads(capsys.readouterr().out)["required_bytes"] == 150


def test_cli_capacity_blocked(backup, capsys):
    assert backup.main(["plan", "--free-bytes", "149", "--next-bytes", "100",
                        "--growth-bytes-per-month", "10", "--months", "3",
                        "--reserve-bytes", "20"]) != 0
    assert json.loads(capsys.readouterr().out)["status"] == "BLOCKED"


def test_cli_missing_policy_input(backup):
    with pytest.raises(SystemExit):
        backup.main(["plan", "--free-bytes", "10"])


def test_source_subtree_symlink_rejected(backup, archive, tmp_path, commands):
    (archive / "linked").symlink_to(tmp_path, target_is_directory=True)
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert commands[0][0][0] == "notify"


def test_walk_permission_error_alerts(backup, archive, monkeypatch, commands):
    def denied(*args, **kwargs):
        kwargs["onerror"](PermissionError("unreadable subtree"))

    monkeypatch.setattr(backup.os, "walk", denied)
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert commands[0][0][0] == "notify"


def test_notify_nonzero_is_visible(backup, archive, monkeypatch, capsys):
    mock_tools(backup, monkeypatch, lambda argv, **kw:
               subprocess.CompletedProcess(argv, 1))
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert "notification failed" in capsys.readouterr().err


def test_units_require_configuration_and_weekly_persistence():
    import configparser

    root = MODULE.parents[2] / "config/phone-media"
    service = configparser.ConfigParser(interpolation=None)
    service.read(root / "phone-media-backup-check.service")
    settings = service["Service"]
    assert not settings["EnvironmentFile"].startswith("-")
    assert "--alert-command ${PHONE_MEDIA_ALERT_COMMAND}" in settings["ExecStart"]
    assert "--timeout-seconds ${PHONE_MEDIA_TIMEOUT_SECONDS}" in settings["ExecStart"]
    assert settings["TimeoutStartSec"] == "1h"
    assert settings["TimeoutStopSec"] == "10s"
    assert service["Unit"]["OnFailure"] == "phone-media-backup-alert.service"
    alert = configparser.ConfigParser(interpolation=None)
    alert.read(root / "phone-media-backup-alert.service")
    assert alert["Service"]["EnvironmentFile"] != settings["EnvironmentFile"]
    assert alert["Service"]["TimeoutStartSec"] == "1min"
    assert "${PHONE_MEDIA_ALERT_COMMAND}" in alert["Service"]["ExecStart"]
    assert "python" not in alert["Service"]["ExecStart"]
    timer = configparser.ConfigParser(interpolation=None)
    timer.read(root / "phone-media-backup-check.timer")
    assert timer["Timer"]["OnCalendar"] == "weekly"
    assert timer["Timer"]["Persistent"] == "true"
    assert timer["Timer"]["Unit"] == "phone-media-backup-check.service"


def test_ambient_rclone_options_cannot_hide_differences(backup, archive, commands, monkeypatch):
    monkeypatch.setenv("RCLONE_EXCLUDE", "*")
    monkeypatch.setenv("RCLONE_SIZE_ONLY", "true")
    monkeypatch.setenv("RCLONE_PASSWORD_COMMAND", "private-password-helper")
    monkeypatch.setenv("RCLONE_CONFIG", "private-config")
    monkeypatch.setenv("RCLONE_CONFIG_ARCHIVE_TYPE", "drive")
    assert backup.verify(archive, "archive:media", 60, "notify") == 0
    env = commands[0][1]["env"]
    assert "RCLONE_EXCLUDE" not in env
    assert "RCLONE_SIZE_ONLY" not in env
    assert env["RCLONE_PASSWORD_COMMAND"] == "private-password-helper"
    assert env["RCLONE_CONFIG"] == "private-config"
    assert env["RCLONE_CONFIG_ARCHIVE_TYPE"] == "drive"


@pytest.mark.skipif(os.name == "nt", reason="executable fixtures use POSIX shebangs")
@pytest.mark.parametrize("code", [0, 1])
def test_real_subprocess_boundary(backup, archive, tmp_path, monkeypatch, code):
    """Fake external tools establish argv transport and notification, without remote I/O."""
    tools = tmp_path / "tools"
    tools.mkdir()
    marker = tmp_path / "notification.json"
    rclone = tools / "rclone"
    rclone.write_text(
        f"#!{sys.executable}\nimport sys\n"
        "assert sys.argv[1] == 'check'\n"
        "assert sys.argv[3] == 'archive:media'\n"
        "assert '--download' in sys.argv\n"
        f"sys.exit({code})\n"
    )
    notifier = tools / "notify"
    notifier.write_text(
        f"#!{sys.executable}\nimport json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['NOTIFICATION_MARKER']).write_text(json.dumps(sys.argv[1:]))\n"
    )
    rclone.chmod(0o700)
    notifier.chmod(0o700)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("NOTIFICATION_MARKER", str(marker))
    assert backup.verify(archive, "archive:media", 60, str(notifier)) == code
    assert marker.exists() == bool(code)
    if code:
        assert len(json.loads(marker.read_text())) == 1


@pytest.mark.parametrize("source", ["", pytest.param(" ", marks=pytest.mark.skipif(
    os.name == "nt", reason="Windows normalizes whitespace-only directory names")),
    "relative-archive"])
def test_source_must_be_explicit_and_absolute(backup, source, commands, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    directory = tmp_path / source
    directory.mkdir(exist_ok=True)
    (directory / "photo.bin").write_bytes(b"synthetic media")
    assert backup.verify(source, "archive:media", 60, "notify") != 0
    assert commands[0][0][0] == "notify"


def test_notification_timeout_is_reported(backup, archive, monkeypatch, capsys):
    def run(argv, **kwargs):
        if argv[0] == "rclone":
            return subprocess.CompletedProcess(argv, 1)
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    mock_tools(backup, monkeypatch, run)
    assert backup.verify(archive, "archive:media", 60, "notify") != 0
    assert "notification failed" in capsys.readouterr().err


def test_slow_walk_is_bounded(backup, archive, tmp_path, monkeypatch):
    """A stalled tree walk must expire before rclone starts."""
    original_walk = os.walk

    def slow_walk(*args, **kwargs):
        time.sleep(2)
        return original_walk(*args, **kwargs)

    wrapper = tmp_path / "slow_preflight.py"
    wrapper.write_text(
        "import os, runpy, time\n"
        "original_walk = os.walk\n"
        "def slow_walk(*args, **kwargs):\n"
        "    time.sleep(2)\n"
        "    return original_walk(*args, **kwargs)\n"
        "os.walk = slow_walk\n"
        f"runpy.run_path({str(MODULE)!r}, run_name='__main__')\n"
    )
    monkeypatch.setattr(backup, "__file__", str(wrapper))
    monkeypatch.setattr(os, "walk", slow_walk)
    alerts = []
    monkeypatch.setattr(backup, "_notify", lambda *args: alerts.append(args))
    launches = []
    original_popen = subprocess.Popen

    def launch(argv, **kwargs):
        launches.append(argv)
        return original_popen(argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)
    started = time.monotonic()
    assert backup.verify(archive, "archive:media", 0.2, "notify") == 1
    assert time.monotonic() - started < 1.5
    assert alerts == [("notify", 0.2)]
    assert len(launches) == 1 and launches[0][2] == "_preflight"


def test_subprocess_timeout_does_not_wait_after_kill(backup, monkeypatch):
    calls = []

    class StalledProcess:
        def __init__(self, argv, **kwargs):
            calls.append("start")

        def wait(self, timeout):
            calls.append("wait")
            assert timeout > 0
            raise subprocess.TimeoutExpired("tool", timeout)

        def kill(self):
            calls.append("kill")

    monkeypatch.setattr(subprocess, "Popen", StalledProcess)
    with pytest.raises(subprocess.TimeoutExpired):
        backup._run_bounded(["tool"], timeout=0.1)
    assert calls == ["start", "wait", "kill"]


def test_phone_tests_are_collected_by_hosted_workflow():
    workflow = MODULE.parents[2] / ".github/workflows/baseline-check.yml"
    assert "tests/phone_media" in workflow.read_text()


def test_preflight_and_comparison_share_one_deadline(backup, archive, monkeypatch):
    clock = [100.0]
    budgets = []

    def run(argv, **kwargs):
        budgets.append(kwargs["timeout"])
        if len(argv) == 4 and argv[2] == "_preflight":
            clock[0] += 7
            return subprocess.CompletedProcess(argv, 0)
        return subprocess.CompletedProcess(argv, 1 if argv[0] == "rclone" else 0)

    monkeypatch.setattr(backup.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(backup, "_run_bounded", run)
    assert backup.verify(archive, "archive:media", 10, "notify") == 1
    assert budgets == [10, 3, 10]  # Inspection, remaining comparison, separate alert.


def test_html_captions_are_first_table_children():
    from html.parser import HTMLParser

    class Tables(HTMLParser):
        def __init__(self):
            super().__init__()
            self.first_children = []
            self.awaiting_child = False

        def handle_starttag(self, tag, attrs):
            if self.awaiting_child:
                self.first_children.append(tag)
                self.awaiting_child = False
            if tag == "table":
                self.awaiting_child = True

    parser = Tables()
    parser.feed((MODULE.parents[2] / "docs/phone-media-backup.html").read_text())
    assert parser.first_children == ["caption", "caption"]


@pytest.mark.parametrize("kind", ["missing", "empty", "file", "relative"])
def test_real_preflight_rejects_invalid_source(backup, tmp_path, monkeypatch, kind, capsys):
    source = tmp_path / "source"
    if kind == "empty":
        source.mkdir()
    elif kind == "file":
        source.write_bytes(b"synthetic media")
    elif kind == "relative":
        source = Path("relative")
    alerts = []
    monkeypatch.setattr(backup, "_notify", lambda *args: alerts.append(args))
    launches = []
    original_popen = subprocess.Popen

    def launch(argv, **kwargs):
        launches.append(argv)
        return original_popen(argv, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", launch)
    assert backup.verify(source, "archive:media", 10, "notify") == 1
    assert len(launches) == 1 and launches[0][2] == "_preflight"
    assert alerts == [("notify", 10)]
    assert str(source) not in capsys.readouterr().err


def test_real_external_tool_timeout(backup):
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        backup._run_bounded([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.2)
    assert time.monotonic() - started < 1.5
