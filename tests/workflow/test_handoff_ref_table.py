"""Synthetic, offline examples for independent local-ref table resolution."""

import json
import subprocess
from pathlib import Path

import pytest

from workflow import handoff_ref_table as table


# Git hash-function-transition, Object names: SHA-1 and SHA-256 use 40 and
# 64 hex digits. Repeated letters are synthetic responses, not repository IDs.
FIRST_ID = "a" * 40
SECOND_ID = "b" * 40
WIDE_ID = "c" * 64
FIRST_REF = "origin/plan/issue-1-example"
SECOND_REF = "origin/plan/issue-2-example"
# Independent ordering example: positive issue ordinals satisfy 1 < 2.
ROWS = [{"issue": 2, "ref": SECOND_REF}, {"issue": 1, "ref": FIRST_REF}]
ROOT = Path(__file__).parent


class GitResponses:
    """Capture all commands; provide only explicitly listed read responses."""

    def __init__(self, commits=None):
        self.commits = commits if commits is not None else {
            FIRST_REF: FIRST_ID, SECOND_REF: SECOND_ID,
        }
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        assert argv[:len(self.prefix)] == self.prefix
        assert kwargs["check"] is True
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert "shell" not in kwargs
        operand = argv[-1]
        for ref, commit in self.commits.items():
            canonical = ref if ref.startswith("refs/") else "refs/remotes/" + ref
            if operand == ref:
                assert argv[len(self.prefix):-1] == [
                    "--verify", "--symbolic-full-name", "--end-of-options",
                ]
                return subprocess.CompletedProcess(argv, 0, canonical + "\n", "")
            if operand == canonical + "^{commit}":
                assert argv[len(self.prefix):-1] == ["--verify", "--end-of-options"]
                return subprocess.CompletedProcess(argv, 0, commit + "\n", "")
        # POSIX exit status: zero means success; nonzero means failure.
        raise subprocess.CalledProcessError(1, argv, stderr="restricted diagnostic")

    @property
    def prefix(self):
        return ["git", "-C", str(ROOT), "-c", "core.warnAmbiguousRefs=true", "rev-parse"]


def test_distinct_refs_keep_distinct_commits():
    git = GitResponses()
    result = table.render_table(ROWS, ROOT, run=git)
    # Expected rows are transcribed from the two independent fixture pairs.
    assert result == (
        "| Issue | Local ref | Commit ID |\n"
        "| --- | --- | --- |\n"
        f"| #1 | <code>{FIRST_REF}</code> | `{FIRST_ID}` |\n"
        f"| #2 | <code>{SECOND_REF}</code> | `{SECOND_ID}` |\n"
    )
    assert [argv[-1] for argv, _ in git.calls] == [
        FIRST_REF, "refs/remotes/" + FIRST_REF + "^{commit}",
        SECOND_REF, "refs/remotes/" + SECOND_REF + "^{commit}",
    ]


def test_reordered_input_is_stable():
    assert table.render_table(ROWS, ROOT, run=GitResponses()) == table.render_table(
        list(reversed(ROWS)), ROOT, run=GitResponses(),
    )


def test_distinct_refs_may_share_a_commit():
    git = GitResponses({FIRST_REF: FIRST_ID, SECOND_REF: FIRST_ID})
    result = table.render_table(ROWS, ROOT, run=git)
    assert f"| #1 | <code>{FIRST_REF}</code> | `{FIRST_ID}` |" in result
    assert f"| #2 | <code>{SECOND_REF}</code> | `{FIRST_ID}` |" in result
    assert [argv[-1] for argv, _ in git.calls] == [
        FIRST_REF, "refs/remotes/" + FIRST_REF + "^{commit}",
        SECOND_REF, "refs/remotes/" + SECOND_REF + "^{commit}",
    ]


def test_aliases_of_the_same_ref_are_duplicates():
    canonical = "refs/remotes/" + FIRST_REF
    git = GitResponses({FIRST_REF: FIRST_ID, canonical: FIRST_ID})
    rows = [{"issue": 1, "ref": FIRST_REF}, {"issue": 2, "ref": canonical}]
    with pytest.raises(table.RefTableError, match="duplicate local ref"):
        table.render_table(rows, ROOT, run=git)


def test_missing_ref_refused():
    with pytest.raises(table.RefTableError, match="local commit ref"):
        table.render_table(ROWS, ROOT, run=GitResponses({}))


@pytest.mark.parametrize("ref", ["--help", "--output=unexpected", "-q"])
def test_ref_cannot_inject_git_option(ref):
    git = GitResponses()
    with pytest.raises(table.RefTableError):
        table.render_table([{"issue": 1, "ref": ref}], ROOT, run=git)
    assert git.calls == []


@pytest.mark.parametrize("stdout,stderr", [
    ("", "warning: refname is ambiguous"),
    ("refs/heads/example\nrefs/tags/example\n", ""),
    ("refs/heads/example\n", "warning: refname is ambiguous"),
    ("HEAD\n", ""),
])
def test_ambiguous_or_unnamed_ref_refused(stdout, stderr):
    def ambiguous(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout, stderr)

    with pytest.raises(table.RefTableError):
        table.render_table(ROWS, ROOT, run=ambiguous)


