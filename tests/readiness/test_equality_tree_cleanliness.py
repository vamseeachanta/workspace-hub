"""TDD tests for #3702 — equality generation must write OUT of the tracked working tree.

The defect: `collect-equality.sh` writes `.claude/state/equality-<machine>.yaml` and
`build-equality-matrix.py` writes `docs/reports/*machine-equality-matrix.html` straight
into the tracked checkout. Both paths are also advanced on `origin/main` by every peer's
publish, so `git pull --ff-only` aborts with "local changes would be overwritten", the
box never catches up, `behind_main` ratchets, and `is_stale()` stamps STALE-CHECKOUT on
all 27 dimensions.

The fix: an `EQ_STATE_DIR` / `EQ_REPORT_DIR` seam whose default resolves OUT of the
repo (`${XDG_STATE_HOME:-$HOME/.local/state}/workspace-hub/equality`). The published
surface on `origin/main` is unchanged — `publish-equality.sh` already writes through a
disposable sparse worktree.

RED rows (must fail against `main`) and REGRESSION rows (guards) are separated below.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RD = REPO_ROOT / "scripts" / "readiness"
COLLECT = RD / "collect-equality.sh"
BUILDER = RD / "build-equality-matrix.py"
CRON = RD / "equality-matrix-cron.sh"
PUBLISH = RD / "publish-equality.sh"
PREFLIGHT_LIB = RD / "lib" / "ff-preflight.sh"
PREFLIGHT_WRAPPER = RD / "equality-preflight.sh"
CURATION = REPO_ROOT / "scripts" / "curation" / "curate-session-memory.sh"
CURATION_PREFLIGHT = REPO_ROOT / "scripts" / "curation" / "session-curation-preflight.sh"
ENFORCE = REPO_ROOT / "scripts" / "enforcement" / "check-equality-artifacts-out-of-tree.sh"
COLLECT_PS1 = RD / "collect-equality.ps1"
REPORT_PS1 = REPO_ROOT / "scripts" / "windows" / "equality-report.ps1"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@example.com",
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
}


# ── fixture plumbing ─────────────────────────────────────────────────────────
def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    res = subprocess.run(["git", *args], cwd=cwd, env={**os.environ, **GIT_ENV},
                         capture_output=True, text=True, timeout=120)
    if check:
        assert res.returncode == 0, f"git {' '.join(args)}: {res.stdout}\n{res.stderr}"
    return res


def _copy(rel: str, ws: Path) -> None:
    src, dst = REPO_ROOT / rel, ws / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def _stub(ws: Path, rel: str, body: str = "#!/usr/bin/env bash\nexit 0\n") -> None:
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    p.chmod(0o755)


HARNESS_CONFIG = yaml.safe_dump({
    "workstations": {
        "dev-primary": {"status": "active"},
        "peer-box": {"status": "active"},
    },
    "tier1_repos": ["assetutilities", "digitalmodel", "worldenergydata", "assethold"],
})

STALE_SEED_YAML = (
    'generated_at: "2020-01-01T00:00:00"\n'
    'machine: "dev-primary"\n'
    'os: "linux"\n'
    'status: "active"\n'
    '# committed payload deliberately DIFFERS from what the collector emits, so the\n'
    '# canonical-payload commit-on-change guard (collect-equality.sh) cannot suppress\n'
    '# the write and make the cleanliness assertion pass vacuously (r1 M5).\n'
    'dimensions: {}\n'
)

# Repo layer: no provenance ⇒ STALE-CHECKOUT on every dimension.
PEER_REPO_YAML = (
    'generated_at: "2026-06-01T00:00:00"\nmachine: "peer-box"\nos: "linux"\n'
    'status: "active"\ndimensions: {}\n'
)
# Seam layer: provably fresh provenance ⇒ anything BUT STALE-CHECKOUT.
PEER_SEAM_YAML = (
    'generated_at: "2026-07-30T12:00:00"\nmachine: "peer-box"\nos: "linux"\n'
    'status: "active"\n'
    'provenance:\n  checkout_sha: "abc1234"\n  dirty: false\n  behind_main: 0\n'
    '  ahead_main: 0\n  origin_ref_age_h: 1\n'
    'dimensions: {}\n'
)


def _ws_fixture(tmp_path: Path, *, with_publisher: bool = False,
                with_curation: bool = False, seed_stale_evidence: bool = True) -> Path:
    """A committed git repo laid out like workspace-hub, carrying REAL generators."""
    ws = tmp_path / "ws"
    ws.mkdir()
    for rel in ("scripts/readiness/collect-equality.sh",
                "scripts/readiness/build-equality-matrix.py",
                "scripts/readiness/equality-matrix-cron.sh",
                "scripts/readiness/lib"):
        _copy(rel, ws)
    for optional in ("scripts/readiness/equality-preflight.sh",):
        if (REPO_ROOT / optional).exists():
            _copy(optional, ws)
    if with_publisher:
        _copy("scripts/readiness/publish-equality.sh", ws)
    else:
        _stub(ws, "scripts/readiness/publish-equality.sh")
    if with_curation:
        _copy("scripts/curation/curate-session-memory.sh", ws)
        if CURATION_PREFLIGHT.exists():
            _copy("scripts/curation/session-curation-preflight.sh", ws)
        for rel in ("scripts/curation/curate_session_memory.py",
                    "scripts/curation/audit_skill_currency.py",
                    "scripts/curation/detect_skill_drift.py",
                    "scripts/curation/audit_memory_freshness.py",
                    "scripts/skills/generate_skills_index.py"):
            _stub(ws, rel, "import sys\nsys.exit(0)\n")
        _stub(ws, "scripts/skills/resync-skill-links.sh")
    _stub(ws, "scripts/notify.sh")
    (ws / "scripts" / "readiness" / "harness-config.yaml").write_text(HARNESS_CONFIG)

    (ws / ".claude" / "skills" / "cat" / "skillA").mkdir(parents=True)
    (ws / ".claude" / "skills" / "cat" / "skillA" / "SKILL.md").write_text("x")
    (ws / ".claude" / "dispatch").mkdir(parents=True)
    (ws / ".claude" / "dispatch" / "dev-primary.yaml").write_text("x")
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    state = ws / ".claude" / "state"
    state.mkdir(parents=True)
    (state / "harness-readiness-dev-primary.yaml").write_text("overall: fail\npass_count: 17\n")
    if seed_stale_evidence:
        (state / "equality-dev-primary.yaml").write_text(STALE_SEED_YAML)
    # Repo-layer peer evidence carries NO provenance block ⇒ is_stale() fail-closes ⇒ every
    # peer-box dimension grades STALE-CHECKOUT. That verdict is the discriminator the
    # input-layering tests below key on.
    (state / "equality-peer-box.yaml").write_text(PEER_REPO_YAML)
    (ws / "docs" / "reports").mkdir(parents=True)
    (ws / "docs" / "reports" / ".gitkeep").write_text("")

    _git(ws, "init", "-q", "-b", "main")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "seed")
    _git(ws, "update-ref", "refs/remotes/origin/main", "HEAD")
    return ws


def _home(tmp_path: Path) -> Path:
    h = tmp_path / "home"
    h.mkdir(exist_ok=True)
    return h


def _env(ws: Path, tmp_path: Path, **extra: str) -> dict:
    """Runtime env for a generator run. HOME is redirected so the out-of-tree default
    resolves inside tmp_path — the tests never touch the operator's real state dir."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(_home(tmp_path)),
        "WORKSPACE_HUB": str(ws),
        "EQ_MACHINE": "dev-primary",
        "TMPDIR": str(tmp_path),
        # keep uv's package cache (HOME is redirected, so uv would otherwise re-resolve)
        "UV_CACHE_DIR": os.environ.get("UV_CACHE_DIR") or str(Path.home() / ".cache" / "uv"),
        **GIT_ENV,
    }
    env.pop("XDG_STATE_HOME", None)
    env.update(extra)
    return env


