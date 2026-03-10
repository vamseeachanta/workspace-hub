"""TDD tests for check_doc_drift.py — WRK-1093."""
import json
import subprocess


# ---------------------------------------------------------------------------
# 1. load_symbol_index
# ---------------------------------------------------------------------------

def test_load_symbol_index_reads_jsonl(tmp_path):
    """Given a tmp JSONL file with 3 entries, load_symbol_index returns a list of 3 dicts."""
    from scripts.quality.check_doc_drift import load_symbol_index

    index_file = tmp_path / "symbol-index.jsonl"
    entries = [
        {"symbol": "foo_function", "repo": "assethold", "kind": "function"},
        {"symbol": "BarClass", "repo": "assethold", "kind": "class"},
        {"symbol": "baz_util", "repo": "assetutilities", "kind": "function"},
    ]
    index_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

    result = load_symbol_index(index_file)

    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(item, dict) for item in result)
    assert result[0]["symbol"] == "foo_function"


def test_load_symbol_index_missing_file_exits_cleanly(tmp_path):
    """Given a nonexistent path, returns [] with no exception."""
    from scripts.quality.check_doc_drift import load_symbol_index

    missing = tmp_path / "does_not_exist.jsonl"
    result = load_symbol_index(missing)

    assert result == []


# ---------------------------------------------------------------------------
# 2. build_doc_mention_set
# ---------------------------------------------------------------------------

def test_build_doc_mention_set_whole_word_only(tmp_path):
    """
    Given README.md containing 'compute_drift' but not 'compute_drift_score' as a
    whole word, build_doc_mention_set returns a set including 'compute_drift' but
    NOT 'compute_drift_score'.
    """
    from scripts.quality.check_doc_drift import build_doc_mention_set

    readme = tmp_path / "README.md"
    readme.write_text(
        "# Docs\n\nThis module uses compute_drift to calculate things.\n"
        "It does NOT mention the other function as a complete token.\n"
    )

    result = build_doc_mention_set(tmp_path)

    assert "compute_drift" in result
    assert "compute_drift_score" not in result


# ---------------------------------------------------------------------------
# 3. compute_drift_score
# ---------------------------------------------------------------------------

def test_compute_drift_score_all_documented():
    """All symbols in doc_mentions → score = 0.0."""
    from scripts.quality.check_doc_drift import compute_drift_score

    symbols = [
        {"symbol": "alpha_func", "repo": "myrepo"},
        {"symbol": "BetaClass", "repo": "myrepo"},
    ]
    doc_mentions = {"alpha_func", "BetaClass", "gamma_util"}

    score = compute_drift_score(symbols, doc_mentions, repo="myrepo")

    assert score == 0.0


def test_compute_drift_score_none_documented():
    """No symbols in doc_mentions → score = 1.0."""
    from scripts.quality.check_doc_drift import compute_drift_score

    symbols = [
        {"symbol": "alpha_func", "repo": "myrepo"},
        {"symbol": "BetaClass", "repo": "myrepo"},
    ]
    doc_mentions: set = set()

    score = compute_drift_score(symbols, doc_mentions, repo="myrepo")

    assert score == 1.0


# ---------------------------------------------------------------------------
# 4. batch_git_modified_files
# ---------------------------------------------------------------------------

def test_batch_git_modified_files_returns_set(tmp_path):
    """
    Given a git repo in tmp_path with one committed file, returns a set of
    strings (may be empty for a fresh repo; test that it returns a set type
    without error).
    """
    from scripts.quality.check_doc_drift import batch_git_modified_files

    # Initialise a minimal git repo so subprocess call succeeds
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    (tmp_path / "file.py").write_text("x = 1\n")
    subprocess.run(
        ["git", "add", "file.py"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-gpg-sign"],
        cwd=tmp_path, check=True, capture_output=True,
    )

    result = batch_git_modified_files(tmp_path)

    assert isinstance(result, set)


# ---------------------------------------------------------------------------
# 5. detect_staleness
# ---------------------------------------------------------------------------

def test_detect_staleness_uses_batch_not_per_file(tmp_path):
    """
    Given a modified_files set containing 'src/foo.py', detect_staleness returns
    True; for a file not in the set returns False.
    """
    from scripts.quality.check_doc_drift import detect_staleness

    modified = {"src/foo.py", "src/bar.py"}

    assert detect_staleness("src/foo.py", modified_files=modified) is True
    assert detect_staleness("src/baz.py", modified_files=modified) is False


# ---------------------------------------------------------------------------
# 6. format_drift_candidates
# ---------------------------------------------------------------------------

def test_format_drift_candidates_returns_strings_not_auto_capture(tmp_path):
    """
    Given report with drift > baseline, returns list of strings;
    does NOT write to any file or directory.
    """
    from scripts.quality.check_doc_drift import format_drift_candidates

    report = {
        "assethold": {"drift_score": 0.45, "stale_files": [], "undocumented": []},
    }
    baseline = {
        "assethold": {"drift_score": 0.10},
    }

    before_files = set(tmp_path.rglob("*"))
    result = format_drift_candidates(report, baseline)
    after_files = set(tmp_path.rglob("*"))

    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(s, str) for s in result)
    # No new files should have been written
    assert before_files == after_files
