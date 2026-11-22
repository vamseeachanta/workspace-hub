"""Synthetic examples for BUILD_COMMANDS.md revision 1.

Expected values follow set membership and literal comparisons written out in
each test; no expected value is computed by the verifier under test.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from hygiene import check_build_commands as checker

CLI = Path(checker.__file__).resolve()


def git(repo, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, env=env,
    )


def write(repo, path, text):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repository"
    root.mkdir()
    git(root, "init", "-q")
    write(root, "build.py", "print('build')\n")
    write(root, "docs/reports/example.html", "<p>example</p>\n")
    write(root, "artifacts.registry.json", json.dumps([entry()]))
    git(root, "add", "--all")
    return root


def cli(repo, *args, env=None):
    return subprocess.run(
        [sys.executable, "-I", str(CLI), "--repo", str(repo), *args],
        check=False, capture_output=True, text=True, env=env,
    )

def entry(path="docs/reports/example.html"):
    return {
        "path": path,
        "kind": "report",
        "build": {"cwd": ".", "argv": ["python", "build.py"]},
        "inputs": ["build.py"],
    }


def test_valid_registry(tmp_path):
    """One complete entry maps to one artifact with unchanged arguments."""
    registry = tmp_path / "artifacts.registry.json"
    registry.write_text(json.dumps([entry()]))
    artifacts = checker.load_registry(registry)
    assert len(artifacts) == 1
    assert artifacts[0].path == "docs/reports/example.html"
    assert artifacts[0].argv == ("python", "build.py")


@pytest.mark.parametrize("field", ["path", "kind", "build", "inputs"])
def test_missing_field(field):
    """Removing a required field leaves an incomplete entry."""
    item = entry()
    del item[field]
    with pytest.raises(checker.ValidationError, match=field):
        checker.validate_registry([item])


@pytest.mark.parametrize("build", ["python build.py", {"cwd": ".", "argv": "python build.py"}])
def test_shell_string_refused(build):
    """The schema accepts argument arrays only, never a shell string."""
    item = entry()
    item["build"] = build
    with pytest.raises(checker.ValidationError, match="shell strings are not allowed"):
        checker.validate_registry([item])


@pytest.mark.parametrize("field", ["path", "cwd", "input"])
@pytest.mark.parametrize("value", ["/outside/output", "../output", "C:\\outside\\output"])
def test_unsafe_paths_refused(field, value):
    """Absolute or parent-traversing paths cannot identify repository files."""
    item = entry()
    if field == "cwd":
        item["build"]["cwd"] = value
    elif field == "input":
        item["inputs"] = [value]
    else:
        item[field] = value
    with pytest.raises(checker.ValidationError, match="relative"):
        checker.validate_registry([item])


def test_duplicate_path():
    """Two entries with the same output are ambiguous and must be refused."""
    with pytest.raises(checker.ValidationError, match="duplicate path"):
        checker.validate_registry([entry(), copy.deepcopy(entry())])


def test_unknown_kind():
    """The revision 1 kinds are report, page, figure and data; other is absent."""
    item = entry()
    item["kind"] = "other"
    with pytest.raises(checker.ValidationError, match="unknown kind"):
        checker.validate_registry([item])


@pytest.mark.parametrize("value", [0, -1, True, "120", float("inf"), float("nan")])
def test_invalid_budget(value):
    """A timeout must be a finite positive number, excluding JSON booleans."""
    item = entry()
    item["budget_seconds"] = value
    with pytest.raises(checker.ValidationError, match="budget_seconds"):
        checker.validate_registry([item])


@pytest.mark.parametrize("argv", [[], [""], ["python", None]])
def test_invalid_arguments(argv):
    """An executable and every argument must be nonempty strings."""
    item = entry()
    item["build"]["argv"] = argv
    with pytest.raises(checker.ValidationError, match="argv"):
        checker.validate_registry([item])


def test_duplicate_json_key(tmp_path):
    """Repeated object keys must not silently discard a declared value."""
    registry = tmp_path / "artifacts.registry.json"
    registry.write_text('[{"path":"a","path":"b"}]')
    with pytest.raises(checker.ValidationError, match="duplicate JSON key"):
        checker.load_registry(registry)


def test_static_all_clear(repo):
    """One present output, command and input means zero findings and exit zero."""
    result = cli(repo)
    assert (result.returncode, result.stdout, result.stderr) == (0, "OK\n", "")


@pytest.mark.parametrize(
    ("change", "expected"),
    [
        ("extra", 'UNREGISTERED: "docs/reports/extra.pdf"'),
        ("output", 'MISSING_OUTPUT: "docs/reports/example.html"'),
        ("command", 'MISSING_COMMAND: "docs/reports/example.html"'),
        ("input", 'MISSING_INPUT: "build.py"'),
    ],
)
def test_static_findings(repo, change, expected):
    """Each removal or addition creates exactly the stated set difference."""
    item = entry()
    if change == "extra":
        write(repo, "docs/reports/extra.pdf", "pdf")
    elif change == "output":
        (repo / item["path"]).unlink()
    elif change == "command":
        item["build"]["argv"] = ["not-an-installed-executable-unique-example"]
    else:
        item["inputs"] = ["absent-input"]
        expected = 'MISSING_INPUT: "absent-input"'
    write(repo, "artifacts.registry.json", json.dumps([item]))
    result = cli(repo)
    assert result.returncode == 1
    assert result.stdout.splitlines() == [expected]


def test_default_svg_patterns(repo):
    """Root/nested figure SVGs and asset SVGs match; unrelated SVGs do not."""
    for path in ["figures/a.svg", "docs/figures/nested/b.svg", "assets/c.svg", "other.svg"]:
        write(repo, path, "svg")
    result = cli(repo)
    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        'UNREGISTERED: "assets/c.svg"',
        'UNREGISTERED: "docs/figures/nested/b.svg"',
        'UNREGISTERED: "figures/a.svg"',
    ]


def test_custom_patterns_replace_defaults(repo):
    """With only *.csv requested, an extra report is outside the selected set."""
    write(repo, "docs/reports/extra.html", "html")
    write(repo, "data/example.csv", "a,b")
    write(repo, "patterns.json", json.dumps({"patterns": ["data/*.csv"]}))
    result = cli(repo, "--patterns", str(repo / "patterns.json"))
    assert result.stdout.splitlines() == ['UNREGISTERED: "data/example.csv"']


@pytest.mark.parametrize("command", ["python", "python3", "build.py"])
def test_command_resolution(repo, command):
    """Python aliases and a repository file each satisfy static presence only."""
    item = entry()
    item["build"]["argv"] = [command]
    write(repo, "artifacts.registry.json", json.dumps([item]))
    assert cli(repo).returncode == 0


def test_command_relative_to_build_cwd(repo):
    """tools/build.py exists relative to tools, where the command will execute."""
    write(repo, "tools/build.py", "pass")
    item = entry()
    item["build"] = {"cwd": "tools", "argv": ["./build.py"]}
    write(repo, "artifacts.registry.json", json.dumps([item]))
    assert cli(repo).returncode == 0


def test_executable_on_path(repo, tmp_path):
    """A test-controlled executable on PATH satisfies the command rule."""
    executable = tmp_path / "example-tool"
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)  # POSIX executable mode; BUILD_COMMANDS.md, Portability.
    item = entry()
    item["build"]["argv"] = ["example-tool"]
    write(repo, "artifacts.registry.json", json.dumps([item]))
    env = dict(os.environ, PATH=str(tmp_path))
    assert cli(repo, env=env).returncode == 0


@pytest.mark.parametrize(
    "config",
    [
        {"patterns": "*.html"}, {"patterns": ["../*.html"]},
        {"default_timeout_seconds": 0}, {"unknown": True},
        {"normalise": [{"pattern": "*.html", "regex": "["}]},
        {"normalise": [{"pattern": "*.html", "regex": ".*"}]},
    ],
)
def test_invalid_config(repo, config):
    """Invalid types, escapes, timeout and unanchored/bad regexes fail closed."""
    write(repo, "patterns.json", json.dumps(config))
    result = cli(repo, "--patterns", str(repo / "patterns.json"))
    assert result.returncode == 2
    assert result.stderr.startswith("CONFIG_ERROR:")


def test_symlink_escape_refused(repo, tmp_path):
    """A declared input symlink to a sibling file violates the copy boundary."""
    outside = tmp_path / "outside"
    outside.write_text("private")
    (repo / "link").symlink_to(outside)
    item = entry()
    item["inputs"] = ["link"]
    write(repo, "artifacts.registry.json", json.dumps([item]))
    result = cli(repo)
    assert result.returncode == 2
    assert "symlink" in result.stderr
    assert str(tmp_path) not in result.stderr


def test_missing_registry_is_error(repo):
    """Absence of the declaration cannot be interpreted as an empty registry."""
    (repo / "artifacts.registry.json").unlink()
    assert cli(repo).returncode == 2


def builder(repo, code, *, cwd=".", budget=None):
    item = entry()
    item["build"]["cwd"] = cwd
    if budget is not None:
        item["budget_seconds"] = budget
    write(repo, "build.py", code)
    write(repo, "artifacts.registry.json", json.dumps([item]))
    git(repo, "add", "--all")


DETERMINISTIC = (
    "from pathlib import Path\n"
    "Path('docs/reports/example.html').write_text('<p>example</p>\\n')\n"
)


def test_deterministic_build_preserves_source(repo):
    """Literal generated bytes equal '<p>example</p>\n'; source/index stay equal."""
    builder(repo, DETERMINISTIC)
    before = {path: path.read_bytes() for path in repo.rglob("*") if path.is_file()}
    result = cli(repo, "--run")
    assert (result.returncode, result.stdout) == (0, "OK\n")
    after = {path: path.read_bytes() for path in repo.rglob("*") if path.is_file()}
    assert after == before


def test_noop_does_not_reuse_copied_output(repo):
    """A command producing nothing cannot reproduce the pre-existing output."""
    builder(repo, "pass\n")
    result = cli(repo, "--run")
    assert result.returncode == 1
    assert result.stdout == 'NOT_REPRODUCED: "docs/reports/example.html"\n'


def test_timestamp_needs_explicit_normalisation(repo):
    """Removing built-at lines leaves 'body\n' on both sides; raw bytes differ."""
    builder(
        repo,
        "from pathlib import Path\nimport time\n"
        "Path('docs/reports/example.html').write_text(f'built-at: {time.time_ns()}\\nbody\\n')\n",
    )
    write(repo, "docs/reports/example.html", "built-at: reference\nbody\n")
    write(repo, "patterns.json", json.dumps({"normalise": [
        {"pattern": "docs/reports/*.html", "regex": "^built-at: .*$"},
    ]}))
    git(repo, "add", "--all")
    args = ("--run", "--patterns", str(repo / "patterns.json"))
    raw = cli(repo, *args)
    assert raw.returncode == 1
    assert "NOT_REPRODUCED" in raw.stdout
    normalised = cli(repo, *args, "--normalise")
    assert (normalised.returncode, normalised.stdout) == (0, "OK\n")


def test_normalisation_keeps_non_timestamp_difference(repo):
    """Deleting timestamp lines cannot make 'wrong' equal 'body'."""
    builder(repo, "from pathlib import Path\nPath('docs/reports/example.html').write_text('wrong\\n')\n")
    write(repo, "patterns.json", json.dumps({"normalise": [
        {"pattern": "**/*.html", "regex": "^built-at: .*$"},
    ]}))
    assert cli(repo, "--run", "--normalise", "--patterns", str(repo / "patterns.json")).returncode == 1


def test_build_failed_does_not_echo_child_output(repo):
    """A nonzero script exit reports BUILD_FAILED without its diagnostic text."""
    builder(repo, "import sys\nprint('diagnostic-marker')\nsys.exit(1)\n")
    result = cli(repo, "--run")
    assert result.returncode == 1
    assert result.stdout == 'BUILD_FAILED: "docs/reports/example.html"\n'
    assert "diagnostic-marker" not in result.stdout + result.stderr


def test_timeout(repo):
    """A configured 1 s budget is shorter than the synthetic 10 s sleep."""
    builder(repo, "import time\ntime.sleep(10)\n", budget=1)
    result = cli(repo, "--run")
    assert result.returncode == 1
    assert result.stdout == 'TIMEOUT: "docs/reports/example.html"\n'


def test_configured_timeout(repo):
    """The configuration's 1 s budget also expires before the 10 s sleep."""
    builder(repo, "import time\ntime.sleep(10)\n")
    write(repo, "patterns.json", '{"default_timeout_seconds": 1}')
    result = cli(repo, "--run", "--patterns", str(repo / "patterns.json"))
    assert result.returncode == 1
    assert "TIMEOUT" in result.stdout