def test_non_commit_ref_refused():
    git = GitResponses()

    def blob(argv, **kwargs):
        if argv[-1].endswith("^{commit}"):
            raise subprocess.CalledProcessError(1, argv)
        return git(argv, **kwargs)

    with pytest.raises(table.RefTableError):
        table.render_table(ROWS, ROOT, run=blob)


@pytest.mark.parametrize("commit", ["", "abc", "g" * 40, FIRST_ID + "\n" + SECOND_ID])
def test_only_full_commit_ids_accepted(commit):
    with pytest.raises(table.RefTableError):
        table.render_table(ROWS, ROOT, run=GitResponses({FIRST_REF: commit}))


def test_sha256_repository_supported():
    assert f"`{WIDE_ID}`" in table.render_table(
        [{"issue": 1, "ref": FIRST_REF}], ROOT,
        run=GitResponses({FIRST_REF: WIDE_ID}),
    )


@pytest.mark.parametrize("rows", [
    {}, [None], [{"issue": True, "ref": FIRST_REF}],
    [{"issue": 0, "ref": FIRST_REF}], [{"issue": "1", "ref": FIRST_REF}],
    [{"issue": 1}], [{"issue": 1, "ref": None}],
    [{"issue": 1, "ref": FIRST_REF, "commit": SECOND_ID}],
    [{"issue": 1, "ref": FIRST_REF, "approval": True}],
    [ROWS[-1], ROWS[-1]],
    [ROWS[-1], {"issue": 1, "ref": SECOND_REF}],
    [ROWS[-1], {"issue": 2, "ref": FIRST_REF}],
])
def test_invalid_or_duplicate_rows_refused_before_git(rows):
    git = GitResponses()
    with pytest.raises(table.RefTableError):
        table.render_table(rows, ROOT, run=git)
    assert git.calls == []


@pytest.mark.parametrize("ref", [
    "", " ref", "ref\nother", "ref\x00other", "HEAD~1", "HEAD^{commit}",
    "ref:path", "ref@{1}", "ref..other", "refs/heads/.hidden",
])
def test_revision_expressions_and_invalid_names_refused(ref):
    git = GitResponses()
    with pytest.raises(table.RefTableError):
        table.render_table([{"issue": 1, "ref": ref}], ROOT, run=git)
    assert git.calls == []


def test_ref_markup_cannot_change_table_shape():
    ref = "refs/heads/example|<b>&`"
    result = table.render_table(
        [{"issue": 1, "ref": ref}], ROOT, run=GitResponses({ref: FIRST_ID}),
    )
    assert "<code>refs/heads/example&#124;&lt;b&gt;&amp;&#96;</code>" in result


def test_inherited_git_bindings_are_isolated(monkeypatch, tmp_path):
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_CONFIG_COUNT"):
        monkeypatch.setenv(name, str(tmp_path / "unrelated"))
    git = GitResponses()
    table.render_table(ROWS, ROOT, run=git)
    for _, kwargs in git.calls:
        env = kwargs["env"]
        assert {key: value for key, value in env.items() if key.startswith("GIT_")} == {
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
        }


def test_no_commit_cache_between_calls():
    first = table.render_table(ROWS, ROOT, run=GitResponses())
    second = table.render_table(
        ROWS, ROOT, run=GitResponses({FIRST_REF: SECOND_ID, SECOND_REF: FIRST_ID}),
    )
    assert first != second
    assert f"| #1 | <code>{FIRST_REF}</code> | `{SECOND_ID}` |" in second


def test_empty_list_renders_header_without_git():
    git = GitResponses()
    assert table.render_table([], ROOT, run=git) == (
        "| Issue | Local ref | Commit ID |\n| --- | --- | --- |\n"
    )
    assert git.calls == []


def test_cli_reads_explicit_json_and_prints_table(monkeypatch, tmp_path, capsys):
    source = tmp_path / "rows.json"
    source.write_text(json.dumps(ROWS), encoding="utf-8")
    git = GitResponses()
    monkeypatch.setattr(table.subprocess, "run", git)
    assert table.main([str(source), "--repo", str(ROOT)]) == 0
    assert capsys.readouterr().out == table.render_table(ROWS, ROOT, run=GitResponses())


@pytest.mark.parametrize("text", ["not JSON", '{"issue":1}', '[{"issue":1,"issue":2}]'])
def test_cli_rejects_invalid_json_without_git(monkeypatch, tmp_path, capsys, text):
    source = tmp_path / "invalid.json"
    source.write_text(text, encoding="utf-8")
    git = GitResponses()
    monkeypatch.setattr(table.subprocess, "run", git)
    assert table.main([str(source), "--repo", str(ROOT)]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "error:" in captured.err
    assert git.calls == []


def test_cli_failure_never_prints_partial_table_or_git_diagnostics(
    monkeypatch, tmp_path, capsys,
):
    source = tmp_path / "rows.json"
    source.write_text(json.dumps(ROWS), encoding="utf-8")
    monkeypatch.setattr(table.subprocess, "run", GitResponses({FIRST_REF: FIRST_ID}))
    assert table.main([str(source), "--repo", str(ROOT)]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "restricted diagnostic" not in captured.err


def test_git_executable_unavailable_is_sanitized():
    def unavailable(argv, **kwargs):
        raise FileNotFoundError("restricted diagnostic")

    with pytest.raises(table.RefTableError) as exc:
        table.render_table(ROWS, ROOT, run=unavailable)
    assert "restricted diagnostic" not in str(exc.value)
