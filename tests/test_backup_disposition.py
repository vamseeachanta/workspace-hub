from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "data" / "backup_disposition.py"
)
spec = importlib.util.spec_from_file_location("backup_disposition", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["backup_disposition"] = module
spec.loader.exec_module(module)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _backup_and_active(tmp_path: Path) -> tuple[Path, Path]:
    backup = tmp_path / "ClientAcma.preexisting-before-repo-move-20260520-075928"
    active = tmp_path / "acma-projects"
    return backup, active


def test_fully_redundant_backup_is_classified_against_active_tree(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "engineering" / "model.dat", "payload-a")
    _write(backup / "engineering" / "notes.txt", "payload-b")
    _write(active / "engineering" / "model.dat", "payload-a")
    _write(active / "engineering" / "notes.txt", "payload-b")

    comparison = module.compare_backup_to_active(backup, active)

    assert comparison.classification == "fully_redundant"
    assert comparison.unique_file_count == 0
    assert comparison.overlap_file_count == 2
    assert comparison.backup_file_count == 2


def test_partially_unique_backup_lists_unique_count(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "engineering" / "model.dat", "payload-a")
    _write(backup / "engineering" / "secret-bid.xlsx", "payload-unique")
    _write(active / "engineering" / "model.dat", "payload-a")

    comparison = module.compare_backup_to_active(backup, active)

    assert comparison.classification == "partially_unique"
    assert comparison.unique_file_count == 1
    assert comparison.overlap_file_count == 1


def test_entirely_unique_backup_blocks_dedup_recommendation(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "engineering" / "model.dat", "payload-only-in-backup")
    _write(active / "engineering" / "model.dat", "payload-only-in-active")

    comparison = module.compare_backup_to_active(backup, active)

    assert comparison.classification == "entirely_unique"
    assert comparison.unique_file_count == 1
    assert comparison.overlap_file_count == 0


def test_inaccessible_active_tree_forces_incomplete_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "engineering" / "model.dat", "payload")
    _write(active / "engineering" / "model.dat", "payload")
    blocked = active / "blocked"
    blocked.mkdir()

    original_iterdir = Path.iterdir

    def fake_iterdir(path: Path):
        if path == blocked:
            raise PermissionError("synthetic denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    comparison = module.compare_backup_to_active(backup, active)

    assert comparison.classification == "incomplete_scan"


def test_high_disk_pressure_triggers_threshold_exceeded(tmp_path: Path) -> None:
    def fake_disk_usage(path):
        # 95% used: total=100, used=95, free=5
        return module.DiskUsageTriple(total=100, used=95, free=5)

    snapshot = module.measure_disk_pressure(tmp_path, disk_usage_fn=fake_disk_usage)

    assert snapshot.threshold_exceeded is True
    assert snapshot.severity == "high"
    assert 0.94 < snapshot.used_fraction < 0.96


def test_elevated_disk_pressure_between_85_and_95(tmp_path: Path) -> None:
    def fake_disk_usage(path):
        return module.DiskUsageTriple(total=100, used=88, free=12)

    snapshot = module.measure_disk_pressure(tmp_path, disk_usage_fn=fake_disk_usage)

    assert snapshot.threshold_exceeded is True
    assert snapshot.severity == "elevated"


def test_low_disk_pressure_does_not_trip_threshold(tmp_path: Path) -> None:
    def fake_disk_usage(path):
        return module.DiskUsageTriple(total=100, used=50, free=50)

    snapshot = module.measure_disk_pressure(tmp_path, disk_usage_fn=fake_disk_usage)

    assert snapshot.threshold_exceeded is False
    assert snapshot.severity == "normal"


def test_disposition_status_blocked_when_any_dependency_open(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "f.txt", "x")
    _write(active / "f.txt", "x")

    report = module.build_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[
            module.BlockedByItem(issue_id="#2731", status="open"),
            module.BlockedByItem(issue_id="#2732", status="closed"),
        ],
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=50, free=50),
    )

    assert report.disposition_status == "blocked"
    assert report.recommended_action.startswith("deferred:")
    assert "dependency" in report.recommended_action


def test_disposition_status_blocked_when_disk_pressure_high_even_with_redundancy(
    tmp_path: Path,
) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "f.txt", "x")
    _write(active / "f.txt", "x")

    report = module.build_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[],
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=95, free=5),
    )

    assert report.disposition_status == "blocked"
    assert "high_disk_pressure" in report.recommended_action


def test_disposition_status_ready_when_clean_state(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "f.txt", "x")
    _write(active / "f.txt", "x")

    report = module.build_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[module.BlockedByItem(issue_id="#2731", status="closed")],
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=40, free=60),
    )

    assert report.disposition_status == "ready_for_recommendation"
    assert report.recommended_action == "deferred:awaiting_approved_execution_issue"