def _default_seam(tmp_path: Path) -> Path:
    """The out-of-tree default, resolved with the SAME precedence the scripts use."""
    return _home(tmp_path) / ".local" / "state" / "workspace-hub" / "equality"


def _snapshot(ws: Path) -> bytes:
    res = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ws, env={**os.environ, **GIT_ENV}, capture_output=True, timeout=120)
    assert res.returncode == 0, res.stderr
    return res.stdout


def _run_collect(ws: Path, tmp_path: Path, *args: str, expect_rc: int = 0,
                 **envx: str) -> subprocess.CompletedProcess:
    res = subprocess.run(["bash", str(ws / "scripts" / "readiness" / "collect-equality.sh"), *args],
                         env=_env(ws, tmp_path, **envx), capture_output=True, text=True,
                         timeout=180)
    assert res.returncode == expect_rc, f"rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res


def _run_builder(ws: Path, tmp_path: Path, *args: str, expect_rc: int = 0,
                 **envx: str) -> subprocess.CompletedProcess:
    res = subprocess.run([sys.executable,
                          str(ws / "scripts" / "readiness" / "build-equality-matrix.py"), *args],
                         env=_env(ws, tmp_path, **envx), capture_output=True, text=True,
                         timeout=180)
    assert res.returncode == expect_rc, f"rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res


