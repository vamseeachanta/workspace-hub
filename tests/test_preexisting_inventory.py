from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "data" / "preexisting_inventory.py"
spec = importlib.util.spec_from_file_location("preexisting_inventory", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["preexisting_inventory"] = module
spec.loader.exec_module(module)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_classifies_duplicate_partial_unique_empty_symlink_and_hardlink_sources(tmp_path: Path) -> None:
    exact_a = tmp_path / "ClientAlpha.preexisting-before-repo-move-20260520-064502"
    exact_b = tmp_path / "ClientAlpha-copy.preexisting-before-repo-move-20260520-064502"
    partial = tmp_path / "ClientBeta.preexisting-before-repo-move-20260520-064502"
    unique = tmp_path / "ClientGamma.preexisting-before-repo-move-20260520-064502"

    _write(exact_a / "engineering" / "model.dat", "same model")
    _write(exact_a / "engineering" / "notes.txt", "same notes")
    _write(exact_b / "engineering" / "model.dat", "same model")
    _write(exact_b / "engineering" / "notes.txt", "same notes")
    _write(partial / "engineering" / "model.dat", "same model")
    _write(partial / "engineering" / "private-client-name.txt", "different")
    _write(unique / "only-here" / "result.csv", "unique")
    (unique / "empty-dir").mkdir(parents=True)
    os.symlink(exact_a / "engineering" / "model.dat", unique / "model-link")
    os.link(unique / "only-here" / "result.csv", unique / "only-here" / "result-hardlink.csv")

    manifest = module.build_inventory([exact_a, exact_b, partial, unique])
    recommendations = module.recommend_disposition(manifest)

    assert recommendations.by_source[manifest.source_id(exact_a)].classification == "exact_duplicate_tree"
    assert recommendations.by_source[manifest.source_id(exact_b)].classification == "exact_duplicate_tree"
    assert recommendations.by_source[manifest.source_id(partial)].classification == "partial_overlap"
    assert recommendations.by_source[manifest.source_id(unique)].classification == "unique_only"

    unique_record = manifest.sources[manifest.source_id(unique)]
    assert unique_record.empty_dir_count == 1
    assert unique_record.symlink_count == 1
    assert unique_record.hardlink_count == 2


def test_empty_only_source_is_classified_as_empty_not_unique(tmp_path: Path) -> None:
    empty_root = tmp_path / "ClientEmpty.preexisting-before-repo-move-20260520-064502"
    (empty_root / "nested-empty").mkdir(parents=True)

    manifest = module.build_inventory([empty_root])
    recommendations = module.recommend_disposition(manifest)

    assert recommendations.by_source[manifest.source_id(empty_root)].classification == "empty_only"


def test_source_ids_are_stable_when_roots_are_reordered(tmp_path: Path) -> None:
    first = tmp_path / "ClientOne.preexisting-before-repo-move-20260520-064502"
    second = tmp_path / "ClientTwo.preexisting-before-repo-move-20260520-064502"
    _write(first / "a.txt", "same")
    _write(second / "a.txt", "same")

    manifest_a = module.build_inventory([first, second])
    manifest_b = module.build_inventory([second, first])

    assert manifest_a.source_id(first) == manifest_b.source_id(first)
    assert manifest_a.source_id(second) == manifest_b.source_id(second)
    assert manifest_a.sources.keys() == manifest_b.sources.keys()


def test_inaccessible_paths_are_reported_without_aborting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "ClientDelta.preexisting-before-repo-move-20260520-064502"
    _write(root / "visible.txt", "visible")
    blocked = root / "blocked"
    blocked.mkdir()
    flaky_file = root / "flaky.txt"
    _write(flaky_file, "flaky")

    original_iterdir = Path.iterdir
    original_stat = Path.stat

    def fake_iterdir(path: Path):
        if path == blocked:
            raise PermissionError("synthetic denied")
        return original_iterdir(path)

    def fake_stat(path: Path, *args, **kwargs):
        if path == flaky_file:
            raise OSError("synthetic stat failure")
        return original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)
    monkeypatch.setattr(Path, "stat", fake_stat)

    manifest = module.build_inventory([root])
    recommendations = module.recommend_disposition(manifest)

    source = manifest.sources[manifest.source_id(root)]
    assert source.inaccessible_count == 2
    assert source.file_count == 1
    assert {error.reason for error in source.errors} == {"permission_denied", "oserror"}
    assert recommendations.by_source[source.source_id].classification == "incomplete_scan"


