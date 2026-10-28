"""Exercise ingestion using only the adjacent synthetic fixture and temporary files."""

import json
import os
from pathlib import Path
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
INGEST = REPO_ROOT / "scripts" / "analysis" / "ingest-codex-sessions.sh"
FIXTURE = HERE / "fixtures" / "rollout-synthetic.jsonl"

# Independent oracle: rollout-synthetic.jsonl, in file order. The metadata date
# supplies the partition. Only the user, assistant and final user rows are
# messages: one + one + one = three turns; metadata and tool events add none.
FIXTURE_RECORDS = [
    {"type": "metadata", "synthetic": True, "date": "2000-01-02"},
    {"type": "message", "role": "user", "content": "Count the sample items."},
    {"type": "message", "role": "assistant", "content": "Reading the sample."},
    {"type": "tool_event", "content": "Sample read complete."},
    {"type": "message", "role": "user", "content": "Return the total."},
]
DATE = "2000-01-02"  # The literal metadata date in rollout-synthetic.jsonl.
EXPECTED_SIGNAL = {
    "event": "codex_session",
    "date": DATE,
    "session_id": "rollout-synthetic",  # Fixture basename, per the input contract.
    "turns": 3,  # Hand calculation above, independent of the production counter.
    "source": "codex",
}


def _check_ingestion(root: Path) -> None:
    original = FIXTURE.read_bytes()
    assert [json.loads(line) for line in original.splitlines()] == FIXTURE_RECORDS
    assert "logs" not in FIXTURE.relative_to(REPO_ROOT).parts

    # Check ignore rules even after the fixture is tracked in a clean checkout.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "--", str(FIXTURE)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    # git-check-ignore(1), EXIT STATUS: one means no supplied path is ignored.
    assert ignored.returncode == 1, ignored.stderr or ignored.stdout

    inputs = root / "inputs"
    partition = inputs.joinpath(*DATE.split("-"))
    partition.mkdir(parents=True)
    copied = partition / FIXTURE.name
    shutil.copyfile(FIXTURE, copied)
    signals = root / "signals"
    unrelated = root / "unrelated"
    unrelated.mkdir()
    isolated_home = root / "empty-home"
    isolated_home.mkdir()
    scratch = root / "scratch"
    scratch.mkdir()
    env.update(HOME=str(isolated_home), TMPDIR=str(scratch))

    result = subprocess.run(
        [
            "bash",
            str(INGEST),
            "--date",
            DATE,
            "--codex-dir",
            str(inputs),
            "--signals-dir",
            str(signals),
        ],
        cwd=unrelated,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    # bash(1), EXIT STATUS: zero denotes successful command execution.
    assert result.returncode == 0, result.stderr or result.stdout
    output = signals / f"{DATE}.jsonl"
    assert [json.loads(line) for line in output.read_text().splitlines()] == [EXPECTED_SIGNAL]
    assert copied.read_bytes() == original == FIXTURE.read_bytes()
    # Every file created by setup or ingestion is accounted for under this root.
    assert {path for path in root.rglob("*") if path.is_file()} == {copied, output}


def test_committed_ingest_fixture_is_relocatable(tmp_path: Path) -> None:
    _check_ingestion(tmp_path / "ordinary-root")


def test_ingest_fixture_under_spaced_root(tmp_path: Path) -> None:
    _check_ingestion(tmp_path / "parent with spaces" / "fixture root")
