import subprocess
from pathlib import Path
from unittest.mock import patch
from scripts.ecosystem_sync.run import main
from scripts.ecosystem_sync.config import SyncConfig, RepoConfig


def _minimal_cfg(tmp_path: Path) -> SyncConfig:
    state_file = tmp_path / "state.yaml"
    digest_dir = tmp_path / "digests"
    return SyncConfig(
        repos=[RepoConfig(name="demo", path=str(tmp_path / "demo"), readme_sections=["Capabilities"])],
        issue_repo="vamseeachanta/aceengineer-website",
        digest_dir=str(digest_dir),
        state_file=str(state_file),
        max_issues_per_run=20,
    )


def test_doctor_success(tmp_path, monkeypatch):
    cfg = _minimal_cfg(tmp_path)
    (tmp_path / "demo").mkdir()
    subprocess.run(["git", "init", "-q", str(tmp_path / "demo")], check=True)
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")
    digest_dir = Path(cfg.digest_dir)
    digest_dir.mkdir(parents=True, exist_ok=True)

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "ok", "")
        rc = main(["--doctor"])
    assert rc == 0


def test_doctor_fails_on_missing_repo(tmp_path):
    cfg = _minimal_cfg(tmp_path)  # demo path does NOT exist
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg):
        rc = main(["--doctor"])
    assert rc != 0


def test_dry_run_writes_no_issues(tmp_path):
    cfg = _minimal_cfg(tmp_path)
    (tmp_path / "demo").mkdir()
    subprocess.run(["git", "init", "-q", str(tmp_path / "demo")], check=True)
    digest_dir = Path(cfg.digest_dir)
    digest_dir.mkdir(parents=True, exist_ok=True)
    state_file = Path(cfg.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("")

    with patch("scripts.ecosystem_sync.run.load_config", return_value=cfg), \
         patch("scripts.ecosystem_sync.run.open_issue_if_new") as mock_open, \
         patch("scripts.ecosystem_sync.signals.subprocess.run") as mock_sub:
        mock_sub.return_value = subprocess.CompletedProcess([], 0, "", "")
        rc = main(["--dry-run"])
    assert rc == 0
    assert mock_open.call_count == 0
