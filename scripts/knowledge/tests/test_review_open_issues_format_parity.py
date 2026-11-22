"""Subprocess contracts for normal issue review; no authenticated CLI is used.

Independent synthetic example: issues 11 and 22 have category alpha, 33 has
category beta, and 44 and 55 have no category. Thus category (and its label
alias) counts are alpha=2, beta=1, uncategorized=2. Priorities cross categories:
high={11, 33}, low={22, 44}, unset={55}, giving counts 2, 2, 1. Each view has
2 + 1 + 2 = 5 issues. All expected identities and counts below come from this
hand calculation, not from importing the command. The forwarding probe uses
limit 7, independently chosen to differ from both the fixture size and default.
Exit statuses 0 (success) and 2 (invalid choice) follow the argparse contract.
The subprocess timeout is a test safety bound, not a performance requirement.
"""

import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml

CLI = Path(__file__).resolve().parents[1] / "review-open-issues.py"
FORMATS = ("table", "yaml", "json")
ISSUES = [
    {"number": 11, "title": "First item",
     "labels": [{"name": "enhancement"}, {"name": "cat:alpha"},
                {"name": "priority:high"}]},
    {"number": 22, "title": "Second item",
     "labels": [{"name": "cat:alpha"}, {"name": "priority:low"}]},
    {"number": 33, "title": "Third item",
     "labels": [{"name": "cat:beta"}, {"name": "priority:high"}]},
    {"number": 44, "title": "Fourth item",
     "labels": [{"name": "priority:low"}]},
    {"number": 55, "title": "Fifth item", "labels": []},
]
CATEGORY = {
    "alpha": (2, [(11, "First item"), (22, "Second item")]),
    "beta": (1, [(33, "Third item")]),
    "uncategorized": (2, [(44, "Fourth item"), (55, "Fifth item")]),
}
PRIORITY = {
    "high": (2, [(11, "First item"), (33, "Third item")]),
    "low": (2, [(22, "Second item"), (44, "Fourth item")]),
    "unset": (1, [(55, "Fifth item")]),
}


@pytest.fixture
def issue_cli(tmp_path):
    """An isolated executable search path makes a real gh call impossible."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    payload = tmp_path / "issues.json"
    calls = tmp_path / "calls.jsonl"
    stub = bin_dir / "gh"
    stub.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "with open(os.environ['ISSUE_STUB_CALLS'], 'a') as log:\n"
        "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "print(Path(os.environ['ISSUE_STUB_INPUT']).read_text())\n",
        encoding="utf-8",
    )
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    env = dict(os.environ, PATH=str(bin_dir),
               ISSUE_STUB_INPUT=str(payload), ISSUE_STUB_CALLS=str(calls))

    def run(*options, issues=ISSUES):
        payload.write_text(json.dumps(issues), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CLI), *options], cwd=tmp_path, env=env,
            capture_output=True, text=True, check=False, timeout=30,
        )
        recorded = ([json.loads(line) for line in calls.read_text().splitlines()]
                    if calls.exists() else [])
        return result, recorded

    return run


def parse_output(stdout, output_format):
    """Parse rendered data; retain counts and duplicate identities for checks."""
    if output_format != "table":
        data = (json.loads(stdout) if output_format == "json"
                else yaml.safe_load(stdout))
        assert set(data) == {"generated_at", "total_open", "groups"}
        # Only the generated timestamp is removed from the structured document.
        timestamp = data.pop("generated_at")
        assert timestamp.endswith("Z")
        assert datetime.fromisoformat(timestamp.replace("Z", "+00:00")).tzinfo
        return data

    data = {"groups": {}}
    current = None
    for line in stdout.splitlines():
        header = re.fullmatch(r"Category: (.+) \((\d+) issues\)", line)
        row = re.fullmatch(r"  #(\d+)\s+(.*?)\s{2,}(.*)", line)
        summary = re.fullmatch(
            r"Summary: (\d+) open issues across (\d+) categories", line)
        if header:
            name, count = header.groups()
            assert name not in data["groups"], "duplicate rendered group"
            current = {"count": int(count), "issues": []}
            data["groups"][name] = current
        elif row:
            assert current is not None
            number, title, labels = row.groups()
            current["issues"].append({
                "number": int(number), "title": title,
                "labels": labels.split(),
            })
        elif summary:
            assert "total_open" not in data, "duplicate summary"
            total, count = summary.groups()
            data["total_open"] = int(total)
            assert int(count) == len(data["groups"])
        else:
            assert line in (
                "", "  Action needed: review each group, decide keep/close/merge")
    assert "total_open" in data
    return data


def assert_view(data, expected, output_format):
    assert data["total_open"] == 5
    assert set(data["groups"]) == set(expected)
    all_numbers = []
    for name, (count, identities) in expected.items():
        group = data["groups"][name]
        assert group["count"] == count
        assert len(group["issues"]) == count
        assert [(issue["number"], issue["title"])
                for issue in group["issues"]] == identities
        all_numbers.extend(issue["number"] for issue in group["issues"])
        for issue in group["issues"]:
            source = next(item for item in ISSUES
                          if item["number"] == issue["number"])
            labels = [label["name"] for label in source["labels"]]
            if output_format == "table":
                labels = [label for label in labels
                          if label.startswith("priority:")]
            assert issue["labels"] == labels
    assert sorted(all_numbers) == [11, 22, 33, 44, 55]


@pytest.mark.parametrize("output_format", FORMATS)
@pytest.mark.parametrize("group_by, expected", (
    ("category", CATEGORY), ("priority", PRIORITY), ("label", CATEGORY),
))
def test_group_by_changes_membership_in_every_format(
        issue_cli, output_format, group_by, expected):
    result, calls = issue_cli("--format", output_format, "--group-by", group_by)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert len(calls) == 1
    assert calls[0][:2] == ["issue", "list"]
    assert_view(parse_output(result.stdout, output_format), expected,
                output_format)


@pytest.mark.parametrize("output_format", FORMATS)
def test_repo_and_limit_forwarded(issue_cli, output_format):
    result, calls = issue_cli(
        "--format", output_format, "--repo", "example/fixture", "--limit", "7")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert calls == [[
        "issue", "list", "--repo", "example/fixture", "--state", "open",
        "--limit", "7", "--json", "number,title,labels",
    ]]
    assert_view(parse_output(result.stdout, output_format), CATEGORY,
                output_format)


@pytest.mark.parametrize("output_format", FORMATS)
@pytest.mark.parametrize("group_by", ("category", "priority", "label"))
def test_empty_input(issue_cli, output_format, group_by):
    result, calls = issue_cli(
        "--format", output_format, "--group-by", group_by, issues=[])
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert len(calls) == 1
    # Empty YAML currently represents the groups mapping as null; assert that
    # representation explicitly rather than silently coercing it to a mapping.
    assert parse_output(result.stdout, output_format) == {
        "total_open": 0, "groups": None if output_format == "yaml" else {},
    }


def test_csv_rejected(issue_cli):
    result, calls = issue_cli("--format", "csv")
    assert result.returncode == 2
    assert result.stdout == ""
    assert "invalid choice: 'csv'" in result.stderr
    assert all(value in result.stderr for value in FORMATS)
    assert calls == []