# ══════════════════════════════════════════════════════════════════════════════
# RED — must FAIL against main before implementation
# ══════════════════════════════════════════════════════════════════════════════

def test_build_matrix_leaves_working_tree_clean(tmp_path):
    ws = _ws_fixture(tmp_path)
    before = _snapshot(ws)
    _run_builder(ws, tmp_path)
    assert _snapshot(ws) == before, "builder dirtied the tracked working tree"


def test_collect_leaves_working_tree_clean(tmp_path):
    # r1 M5: the seeded equality yaml is TRACKED and its canonical payload DIFFERS from
    # what the collector emits, so collect-equality.sh's commit-on-change guard cannot
    # suppress the write and let this pass vacuously against unfixed code.
    ws = _ws_fixture(tmp_path)
    before = _snapshot(ws)
    _run_collect(ws, tmp_path)
    assert _snapshot(ws) == before, "collector dirtied the tracked working tree"


def test_cron_leaves_working_tree_clean(tmp_path):
    ws = _ws_fixture(tmp_path)          # publisher is stubbed to exit 0
    before = _snapshot(ws)
    res = subprocess.run(["bash", str(ws / "scripts" / "readiness" / "equality-matrix-cron.sh")],
                         env=_env(ws, tmp_path), capture_output=True, text=True, timeout=300)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    assert _snapshot(ws) == before, "equality-matrix-cron.sh dirtied the tracked working tree"


def test_curate_session_memory_leaves_tree_clean(tmp_path):
    # r1 M2: the 6-hourly, 6-machine path that never publishes. If it keeps dirtying the
    # tree, behind_main keeps ratcheting and this issue does not land.
    ws = _ws_fixture(tmp_path, with_curation=True)
    before = _snapshot(ws)
    res = subprocess.run(["bash", str(ws / "scripts" / "curation" / "curate-session-memory.sh")],
                         env=_env(ws, tmp_path), capture_output=True, text=True, timeout=300)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    assert _snapshot(ws) == before, "curate-session-memory.sh dirtied the tracked working tree"


def test_ff_pull_unblocked_after_collect_and_build(tmp_path):
    """The regression this issue exists for: origin advances the two artifact paths, the
    box collects+builds, and `git pull --ff-only` must still fast-forward."""
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    ws = _ws_fixture(tmp_path)
    _git(ws, "remote", "add", "origin", str(origin))
    _git(ws, "push", "-q", "origin", "main")

    # A peer publishes: origin/main moves on BOTH artifact paths.
    peer = tmp_path / "peer"
    _git(tmp_path, "clone", "-q", str(origin), str(peer))
    (peer / ".claude" / "state" / "equality-peer-box.yaml").write_text(
        'generated_at: "2026-07-29T00:00:00"\nmachine: "peer-box"\nos: "linux"\n'
        'status: "active"\ndimensions: {}\n')
    (peer / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        STALE_SEED_YAML.replace("2020-01-01", "2020-01-02"))
    (peer / "docs" / "reports" / "machine-equality-matrix.html").write_text("<html>peer</html>")
    _git(peer, "add", "-A")
    _git(peer, "commit", "-q", "-m", "peer publish")
    _git(peer, "push", "-q", "origin", "main")

    _git(ws, "fetch", "-q", "origin", "main")
    assert _git(ws, "rev-list", "--count", "HEAD..origin/main").stdout.strip() == "1"

    _run_collect(ws, tmp_path)
    _run_builder(ws, tmp_path)

    pull = _git(ws, "pull", "--ff-only", "origin", "main", check=False)
    assert pull.returncode == 0, (
        "git pull --ff-only aborted after a collection run — the artifacts are still "
        f"blocking the fast-forward:\n{pull.stdout}\n{pull.stderr}")
    assert _git(ws, "rev-list", "--count", "HEAD..origin/main").stdout.strip() == "0"


