"""Consumer-only regression contract for issue 2377; no emitter is exercised.

The synthetic example has four signal files. Its session_end arrays are
[alpha, beta, alpha], [beta, gamma], [alpha], and []. Hand calculation gives
alpha: 3 / 4 = 0.75, beta: 2 / 4 = 0.50, gamma: 1 / 4 = 0.25. Repeated
invocations count separately; extra events do not add signal files. These are
independent expectations, not values extracted from the consumer.

Dates are arbitrary frozen fixture inputs. Version and output field spellings
cite scripts/analysis/session-analysis.sh, Step 3. Shell exit statuses use the
POSIX success/failure convention; the subprocess timeout is a safety limit.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import stat
import subprocess
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[2] / "scripts/analysis/session-analysis.sh"
ANALYSIS_DATE = "2026-01-14"
TODAY = "2026-01-15"
NOW = f"{TODAY}T12:00:00Z"
TIMEOUT_SECONDS = 30  # Safety cap only; unrelated to any scoring expectation.

# Issue-defined event names. Poison skill arrays make an overly broad selector
# observable even when a new event otherwise resembles session_end.
EXTRA_EVENTS = (
    {"event": "verify_gate_evidence_result", "result": "pass"},
    {"event": "test_write_event", "file_path": "tests/example.py"},
    {"event": "impl_write_event", "file_path": "src/example.py"},
    {"event": "skill_invoke", "skill": "poison"},
    {"event": "gate_bypass", "reason": "synthetic fixture"},
)
INVOCATIONS = (
    ("alpha", "beta", "alpha"),
    ("beta", "gamma"),
    ("alpha",),
    (),
)
# One consolidated name and three legacy suffix names; four files in total.
SIGNAL_NAMES = (
    f"{ANALYSIS_DATE}.jsonl",
    f"{ANALYSIS_DATE}-010000.jsonl",
    f"{ANALYSIS_DATE}-020000.jsonl",
    f"{ANALYSIS_DATE}-030000.jsonl",
)


def _stub(path: Path, bash: str, body: str) -> None:
    path.write_text(f"#!{bash}\nset -eu\n{body}\n")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def _scorecard(text: str) -> tuple[str, dict[str, dict[str, str]]]:
    """Compare all fields while allowing Bash's associative-key ordering."""
    header, skills = text.split("\nskills:\n")
    entries = {}
    for block in re.split(r"(?m)(?=^  [a-z]+:\n)", skills):
        if not block:
            continue
        name, *fields = block.splitlines()
        assert name.endswith(":"), block
        assert name.strip() not in entries, "duplicate skill block"
        pairs = [field.strip().split(": ", maxsplit=1) for field in fields]
        assert len(dict(pairs)) == len(pairs), "duplicate score field"
        entries[name.strip().removesuffix(":")] = dict(pairs)
    return header, entries


def _assert_hand_counted_scorecard(text: str) -> None:
    header, entries = _scorecard(text)
    assert header == (
        "# Skill performance scorecard — updated by session-analysis.sh (3AM cron)\n"
        "# Fields: usage_rate, one_shot_rate, mean_corrections, last_used, sessions_tracked\n"
        "version: 1.0.0\n"
        f"updated: {TODAY}"
    )
    expected = {}
    # The invocation counts and rates are the independent calculation above.
    for skill, count, rate in (
        ("alpha", "3", "0.75"),
        ("beta", "2", "0.50"),
        ("gamma", "1", "0.25"),
    ):
        expected[skill] = {
            "usage_rate": rate,
            "one_shot_rate": "null",
            "mean_corrections": "null",
            "last_used": f'"{ANALYSIS_DATE}"',
            "sessions_tracked": count,
        }
    assert entries == expected