def test_budget_overrides_config(repo):
    """An explicit 1 s artifact budget expires despite a 120 s config budget."""
    builder(repo, "import time\ntime.sleep(10)\n", budget=1)
    write(repo, "patterns.json", '{"default_timeout_seconds": 120}')
    assert "TIMEOUT" in cli(repo, "--run", "--patterns", str(repo / "patterns.json")).stdout


def test_ignored_cache_not_copied(repo):
    """The ignored helper exists in the source but is absent from tracked export."""
    builder(repo, "import cached_helper\n" + DETERMINISTIC)
    write(repo, ".gitignore", "cached_helper.py\n")
    write(repo, "cached_helper.py", "value = 'cached'\n")
    git(repo, "add", "--all")
    result = cli(repo, "--run")
    assert result.returncode == 1
    assert "BUILD_FAILED" in result.stdout
    assert (repo / "cached_helper.py").read_text() == "value = 'cached'\n"


def test_git_bindings_do_not_redirect_export(repo, tmp_path):
    """Foreign GIT_DIR and index bindings must not redirect git ls-files."""
    builder(repo, DETERMINISTIC)
    other = tmp_path / "other"
    other.mkdir()
    git(other, "init", "-q")
    env = dict(os.environ, GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other))
    assert cli(repo, "--run", env=env).returncode == 0


