"""Local snapshot contract from scripts/ai/assessment/lib/providers.sh.

The acceptance cases are specified in issue 2843. All records below are literal
synthetic examples, independent of the implementation: zero usage leaves 100
percent remaining (100 - 0); 37 percent usage leaves 63 (100 - 37). The separate
short-window example uses 25 percent. No live usage or credentials are inputs.
Shell status values use the Bash convention: success is 0, false is 1. The
10-second subprocess timeout is a test safety bound, not a quota assumption.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

# This file is two directories below the repository root.
PROVIDERS = Path(__file__).resolve().parents[2] / "scripts/ai/assessment/lib/providers.sh"

ZERO = {
    "provider": "claude",
    "source": "oauth-api",
    "week_pct": 0,
    "five_hour_pct": 0,
    "pct_remaining": 100,
    "fixture": "zero",
}
NONZERO = {
    "provider": "claude",
    "source": "oauth-api",
    "week_pct": 37,
    "five_hour_pct": 25,
    "pct_remaining": 63,
    "fixture": "nonzero",
}
OTHER_PROVIDER = {"provider": "gemini", "source": "oauth-api", "week_pct": 37}
WRONG_SOURCE = {"provider": "claude", "source": "stats-cache.json", "week_pct": 37}


@pytest.fixture
def snapshot_shell(tmp_path):
    """Expose only jq; reject attempted tools even if their status is swallowed."""
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    assert bash and jq, "The snapshot contract requires Bash and jq"
    tools = tmp_path / "bin"
    tools.mkdir()
    (tools / "jq").symlink_to(jq)
    isolated_home = tmp_path / "empty-home"
    isolated_home.mkdir()
    snapshot = tmp_path / "quota.json"
    attempts = tmp_path / "forbidden-attempts"
    # Build a fresh environment: no inherited startup scripts, credentials,
    # exported functions, provider configuration or repository bindings.
    env = {
        "PATH": str(tools),
        "HOME": str(isolated_home),
        "XDG_CONFIG_HOME": str(isolated_home),
        "TMPDIR": str(tmp_path),
        "REPO_QUOTA_FILE": str(snapshot),
        "ATTEMPTS": str(attempts),
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    shell = r'''
        forbidden() {
            printf '%s\n' 'unexpected fallback or external access' >> "$ATTEMPTS"
            return 1
        }
        command_not_found_handle() { forbidden; }
        source "$1"
        # These functions must never be reached by either contract entry point.
        get_ccusage_weekly() { forbidden; }
        query_claude_stats() { forbidden; }
        query_codex() { forbidden; }
        query_gemini() { forbidden; }
        # The authoritative branch is checked independently of enrichment.
        _enrich_with_ccusage() { printf '%s\n' "$1"; }
        jq() {
            local arg
            for arg in "$@"; do
                if [[ "$arg" == /* && "$arg" != "$REPO_QUOTA_FILE" ]]; then
                    forbidden
                    return 1
                fi
            done
            command jq "$@"
        }
        "$2"
    '''

    def run(payload, function="get_claude_oauth_entry"):
        if payload is not None:
            snapshot.write_text(payload, encoding="utf-8")
        result = subprocess.run(
            [bash, "--noprofile", "--norc", "-c", shell, "snapshot-test",
             str(PROVIDERS), function],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        assert not attempts.exists(), "A forbidden fallback or tool was attempted"
        assert result.stderr == ""
        return result

    return run


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(None, id="absent-file"),
        pytest.param("{", id="malformed-json"),
        pytest.param("", id="empty-file"),
        pytest.param("null", id="null-document"),
        pytest.param('{}', id="missing-agents"),
        pytest.param('{"agents":[]}', id="empty-agents"),
        pytest.param(json.dumps({"agents": [OTHER_PROVIDER]}), id="other-provider"),
        pytest.param(json.dumps({"agents": [WRONG_SOURCE]}), id="wrong-source"),
        pytest.param(
            '{"agents":[{"provider":"claude","source":"unavailable","week_pct":null}]}',
            id="unavailable",
        ),
        pytest.param(
            '{"agents":[{"provider":"claude","source":"oauth-api","week_pct":null}]}',
            id="null-week",
        ),
        pytest.param(
            '{"agents":[{"provider":"claude","source":"oauth-api"}]}',
            id="missing-week",
        ),
        pytest.param('{"agents":[{"provider":"claude","week_pct":37}]}', id="missing-source"),
    ],
)
def test_rejects_unavailable_or_non_authoritative_snapshots(snapshot_shell, payload):
    # Never exercise query_claude's missing-source fallback, even in isolation.
    result = snapshot_shell(payload)
    assert result.returncode in (0, 1)
    assert result.stdout == ""


@pytest.mark.parametrize("entry", [ZERO, NONZERO], ids=["zero", "nonzero"])
@pytest.mark.parametrize("mixed", [False, True], ids=["single", "mixed"])
@pytest.mark.parametrize("function", ["get_claude_oauth_entry", "query_claude"])
def test_authoritative_entry_is_preserved(snapshot_shell, entry, mixed, function):
    agents = [OTHER_PROVIDER, WRONG_SOURCE, entry] if mixed else [entry]
    result = snapshot_shell(json.dumps({"agents": agents}), function)
    assert result.returncode == 0
    # Literal records supply the oracle; no quota arithmetic comes from the shell.
    assert json.loads(result.stdout) == entry