def test_collect_default_state_dir_is_outside_repo(tmp_path):
    ws = _ws_fixture(tmp_path)
    _run_collect(ws, tmp_path)
    written = _default_seam(tmp_path) / "equality-dev-primary.yaml"
    assert written.is_file(), f"collector did not write to the out-of-tree default {written}"
    toplevel = Path(_git(ws, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert toplevel not in written.resolve().parents, "default output is inside the repo"
    # …and the tracked in-tree copy is left exactly as committed.
    assert (ws / ".claude" / "state" / "equality-dev-primary.yaml").read_text() == STALE_SEED_YAML


def test_collect_honors_eq_state_dir_env(tmp_path):
    ws = _ws_fixture(tmp_path)
    seam = tmp_path / "seam-env"
    _run_collect(ws, tmp_path, EQ_STATE_DIR=str(seam))
    assert (seam / "equality-dev-primary.yaml").is_file()


def test_collect_honors_state_dir_flag_over_env(tmp_path):
    ws = _ws_fixture(tmp_path)
    env_seam, flag_seam = tmp_path / "seam-env", tmp_path / "seam-flag"
    _run_collect(ws, tmp_path, "--state-dir", str(flag_seam), EQ_STATE_DIR=str(env_seam))
    assert (flag_seam / "equality-dev-primary.yaml").is_file(), "--state-dir did not win"
    assert not (env_seam / "equality-dev-primary.yaml").exists(), "env seam was written too"


def test_build_matrix_honors_out_dir(tmp_path):
    ws = _ws_fixture(tmp_path)
    out = tmp_path / "outdir"
    _run_builder(ws, tmp_path, "--out-dir", str(out))
    assert (out / "machine-equality-matrix.html").is_file()
    assert len(list(out.glob("*-machine-equality-matrix.html"))) == 1, "dated report missing"
    assert not list((ws / "docs" / "reports").glob("*machine-equality-matrix.html"))


def test_build_matrix_state_dir_replaces_default_layers(tmp_path):
    """r1 M1 — `--state-dir` must REPLACE the default input list, never overlay it.

    Otherwise the publisher's in-worktree render folds the interactive checkout's stale
    peer evidence into the PUBLISHED matrix and destroys the union-of-freshest guarantee.
    """
    ws = _ws_fixture(tmp_path)
    only = tmp_path / "only"
    only.mkdir()
    (only / "equality-dev-primary.yaml").write_text(
        'generated_at: "2026-07-30T00:00:00"\nmachine: "dev-primary"\nos: "linux"\n'
        'status: "active"\ndimensions: {}\n')
    # Control: with the default layers the repo's peer-box evidence IS read (STALE-CHECKOUT).
    control = json.loads(_run_builder(ws, tmp_path, "--json").stdout)
    assert control["peer-box"]["compute"] == "STALE-CHECKOUT"
    # With --state-dir the repo layer must be REPLACED, so peer-box has no evidence at all.
    verdicts = json.loads(_run_builder(ws, tmp_path, "--state-dir", str(only), "--json").stdout)
    assert verdicts["peer-box"]["compute"] == "MISSING-EVIDENCE", (
        "peer-box evidence was folded in from the repo layer despite --state-dir "
        f"(got {verdicts['peer-box']['compute']})")


def test_build_matrix_overlays_local_over_repo_in_default_mode(tmp_path):
    ws = _ws_fixture(tmp_path)
    seam = tmp_path / "seam"
    seam.mkdir()
    (seam / "equality-peer-box.yaml").write_text(PEER_SEAM_YAML)   # fresh provenance
    # Control: without the seam layer the repo copy (no provenance) grades STALE-CHECKOUT.
    control = json.loads(_run_builder(ws, tmp_path, "--json").stdout)
    assert control["peer-box"]["compute"] == "STALE-CHECKOUT"
    verdicts = json.loads(
        _run_builder(ws, tmp_path, "--json", EQ_STATE_DIR=str(seam)).stdout)
    assert verdicts["peer-box"]["compute"] != "STALE-CHECKOUT", (
        "the seam copy did not override the repo copy in default mode")


def test_publish_reads_local_evidence_from_seam(tmp_path):
    origin, clone = _publish_fixture(tmp_path)
    seam = tmp_path / "seam"
    seam.mkdir()
    (seam / "equality-dev-primary.yaml").write_text(
        'generated_at: "2026-07-30T12:00:00"\nmachine: "dev-primary"\n')
    _run_publish(clone, tmp_path, EQ_STATE_DIR=str(seam))
    assert "2026-07-30T12:00:00" in _origin_file(
        origin, ".claude/state/equality-dev-primary.yaml")


def test_publish_ignores_stale_in_tree_copy(tmp_path):
    origin, clone = _publish_fixture(tmp_path)
    (clone / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        'generated_at: "2026-12-31T23:59:59"\nmachine: "dev-primary"\n')   # newer, in-tree
    seam = tmp_path / "seam"
    seam.mkdir()
    (seam / "equality-dev-primary.yaml").write_text(
        'generated_at: "2026-07-30T12:00:00"\nmachine: "dev-primary"\n')   # the seam is truth
    _run_publish(clone, tmp_path, EQ_STATE_DIR=str(seam))
    published = _origin_file(origin, ".claude/state/equality-dev-primary.yaml")
    assert "2026-07-30T12:00:00" in published
    assert "2026-12-31" not in published, "stale in-tree working copy was resurrected"


def test_publish_fails_loud_on_empty_seam_dir(tmp_path):
    """r1 M7 — an empty seam dir currently prints `nothing newer` and exits 0, taking a
    box dark on the matrix while every scheduled task reports success."""
    origin, clone = _publish_fixture(tmp_path)
    empty = tmp_path / "empty-seam"
    empty.mkdir()
    before = _git(origin, "rev-parse", "main").stdout.strip()
    res = _run_publish(clone, tmp_path, expect_rc=1, EQ_STATE_DIR=str(empty))
    assert "no commit needed" not in res.stdout, "silent dark-box: reported noop and exited 0"
    assert "no local equality evidence" in (res.stdout + res.stderr).lower()
    assert _git(origin, "rev-parse", "main").stdout.strip() == before


def test_preflight_ff_pulls_when_clean_on_main(tmp_path):
    clone, _origin = _preflight_fixture(tmp_path)
    assert _git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip() == "1"
    _run_ff_preflight(clone, tmp_path)
    assert _git(clone, "rev-list", "--count", "HEAD..origin/main").stdout.strip() == "0"


def test_preflight_warns_and_continues_when_diverged(tmp_path):
    clone, _origin = _preflight_fixture(tmp_path)
    (clone / "local.txt").write_text("local")
    _git(clone, "add", "local.txt")
    _git(clone, "commit", "-q", "-m", "local divergence")
    res = _run_ff_preflight(clone, tmp_path)
    assert res.returncode == 0, "preflight must never block the run"
    assert "diverged" in res.stderr.lower()
    assert "local divergence" in _git(clone, "log", "-1", "--format=%s").stdout


def test_preflight_skips_when_not_on_main(tmp_path):
    clone, _origin = _preflight_fixture(tmp_path)
    _git(clone, "switch", "-q", "-c", "feature/x")
    head = _git(clone, "rev-parse", "HEAD").stdout.strip()
    res = _run_ff_preflight(clone, tmp_path)
    assert res.returncode == 0
    assert _git(clone, "branch", "--show-current").stdout.strip() == "feature/x"
    assert _git(clone, "rev-parse", "HEAD").stdout.strip() == head, "preflight moved HEAD"


def test_preflight_skips_when_tracked_files_dirty(tmp_path):
    clone, _origin = _preflight_fixture(tmp_path)
    tracked = clone / "seed.txt"
    tracked.write_text("operator work in progress")
    head = _git(clone, "rev-parse", "HEAD").stdout.strip()
    res = _run_ff_preflight(clone, tmp_path)
    assert res.returncode == 0
    assert tracked.read_text() == "operator work in progress", "operator work was clobbered"
    assert _git(clone, "rev-parse", "HEAD").stdout.strip() == head, "preflight merged anyway"


def test_preflight_execs_rather_than_sourcing_after_merge(tmp_path):
    """r1 M3 — a mid-run `git merge --ff-only` can rewrite the script bash is executing.

    Ordering probe: origin/main replaces equality-matrix-cron.sh. If the wrapper merges
    and then `exec`s, the NEW cron script runs. If the preflight lived inside the cron
    script, the OLD (already-open) copy would run instead.
    """
    assert PREFLIGHT_WRAPPER.exists(), f"missing wrapper {PREFLIGHT_WRAPPER}"
    text = PREFLIGHT_WRAPPER.read_text(encoding="utf-8")
    assert "exec " in text, "wrapper must exec the entry point, not source/call it"

    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    ws = _ws_fixture(tmp_path)
    (ws / "scripts" / "readiness" / "equality-matrix-cron.sh").write_text(
        "#!/usr/bin/env bash\necho CRON-OLD\n")
    _git(ws, "add", "-A")
    _git(ws, "commit", "-q", "-m", "old cron")
    _git(ws, "remote", "add", "origin", str(origin))
    _git(ws, "push", "-q", "origin", "main")

    peer = tmp_path / "peer"
    _git(tmp_path, "clone", "-q", str(origin), str(peer))
    (peer / "scripts" / "readiness" / "equality-matrix-cron.sh").write_text(
        "#!/usr/bin/env bash\necho CRON-NEW\n")
    _git(peer, "add", "-A")
    _git(peer, "commit", "-q", "-m", "new cron")
    _git(peer, "push", "-q", "origin", "main")
    _git(ws, "fetch", "-q", "origin", "main")

    res = subprocess.run(["bash", str(ws / "scripts" / "readiness" / "equality-preflight.sh")],
                         env=_env(ws, tmp_path), capture_output=True, text=True, timeout=180)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"
    assert "CRON-NEW" in res.stdout, (
        "the wrapper ran a cron script that the merge had already replaced:\n" + res.stdout)


def test_windows_report_ps1_pins_state_and_report_dirs():
    """Codex r2 M2 — static contract test. PowerShell is unavailable on the Linux/macOS
    test hosts, so Windows coverage here is textual, not behavioural."""
    text = REPORT_PS1.read_text(encoding="utf-8-sig")
    assert "EQ_STATE_DIR" in text and "EQ_REPORT_DIR" in text, (
        "equality-report.ps1 does not pin the seam; both Windows boxes would go dark "
        "on the matrix while every scheduled task reported success")
    state_idx = text.index("$env:EQ_STATE_DIR")
    report_idx = text.index("$env:EQ_REPORT_DIR")
    # the seam must be pinned before the collector and the builder are INVOKED
    # (matching the invocation sites, not the `$collector = …` / `$builder = …` assignments)
    invoke_idx = text.index('"-File", $collector')
    builder_idx = text.index('"python", $builder')
    assert state_idx < invoke_idx and report_idx < invoke_idx, "seam pinned after the collector run"
    assert state_idx < builder_idx and report_idx < builder_idx, "seam pinned after the builder run"
    assert ".claude" in text[state_idx:state_idx + 300], "state seam is not the in-tree path"
    assert "docs" in text[report_idx:report_idx + 300], "report seam is not the in-tree path"


def test_windows_collect_ps1_pins_or_forwards_seam():
    """Codex r2 M1 — collect-equality.ps1:196-206 delegates straight to the bash
    collector, so it must carry the seam or Windows collection silently relocates."""
    text = COLLECT_PS1.read_text(encoding="utf-8-sig")
    assert "EQ_STATE_DIR" in text, "collect-equality.ps1 does not carry the seam"
    seam_idx = text.index("EQ_STATE_DIR")
    delegate_idx = text.index("$bashExe @shArgs")
    assert seam_idx < delegate_idx, "seam set after the delegation to collect-equality.sh"
    assert ".claude" in text[seam_idx:seam_idx + 400], "in-tree default is not pinned"


def test_enforcement_check_flags_in_tree_default(tmp_path):
    assert ENFORCE.exists(), f"missing enforcement script {ENFORCE}"
    regressed = tmp_path / "regressed"
    for rel in ("scripts/readiness/collect-equality.sh",
                "scripts/readiness/build-equality-matrix.py",
                "scripts/readiness/publish-equality.sh",
                "scripts/readiness/lib",
                "scripts/curation/curate-session-memory.sh"):
        src, dst = REPO_ROOT / rel, regressed / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    # the unregressed copy must pass, so the non-zero below is attributable to the regression
    ok = subprocess.run(["bash", str(ENFORCE), "--root", str(regressed)],
                        capture_output=True, text=True, timeout=120)
    assert ok.returncode == 0, f"copy of HEAD failed the check:\n{ok.stdout}\n{ok.stderr}"

    c = regressed / "scripts" / "readiness" / "collect-equality.sh"
    text = c.read_text(encoding="utf-8")
    regressed_text = re.sub(r'^EQ_OUT_DIR=.*$', 'EQ_OUT_DIR="${WS}/.claude/state"',
                            text, count=1, flags=re.M)
    assert regressed_text != text, "no EQ_OUT_DIR assignment found to regress"
    c.write_text(regressed_text)
    res = subprocess.run(["bash", str(ENFORCE), "--root", str(regressed)],
                         capture_output=True, text=True, timeout=120)
    assert res.returncode != 0, "enforcement check passed a deliberately regressed copy"
    assert "collect-equality.sh" in res.stdout + res.stderr


def test_enforcement_check_passes_on_head():
    """The plan files this under REGRESSION, but the script it exercises is CREATED by
    this issue, so it cannot be green on `main`. Classified RED here and reported."""
    assert ENFORCE.exists(), f"missing enforcement script {ENFORCE}"
    res = subprocess.run(["bash", str(ENFORCE)], cwd=str(REPO_ROOT),
                         capture_output=True, text=True, timeout=120)
    assert res.returncode == 0, f"{res.stdout}\n{res.stderr}"


# ══════════════════════════════════════════════════════════════════════════════
# REGRESSION — must pass BEFORE and AFTER (guards, not TDD)
# ══════════════════════════════════════════════════════════════════════════════

MEASURED_BLOCK = """MEASURED=(.claude/skills .claude/memory/context.md .claude/memory/agents.md .codex/skills \\
          .claude/dispatch .claude/rules AGENTS.md \\
          .claude/hooks/plan-approval-gate.sh .claude/settings.json \\
          scripts/readiness/harness-config.yaml scripts/readiness/provider_harness_parity.py \\
          config/agents/claude/SOUL.runtime.md config/agents/codex/AGENTS.runtime.md \\
          config/agents/codex/MEMORY.runtime.md config/agents/hermes/SOUL.runtime.md \\
          config/scheduled-tasks/schedule-tasks.yaml)"""


def test_measured_allowlist_unchanged():
    # The `dirty` provenance scoping must stay byte-identical — widening it would
    # false-STALE healthy machines; narrowing it would hide real drift.
    assert MEASURED_BLOCK in COLLECT.read_text(encoding="utf-8")


def test_is_stale_semantics_unchanged():
    text = BUILDER.read_text(encoding="utf-8")
    for line in ('if p.get("dirty") is not False:',
                 'if p.get("behind_main") not in (0, "0"):',
                 'if p.get("ahead_main") not in (0, "0"):'):
        assert line in text, f"is_stale() drifted: {line!r} missing"


def test_collect_still_reads_sidecar_state_from_the_tracked_tree(tmp_path):
    # The seam relocates the collector's OUTPUT only. Its sidecar INPUTS
    # (harness-readiness / session-curation / skill-currency / memory-freshness /
    # skill-link-health) are tracked repo state and must keep resolving in-tree, or
    # five matrix dimensions go MISSING-EVIDENCE on every box.
    ws = _ws_fixture(tmp_path)
    res = _run_collect(ws, tmp_path, "--stdout")
    doc = yaml.safe_load(res.stdout)
    assert doc["dimensions"]["harness"]["readiness_overall"] == "fail"


def test_collect_commit_on_change_still_suppresses_rewrite(tmp_path):
    # Location-agnostic: the destination is read back out of the collector's own
    # "wrote <path>" line, so this guard is meaningful before AND after the relocation.
    ws = _ws_fixture(tmp_path)
    first_run = _run_collect(ws, tmp_path)
    m = re.search(r"wrote (\S+)", first_run.stdout)
    assert m, first_run.stdout
    out = Path(m.group(1))
    first_mtime = out.stat().st_mtime_ns
    second = _run_collect(ws, tmp_path)
    assert "unchanged" in second.stdout, second.stdout
    assert out.stat().st_mtime_ns == first_mtime


def test_build_matrix_json_mode_writes_nothing(tmp_path):
    ws = _ws_fixture(tmp_path)
    before = _snapshot(ws)
    _run_builder(ws, tmp_path, "--json")
    assert _snapshot(ws) == before
    assert not list((ws / "docs" / "reports").glob("*machine-equality-matrix.html"))


def test_build_matrix_reads_repo_peer_evidence_readonly(tmp_path):
    # --json writes nothing on either side of the change, so this is a true both-ways guard.
    ws = _ws_fixture(tmp_path)
    peer = ws / ".claude" / "state" / "equality-peer-box.yaml"
    before = peer.read_text()
    verdicts = json.loads(_run_builder(ws, tmp_path, "--json").stdout)
    assert peer.read_text() == before, "peer evidence in the tracked tree was mutated"
    assert verdicts["peer-box"]["compute"] == "STALE-CHECKOUT", (
        "repo peer evidence was not read in default mode")


# ── publisher / preflight fixture helpers (defined after use, module scope) ───
def _publish_fixture(tmp_path: Path) -> tuple[Path, Path]:
    origin = tmp_path / "porigin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "pseed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    (seed / ".claude" / "state").mkdir(parents=True)
    (seed / "docs" / "reports").mkdir(parents=True)
    (seed / "scripts" / "readiness").mkdir(parents=True)
    (seed / ".claude" / "state" / "equality-dev-primary.yaml").write_text(
        'generated_at: "2026-06-01T00:00:00"\nmachine: "dev-primary"\n')
    (seed / "docs" / "reports" / ".gitkeep").write_text("")
    (seed / "scripts" / "readiness" / ".gitkeep").write_text("")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "seed")
    _git(seed, "push", "-q", "origin", "main")
    clone = tmp_path / "pclone"
    _git(tmp_path, "clone", "-q", str(origin), str(clone))
    return origin, clone


def _run_publish(clone: Path, tmp_path: Path, *args: str, expect_rc: int = 0,
                 **envx: str) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(_home(tmp_path)),
        "TMPDIR": str(tmp_path),
        "EQ_MACHINE": "dev-primary",
        **GIT_ENV, **envx,
    }
    res = subprocess.run(["bash", str(PUBLISH), "--repo", str(clone), *args],
                         env=env, capture_output=True, text=True, timeout=180)
    assert res.returncode == expect_rc, f"rc={res.returncode}\n{res.stdout}\n{res.stderr}"
    return res


