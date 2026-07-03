from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
MIGRATION = REPO_ROOT / "scripts/data/document-index/migrate-canonical-paths.py"
PHASE_B = REPO_ROOT / "scripts/data/document-index/phase-b-claude-worker.py"


def load_migration():
    sys.path.insert(0, str(MIGRATION.parent))
    spec = importlib.util.spec_from_file_location("migrate_canonical_paths", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_migration_rewrites_dde_roots_and_preserves_warning(tmp_path: Path) -> None:
    mod = load_migration()
    target = tmp_path / "config.yaml"
    warning = mod.RETENTION_WARNING
    target.write_text(
        "sources:\n"
        "  dde_project:\n"
        f"{warning}"
        "    enabled: false\n"
        "    paths:\n"
        "      - /mnt/remote/dev-secondary/dde/documents\n"  # abs-path-allowed
        "    host: dev-secondary\n"
        "output:\n"
        "  summaries_dir: /mnt/remote/ace-linux-1/ace/data/document-index/summaries\n"  # abs-path-allowed
    )
    before_warning_count = target.read_text().count(warning)
    assert mod.migrate_file(target, mod.load_alias_map(), check=False)
    text = target.read_text()
    assert before_warning_count == 1
    assert text.count(warning) == 1
    assert "/mnt/dde/documents" in text  # abs-path-allowed
    assert "host: ace-linux-2" in text
    assert "/mnt/ace/data/document-index/summaries" in text  # abs-path-allowed


def test_migration_enforces_dde_disabled(tmp_path: Path) -> None:
    mod = load_migration()
    target = tmp_path / "config.yaml"
    target.write_text(
        "sources:\n"
        "  dde_project:\n"
        "    enabled: true\n"
        "    paths:\n"
        "      - /mnt/remote/dev-secondary/dde/Literature\n"  # abs-path-allowed
        "    host: dev-secondary\n"
    )
    assert mod.migrate_file(target, mod.load_alias_map(), check=False)
    text = target.read_text()
    assert "enabled: false" in text
    assert mod.RETENTION_WARNING in text
    assert "/mnt/dde/Literature" in text  # abs-path-allowed


def test_migration_idempotent_and_check_mode(tmp_path: Path) -> None:
    mod = load_migration()
    target = tmp_path / "catalog.yaml"
    target.write_text("path: /mnt/remote/ace-linux-2/dde/documents/a.pdf\n")  # abs-path-allowed
    assert mod.migrate_file(target, mod.load_alias_map(), check=True)
    assert "/mnt/remote/" in target.read_text()  # abs-path-allowed
    assert mod.migrate_file(target, mod.load_alias_map(), check=False)
    once = target.read_text()
    assert not mod.migrate_file(target, mod.load_alias_map(), check=False)
    assert target.read_text() == once


def test_migration_rewrites_dedup_report_keys(tmp_path: Path) -> None:
    mod = load_migration()
    target = tmp_path / "cross-drive-dedup-report.json"
    target.write_text(
        '{"pairs":[{"dde_path":"/mnt/remote/ace-linux-2/dde/documents/a.pdf",'  # abs-path-allowed
        '"ace_path":"/mnt/ace/docs/a.pdf"}]}\n'  # abs-path-allowed
    )
    assert mod.migrate_file(target, mod.load_alias_map(), check=False)
    text = target.read_text()
    assert "/mnt/dde/documents/a.pdf" in text  # abs-path-allowed
    assert "/mnt/remote/" not in text  # abs-path-allowed


def test_migration_never_touches_frozen_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, str(MIGRATION), "--targets", "data/document-index/index.jsonl"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "refusing to migrate frozen index.jsonl" in (result.stdout + result.stderr)


def test_migration_preserves_structure_with_sentinel_history(tmp_path: Path) -> None:
    mod = load_migration()
    target = tmp_path / "mounted-source-registry.yaml"
    target.write_text(
        "entry:\n"
        "  mount_root: /mnt/ace-data/digitalmodel/docs/domains\n"  # abs-path-allowed
        "  symlink_note: /mnt/ace-data is a symlink to /mnt/ace\n"  # abs-path-allowed
    )
    assert mod.migrate_file(target, mod.load_alias_map(), check=False)
    parsed = yaml.safe_load(target.read_text())
    assert parsed["entry"]["mount_root"] == "/mnt/ace/digitalmodel/docs/domains"  # abs-path-allowed
    assert parsed["entry"]["symlink_note"].startswith("/mnt/ace-data is a symlink")  # abs-path-allowed
    assert "# transport-path-allowed" in target.read_text()


def test_phase_b_worker_uses_shared_map() -> None:
    source = PHASE_B.read_text()
    assert "PATH_REMAPS" not in source
    spec = importlib.util.spec_from_file_location("phase_b_claude_worker", PHASE_B)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(PHASE_B.parent))
    spec.loader.exec_module(module)
    assert module._remap_path("/mnt/remote/ace-linux-2/dde/documents/a.pdf") == "/mnt/dde/documents/a.pdf"  # abs-path-allowed