def test_incomplete_source_cannot_make_peer_exact_duplicate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    complete = tmp_path / "ClientComplete.preexisting-before-repo-move-20260520-064502"
    incomplete = tmp_path / "ClientIncomplete.preexisting-before-repo-move-20260520-064502"
    _write(complete / "engineering" / "model.dat", "same payload")
    _write(incomplete / "engineering" / "model.dat", "same payload")
    blocked = incomplete / "blocked"
    blocked.mkdir()

    original_iterdir = Path.iterdir

    def fake_iterdir(path: Path):
        if path == blocked:
            raise PermissionError("synthetic denied")
        return original_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    manifest = module.build_inventory([complete, incomplete])
    recommendations = module.recommend_disposition(manifest)

    assert recommendations.by_source[manifest.source_id(incomplete)].classification == "incomplete_scan"
    assert recommendations.by_source[manifest.source_id(complete)].classification == "partial_overlap"


def test_exact_duplicate_tree_requires_same_relative_layout(tmp_path: Path) -> None:
    first = tmp_path / "ClientLayoutA.preexisting-before-repo-move-20260520-064502"
    second = tmp_path / "ClientLayoutB.preexisting-before-repo-move-20260520-064502"
    _write(first / "engineering" / "model.dat", "same payload")
    _write(second / "renamed" / "model-copy.dat", "same payload")

    manifest = module.build_inventory([first, second])
    recommendations = module.recommend_disposition(manifest)

    assert recommendations.by_source[manifest.source_id(first)].classification == "partial_overlap"
    assert recommendations.by_source[manifest.source_id(second)].classification == "partial_overlap"


def test_relative_evidence_ids_are_source_scoped(tmp_path: Path) -> None:
    first = tmp_path / "ClientEvidenceA.preexisting-before-repo-move-20260520-064502"
    second = tmp_path / "ClientEvidenceB.preexisting-before-repo-move-20260520-064502"
    _write(first / "same" / "file.txt", "alpha")
    _write(second / "same" / "file.txt", "beta")

    manifest = module.build_inventory([first, second])
    first_record = manifest.sources[manifest.source_id(first)].file_records[0]
    second_record = manifest.sources[manifest.source_id(second)].file_records[0]

    assert first_record.relative_evidence_id != second_record.relative_evidence_id


def test_public_summary_redacts_client_names_raw_paths_and_sensitive_filenames(tmp_path: Path) -> None:
    root = tmp_path / "VerySensitiveClient.preexisting-before-repo-move-20260520-064502"
    _write(root / "Secret Project" / "sensitive-bid-client-name.xlsx", "numbers")

    manifest = module.build_inventory([root])
    recommendations = module.recommend_disposition(manifest)
    summary = module.public_summary(manifest, recommendations)

    rendered = "\n".join(summary)
    assert "VerySensitiveClient" not in rendered
    assert "Secret Project" not in rendered
    assert "sensitive-bid-client-name.xlsx" not in rendered
    assert str(tmp_path) not in rendered
    assert "/mnt/ace" not in rendered
    assert "source:" in rendered
    assert "evidence: redacted" in rendered
    assert module._evidence_id(root) not in rendered


def test_cli_writes_redacted_metadata_only_summary(tmp_path: Path) -> None:
    root = tmp_path / "PrivateClient.preexisting-before-repo-move-20260520-064502"
    _write(root / "Confidential Job" / "bid.xlsx", "numbers")
    output = tmp_path / "out" / "inventory-summary.md"

    result = module.main([str(root), "--summary-out", str(output), "--dry-run"])

    assert result == 0
    rendered = output.read_text(encoding="utf-8")
    assert "PrivateClient" not in rendered
    assert "Confidential Job" not in rendered
    assert "bid.xlsx" not in rendered
    assert str(tmp_path) not in rendered
    assert "metadata-only" in rendered
    assert module._evidence_id(root) not in rendered


def test_missing_root_is_reported_not_fatal(tmp_path: Path) -> None:
    missing = tmp_path / "MissingClient.preexisting-before-repo-move-20260520-064502"

    manifest = module.build_inventory([missing])

    source = manifest.sources[manifest.source_id(missing)]
    assert source.file_count == 0
    assert source.inaccessible_count == 1
    assert source.errors[0].reason == "missing_root"


def test_destructive_actions_are_blocked_and_do_not_call_mutation_functions(tmp_path: Path) -> None:
    root = tmp_path / "ClientEpsilon.preexisting-before-repo-move-20260520-064502"
    _write(root / "data.txt", "payload")
    calls: list[str] = []

    class MutatingOps:
        def move(self, *_args, **_kwargs):
            calls.append("move")

        def delete(self, *_args, **_kwargs):
            calls.append("delete")

        def archive(self, *_args, **_kwargs):
            calls.append("archive")

        def compress(self, *_args, **_kwargs):
            calls.append("compress")

    with pytest.raises(module.DestructiveActionBlocked):
        module.execute_disposition_actions(
            [module.DispositionAction(kind="delete", source_id="source:0001", target_id=None)],
            fs_ops=MutatingOps(),
            dry_run=True,
        )

    assert calls == []