def _origin_file(origin: Path, path: str) -> str:
    res = subprocess.run(["git", "show", f"main:{path}"], cwd=origin,
                         env={**os.environ, **GIT_ENV}, capture_output=True, text=True,
                         timeout=60)
    return res.stdout if res.returncode == 0 else ""


def _preflight_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Clone sitting one FF-able commit behind origin/main, tree clean, on main."""
    origin = tmp_path / "fforigin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "ffseed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    (seed / "seed.txt").write_text("seed")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "seed")
    _git(seed, "push", "-q", "origin", "main")
    clone = tmp_path / "ffclone"
    _git(tmp_path, "clone", "-q", str(origin), str(clone))
    (seed / "advance.txt").write_text("advance")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "advance")
    _git(seed, "push", "-q", "origin", "main")
    _git(clone, "fetch", "-q", "origin", "main")
    return clone, origin


def _run_ff_preflight(clone: Path, tmp_path: Path) -> subprocess.CompletedProcess:
    assert PREFLIGHT_LIB.exists(), f"missing {PREFLIGHT_LIB}"
    driver = f'. "{PREFLIGHT_LIB}"\nff_preflight "{clone}"\n'
    return subprocess.run(
        ["bash", "-c", driver],
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(_home(tmp_path)),
             **GIT_ENV},
        capture_output=True, text=True, timeout=180)
