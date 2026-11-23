"""Tests for scripts/cron/mcp-re-eval.sh — TDD per #2316 plan."""

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "mcp-re-eval.sh"


def _mk_mcp_config(root: Path, repo: str, servers: dict):
    """Write a .mcp.json in tmp_path/repos/<repo>/.mcp.json with given servers."""
    repo_dir = root / repo
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / ".mcp.json").write_text(json.dumps({"mcpServers": servers}, indent=2))


def _baseline(quarter: str, usage: dict[str, int]) -> str:
    lines = [
        f"# mcp-re-eval — {quarter}",
        "",
        "**Status:** GREEN — seed baseline.",
        "",
        "## Per-MCP scorecard",
        "",
        "| MCP | Repos using | This Q | Last Q | Decision |",
        "|-----|-------------|--------|--------|----------|",
    ]
    for name, count in usage.items():
        lines.append(f"| {name} | {count} | {count} | — | keep |")
    lines.append("")
    return "\n".join(lines)


def _run(tmp_path: Path, repos: dict, baseline: str | None = None):
    scan_root = tmp_path / "scan"
    scan_root.mkdir(parents=True, exist_ok=True)
    for repo, servers in repos.items():
        _mk_mcp_config(scan_root, repo, servers)

    out_dir = tmp_path / "out"
    if baseline is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "mcp-re-eval-2026-Q1.md").write_text(baseline)

    env = os.environ.copy()
    env["MCP_OUT_DIR"] = str(out_dir)
    env["MCP_QUARTER"] = "2026-Q2"
    env["MCP_PREV_QUARTER"] = "2026-Q1"
    env["MCP_SCAN_ROOT"] = str(scan_root)
    env["REPO_ROOT"] = str(tmp_path)
    r = subprocess.run(["bash", str(SCRIPT)],
                       env=env, capture_output=True, text=True, timeout=15)
    return r, out_dir / "mcp-re-eval-2026-Q2.md"


def test_mcp_re_eval_lists_all_configured(tmp_path):
    repos = {
        "repo_a": {"server_x": {"command": "uvx"}, "server_y": {"command": "uvx"}},
        "repo_b": {"server_y": {"command": "uvx"}},
    }
    r, report = _run(tmp_path, repos)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "server_x" in body
    assert "server_y" in body


def test_mcp_re_eval_counts_usage(tmp_path):
    repos = {
        "repo_a": {"shared": {"command": "uvx"}},
        "repo_b": {"shared": {"command": "uvx"}},
        "repo_c": {"shared": {"command": "uvx"}},
    }
    r, report = _run(tmp_path, repos)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    # Row for "shared" should show 3 repos using
    scorecard = body.split("## Per-MCP scorecard", 1)[1].split("## ", 1)[0]
    assert "shared" in scorecard
    # the count column should include "3"
    shared_row = [ln for ln in scorecard.splitlines() if "shared" in ln and ln.startswith("|")]
    assert shared_row, "no row for 'shared'"
    assert "| 3 " in shared_row[0] or " 3 |" in shared_row[0]


def test_mcp_re_eval_green_when_all_positive(tmp_path):
    baseline = _baseline("2026-Q1", {"server_x": 2})
    repos = {
        "repo_a": {"server_x": {"command": "uvx"}},
        "repo_b": {"server_x": {"command": "uvx"}},
    }
    r, report = _run(tmp_path, repos, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body


def test_mcp_re_eval_yellow_on_one_regression(tmp_path):
    """One MCP dropped in usage since last quarter → YELLOW."""
    baseline = _baseline("2026-Q1", {"declining": 3})
    repos = {"repo_a": {"declining": {"command": "uvx"}}}  # now only 1 repo
    r, report = _run(tmp_path, repos, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** YELLOW" in body


def test_mcp_re_eval_red_on_multiple(tmp_path):
    baseline = _baseline("2026-Q1", {f"srv_{i}": 5 for i in range(4)})
    # All 4 dropped to 1 repo → 4 regressions → RED (block=3)
    repos = {"repo_a": {f"srv_{i}": {"command": "uvx"} for i in range(4)}}
    r, report = _run(tmp_path, repos, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** RED" in body


def test_mcp_re_eval_handles_first_run(tmp_path):
    repos = {"repo_a": {"server_x": {"command": "uvx"}}}
    r, report = _run(tmp_path, repos, baseline=None)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body
    # Last Q column should be "—" on first run
    scorecard = body.split("## Per-MCP scorecard", 1)[1].split("## ", 1)[0]
    assert "—" in scorecard


def test_mcp_re_eval_suggests_prunes(tmp_path):
    """MCP with declining value → listed in Recommended prunes."""
    baseline = _baseline("2026-Q1", {"unused": 5})
    repos = {"repo_a": {}}  # no servers at all → unused's count drops to 0
    r, report = _run(tmp_path, repos, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    prunes = body.split("## Recommended prunes", 1)[1].split("## ", 1)[0]
    assert "unused" in prunes