def _run_analysis(root: Path, extra_events: tuple[dict, ...] = ()) -> str:
    # Only these executables are exposed to the child. Require real arithmetic:
    # missing bc must fail setup, never exercise the consumer's silent zero fallback.
    commands = (
        "bash", "jq", "bc", "dirname", "mkdir", "find", "grep", "awk", "mv",
        "wc", "tr", "sort", "uniq", "head", "tail", "ls", "basename",
    )
    tools = {name: shutil.which(name) for name in commands}
    missing = [name for name, path in tools.items() if path is None]
    assert not missing, f"Required fixture tools unavailable: {', '.join(missing)}"
    bash = tools["bash"]
    script = root / "scripts/analysis/session-analysis.sh"
    script.parent.mkdir(parents=True)
    shutil.copyfile(SOURCE, script)
    state = root / ".claude/state"
    signals = state / "session-signals"
    signals.mkdir(parents=True)
    bin_dir = root / "bin"
    bin_dir.mkdir()
    for name, target in tools.items():
        (bin_dir / name).symlink_to(target)
    for name in ("user", "tmp"):
        (root / name).mkdir()

    for name, invocations in zip(SIGNAL_NAMES, INVOCATIONS, strict=True):
        end = {"event": "session_end", "signals": {"skill_invocations": invocations}}
        start = {"event": "session_start"}
        poison = [
            {**event, "signals": {"skill_invocations": ["poison", "alpha"]}}
            for event in extra_events
        ]
        # Exercise extra records before, between and after the existing records,
        # including the file with an empty skill array.
        records = [*poison, start, *poison, end, *poison]
        (signals / name).write_text("".join(json.dumps(row) + "\n" for row in records))

    # A discovery probe is the only permitted Git invocation; it reports a fake
    # non-repository. Any pull or other operation is recorded and fails the test,
    # even if the consumer suppresses its exit status or stderr.
    _stub(bin_dir / "git", bash, """
if [[ "$*" == "-C $FIXTURE_ROOT rev-parse --git-dir" ]]; then
    printf 'git discovery\n' >> "$FIXTURE_CALLS"
    exit 1
fi
printf 'git\n' >> "$FIXTURE_DENIALS"
exit 1
""")
    _stub(bin_dir / "date", bash, f"""
case "$*" in
    '+%Y-%m-%d') printf '%s\\n' {shlex.quote(TODAY)} ;;
    '-u +%Y-%m-%dT%H:%M:%SZ') printf '%s\\n' {shlex.quote(NOW)} ;;
    *) printf 'date\\n' >> "$FIXTURE_DENIALS"; exit 1 ;;
esac
""")
    # No real provider, network client or aggregation program is reachable.
    # Unknown commands also fail via the restricted PATH and stderr assertion.
    for name in ("curl", "wget", "ssh", "scp", "sftp", "rsync", "gh",
                 "claude", "codex", "gemini", "session-aggregate.sh"):
        _stub(bin_dir / name, bash, """
printf '%s\n' "${0##*/}" >> "$FIXTURE_DENIALS"
exit 1
""")
    calls = root / "calls.txt"
    denials = root / "denials.txt"
    # A fresh environment drops inherited Git bindings, shell startup files,
    # credentials, provider configuration and executable search paths.
    env = {
        "PATH": str(bin_dir), "HOME": str(root / "user"),
        "TMPDIR": str(root / "tmp"), "PYTHONDONTWRITEBYTECODE": "1",
        "LANG": "C", "LC_ALL": "C", "TZ": "UTC",
        "FIXTURE_ROOT": str(root), "FIXTURE_CALLS": str(calls),
        "FIXTURE_DENIALS": str(denials),
    }
    before = {p.relative_to(root): p.read_bytes()
              for p in root.rglob("*") if p.is_file() and not p.is_symlink()}
    result = subprocess.run(
        [bash, str(script), "--date", ANALYSIS_DATE], cwd=root, env=env,
        capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False,
    )
    assert not denials.exists(), "Forbidden external command attempted"
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr.splitlines() == [
        "[session-analysis] WARN: git not available — skipping cross-machine aggregation"
    ]
    assert calls.read_text().splitlines() == ["git discovery"]
    after = {p.relative_to(root): p.read_bytes()
             for p in root.rglob("*") if p.is_file() and not p.is_symlink()}
    assert all(after.get(path) == content for path, content in before.items())
    expected_outputs = {
        Path("calls.txt"), Path(".claude/state/skill-scores.yaml"),
        Path(f".claude/state/session-analysis/{ANALYSIS_DATE}.md"),
    }
    assert after.keys() - before.keys() == expected_outputs
    summary = (state / "session-analysis" / f"{ANALYSIS_DATE}.md").read_text()
    # Independently counted: four input files and three distinct scored skills.
    assert "Sessions analysed: 4\n" in summary
    assert "Skills scored: 3\n" in summary
    assert f"_Generated: {NOW}_" in summary
    scorecard = (state / "skill-scores.yaml").read_text()
    _assert_hand_counted_scorecard(scorecard)
    return scorecard


def test_session_end_baseline(tmp_path: Path) -> None:
    _run_analysis(tmp_path / "baseline")


@pytest.mark.parametrize("event", EXTRA_EVENTS, ids=lambda event: event["event"])
def test_new_event_preserves_scoring(tmp_path: Path, event: dict) -> None:
    baseline = _run_analysis(tmp_path / "baseline")
    enriched = _run_analysis(tmp_path / "enriched", (event,))
    assert _scorecard(enriched) == _scorecard(baseline)


def test_mixed_events_preserve_scoring(tmp_path: Path) -> None:
    baseline = _run_analysis(tmp_path / "baseline")
    enriched = _run_analysis(tmp_path / "enriched", EXTRA_EVENTS)
    assert _scorecard(enriched) == _scorecard(baseline)
