"""Exercise merge gating with offline shell stubs; no GitHub operation occurs."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts/operations/merge-when-clean.sh"
HEAD = "1" * 40
OTHER = "2" * 40

GH_STUB = r'''#!/usr/bin/env bash
printf '%s\t' "$@" >> "$CALL_LOG"
printf '\n' >> "$CALL_LOG"
if [[ "$1 $2" == 'pr merge' ]]; then
  exit "${MERGE_RC:-0}"
fi
if [[ "$1 $2" != 'pr view' ]]; then exit 99; fi
if [[ " $* " == *' --json state '* ]]; then
  printf '%s\n' MERGED
elif [[ " $* " == *headRefOid* ]]; then
  printf '%s %s %s\n' "$PR_STATE" "$MERGE_STATE" "$OBSERVED_HEAD"
else
  printf '%s %s\n' "$PR_STATE" "$MERGE_STATE"
fi
'''


@pytest.fixture
def harness(tmp_path):
    bash = shutil.which("bash")
    if not bash and os.name == "nt":
        candidate = Path(os.environ["LOCALAPPDATA"]) / "Programs/Git/usr/bin/bash.exe"
        bash = str(candidate) if candidate.is_file() else None
    assert bash, "A real Bash runtime is required for this fixture"
    bins = tmp_path / "bins"
    bins.mkdir()
    for name, body in {"gh": GH_STUB, "sleep": "#!/usr/bin/env bash\nexit 0\n"}.items():
        path = bins / name
        path.write_text(body, encoding="utf-8", newline="\n")
        path.chmod(0o755)
    env = dict(os.environ)
    env.update(PATH=os.pathsep.join([str(bins), str(Path(bash).parent), env["PATH"]]),
               CALL_LOG=str(tmp_path / "calls.tsv"), PR_STATE="OPEN",
               MERGE_STATE="CLEAN", OBSERVED_HEAD=HEAD)
    return bash, env, tmp_path


def invoke(harness, *arguments, **changes):
    bash, initial, cwd = harness
    env = dict(initial, **changes)
    # Native Windows argv conversion strips an unquoted trailing newline.
    # Quoted shell expansion preserves each adversarial argument exactly.
    args = [str(HELPER), "123", "--repo", "fixture/owned", "--once", *arguments]
    env.update({f"TEST_ARG_{i}": value for i, value in enumerate(args)})
    command = 'exec bash --noprofile --norc ' + " ".join(
        f'"$TEST_ARG_{i}"' for i in range(len(args)))
    result = subprocess.run([bash, "--noprofile", "--norc", "-c", command],
                            cwd=cwd, env=env, capture_output=True, text=True, timeout=15)
    log = Path(env["CALL_LOG"])
    calls = [line.rstrip("\t").split("\t") for line in log.read_text().splitlines()] if log.exists() else []
    return result, calls


def merges(calls):
    return [call for call in calls if call[:2] == ["pr", "merge"]]


@pytest.mark.parametrize("explicit", [False, True])
def test_clean_merge_binds_server_head(harness, explicit):
    args = ["--merge"] + (["--expected-head", HEAD] if explicit else [])
    result, calls = invoke(harness, *args)
    assert result.returncode == 0, result.stderr
    merge = merges(calls)
    assert len(merge) == 1
    assert merge[0] == ["pr", "merge", "123", "--repo", "fixture/owned",
                        "--squash", "--delete-branch", "--match-head-commit", HEAD]
    assert any("headRefOid" in argument for call in calls for argument in call)


def test_expected_head_mismatch_refuses(harness):
    result, calls = invoke(harness, "--merge", "--expected-head", HEAD, OBSERVED_HEAD=OTHER)
    assert result.returncode == 6
    assert calls and not merges(calls)


@pytest.mark.parametrize("arguments", [
    ["--expected-head"], ["--expected-head", ""], ["--expected-head", "short"],
    ["--expected-head", "A" * 40], ["--expected-head", "g" * 40],
    ["--expected-head", "1" * 39], ["--expected-head", "1" * 41],
    ["--expected-head", "--merge"], ["--expected-head", HEAD + "\n"]])
def test_invalid_expected_head_stops_before_gh(harness, arguments):
    result, calls = invoke(harness, *arguments)
    assert result.returncode == 5
    assert not calls


@pytest.mark.parametrize("head", ["", "null", "bad", "A" * 40, "1" * 39])
def test_invalid_observed_head_never_merges(harness, head):
    result, calls = invoke(harness, "--merge", OBSERVED_HEAD=head)
    assert result.returncode != 0
    assert not merges(calls)


@pytest.mark.parametrize("explicit", [False, True])
def test_server_race_refusal_is_not_retried(harness, explicit):
    args = ["--merge"] + (["--expected-head", HEAD] if explicit else [])
    result, calls = invoke(harness, *args, MERGE_RC="7")
    assert result.returncode != 0
    assert len(merges(calls)) == 1
    assert merges(calls)[0][-2:] == ["--match-head-commit", HEAD]
    assert calls[-1][:2] == ["pr", "merge"]


@pytest.mark.parametrize("explicit", [False, True])
def test_watch_only_prints_bound_command_without_merging(harness, explicit):
    args = ["--expected-head", HEAD] if explicit else []
    result, calls = invoke(harness, *args)
    assert result.returncode == 0
    assert not merges(calls)
    assert "--match-head-commit " + HEAD in result.stdout


@pytest.mark.parametrize("status,code", [
    ("BLOCKED", 0), ("BEHIND", 0), ("UNSTABLE", 0), ("UNKNOWN", 0), ("DIRTY", 2)])
def test_nonclean_once_never_merges(harness, status, code):
    result, calls = invoke(harness, "--merge", MERGE_STATE=status)
    assert result.returncode == code
    assert not merges(calls)


@pytest.mark.parametrize("state,code", [("MERGED", 0), ("CLOSED", 4)])
def test_terminal_pr_state_preserved(harness, state, code):
    result, calls = invoke(harness, "--merge", PR_STATE=state)
    assert result.returncode == code
    assert not merges(calls)
