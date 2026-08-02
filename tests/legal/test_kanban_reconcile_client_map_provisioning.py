"""kanban-reconcile.yml must provision the private client map (#3768 / #3775).

`scripts/kanban/reconcile.py` fails CLOSED (exit 3, writes nothing) when the
client-codename map is absent, because board cards embed raw GitHub issue titles
and this repo is PUBLIC and pushed to `main` every 20 minutes. The workflow did
not materialize the LEGAL_CLIENT_MAP secret, so the */20 cron would exit 3 on
every run and the boards would stop reconciling entirely.

These assertions are structural (ordering, scoping, secret handling). The point
they defend is that the fix must be PROVISIONING, never a relaxation of the
fail-closed behaviour — so several of them assert the absence of an escape hatch.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[2]
WF_PATH = REPO_ROOT / ".github" / "workflows" / "kanban-reconcile.yml"
JOB = "reconcile"


@pytest.fixture(scope="module")
def wf() -> dict:
    return yaml.safe_load(WF_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def raw() -> str:
    return WF_PATH.read_text(encoding="utf-8")


def steps(wf: dict) -> list[dict]:
    return wf["jobs"][JOB]["steps"]


def index_of(wf: dict, needle: str) -> int:
    """Index of the first step whose run body or env mentions `needle`.

    Raises rather than returning -1: `steps(wf)[-1]` is the LAST step, so a
    sentinel index silently makes every downstream assertion test the wrong step
    (two of these tests passed vacuously that way before this raise existed).
    """
    for i, s in enumerate(steps(wf)):
        if needle in str(s.get("run", "")) or needle in str(s.get("env", "")):
            return i
    raise AssertionError(f"no step in job '{JOB}' mentions {needle!r}")


def has_step(wf: dict, needle: str) -> bool:
    try:
        index_of(wf, needle)
        return True
    except AssertionError:
        return False


# ── the provisioning must exist, in this job, before the reconcile ────────────


def test_client_map_secret_is_materialized(wf):
    assert has_step(wf, "LEGAL_CLIENT_MAP"), (
        "reconcile.py exits 3 without the map — the */20 cron would never reconcile"
    )


def test_provisioning_precedes_the_reconcile_invocation(wf):
    prov = index_of(wf, "LEGAL_CLIENT_MAP")
    recon = index_of(wf, "scripts/kanban/reconcile.py")
    assert prov < recon, "the map is provisioned after reconcile.py already needed it"


def test_provisioning_is_in_the_same_job_as_the_reconcile(wf):
    """$GITHUB_ENV does not cross jobs, and RUNNER_TEMP is per-job."""
    bodies = [str(s.get("run", "")) + str(s.get("env", "")) for s in steps(wf)]
    assert any("LEGAL_CLIENT_MAP" in b for b in bodies)
    assert any("scripts/kanban/reconcile.py" in b for b in bodies)


def test_provisioning_exports_via_github_env_not_a_local_shell_var(wf):
    """$GITHUB_ENV writes are the only thing a LATER step can see."""
    i = index_of(wf, "LEGAL_CLIENT_MAP")
    body = steps(wf)[i]["run"]
    assert "GITHUB_ENV" in body
    assert re.search(r'LEGAL_CLIENT_MAP=.*>>\s*"?\$GITHUB_ENV', body)


def test_provisioning_and_reconcile_are_separate_steps(wf):
    """A $GITHUB_ENV export is not visible within the step that writes it."""
    assert index_of(wf, "LEGAL_CLIENT_MAP") != index_of(wf, "scripts/kanban/reconcile.py")


# ── secret handling matches the PII gate exactly ─────────────────────────────


def test_secret_reaches_the_shell_only_through_env(raw):
    """`${{ secrets.* }}` inlined into a shell body is a leak/injection risk.

    The positive assertion is load-bearing: a loop over zero matching lines
    passes vacuously, so "no bad reference" must be paired with "a reference
    exists at all" (this test survived mutation without it).
    """
    refs = [ln for ln in raw.splitlines() if "secrets.LEGAL_CLIENT_MAP" in ln]
    assert refs, "the workflow no longer references the LEGAL_CLIENT_MAP secret"
    for line in refs:
        assert re.match(r"\s*[A-Z_]+:\s*\$\{\{\s*secrets\.", line), line


def test_secret_is_written_with_printf_not_echo(wf):
    """`printf '%s'` — no trailing newline, no backslash interpretation."""
    body = steps(wf)[index_of(wf, "LEGAL_CLIENT_MAP")]["run"]
    assert "printf '%s'" in body


def test_map_file_is_never_read_back_to_a_log(wf):
    """These logs are PUBLIC. The map is written and passed by path, never dumped."""
    for s in steps(wf):
        body = str(s.get("run", ""))
        assert not re.search(
            r"\b(cat|head|tail|base64|xxd|od|less|more)\b[^\n]*client-map\.yaml", body
        )


def test_secret_value_only_ever_goes_into_a_file(wf):
    """The secret may be tested for emptiness or redirected into RUNNER_TEMP.

    Anything else — a bare `echo "$SECRET"`, or a redirect to `>&2`/`>&1` —
    puts the private client list into a PUBLIC Actions log.
    """
    for s in steps(wf):
        for line in str(s.get("run", "")).splitlines():
            if "$LEGAL_CLIENT_MAP_SECRET" not in line:
                continue
            if re.match(r'\s*if \[\[ -z "\$LEGAL_CLIENT_MAP_SECRET" \]\]', line):
                continue  # emptiness test, value not expanded into output
            assert re.search(r'>\s*"\$RUNNER_TEMP/[^"]+"\s*$', line), (
                f"secret value reaches a log stream: {line!r}"
            )


def test_map_lands_outside_the_workspace(wf):
    """The reconcile loop runs `git reset --hard`; RUNNER_TEMP survives it, and the
    map must never become a committable working-tree file in a PUBLIC repo."""
    body = steps(wf)[index_of(wf, "LEGAL_CLIENT_MAP")]["run"]
    assert "RUNNER_TEMP" in body
    assert "GITHUB_WORKSPACE" not in body


# ── the fix must not weaken fail-closed ──────────────────────────────────────


def test_reconcile_is_not_given_a_redaction_escape_hatch(wf):
    """--no-redact is preview-only; it must never appear on the writing path."""
    for s in steps(wf):
        assert "--no-redact" not in str(s.get("run", ""))


def test_missing_secret_does_not_degrade_to_a_write(wf):
    """Unlike the PII gate (which runs on fork PRs), this cron has no fork story.

    A missing secret must go RED, never silently reconcile. Structural check
    only — see the behavioural tests below, which actually run the step; a bare
    grep for `exit 1` survives mutation because the token appears elsewhere.
    """
    body = steps(wf)[index_of(wf, "LEGAL_CLIENT_MAP")]["run"]
    assert re.search(r"exit\s+1", body), (
        "no abort path: a missing secret would fall through to reconcile.py"
    )


# ── behavioural: actually run the provisioning step ──────────────────────────

SENTINEL_MAP = "version: 1\nrules:\n  - {pattern: 'zzsynth', replacement: 'c-a'}\n"


def _provision(tmp_path: Path, wf: dict, secret: str):
    """Execute the provisioning step's shell body with a synthetic secret."""
    body = steps(wf)[index_of(wf, "LEGAL_CLIENT_MAP")]["run"]
    work = tmp_path / "w"
    work.mkdir(exist_ok=True)
    ws = tmp_path / "ws"
    ws.mkdir(exist_ok=True)
    gh_env = tmp_path / "github_env"
    gh_env.write_text("", encoding="utf-8")
    script = tmp_path / "prov.sh"
    script.write_text(body, encoding="utf-8")
    env = dict(os.environ)
    env.update(
        LEGAL_CLIENT_MAP_SECRET=secret,
        RUNNER_TEMP=str(work),
        GITHUB_WORKSPACE=str(ws),
        GITHUB_ENV=str(gh_env),
    )
    p = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
    return p, work / "client-map.yaml", gh_env.read_text(encoding="utf-8")


