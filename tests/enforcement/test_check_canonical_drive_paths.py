from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts/enforcement/check-canonical-drive-paths.sh"


def run_check(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=REPO_ROOT, capture_output=True, text=True)


def empty_baseline(tmp_path: Path) -> str:
    baseline = tmp_path / "baseline.txt"
    baseline.write_text("# empty\n")
    return str(baseline)


def test_lint_rejects_transport_path(tmp_path: Path) -> None:
    target = tmp_path / "bad.yaml"
    target.write_text("path: /mnt/remote/ace-linux-2/dde/x\n")  # abs-path-allowed
    result = run_check("--baseline", empty_baseline(tmp_path), str(target))
    assert result.returncode == 1
    assert "bad.yaml:1" in result.stdout


def test_lint_accepts_canonical(tmp_path: Path) -> None:
    target = tmp_path / "ok.yaml"
    target.write_text("paths:\n  - /mnt/dde/x\n  - /mnt/ace/y\n")  # abs-path-allowed
    result = run_check("--baseline", empty_baseline(tmp_path), str(target))
    assert result.returncode == 0, result.stdout + result.stderr


def test_lint_sentinel_allows_line(tmp_path: Path) -> None:
    target = tmp_path / "ok.yaml"
    target.write_text("note: /mnt/remote/<workstation>/dde  # transport-path-allowed\n")  # abs-path-allowed
    result = run_check("--baseline", empty_baseline(tmp_path), str(target))
    assert result.returncode == 0, result.stdout + result.stderr


def test_lint_baseline_ratchet(tmp_path: Path) -> None:
    target = tmp_path / "bad.yaml"
    target.write_text("a: /mnt/remote/ace-linux-2/dde/x\nb: /mnt/ace-data\n")  # abs-path-allowed
    baseline = tmp_path / "baseline.txt"
    baseline.write_text(f"{target.relative_to(REPO_ROOT) if target.is_relative_to(REPO_ROOT) else target}:1\n")
    result = run_check("--baseline", str(baseline), str(target))
    assert result.returncode == 1
    assert "bad.yaml:2" in result.stdout


def test_lint_update_baseline(tmp_path: Path) -> None:
    target = tmp_path / "bad.yaml"
    target.write_text("path: /mnt/ace-data/x\n")  # abs-path-allowed
    baseline = tmp_path / "baseline.txt"
    result = run_check("--update-baseline", "--baseline", str(baseline), str(target))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "bad.yaml:1" in baseline.read_text()


def test_lint_exempts_registry_alias_block(tmp_path: Path) -> None:
    target = tmp_path / "drive-index-registry.yml"
    target.write_text(
        "canonical_aliases:\n"
        "  /mnt/remote/ace-linux-2/dde: /mnt/dde\n"  # abs-path-allowed
        "defaults:\n"
        "  path: /mnt/remote/ace-linux-2/dde/x\n"  # abs-path-allowed
    )
    result = run_check("--baseline", empty_baseline(tmp_path), str(target))
    assert result.returncode == 1
    assert "drive-index-registry.yml:4" in result.stdout


def test_lint_bare_ace_data_rejected(tmp_path: Path) -> None:
    target = tmp_path / "bad.yaml"
    target.write_text("mount_root: /mnt/ace-data\n")  # abs-path-allowed
    result = run_check("--baseline", empty_baseline(tmp_path), str(target))
    assert result.returncode == 1
    assert "bad.yaml:1" in result.stdout
