from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = SOURCE_REPO_ROOT / "scripts" / "enforcement" / "compliance-dashboard.sh"


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def init_repo(path: Path) -> None:
    run(["git", "init", "-b", "main"], cwd=path)
    run(["git", "config", "user.name", "Test User"], cwd=path)
    run(["git", "config", "user.email", "test@example.com"], cwd=path)


def extract_json(stdout: str) -> dict[str, object]:
    marker = "JSON Report:\n"
    assert marker in stdout
    tail = stdout.split(marker, 1)[1]
    json_blob = tail.split("\n\nReport saved to:", 1)[0]
    return json.loads(json_blob)


def run_dashboard(repo_root: Path, env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.setdefault("COMPLIANCE_WINDOW_HOURS", "48")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_dashboard_summarizes_stage_prompt_drift_events(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "README.md").write_text("hello\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=tmp_path)
    run(["git", "commit", "-m", "feat(core): add dashboard coverage"], cwd=tmp_path)

    log_dir = tmp_path / "logs" / "hooks"
    log_dir.mkdir(parents=True)
    (log_dir / "stage-prompt-drift-events.jsonl").write_text(
        "\n".join(
            [
                '{"timestamp":"2026-04-10T01:00:00Z","branch":"main","base_ref":"origin/main","head_ref":"HEAD","strict_mode":"1","verdict":"pass","detail":"clean diff"}',
                '{"timestamp":"2026-04-10T02:00:00Z","branch":"main","base_ref":"origin/main","head_ref":"HEAD","strict_mode":"0","verdict":"warning","detail":"drift detected in advisory mode"}',
                '{"timestamp":"2026-04-10T03:00:00Z","branch":"feature/drift","base_ref":"origin/main","head_ref":"HEAD","strict_mode":"1","verdict":"fail","detail":"newly introduced stage prompt drift detected"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_dashboard(tmp_path)

    assert result.returncode == 1
    assert "Stage prompt drift events:" in result.stdout
    assert "Counts: pass=1, warning=1, fail=1, skip=0" in result.stdout
    assert "Latest event: 2026-04-10T03:00:00Z [fail] branch=feature/drift newly introduced stage prompt drift detected" in result.stdout

    payload = extract_json(result.stdout)
    stage_prompt_drift = payload["stage_prompt_drift"]
    assert payload["total_commits"] == 1
    assert payload["unreviewed"] == 1
    assert stage_prompt_drift["total_events"] == 3
    assert stage_prompt_drift["counts"] == {
        "pass": 1,
        "warning": 1,
        "fail": 1,
        "skip": 0,
        "unknown": 0,
    }
    assert stage_prompt_drift["latest_event"]["verdict"] == "fail"
    assert stage_prompt_drift["latest_event"]["branch"] == "feature/drift"


def test_dashboard_reports_missing_drift_log_even_without_commits(tmp_path: Path) -> None:
    init_repo(tmp_path)

    result = run_dashboard(tmp_path)

    assert result.returncode == 0
    assert "Note:               No commits in window" in result.stdout
    assert "Stage prompt drift events:" in result.stdout
    assert "Log file: missing" in result.stdout
    assert "Latest event: none recorded" in result.stdout

    payload = extract_json(result.stdout)
    assert payload["total_commits"] == 0
    assert payload["message"] == "No commits in window"
    assert payload["stage_prompt_drift"] == {
        "log_file": str(tmp_path / "logs" / "hooks" / "stage-prompt-drift-events.jsonl"),
        "present": False,
        "total_events": 0,
        "counts": {
            "pass": 0,
            "warning": 0,
            "fail": 0,
            "skip": 0,
            "unknown": 0,
        },
        "latest_event": None,
    }
