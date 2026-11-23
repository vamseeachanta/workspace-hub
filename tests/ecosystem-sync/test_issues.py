import json
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock
from scripts.ecosystem_sync.issues import open_issue_if_new, IssueResult
from scripts.ecosystem_sync.models import Signal


def _sig():
    return Signal(
        repo="digitalmodel", kind="release",
        title="[sync] digitalmodel released v2.1.3",
        body="body",
        dedupe_key="release:digitalmodel:v2.1.3",
        payload={"tag": "v2.1.3"},
    )


def test_skips_when_open_dup_exists():
    fake_list = CompletedProcess(
        [], 0, stdout=json.dumps([{"number": 100, "title": "[sync] digitalmodel released v2.1.3"}]),
        stderr="",
    )
    with patch("subprocess.run", return_value=fake_list):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "skipped-duplicate"


def test_creates_when_no_dup():
    outputs = [
        CompletedProcess([], 0, stdout="[]", stderr=""),                     # list returns empty
        CompletedProcess([], 0, stdout="https://github.com/x/y/issues/5\n", stderr=""),  # create
    ]
    with patch("subprocess.run", side_effect=outputs):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "created"
    assert "issues/5" in (result.url or "")


def test_retry_once_on_create_failure():
    from subprocess import CalledProcessError
    outputs = [
        CompletedProcess([], 0, stdout="[]", stderr=""),  # list
        CalledProcessError(1, "gh", stderr="transient"),  # create fails
        CompletedProcess([], 0, stdout="https://github.com/x/y/issues/6\n", stderr=""),  # retry
    ]
    def side_effect(*a, **k):
        val = outputs.pop(0)
        if isinstance(val, CalledProcessError):
            raise val
        return val
    with patch("subprocess.run", side_effect=side_effect), \
         patch("time.sleep"):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "created"


def test_giveup_after_retry():
    from subprocess import CalledProcessError
    def side_effect(*a, **k):
        if "list" in a[0]:
            return CompletedProcess([], 0, stdout="[]", stderr="")
        raise CalledProcessError(1, "gh", stderr="permanent")
    with patch("subprocess.run", side_effect=side_effect), patch("time.sleep"):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "failed"


def test_dedupe_check_failure_returns_unknown():
    from subprocess import CalledProcessError
    with patch("subprocess.run", side_effect=CalledProcessError(1, "gh")):
        result = open_issue_if_new(_sig(), issue_repo="vamseeachanta/aceengineer-website")
    assert result.status == "dedupe-check-failed"