def test_build_cwd_and_executable(repo):
    """Direct execution from tools writes its ../docs target with identical bytes."""
    write(repo, "tools/build", "#!/bin/sh\nprintf '<p>example</p>\\n' > ../docs/reports/example.html\n")
    (repo / "tools/build").chmod(0o755)  # POSIX executable mode; documentation Portability.
    item = entry()
    item["build"] = {"cwd": "tools", "argv": ["./build"]}
    item["inputs"] = ["tools/build"]
    write(repo, "artifacts.registry.json", json.dumps([item]))
    git(repo, "add", "--all")
    assert cli(repo, "--run").returncode == 0


def test_rebuild_rejects_tracked_symlinks(repo, tmp_path):
    """Plain export must not follow even an unrelated tracked symlink."""
    builder(repo, DETERMINISTIC)
    outside = tmp_path / "outside"
    outside.write_text("unchanged")
    (repo / "unrelated-link").symlink_to(outside)
    git(repo, "add", "--all")
    result = cli(repo, "--run")
    assert result.returncode == 2
    assert "symlink" in result.stderr
    assert outside.read_text() == "unchanged"


def test_rebuild_refuses_untracked_reference(repo):
    """An output absent from the Git index is not a publishable reference."""
    builder(repo, DETERMINISTIC)
    git(repo, "rm", "--cached", "docs/reports/example.html")
    result = cli(repo, "--run")
    assert result.returncode == 2
    assert "tracked" in result.stderr


