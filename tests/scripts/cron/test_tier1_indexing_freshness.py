"""Behavioral tests for scripts/cron/tier1-indexing-freshness.sh.

Issue: #2465 — daily tier-1 indexing freshness audit.

The script supports the following test-only env overrides:

* ``REPO_ROOT`` — root used by cadence-common.sh; we point this at a temp
  fixture instead of the live repo.
* ``TIER1_FRESHNESS_OUT_DIR`` — output dir override (default: ``$REPO_ROOT/docs/reports``).
* ``TIER1_FRESHNESS_LOG_DIR`` — log dir override (default: ``$REPO_ROOT/logs/freshness``).
* ``TIER1_FRESHNESS_BUSINESS_BRAIN`` — alternate path to BUSINESS_BRAIN.md.
* ``TIER1_FRESHNESS_CONTRACT`` — alternate path to upstream contract.
* ``TIER1_FRESHNESS_TODAY`` — override the YYYY-MM-DD stamp for deterministic
  artifact names in tests.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

LIVE_REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = LIVE_REPO_ROOT / "scripts/cron/tier1-indexing-freshness.sh"
LIB = LIVE_REPO_ROOT / "scripts/cron/lib/cadence-common.sh"

NEGATIVE_AUTHORITY_SENTENCE = (
    "MUST NOT treat any tier-1 indexing scorecard under docs/reports/ "
    "as required canonical authority"
)


# ─── Source-level guards ──────────────────────────────────────────────────


def test_script_exists_and_is_executable() -> None:
    assert SCRIPT.exists(), f"missing audit script at {SCRIPT}"
    assert os.access(SCRIPT, os.X_OK), f"audit script must be executable: {SCRIPT}"


def test_script_starts_with_bash_shebang_and_strict_mode() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "#!/usr/bin/env bash"
    # strict mode line must appear before any non-comment/non-blank statement
    found_strict = False
    for line in lines[1:80]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "set -" in line and "pipefail" in line and ("u" in line or "uo" in line):
            found_strict = True
        # Stop scanning at first non-comment line so we know strict mode wasn't shoved later
        break
    assert found_strict, "first executable line of the script must enable strict mode (set -uo pipefail)"


def test_script_sources_cadence_common() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "cadence-common.sh" in text
    assert "cadence_init_repo_root" in text


def test_script_has_no_hardcoded_absolute_paths() -> None:
    """Outside comments, the script must not reference ``/home/`` or ``/Users/``
    or ``/mnt/local-analysis/`` literally — paths must derive from ``REPO_ROOT``.

    Allowed: absolute paths that come from env vars or shell substitution.
    """
    text = SCRIPT.read_text(encoding="utf-8")
    code_lines = []
    for raw in text.splitlines():
        stripped = raw.lstrip()
        if stripped.startswith("#"):
            continue
        code_lines.append(raw)
    code = "\n".join(code_lines)
    for banned in ("/home/", "/Users/", "/mnt/local-analysis/", "/mnt/c/"):
        assert banned not in code, (
            f"script contains hardcoded absolute path fragment outside comments: {banned}"
        )


def test_script_makes_no_network_or_remote_calls() -> None:
    """Walk the script source for banned outbound invocations."""
    text = SCRIPT.read_text(encoding="utf-8")
    code_only = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    banned_tokens = (
        "curl ",
        "wget ",
        " nc ",
        "ssh ",
        "rsync ",
        "ping ",
        "git fetch",
        "git push",
    )
    for token in banned_tokens:
        assert token not in code_only, (
            f"script invokes banned outbound command: {token!r}"
        )


# ─── Live behaviour against fixtures ──────────────────────────────────────


def _make_fixture_repo(
    tmp_path: Path,
    *,
    repos: dict[str, dict[str, bool]] | None = None,
    write_contract: bool = True,
    legacy_reference: bool = False,
    add_backup_artifact_in: str | None = None,
) -> Path:
    """Build a synthetic workspace-hub root for the audit script.

    ``repos`` maps tier-1 repo name → dict of surface→present? overrides:
    keys: ``agents``, ``readme``, ``docs_readme``, ``operator_map``, ``registry``.
    Default = all surfaces present.
    """
    repos = repos or {}
    tier1 = ["workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website"]
    root = tmp_path / "workspace-hub-fixture"
    root.mkdir()

    # BUSINESS_BRAIN.md with the tier-1 table the audit must parse
    brain = root / "docs/BUSINESS_BRAIN.md"
    brain.parent.mkdir(parents=True, exist_ok=True)
    brain.write_text(
        "# brain fixture\n"
        "\n"
        "### Tier-1 (actively developed)\n"
        "| Repo | Domain | Language | Visibility |\n"
        "|------|--------|----------|------------|\n"
        + "".join(f"| {r} | x | y | public |\n" for r in tier1)
        + "\n### Tier-2 (skip me)\n"
        "| Repo | Domain |\n"
        "|------|--------|\n"
        "| should-not-appear | x |\n",
        encoding="utf-8",
    )

    # upstream contract
    contract = root / "docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    if write_contract:
        contract.write_text(
            "# Tier-1 contract fixture\n"
            "Required surfaces:\n"
            "- AGENTS.md\n"
            "- README.md\n"
            "- docs/README.md\n"
            "- docs/maps/<repo>-operator-map.md\n"
            "- docs/registry/module-routing.yaml\n",
            encoding="utf-8",
        )

    # workspace-hub root surfaces are co-located at root level.
    # Per upstream contract, the workspace-hub repo's surfaces live at root.
    # The other tier-1 repos live in subdirectories.
    for repo in tier1:
        cfg = repos.get(repo, {})
        # Determine target dir: workspace-hub uses root; siblings use sub-tree.
        base = root if repo == "workspace-hub" else (root / repo)
        if repo != "workspace-hub":
            base.mkdir(parents=True, exist_ok=True)
        if cfg.get("agents", True):
            (base / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
        if cfg.get("readme", True):
            (base / "README.md").write_text("# README\n", encoding="utf-8")
        if cfg.get("docs_readme", True):
            (base / "docs").mkdir(parents=True, exist_ok=True)
            (base / "docs" / "README.md").write_text("# docs\n", encoding="utf-8")
        if cfg.get("operator_map", True):
            (base / "docs" / "maps").mkdir(parents=True, exist_ok=True)
            (base / "docs" / "maps" / f"{repo}-operator-map.md").write_text(
                "# operator map\n", encoding="utf-8"
            )
        if cfg.get("registry", True):
            (base / "docs" / "registry").mkdir(parents=True, exist_ok=True)
            (base / "docs" / "registry" / "module-routing.yaml").write_text(
                "version: 1\n", encoding="utf-8"
            )

    # Optional source-hygiene artifact
    if add_backup_artifact_in:
        target = root / add_backup_artifact_in / "scripts"
        target.mkdir(parents=True, exist_ok=True)
        (target / "old_thing.py.bak").write_text("backup\n", encoding="utf-8")

    if legacy_reference:
        # AGENTS.md in workspace-hub references a non-existent file
        (root / "AGENTS.md").write_text(
            "# AGENTS\nSee `docs/legacy-product-doc-that-does-not-exist.md`\n",
            encoding="utf-8",
        )

    # Plans dir not required by the script
    (root / "docs" / "reports").mkdir(parents=True, exist_ok=True)
    return root


def _run_audit(root: Path, today: str = "2026-04-26") -> subprocess.CompletedProcess[str]:
    env = {**os.environ}
    env["REPO_ROOT"] = str(root)
    env["TIER1_FRESHNESS_TODAY"] = today
    return subprocess.run(
        ["bash", str(SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(root),
    )


def test_audit_exits_green_on_clean_fixture(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    res = _run_audit(root)
    assert res.returncode == 0, (
        f"green fixture should exit 0, got {res.returncode}\n"
        f"stdout={res.stdout}\nstderr={res.stderr}"
    )
    latest = root / "docs/reports/tier-1-indexing-freshness-latest.md"
    assert latest.exists()
    body = latest.read_text(encoding="utf-8")
    assert "Portfolio status: green" in body


def test_audit_exits_yellow_when_one_surface_missing(tmp_path: Path) -> None:
    root = _make_fixture_repo(
        tmp_path,
        repos={"digitalmodel": {"docs_readme": False}},
    )
    res = _run_audit(root)
    assert res.returncode == 1, (
        f"yellow fixture should exit 1, got {res.returncode}\n"
        f"stdout={res.stdout}\nstderr={res.stderr}"
    )
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert "Portfolio status: yellow" in body
    assert re.search(r"^### digitalmodel — yellow\b", body, flags=re.MULTILINE)


def test_audit_exits_red_when_multiple_surfaces_missing(tmp_path: Path) -> None:
    root = _make_fixture_repo(
        tmp_path,
        repos={
            "assetutilities": {
                "agents": False,
                "readme": False,
                "docs_readme": False,
            }
        },
    )
    res = _run_audit(root)
    assert res.returncode == 2, (
        f"red fixture should exit 2, got {res.returncode}\n"
        f"stdout={res.stdout}\nstderr={res.stderr}"
    )
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert "Portfolio status: red" in body
    assert "Action required:" in body
    assert re.search(r"^### assetutilities — red\b", body, flags=re.MULTILINE)


def test_audit_exits_red_when_contract_file_missing(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path, write_contract=False)
    res = _run_audit(root)
    assert res.returncode == 2, (
        f"contract-missing should exit 2, got {res.returncode}\n"
        f"stdout={res.stdout}\nstderr={res.stderr}"
    )
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert "Portfolio status: red" in body
    log_dir = root / "logs/freshness"
    log_files = list(log_dir.glob("*.log"))
    assert log_files, "evidence-line log must be written even on contract-missing"
    log_text = "\n".join(p.read_text(encoding="utf-8") for p in log_files)
    assert "task=tier1-indexing-freshness" in log_text
    assert "status=red" in log_text
    assert "reason=contract-missing" in log_text


def test_audit_emits_cron_health_evidence_line(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    res = _run_audit(root)
    assert res.returncode in (0, 1, 2)
    log_files = list((root / "logs/freshness").glob("*.log"))
    assert log_files, "audit must write log including evidence line"
    log_text = "\n".join(p.read_text(encoding="utf-8") for p in log_files)
    evidence = re.search(
        r"task=tier1-indexing-freshness\s+status=(green|yellow|red)\s+"
        r"artifact=(\S+)\s+log=(\S+)\s+ts=(\S+)",
        log_text,
    )
    assert evidence, f"evidence line missing or malformed in log:\n{log_text}"
    # iso8601-ish timestamp
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", evidence.group(4)), (
        f"evidence timestamp not iso8601: {evidence.group(4)!r}"
    )


def test_audit_writes_dated_snapshot_and_latest(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    _run_audit(root, today="2026-04-26")
    dated = root / "docs/reports/tier-1-indexing-freshness-2026-04-26.md"
    latest = root / "docs/reports/tier-1-indexing-freshness-latest.md"
    assert dated.exists(), "audit must write dated snapshot"
    assert latest.exists(), "audit must write -latest pointer"
    assert dated.read_text(encoding="utf-8") == latest.read_text(encoding="utf-8"), (
        "dated snapshot and -latest must be byte-identical for the same run"
    )


def test_audit_overwrites_latest_on_rerun(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    _run_audit(root, today="2026-04-26")
    latest = root / "docs/reports/tier-1-indexing-freshness-latest.md"
    first = latest.read_text(encoding="utf-8")
    _run_audit(root, today="2026-04-27")
    second = latest.read_text(encoding="utf-8")
    assert "2026-04-27" in second, "second run should write today's date"
    assert first != second or "2026-04-27" in first, (
        "second run should overwrite -latest, not append"
    )


def test_audit_report_contains_negative_authority_disclaimer(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    _run_audit(root)
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert NEGATIVE_AUTHORITY_SENTENCE in body


def test_audit_report_required_sections_present(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    _run_audit(root)
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    for heading in (
        "## Overall Status",
        "## Repo Status",
        "## Assumption Check",
    ):
        assert heading in body, f"report missing required section: {heading}"
    for repo in ("workspace-hub", "digitalmodel", "assetutilities", "aceengineer-website"):
        assert re.search(
            rf"^### {re.escape(repo)} — (green|yellow|red)\b",
            body,
            flags=re.MULTILINE,
        ), f"report missing per-repo subsection for {repo}"
    assert "Current concerns" in body
    assert "Next actions" in body


def test_audit_red_report_has_action_required_prefix(tmp_path: Path) -> None:
    root = _make_fixture_repo(
        tmp_path,
        repos={
            "assetutilities": {
                "agents": False,
                "readme": False,
                "docs_readme": False,
            }
        },
    )
    _run_audit(root)
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert re.search(r"^Action required:\s*\d+\s+tier-1\s+repo", body, flags=re.MULTILINE), (
        "red portfolio reports must prefix the report with 'Action required: N tier-1 repo(s)'"
    )


def test_audit_is_read_only_against_tier1_source_trees(tmp_path: Path) -> None:
    """Run audit; verify nothing was mutated outside docs/reports + logs."""
    root = _make_fixture_repo(tmp_path)
    # snapshot pre-run
    pre_snapshot = {}
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if rel.startswith(("docs/reports/", "logs/")):
                continue
            pre_snapshot[rel] = path.read_bytes()
    _run_audit(root)
    # verify pre-existing files unchanged
    for rel, content in pre_snapshot.items():
        target = root / rel
        assert target.exists(), f"audit deleted pre-existing file: {rel}"
        assert target.read_bytes() == content, (
            f"audit mutated tier-1 source-tree file: {rel}"
        )


def test_audit_evidence_line_artifact_path_resolves(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path)
    _run_audit(root)
    log_files = list((root / "logs/freshness").glob("*.log"))
    log_text = "\n".join(p.read_text(encoding="utf-8") for p in log_files)
    m = re.search(r"artifact=(\S+)", log_text)
    assert m, "evidence line must include artifact=<path>"
    artifact_path = Path(m.group(1))
    if not artifact_path.is_absolute():
        artifact_path = root / artifact_path
    assert artifact_path.exists(), (
        f"evidence-line artifact path does not exist: {artifact_path}"
    )


def test_audit_legacy_reference_drift_demotes_status(tmp_path: Path) -> None:
    root = _make_fixture_repo(tmp_path, legacy_reference=True)
    res = _run_audit(root)
    # legacy reference in workspace-hub AGENTS.md should at minimum yellow
    assert res.returncode in (1, 2), (
        f"legacy-reference fixture should exit yellow/red, got {res.returncode}\n"
        f"stdout={res.stdout}\nstderr={res.stderr}"
    )
    body = (
        root / "docs/reports/tier-1-indexing-freshness-latest.md"
    ).read_text(encoding="utf-8")
    assert re.search(r"^### workspace-hub — (yellow|red)\b", body, flags=re.MULTILINE), (
        "workspace-hub should be flagged yellow/red when AGENTS.md has broken refs"
    )
