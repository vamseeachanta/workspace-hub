"""Unit tests for check_ruff_ratchet pure logic (#3146)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.quality import check_ruff_ratchet as r


def test_parse_found_errors():
    assert r._parse_error_count("...\nFound 473 errors.") == 473
    assert r._parse_error_count("Found 1 error.") == 1


def test_parse_all_checks_passed():
    assert r._parse_error_count("All checks passed!") == 0


def test_parse_empty_is_zero():
    assert r._parse_error_count("") == 0


def test_check_repo_pass_at_baseline():
    res = r.check_repo("au", 473, 473)
    assert res["status"] == "pass" and res["improved"] is False


def test_check_repo_improved_auto_lowers():
    res = r.check_repo("au", 473, 400)
    assert res["status"] == "pass" and res["improved"] is True


def test_check_repo_regression_fails():
    res = r.check_repo("au", 473, 474)
    assert res["status"] == "fail" and "regression of 1" in res["message"]


def test_check_repos_missing_is_failure():
    passes, failures = r.check_repos({"au": {"error_count": 5}}, {})
    assert not passes and failures[0]["status"] == "missing"


def test_check_repos_exempt_skipped():
    passes, failures = r.check_repos(
        {"x": {"error_count": 0, "exempt": True, "exempt_reason": "n/a"}}, {}
    )
    assert passes[0]["status"] == "exempt" and not failures


def test_validate_baseline_ok():
    assert r._validate_baseline({"repos": {"au": {"error_count": 5}}}) is None


def test_validate_baseline_missing_count():
    assert r._validate_baseline({"repos": {"au": {}}}) is not None


def test_validate_baseline_exempt_needs_reason():
    err = r._validate_baseline({"repos": {"au": {"error_count": 0, "exempt": True}}})
    assert err is not None and "exempt_reason" in err
