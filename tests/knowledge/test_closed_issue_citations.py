"""Synthetic offline FLOW-2 examples; expected lines are hand-counted below.

Issue numbers are arbitrary fixture identifiers, not measured constants. Line
numbers use Markdown's first-line-is-one convention. Counts enumerate the
literal references in each fixture, independently of the checker.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

# Repository layout: this file is inside tests/knowledge.
SCRIPT = Path(__file__).resolve().parents[2] / "scripts/knowledge/closed_issue_citations.py"
REPOSITORY = "ORG/REPO"
ISSUE_URL = f"https://github.com/{REPOSITORY}/issues/17"
PROMOTED = "knowledge/topic.md"


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("closed_issue_citations", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_report(checker, tmp_path, text, snapshot=None, **kwargs):
    doc = tmp_path / "docs" / "note.md"
    doc.parent.mkdir(exist_ok=True)
    doc.write_text(text, encoding="utf-8", newline="\n")
    return checker.report(
        [doc], root=tmp_path, repository=REPOSITORY,
        snapshot=snapshot if snapshot is not None else {"#17": {"state": "closed"}},
        domain_sections=["Basis"], operational_sections=["Tracking"], **kwargs,
    )


def test_closed_domain_citation_warns(checker, tmp_path):
    result = run_report(checker, tmp_path, "# Basis\nSee #17.\n", {
        "#17": {"state": "closed", "promoted_artifact": PROMOTED},
    })
    assert result["mode"] == "advisory"
    assert result["references"] == [{
        "file": "docs/note.md", "line": 2, "rule": "FLOW-2",
        "issue": ISSUE_URL, "state": "closed", "scope": "domain-knowledge",
        "status": "warning", "remediation_link": PROMOTED,
        "remediation": "Cite the promoted artifact and retain the issue as provenance if needed.",
    }]


def test_operational_reference_is_distinct(checker, tmp_path):
    refs = run_report(checker, tmp_path, "# Tracking\nClosed by #17.\n")["references"]
    assert [(r["scope"], r["status"], r["state"]) for r in refs] == [
        ("operational-reference", "operational-reference", "closed"),
    ]


@pytest.mark.parametrize("evidence", [{}, {"#17": {}}, {"#17": {"state": "unknown"}}])
def test_unknown_issue_state_is_explicit(checker, tmp_path, evidence):
    ref, = run_report(checker, tmp_path, "# Basis\nSee #17.\n", evidence)["references"]
    assert ref["state"] == "unknown"
    assert ref["status"] == "unknown-state"
    assert "snapshot" in ref["remediation"]


def test_open_issue_is_not_a_warning(checker, tmp_path):
    ref, = run_report(checker, tmp_path, "# Basis\nSee #17.\n", {"#17": {"state": "open"}})["references"]
    assert (ref["state"], ref["status"]) == ("open", "open-issue")


def test_no_keyword_classification_and_nested_scope(checker, tmp_path):
    text = "# Unselected\nDomain knowledge #17\n# Basis\n## Child\n#17\n## Tracking\n#17\n# Other\n#17\n"
    refs = run_report(checker, tmp_path, text)["references"]
    assert [(r["line"], r["scope"]) for r in refs] == [
        (2, "unscoped"), (5, "domain-knowledge"),
        (7, "operational-reference"), (9, "unscoped"),
    ]
    assert refs[0]["status"] == "unscoped"


def test_unknown_operational_state_stays_unknown(checker, tmp_path):
    ref, = run_report(checker, tmp_path, "# Tracking\n#17\n", {})["references"]
    assert (ref["scope"], ref["state"], ref["status"]) == (
        "operational-reference", "unknown", "unknown-state",
    )


def test_linked_unlinked_and_reference_style(checker, tmp_path):
    text = (f"# Basis\n[discussion]({ISSUE_URL}#issuecomment-example)\n"
            f"<{ISSUE_URL}>\n#17\n[discussion][ref]\n\n[ref]: {ISSUE_URL}\n")
    refs = run_report(checker, tmp_path, text)["references"]
    assert [(r["line"], r["issue"]) for r in refs] == [
        (2, ISSUE_URL), (3, ISSUE_URL), (4, ISSUE_URL), (5, ISSUE_URL),
    ]


def test_duplicate_references_once_per_line(checker, tmp_path):
    text = f"# Basis\n[#17]({ISSUE_URL}) #17 {ISSUE_URL}\n#17\n"
    refs = run_report(checker, tmp_path, text)["references"]
    assert [r["line"] for r in refs] == [2, 3]


def test_code_and_comments_are_not_citations_or_headings(checker, tmp_path):
    text = ("# Basis\n```md\n# Tracking\n#17\n```\n"
            "~~~~\n#17\n~~~\n#17\n~~~~\n"
            "    #17\n\t#17\n`#17` ``#17 ` nested``\n"
            "<!--\n# Tracking\n#17\n-->\n#17\n")
    refs = run_report(checker, tmp_path, text)["references"]
    # The only visible citation is the final, eighteenth line.
    assert [(r["line"], r["scope"]) for r in refs] == [(18, "domain-knowledge")]


def test_inline_code_can_cross_lines(checker, tmp_path):
    text = "# Basis\n`example\n#17`\n#17\n"
    refs = run_report(checker, tmp_path, text)["references"]
    assert [r["line"] for r in refs] == [4]


def test_promoted_link_does_not_imply_compliant_use(checker, tmp_path):
    ref, = run_report(checker, tmp_path, f"# Basis\n#17 [{PROMOTED}]({PROMOTED})\n", {
        "#17": {"state": "closed", "promoted_artifact": PROMOTED},
    })["references"]
    assert ref["status"] == "warning"


def test_closed_without_promotion_has_action(checker, tmp_path):
    ref, = run_report(checker, tmp_path, "# Basis\n#17\n")["references"]
    assert ref["remediation_link"] is None
    assert "Promote" in ref["remediation"]


def test_cross_repository_number_does_not_reuse_local_state(checker, tmp_path):
    other = "https://github.com/OTHER/REPO/issues/17"
    ref, = run_report(checker, tmp_path, f"# Basis\n{other}\n")["references"]
    assert ref["issue"] == other.lower()
    assert ref["state"] == "unknown"


def test_snapshot_and_input_order_are_irrelevant(checker, tmp_path):
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("# Basis\n#17 #18\n", encoding="utf-8", newline="\n")
    b.write_text("# Basis\n#18\n", encoding="utf-8", newline="\n")
    snapshot = {"#17": {"state": "closed"}, "#18": {"state": "open"}}
    options = dict(root=tmp_path, repository=REPOSITORY, domain_sections=["Basis"])
    first = checker.report([b, a, a], snapshot=snapshot, **options)
    second = checker.report([a, b], snapshot=dict(reversed(list(snapshot.items()))), **options)
    assert first == second
    assert [(r["file"], r["line"], r["issue"]) for r in first["references"]] == [
        ("a.md", 2, ISSUE_URL), ("a.md", 2, ISSUE_URL.replace("17", "18")),
        ("b.md", 2, ISSUE_URL.replace("17", "18")),
    ]


@pytest.mark.parametrize("snapshot", [
    [], {"#17": "closed"}, {"#17": {"state": "done"}},
    {"#17": {"promoted_artifact": 17}}, {"#17": {"promoted_artifact": ""}},
    {"#17": {"promoted_artifact": "javascript:example"}},
    {"#17": {"state": "closed"}, ISSUE_URL: {"state": "open"}},
])
def test_invalid_snapshot_is_rejected(checker, tmp_path, snapshot):
    with pytest.raises(ValueError):
        run_report(checker, tmp_path, "# Basis\n#17\n", snapshot)


def test_explicit_scope_required_and_must_match(checker, tmp_path):
    doc = tmp_path / "note.md"
    doc.write_text("# Basis\n#17\n", encoding="utf-8", newline="\n")
    for sections in ([], ["Missing"]):
        with pytest.raises(ValueError):
            checker.report([doc], root=tmp_path, repository=REPOSITORY,
                           snapshot={}, domain_sections=sections)
    with pytest.raises(ValueError):
        checker.report([doc], root=tmp_path, repository=REPOSITORY, snapshot={},
                       domain_sections=["Basis"], operational_sections=["Basis"])


def test_outside_root_and_non_markdown_rejected(checker, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    doc = tmp_path / "note.md"
    doc.write_text("# Basis\n#17\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValueError):
        checker.report([doc], root=root, repository=REPOSITORY, snapshot={}, domain_sections=["Basis"])
    with pytest.raises(ValueError):
        checker.report([SCRIPT], root=SCRIPT.parent, repository=REPOSITORY,
                       snapshot={}, domain_sections=["Basis"])


def cli(tmp_path, snapshot_text, text="# Basis\n#17\n"):
    doc = tmp_path / "note.md"
    snapshot = tmp_path / "snapshot.json"
    doc.write_text(text, encoding="utf-8", newline="\n")
    snapshot.write_text(snapshot_text, encoding="utf-8", newline="\n")
    before = (doc.read_bytes(), snapshot.read_bytes())
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), "--repository", REPOSITORY,
         "--snapshot", str(snapshot), "--domain-section", "Basis", "note.md"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert before == (doc.read_bytes(), snapshot.read_bytes())
    return proc


@pytest.mark.parametrize("snapshot_text,state,status", [
    ('{"#17":{"state":"closed"}}', "closed", "warning"),
    ('{}', "unknown", "unknown-state"),
])
def test_cli_advisory_even_with_missing_state(tmp_path, snapshot_text, state, status):
    proc = cli(tmp_path, snapshot_text)
    # Advisory success is exit zero; it is not a conformance pass.
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["mode"] == "advisory"
    assert result["references"][0]["state"] == state
    assert result["references"][0]["status"] == status
    assert "pass" not in result
    assert str(tmp_path) not in proc.stdout


@pytest.mark.parametrize("snapshot_text", ['{"#17":{},"#17":{}}', '{', '[]'])
def test_cli_rejects_bad_snapshot(tmp_path, snapshot_text):
    proc = cli(tmp_path, snapshot_text)
    # argparse reserves exit two for invalid inputs.
    assert proc.returncode == 2
    assert not proc.stdout
    assert "error:" in proc.stderr
    assert str(tmp_path) not in proc.stderr


@pytest.mark.parametrize("example", [
    "```md\n<!--\n```\n", "`<!--`\n", "    <!--\n",
    "<!--\n```\n-->\n", "<!-- ` -->\n",
])
def test_code_and_comment_delimiters_do_not_leak(checker, tmp_path, example):
    text = "# Basis\n" + example + "#17\n"
    refs = run_report(checker, tmp_path, text)["references"]
    # Independent line count: each preceding newline advances the final line once.
    assert [(r["line"], r["scope"]) for r in refs] == [
        (text.count("\n"), "domain-knowledge"),
    ]


def test_unclosed_code_and_comment_remain_excluded(checker, tmp_path):
    for example in ("```\n#17\n", "~~~\n#17\n", "<!--\n#17\n"):
        assert run_report(checker, tmp_path, "# Basis\n" + example)["references"] == []


def test_cli_reordered_snapshot_is_byte_identical(tmp_path):
    first = cli(tmp_path, '{"#17":{"state":"closed"},"#18":{"state":"open"}}')
    second = cli(tmp_path, '{"#18":{"state":"open"},"#17":{"state":"closed"}}')
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


def test_explicit_full_url_snapshot_key(checker, tmp_path):
    ref, = run_report(checker, tmp_path, "# Basis\n#17\n", {
        ISSUE_URL: {"state": "closed", "promoted_artifact": PROMOTED},
    })["references"]
    assert ref["status"] == "warning"
    assert ref["remediation_link"] == PROMOTED


@pytest.mark.parametrize("text,lines", [
    ("# Basis\nA literal ` delimiter.\n\nSee #17.\n\nLater `code`.\n", [4]),
    ("# Basis\nEscaped \\` #17 `code`.\n", [2]),
    ("# Basis\nA literal ` delimiter.\n## Child\nSee #17 `code`.\n", [4]),
    ("# Basis\nA literal ` delimiter.\n~~~\n#17\n~~~\nSee #17 `code`.\n", [6]),
    ("# Basis\nA literal ` delimiter.\n---\nSee #17 `code`.\n", [4]),
    ("# Basis\n## Child `hidden #17`\n    hidden #17\nSee #17.\n", [4]),
    ("# Basis\nA paragraph\n    citing #17.\n", [3]),
    ("# Basis\nA paragraph\n    continued\n    citing #17.\n", [4]),
    ("# Basis\nA paragraph\n\n    hidden #17\nVisible #17.\n", [5]),
    ("# Basis\nA `multiline\n    hidden #17` span.\nSee #17.\n", [4]),
    ("# Basis\nEscaped \\\\`hidden #17` and #17.\n", [2]),
])
def test_block_boundaries_and_escaped_backticks(checker, tmp_path, text, lines):
    refs = run_report(checker, tmp_path, text)["references"]
    assert [(r["line"], r["status"]) for r in refs] == [
        (line, "warning") for line in lines
    ]


@pytest.mark.parametrize("aliases", [
    "{upper} {lower}",
    "[first]({upper}) [second]({lower})",
    "[first][a] [second][b]\n\n[a]: {upper}\n[b]: {lower}",
])
def test_cross_repository_case_aliases_are_one_issue(checker, tmp_path, aliases):
    lower = "https://github.com/other/repo/issues/17"
    upper = "https://github.com/OTHER/REPO/issues/17"
    text = "# Basis\n" + aliases.format(upper=upper, lower=lower) + "\n"
    ref, = run_report(checker, tmp_path, text, {lower: {"state": "closed"}})["references"]
    assert (ref["line"], ref["issue"].casefold(), ref["status"]) == (2, lower, "warning")
    reversed_text = text.replace(upper, "ALIAS").replace(lower, upper).replace("ALIAS", lower)
    assert run_report(checker, tmp_path, reversed_text, {lower: {"state": "closed"}})["references"] == [ref]
