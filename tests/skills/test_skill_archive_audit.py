"""Tests for the non-destructive skill archive-tree audit (#3062, epic #3058)."""
import importlib.util
import os

_SPEC = importlib.util.spec_from_file_location(
    "skill_archive_audit",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "skills", "skill_archive_audit.py"),
)
saa = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(saa)


def _make_tree(base, name, slugs):
    for slug in slugs:
        d = base / name / slug
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"# {slug}\n")
    return str(base / name)


def test_counts_skill_md(tmp_path):
    _make_tree(tmp_path, "arc", ["a", "b", "c"])
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["arc"])
    assert rows[0]["exists"] and rows[0]["skill_md"] == 3


def test_absent_tree_reported(tmp_path):
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["nope"])
    assert rows[0]["exists"] is False


def test_identical_trees_are_duplicates(tmp_path):
    _make_tree(tmp_path, "arc1", ["a", "b"])
    _make_tree(tmp_path, "arc2", ["a", "b"])
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["arc1", "arc2"])
    dups = saa.duplicate_groups(rows)
    assert len(dups) == 1 and set(dups[0]) == {"arc1", "arc2"}


def test_distinct_trees_not_duplicates(tmp_path):
    _make_tree(tmp_path, "arc1", ["a", "b"])
    _make_tree(tmp_path, "arc2", ["a", "c"])
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["arc1", "arc2"])
    assert saa.duplicate_groups(rows) == []


def test_symlink_detected(tmp_path):
    real = _make_tree(tmp_path, "real", ["a"])
    link = tmp_path / "link"
    os.symlink(real, link)
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["link"])
    assert rows[0]["is_symlink"] is True


def test_fingerprint_order_independent(tmp_path):
    # same slug set added in different on-disk order -> same fingerprint
    _make_tree(tmp_path, "arc1", ["b", "a"])
    _make_tree(tmp_path, "arc2", ["a", "b"])
    rows = saa.audit_archives(str(tmp_path), archive_dirs=["arc1", "arc2"])
    assert rows[0]["fingerprint"] == rows[1]["fingerprint"]