def test_rendered_report_never_emits_destructive_command(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "engineering" / "model.dat", "payload")
    _write(active / "engineering" / "model.dat", "payload")

    report = module.build_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[],
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=40, free=60),
    )

    rendered = "\n".join(module.render_public_report(report))

    forbidden_command_patterns = [
        r"\brm\s+-",
        r"\bmv\s+/",
        r"\btar\s+-?-?c",
        r"\bshred\b",
        r"\bdd\s+if=",
        r"\bfind\s+.*-delete",
        r"\bgzip\b",
        r"\bzstd\b",
    ]
    for pattern in forbidden_command_patterns:
        assert not re.search(pattern, rendered), f"forbidden command leaked: {pattern}"


def test_rendered_report_redacts_client_names_and_raw_paths(tmp_path: Path) -> None:
    backup = (
        tmp_path / "VerySensitiveAcmaClient.preexisting-before-repo-move-20260520-075928"
    )
    active = tmp_path / "acma-projects"
    _write(backup / "Confidential Job" / "client-bid.xlsx", "payload")
    _write(active / "Confidential Job" / "client-bid.xlsx", "payload")

    report = module.build_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[],
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=40, free=60),
    )
    rendered = "\n".join(module.render_public_report(report))

    assert "VerySensitiveAcmaClient" not in rendered
    assert "Confidential Job" not in rendered
    assert "client-bid.xlsx" not in rendered
    assert str(tmp_path) not in rendered
    assert "/mnt/ace" not in rendered


def test_write_disposition_report_creates_redacted_markdown(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "Confidential" / "private.xlsx", "payload")
    _write(active / "Confidential" / "private.xlsx", "payload")
    output = tmp_path / "out" / "issue-2769-report.md"

    written = module.write_disposition_report(
        backup_root=backup,
        active_root=active,
        mount_path=tmp_path,
        blocked_by=[],
        output_path=output,
        disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=40, free=60),
    )

    assert written == output
    rendered = output.read_text(encoding="utf-8")
    assert "metadata-only" in rendered
    assert "Confidential" not in rendered
    assert "private.xlsx" not in rendered


def test_write_disposition_report_rejects_mnt_ace_output_target(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "f.txt", "x")
    _write(active / "f.txt", "x")

    with pytest.raises(module.OutputResidencyBlocked):
        module.write_disposition_report(
            backup_root=backup,
            active_root=active,
            mount_path=tmp_path,
            output_path=Path("/mnt/ace/issue-2769-report.md"),
            disk_usage_fn=lambda p: module.DiskUsageTriple(total=100, used=40, free=60),
        )


def test_phase_a_report_artifact_does_not_leak_raw_mnt_ace_path() -> None:
    report_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "reports"
        / "issue-2769-acma-premove-backup-disposition.md"
    )

    rendered = report_path.read_text(encoding="utf-8")

    assert "/mnt/ace" not in rendered


def test_parse_blocked_by_rejects_raw_path_dependency_identifier() -> None:
    with pytest.raises(ValueError):
        module._parse_blocked_by(["/mnt/ace/private-client-path:open"])


def test_parse_blocked_by_accepts_github_issue_dependency_identifier() -> None:
    assert module._parse_blocked_by(["#2747:open"]) == [
        module.BlockedByItem(issue_id="#2747", status="open")
    ]


def test_cli_writes_redacted_metadata_only_report(tmp_path: Path) -> None:
    backup, active = _backup_and_active(tmp_path)
    _write(backup / "ClientStuff" / "data.dat", "payload")
    _write(active / "ClientStuff" / "data.dat", "payload")
    output = tmp_path / "out" / "issue-2769-report.md"

    rc = module.main(
        [
            "--backup-root",
            str(backup),
            "--active-root",
            str(active),
            "--mount-path",
            str(tmp_path),
            "--output",
            str(output),
            "--dry-run",
        ]
    )

    assert rc == 0
    rendered = output.read_text(encoding="utf-8")
    assert "metadata-only" in rendered
    assert "ClientStuff" not in rendered
    assert "data.dat" not in rendered


def test_destructive_execution_helper_remains_blocked() -> None:
    with pytest.raises(module.DestructiveActionBlocked):
        module.execute_disposition_recommendation(
            action_kind="delete",
            backup_source_id="source:0001",
            dry_run=True,
        )


def test_non_destructive_kind_passes_dry_run_helper() -> None:
    # The only non-destructive disposition we allow at this phase is "retain".
    result = module.execute_disposition_recommendation(
        action_kind="retain",
        backup_source_id="source:0001",
        dry_run=True,
    )
    assert result.kind == "retain"
    assert result.executed is False
