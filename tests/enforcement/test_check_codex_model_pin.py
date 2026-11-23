"""Offline checks for committed Codex model defaults."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/enforcement/check-codex-model-pin.sh"
EXCEPTIONS = tuple(
    f".codex/agents/fixture-{role}/config.toml" for role in ("one", "two", "three")
)


@pytest.fixture
def repo(tmp_path):
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    subprocess.run(["git", "init", "-q", str(tmp_path)], env=env, check=True)
    return tmp_path, env


@pytest.fixture
def exception_script(tmp_path):
    source, count = re.subn(
        r"^ALLOWLIST = \(.*?\)", f"ALLOWLIST = {EXCEPTIONS!r}",
        SCRIPT.read_text(), count=1, flags=re.DOTALL | re.MULTILINE,
    )
    assert count == 1
    path = tmp_path / "check-with-fixture-exceptions.sh"
    path.write_text(source)
    return path


def track(repo, name, text):
    root, env = repo
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    subprocess.run(["git", "add", "--", name], cwd=root, env=env, check=True)


def run(repo, *args, script=SCRIPT):
    root, env = repo
    return subprocess.run(
        ["bash", str(script), *args], cwd=root, env=env,
        text=True, capture_output=True, check=False,
    )


def test_clean_tree(repo):
    track(repo, ".codex/config.toml", 'model_provider = "local"\n')
    assert run(repo).returncode == 0


@pytest.mark.parametrize("name", [
    ".codex/config.toml", "config/agents/codex/config.toml",
    "config/agents/codex/nested/settings.toml",
    ".codex/agents/extra/config.toml", ".codex/agents/extra.toml",
])
def test_pin_fails_with_file_line_and_value(repo, name):
    track(repo, name, '# comment\nmodel = "unsupported"\n')
    result = run(repo)
    assert result.returncode == 1
    assert f'{name}:2:' in result.stdout + result.stderr
    assert '"unsupported"' in result.stdout + result.stderr


@pytest.mark.parametrize("text", [
    'model_reasoning_effort = "medium"\n',
    '[profiles.x]\nmodel = "local"\n',
    '[settings]\nmodel = "local"\n',
    '# model = "local"\n',
    'description = """\nmodel = "literal"\n"""\n',
    'description = "[settings]"\n',
])
def test_non_pins_pass(repo, text):
    track(repo, ".codex/config.toml", text)
    assert run(repo).returncode == 0


@pytest.mark.parametrize("key", ['"model"', "'model'", '   model   ', '  "model"  '])
def test_quoted_or_spaced_pin_fails(repo, key):
    track(repo, ".codex/config.toml", f'{key} = "unsupported"\n')
    assert run(repo).returncode == 1


def test_multiline_header_cannot_hide_pin(repo):
    track(repo, ".codex/config.toml", 'text = """\n[settings]\n"""\nmodel = "x"\n')
    assert run(repo).returncode == 1


@pytest.mark.parametrize("prefix", [
    'options = [\n["nested"]\n]\n',
    'description = """quoted""""\n',
    "description = '''quoted''''\n",
])
def test_valid_toml_constructs_cannot_hide_root_pin(repo, prefix):
    """TOML v1.0.0 (2021), Array, String and Table sections:

    Nested arrays and trailing quotes belong to the preceding value. The
    following model key therefore remains in the root table and must fail.
    Source: https://toml.io/en/v1.0.0
    """
    track(repo, ".codex/config.toml", prefix + 'model = "unsupported"\n')
    result = run(repo)
    assert result.returncode == 1
    assert "model =" in result.stdout
    assert "invalid TOML" not in result.stdout + result.stderr


def test_escaped_quoted_model_key_fails(repo):
    """TOML v1.0.0 (2021), Keys: quoted keys follow basic string escapes.

    The Unicode escape for m makes this key equivalent to model, so it fails.
    Source: https://toml.io/en/v1.0.0#keys
    """
    track(repo, ".codex/config.toml", r'"\u006dodel" = "unsupported"' + "\n")
    result = run(repo)
    assert result.returncode == 1
    assert "model =" in result.stdout
    assert "invalid TOML" not in result.stdout + result.stderr


@pytest.mark.parametrize("text", [
    'options = [\n["nested"]\n]\n',
    'description = """quoted""""\n[settings]\nmodel = "local"\n',
    "description = '''quoted''''\n[settings]\nmodel = \"local\"\n",
])
def test_valid_toml_without_root_pin_passes(repo, text):
    """TOML v1.0.0 (2021), Array, String and Table sections:

    These documents have no root model key; a key after settings belongs to
    that table. Expected success follows from the document structure.
    Source: https://toml.io/en/v1.0.0
    """
    track(repo, ".codex/config.toml", text)
    assert run(repo).returncode == 0


@pytest.mark.parametrize("text", [
    'options = ["unclosed"\n',
    'description = "do-not-echo"\ndescription = "duplicate"\n',
])
def test_invalid_toml_fails_without_echoing_contents(repo, text):
    """Python 3.11 tomllib docs, loads: invalid TOML raises TOMLDecodeError.

    A missing closing bracket or duplicate key cannot establish an unpinned
    configuration, so the guard must fail closed without printing contents.
    Source: https://docs.python.org/3.11/library/tomllib.html#tomllib.loads
    """
    name = ".codex/config.toml"
    track(repo, name, text)
    result = run(repo)
    assert result.returncode == 1
    assert name in result.stdout + result.stderr
    assert "invalid TOML" in result.stdout + result.stderr
    assert "do-not-echo" not in result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr


@pytest.mark.parametrize("name", EXCEPTIONS)
def test_allowlisted_pin_passes(repo, exception_script, name):
    for exception in EXCEPTIONS:
        track(repo, exception, 'model = "small"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 0
    assert f"ALLOW {name}" in result.stdout


def test_all_exceptions_and_fourth_pin(repo, exception_script):
    for name in EXCEPTIONS:
        track(repo, name, 'model = "small"\n')
    track(repo, ".codex/agents/fourth/config.toml", 'model = "x"\n')
    assert run(repo, script=exception_script).returncode == 1


def test_stale_allowlist_fails(repo, exception_script):
    track(repo, EXCEPTIONS[0], 'model_reasoning_effort = "medium"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 1
    assert f"{EXCEPTIONS[0]}: stale allowlist entry" in result.stdout + result.stderr


@pytest.mark.parametrize("untracked_present", [False, True])
def test_missing_tracked_exception_fails(repo, exception_script, untracked_present):
    """Set subtraction leaves exactly the last exception missing from Git.

    Track every other exception with a root pin. The last path is either absent
    or present only on disk, so neither case satisfies the tracked-file contract.
    Expected exit status follows the checker header: stale exception means 1.
    """
    for name in EXCEPTIONS[:-1]:
        track(repo, name, 'model = "small"\n')
    missing = EXCEPTIONS[-1]
    if untracked_present:
        root, _ = repo
        path = root / missing
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('model = "small"\n')

    result = run(repo, script=exception_script)

    assert result.returncode == 1
    assert f"{missing}: stale allowlist entry (not tracked)" in result.stdout
    assert "PASS" not in result.stdout
    for name in EXCEPTIONS[:-1]:
        assert f"ALLOW {name}" in result.stdout
        assert f"{name}: stale allowlist entry" not in result.stdout


def test_all_missing_exceptions_fail(repo, exception_script):
    """An empty tracked set leaves every exception stale; header exit code is 1."""
    result = run(repo, script=exception_script)

    assert result.returncode == 1
    for name in EXCEPTIONS:
        assert f"{name}: stale allowlist entry (not tracked)" in result.stdout
    assert "PASS" not in result.stdout


def test_worker_model_pin_readded_is_rejected(repo):
    name = ".codex/agents/worker/config.toml"
    track(repo, name, 'model_reasoning_effort = "medium"\nmodel = "unsupported"\n')
    result = run(repo)
    assert result.returncode == 1
    assert f'{name}:2: model = "unsupported"' in result.stdout
    assert "ALLOW" not in result.stdout


def test_untracked_config_is_not_checked(repo):
    root, _ = repo
    (root / ".codex").mkdir()
    (root / ".codex/config.toml").write_text('model = "x"\n')
    assert run(repo).returncode == 0


@pytest.mark.parametrize("args", [("--bad",), ("extra",), ("--help", "extra")])
def test_usage_errors(repo, args):
    assert run(repo, *args).returncode == 2


def test_help(repo):
    result = run(repo, "--help")
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_repository_has_no_unexpected_pins():
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    result = run((ROOT, env))
    assert result.returncode == 0, result.stdout + result.stderr


# Expected statuses follow the checker header's existing exit-code contract.
# TOML v1.0.0 (2021), Keys, String, Array, Table, Inline Table and Array of
# Tables: https://toml.io/en/v1.0.0 . Each row states the independent structural
# interpretation: only a decoded root model key is a pin (existing policy).
TOML_CASES = [
    ("comment", '# model = "x"\n', 0, "PASS", "comment has no key"),
    ("nested-array", 'matrix = [\n [1, 2],\n]\nmodel = "x"\n',
     1, "model =", "array closes before the root assignment"),
    ("four-quotes", 'x = """a""""\nmodel = "x"\n',
     1, "model =", "four quotes terminate a value containing one quote"),
    ("literal-string", "x = '''\nmodel = 'x'\n'''\n",
     0, "PASS", "model text belongs to a literal string"),
    ("inline-nested", 'x = { model = "x" }\n',
     0, "PASS", "model belongs to x"),
    ("inline-root", 'model = { name = "x" }\n',
     1, "model =", "root model exists even with a table value"),
    ("array-of-tables", '[[profiles.x]]\nmodel = "x"\n',
     0, "PASS", "model belongs to an array element below profiles"),
    ("root-table", '[model]\nname = "x"\n',
     1, "model =", "table declaration creates a root model key"),
    ("dotted-nested", 'profiles.x.model = "x"\n',
     0, "PASS", "dotted key places model below profiles"),
    ("dotted-root", 'model.name = "x"\n',
     1, "model =", "dotted key creates root model table"),
    ("quoted-key", "'model' = 'x'\n",
     1, "model =", "quoted key decodes to model"),
    ("escaped-key", r'"\u006dodel" = "x"' + '\n',
     1, "model =", "Unicode escape decodes to m"),
    ("quoted-dot", '"profiles.x.model" = "x"\n',
     0, "PASS", "quoted dots are literal key characters"),
    ("crlf", '# comment\r\nmodel = "x"\r\n',
     1, "model =", "CRLF is a permitted newline"),
    ("bom", '\ufeffmodel = "x"\n',
     1, "invalid TOML", "BOM is neither a bare key nor TOML whitespace"),
    ("empty", '', 0, "PASS", "empty document contains no key"),
    ("invalid", 'model = [\n',
     1, "invalid TOML", "array delimiter is not closed"),
    ("duplicate", 'model = "x"\nmodel = "y"\n',
     1, "invalid TOML", "duplicate key definitions are prohibited"),
    ("profile", '[profiles.x]\nmodel = "x"\n',
     0, "PASS", "model belongs to a profile table"),
]


@pytest.mark.parametrize(
    "case,text,status,message,basis", TOML_CASES, ids=[row[0] for row in TOML_CASES]
)
def test_toml_fixture_matrix(repo, case, text, status, message, basis):
    """Expected structure and diagnostic are written into each fixture row."""
    name = ".codex/config.toml"
    track(repo, name, text)
    result = run(repo)
    output = result.stdout + result.stderr
    assert result.returncode == status, (case, basis, output)
    assert message in output, (case, basis, output)
    if status:
        assert name in output
        assert "PASS" not in output


def test_exception_inventory_is_separate(repo, exception_script):
    """The three fixture exceptions are tracked root pins, hence exit 0.

    Expected membership is the fixture allowlist, independently of discovery
    order; no stale entry or ordinary configuration belongs in the inventory.
    """
    for name in EXCEPTIONS:
        track(repo, name, 'model = "small"\n')
    track(repo, ".codex/config.toml", '[profiles.x]\nmodel = "large"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 0
    inventory = result.stdout.split("Allowlisted pin inventory:\n", 1)[1]
    for name in EXCEPTIONS:
        assert f'ALLOW {name}: model = \'small\'' in inventory
    assert ".codex/config.toml" not in inventory


def test_empty_exception_inventory(repo):
    """The production allowlist is empty, so no exceptions are invented."""
    result = run(repo)
    assert result.returncode == 0
    assert "Allowlisted pin inventory:\n  (none)" in result.stdout


def test_missing_working_file_has_per_file_error(repo):
    """A tracked file removed from disk is unreadable: header status 1."""
    name = ".codex/config.toml"
    track(repo, name, 'model = "x"\n')
    (repo[0] / name).unlink()
    result = run(repo)
    assert result.returncode == 1
    assert f"{name}: cannot read UTF-8 configuration" in result.stderr
    assert "Traceback" not in result.stderr


def test_exception_without_pin_is_not_in_inventory(repo, exception_script):
    """All paths are tracked, but only the last lacks a root key: stale exit 1."""
    for name in EXCEPTIONS[:-1]:
        track(repo, name, 'model = "small"\n')
    track(repo, EXCEPTIONS[-1], '[profiles.x]\nmodel = "small"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 1
    assert f"{EXCEPTIONS[-1]}: stale allowlist entry (no root model key)" in result.stdout
    assert f"ALLOW {EXCEPTIONS[-1]}" not in result.stdout


def test_documented_example(repo):
    """Execute the documented TOML input and compare the published transcript.

    Array closure leaves a root key (TOML v1.0.0, Array and Table), so the
    checker's exit-code contract requires 1 independently of the transcript.
    """
    doc = (ROOT / "docs/operations/codex-model-pin-checker.md").read_text()
    example = doc.split("```toml\n", 1)[1].split("```", 1)[0]
    expected = doc.split("```text\n", 1)[1].split("```", 1)[0]
    track(repo, ".codex/config.toml", example)
    result = run(repo)
    assert result.returncode == 1
    assert result.stdout == expected
    assert result.stderr == ""


def test_invalid_utf8_has_per_file_error(repo):
    """TOML v1.0.0, Spec: a document must be UTF-8; byte ff is invalid."""
    name = ".codex/config.toml"
    track(repo, name, '')
    (repo[0] / name).write_bytes(b'\xff')
    result = run(repo)
    assert result.returncode == 1
    assert f"{name}: cannot read UTF-8 configuration" in result.stderr
    assert "Traceback" not in result.stderr


def test_inventory_survives_other_file_failure(repo, exception_script):
    """Valid exceptions remain inventory facts when an ordinary pin fails."""
    for name in EXCEPTIONS:
        track(repo, name, 'model = "small"\n')
    track(repo, ".codex/config.toml", 'model = "x"\n')
    result = run(repo, script=exception_script)
    assert result.returncode == 1
    inventory = result.stdout.split("Allowlisted pin inventory:\n", 1)[1]
    for name in EXCEPTIONS:
        assert f"ALLOW {name}" in inventory
    assert "PASS" not in result.stdout