needs_bash = pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")


@needs_bash
def test_empty_secret_aborts_and_writes_no_map(tmp_path, wf):
    p, map_file, gh_env = _provision(tmp_path, wf, "")
    assert p.returncode != 0, "an absent secret let the run continue to reconcile"
    assert not map_file.exists(), "wrote a map file from an empty secret"
    assert "LEGAL_CLIENT_MAP=" not in gh_env, "exported a map path that does not exist"


@needs_bash
def test_present_secret_lands_byte_for_byte(tmp_path, wf):
    """`printf '%s'` semantics as a PROPERTY: no trailing newline, no mangling.

    A YAML map is whitespace-sensitive and the redactor's patterns are regexes,
    so `echo` (which appends \\n and may interpret backslashes) is not equivalent.
    """
    secret = SENTINEL_MAP + "  - {pattern: 'a\\\\d+b', replacement: 'c-b'}"
    p, map_file, gh_env = _provision(tmp_path, wf, secret)
    assert p.returncode == 0, p.stderr
    assert map_file.read_text(encoding="utf-8") == secret
    assert f"LEGAL_CLIENT_MAP={map_file}" in gh_env


@needs_bash
def test_provisioning_never_prints_the_secret(tmp_path, wf):
    """These logs are PUBLIC — the private client list must not reach them."""
    p, _map_file, _gh_env = _provision(tmp_path, wf, SENTINEL_MAP)
    blob = p.stdout + p.stderr
    assert "zzsynth" not in blob
    assert "rules:" not in blob


def test_reconcile_exit_status_is_not_swallowed(wf):
    body = steps(wf)[index_of(wf, "scripts/kanban/reconcile.py")]["run"]
    assert "reconcile.py || true" not in body
    assert not re.search(r"reconcile\.py[^\n]*\|\|\s*:", body)


def test_anti_loop_split_is_preserved(wf):
    """The board push must keep using the DEFAULT token, not the App token.

    A push carrying the App token would retrigger CI — including the new
    push-triggered client-PII scan on main — which is the loop the split exists
    to prevent.
    """
    body = steps(wf)[index_of(wf, "scripts/kanban/reconcile.py")]["run"]
    env = steps(wf)[index_of(wf, "scripts/kanban/reconcile.py")]["env"]
    assert env.get("GH_TOKEN") == "${{ github.token }}"
    assert env.get("GITHUB_TOKEN") == "${{ github.token }}"
    # The App token is scoped to the reconcile invocation only, never exported
    # around the push.
    assert re.search(r'GH_TOKEN="\$APP_TOKEN"[^\n]*reconcile\.py', body)