def test_separate_copy_for_each_build(repo):
    """A first build's marker cannot affect a second build in its fresh copy."""
    first = entry()
    second = entry("docs/reports/second.html")
    second["build"]["argv"] = ["python", "second.py"]
    second["inputs"] = ["second.py"]
    write(repo, "build.py", DETERMINISTIC + "Path('marker').write_text('set')\n")
    write(repo, "second.py", "from pathlib import Path\nassert not Path('marker').exists()\n"
          "Path('docs/reports/second.html').write_text('second\\n')\n")
    write(repo, "docs/reports/second.html", "second\n")
    write(repo, "artifacts.registry.json", json.dumps([first, second]))
    git(repo, "add", "--all")
    assert cli(repo, "--run").returncode == 0


@pytest.mark.parametrize("scripts", [[], ["make_extra.py"], ["make_extra.py", "tools/extra.sh"]])
def test_suggest_candidates(repo, scripts):
    """N tracked scripts naming extra.html produce exactly N candidate arrays."""
    write(repo, "docs/reports/extra.html", "extra")
    for path in scripts:
        write(repo, path, "# rebuild extra.html\n")
    write(repo, "untracked.py", "# extra.html\n")
    write(repo, "notes.txt", "extra.html\n")
    # Stage selected candidates, leaving the unrelated script untracked.
    git(repo, "add", "docs/reports/extra.html", "notes.txt", *scripts)
    before = (repo / "artifacts.registry.json").read_bytes()
    result = cli(repo, "--suggest")
    assert result.returncode == 1
    lines = result.stdout.splitlines()
    assert lines[0] == 'UNREGISTERED: "docs/reports/extra.html"'
    candidates = [json.loads(line.removeprefix("CANDIDATE: ")) for line in lines[1:]]
    assert candidates == [
        {"path": "docs/reports/extra.html", "build": {"cwd": ".", "argv": argv}}
        for argv in (
            [["python3", "make_extra.py"], ["sh", "tools/extra.sh"]][:len(scripts)]
        )
    ]
    assert (repo / "artifacts.registry.json").read_bytes() == before


