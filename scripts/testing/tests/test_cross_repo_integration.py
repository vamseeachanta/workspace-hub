"""TDD tests for run-cross-repo-integration.sh and cross-repo-graph.yaml."""
import os
import subprocess
import yaml
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
GRAPH_FILE = REPO_ROOT / "config/deps/cross-repo-graph.yaml"
SCRIPT = REPO_ROOT / "scripts/testing/run-cross-repo-integration.sh"


def test_graph_yaml_exists():
    assert GRAPH_FILE.exists(), f"Graph file missing: {GRAPH_FILE}"


def test_graph_yaml_has_required_keys():
    with open(GRAPH_FILE) as f:
        data = yaml.safe_load(f)
    assert "version" in data
    assert "graph" in data
    repos = {r["id"] for r in data["graph"]}
    assert "assetutilities" in repos
    assert "digitalmodel" in repos
    assert "worldenergydata" in repos
    assert "assethold" in repos


def test_graph_yaml_layer1_repos_have_pythonpath():
    with open(GRAPH_FILE) as f:
        data = yaml.safe_load(f)
    for repo in data["graph"]:
        if repo.get("layer", 0) == 1:
            assert "pythonpath" in repo, f"{repo['id']} missing pythonpath"
            assert len(repo["pythonpath"]) >= 2, f"{repo['id']} pythonpath too short"


def test_script_exists_and_is_executable():
    assert SCRIPT.exists(), f"Script missing: {SCRIPT}"
    assert os.access(SCRIPT, os.X_OK), f"Script not executable: {SCRIPT}"


def test_script_exits_1_on_unknown_repo():
    result = subprocess.run(
        [str(SCRIPT), "--repo", "nonexistent-repo-xyz"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "Should exit non-zero for unknown repo"


def test_skip_env_var_bypasses_checks():
    """SKIP_CROSS_REPO_CHECK=1 should exit 0 immediately."""
    env = os.environ.copy()
    env["SKIP_CROSS_REPO_CHECK"] = "1"
    result = subprocess.run(
        [str(SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"Bypass should exit 0, got {result.returncode}: {result.stderr}"
    )


@pytest.mark.integration
def test_script_runs_contracts_for_digitalmodel():
    """Integration test: runs real contract tests for digitalmodel."""
    result = subprocess.run(
        [str(SCRIPT), "--repo", "digitalmodel"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"digitalmodel contracts failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "PASS" in result.stdout or "pass" in result.stdout.lower()
