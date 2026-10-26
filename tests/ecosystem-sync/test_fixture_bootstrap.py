"""Bootstrap contracts; literal oracles come from fixtures/repos/build_fixtures.sh."""
import shutil
import subprocess

import pytest

from conftest import FIXTURE_BUILDER, build_fixture_repos


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_bootstrap_from_empty_output(tmp_path):
    output = tmp_path / "fixtures"
    output.mkdir()
    repos = build_fixture_repos(output)
    # The builder declares these release tags and this baseline-to-head addition.
    assert _git(repos.release, "tag", "-l").splitlines() == [
        "nightly-2026-04-20", "pre-release-1", "snapshot-abc", "v1.0.0", "v1.1.0",
    ]
    assert _git(repos.case_study, "diff", "--name-only", repos.baseline_sha, "HEAD").splitlines() == [
        "case-studies/CASE_STUDY_TEMPLATE.md",
        "case-studies/_draft/wip-study.md",
        "case-studies/mooring-failures.md",
    ]
    assert "- thing one\n- thing two" in (repos.readme / "README.md").read_text()
    assert repos.baseline_sha == _git(repos.case_study, "rev-parse", "HEAD^")


def test_bootstrap_reuses_complete_output(tmp_path):
    output = tmp_path / "fixtures"
    first = build_fixture_repos(output)
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    second = build_fixture_repos(output)
    after = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    assert second == first
    assert after == before


def test_builder_failure_is_explicit(tmp_path):
    builder = tmp_path / "broken-builder.sh"
    builder.write_text("echo 'deliberate builder failure' >&2\nexit 1\n")
    with pytest.raises(RuntimeError, match="Fixture builder failed.*deliberate builder failure"):
        build_fixture_repos(tmp_path / "fixtures", builder=builder)


@pytest.mark.parametrize("contents", ["unrelated", "partial", "symlink"])
def test_builder_rejects_unsafe_reuse(tmp_path, contents):
    output = tmp_path / "fixtures"
    output.mkdir()
    preserved = tmp_path / "preserved"
    preserved.mkdir()
    sentinel = preserved / "keep.txt"
    sentinel.write_text("caller data\n")
    if contents == "unrelated":
        (output / "keep.txt").write_text("caller data\n")
    elif contents == "partial":
        (output / "repo-with-release").mkdir()
    else:
        (output / "repo-with-release").symlink_to(preserved, target_is_directory=True)
    before = sorted(output.iterdir())
    with pytest.raises(RuntimeError, match="refusing unsafe fixture output"):
        build_fixture_repos(output)
    assert sorted(output.iterdir()) == before
    assert sentinel.read_text() == "caller data\n"
    if contents == "unrelated":
        assert (output / "keep.txt").read_text() == "caller data\n"


def test_builder_keeps_default_interface(tmp_path):
    builder = tmp_path / "build_fixtures.sh"
    shutil.copyfile(FIXTURE_BUILDER, builder)
    subprocess.run(["bash", str(builder)], check=True, capture_output=True, text=True)
    assert (tmp_path / "repo-with-release" / ".git").is_dir()
    assert (tmp_path / "repo-with-casestudy.baseline-sha").is_file()
    assert (tmp_path / "repo-with-readme" / "README.md").is_file()


def test_builder_ignores_inherited_git_bindings(tmp_path, monkeypatch):
    caller = build_fixture_repos(tmp_path / "caller").release
    before = {p.relative_to(caller): p.read_bytes() for p in caller.rglob("*") if p.is_file()}
    for variable in ("GIT_DIR", "GIT_COMMON_DIR"):
        monkeypatch.setenv(variable, str(caller / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(caller))
    monkeypatch.setenv("GIT_INDEX_FILE", str(caller / ".git" / "index"))
    repos = build_fixture_repos(tmp_path / "fixtures")
    after = {p.relative_to(caller): p.read_bytes() for p in caller.rglob("*") if p.is_file()}
    assert after == before
    assert repos.release != caller