def test_suggest_without_registry(repo):
    """Bootstrap reports the existing output even before a registry is created."""
    git(repo, "rm", "--cached", "artifacts.registry.json")
    (repo / "artifacts.registry.json").unlink()
    result = cli(repo, "--suggest")
    assert result.returncode == 1
    assert result.stdout == 'UNREGISTERED: "docs/reports/example.html"\n'
    assert not (repo / "artifacts.registry.json").exists()


def test_usage_diagnostics_do_not_echo_arguments(repo):
    """Invalid argument text is not part of the fixed usage diagnostic."""
    result = cli(repo, "--unknown", "private-diagnostic-marker")
    assert result.returncode == 2
    assert "private-diagnostic-marker" not in result.stdout + result.stderr


def test_temporary_directory_inside_source_refused(repo):
    """An unsafe temporary root must fail before creating source-tree residue."""
    builder(repo, DETERMINISTIC)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*"))
    env = dict(os.environ, TMPDIR=str(repo))
    result = cli(repo, "--run", env=env)
    assert result.returncode == 2
    assert "outside" in result.stderr
    assert sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*")) == before


@pytest.mark.parametrize("code", ["\x01", "\x7f"])
def test_control_character_path_refused(code):
    """RFC 20 section 2 identifies control codes, including DEL (7*16+15)."""
    item = entry("figures/a" + code + ".svg")
    with pytest.raises(checker.ValidationError, match="relative"):
        checker.validate_registry([item])


def test_non_utf8_normalisation_error(repo):
    """UTF-8 rules cannot be used to silently decode invalid byte 0xff."""
    builder(repo, "from pathlib import Path\nPath('docs/reports/example.html').write_bytes(b'\\xff')\n")
    write(repo, "patterns.json", json.dumps({"normalise": [
        {"pattern": "**/*.html", "regex": "^built-at: .*$"},
    ]}))
    assert cli(repo, "--run", "--normalise", "--patterns", str(repo / "patterns.json")).returncode == 2


def test_normalisation_does_not_match_unselected_output(repo):
    """A rule for PDF outputs cannot remove lines in this HTML output."""
    builder(repo, DETERMINISTIC)
    write(repo, "patterns.json", json.dumps({"normalise": [
        {"pattern": "**/*.pdf", "regex": "^.*$"},
    ]}))
    write(repo, "docs/reports/example.html", "different\n")
    result = cli(repo, "--run", "--normalise", "--patterns", str(repo / "patterns.json"))
    assert result.returncode == 1
    assert "NOT_REPRODUCED" in result.stdout


@pytest.mark.parametrize("path", ["figures/a.svg", "docs/figures/a.svg", "docs/figures/sub/a.svg"])
def test_recursive_rule_glob(path):
    """The ** components admit zero, one and several directory components."""
    assert checker.glob_matches(path, "**/figures/**/*.svg")


def test_build_created_symlink_is_not_an_output(repo):
    """An identical file reached through a generated symlink is not reproduced."""
    builder(repo, "from pathlib import Path\n"
            "Path('reference.html').write_text('<p>example</p>\\n')\n"
            "Path('docs/reports/example.html').symlink_to('../../reference.html')\n")
    assert "NOT_REPRODUCED" in cli(repo, "--run").stdout
