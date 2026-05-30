"""Linux-runnable CONTRACT tests for the #2816 Windows collector (collect-equality.ps1).

PowerShell cannot run on Linux CI, so these tests pin the *contract* the .ps1 must satisfy,
two ways:

1. A committed golden fixture (tests/readiness/fixtures/equality-licensed-win-1.sample.yaml) —
   the exact YAML collect-equality.sh emits when the .ps1 exports its CIM-derived EQ_* compute.
   We parse it through the SAME consumers the matrix uses (is_stale, cold_verdict, coerce_to_mib)
   and assert it grades CONFORMS / not-stale, so a schema drift in the .ps1 output is caught.

2. The EQ_* override seam in collect-equality.sh itself (the .ps1's delegation target). We run
   the .sh on Linux with EQ_OS_OVERRIDE=windows and exercise the W5 validation: bad EQ_* values
   (empty / non-numeric / negative / newline / unit-suffixed) must fall back to "unknown"; a clean
   integer set must flow through.

The .ps1's own PowerShell logic (CIM queries, freshness preflight) is owner-machine-verified per
the plan's owner runbook — it cannot be exercised here.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SH = REPO_ROOT / "scripts" / "readiness" / "collect-equality.sh"
PS1 = REPO_ROOT / "scripts" / "readiness" / "collect-equality.ps1"
FIXTURE = REPO_ROOT / "tests" / "readiness" / "fixtures" / "equality-licensed-win-1.sample.yaml"
CONFIG = REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml"
BASH_PATH = "/mingw64/bin:/usr/bin:/bin:/usr/local/bin"


# ── import the matrix builder as a module (it has no import-time side effects) ──
def _load_matrix():
    path = REPO_ROOT / "scripts" / "readiness" / "build-equality-matrix.py"
    spec = importlib.util.spec_from_file_location("build_equality_matrix", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MATRIX = _load_matrix()


def _fixture() -> dict:
    return yaml.safe_load(FIXTURE.read_text())


def _win1_baseline() -> dict:
    config = yaml.safe_load(CONFIG.read_text())
    return config["workstations"]["licensed-win-1"]


# ════════════════════════════════════════════════════════════════════════════
# 1. Golden fixture parses to schema_version 3 with provenance + all 9 dims
# ════════════════════════════════════════════════════════════════════════════
EXPECTED_DIMS = {"compute", "data_access", "solvers", "harness", "skills",
                 "kanban", "memory", "behavior", "scheduler"}


def test_ps1_sample_output_parses_schema_v3():
    d = _fixture()
    assert d["schema_version"] == 3
    assert d["os"] == "windows"
    assert d["machine"] == "licensed-win-1"
    # provenance block present with the freshness fields is_stale() consumes
    p = d["provenance"]
    assert set(p) >= {"checkout_sha", "dirty", "behind_main", "ahead_main", "origin_ref_age_h"}
    # all 9 dimensions present
    assert set(d["dimensions"]) == EXPECTED_DIMS


# ════════════════════════════════════════════════════════════════════════════
# 2. cold_verdict CONFORMS for compute given the fixture + the real baseline
# ════════════════════════════════════════════════════════════════════════════
def test_ps1_sample_grades_conforms_compute():
    d = _fixture()
    baseline = _win1_baseline()
    probed = ["assetutilities", "digitalmodel", "worldenergydata", "assethold"]
    verdict = MATRIX.cold_verdict("compute", d, baseline, probed)
    assert verdict == "CONFORMS", (
        f"expected CONFORMS, got {verdict} (cores={d['dimensions']['compute']['static']['cores']}, "
        f"ram_total_mib={d['dimensions']['compute']['static']['ram_total_mib']}, floor={baseline.get('compute_floor')})")


# ════════════════════════════════════════════════════════════════════════════
# 3. is_stale()==False for the fresh fixture
# ════════════════════════════════════════════════════════════════════════════
def test_ps1_sample_not_stale():
    assert MATRIX.is_stale(_fixture()) is False


# ════════════════════════════════════════════════════════════════════════════
# 4. ram_total_mib is a bare MiB integer coerce_to_mib accepts, ≥ floor*1024
# ════════════════════════════════════════════════════════════════════════════
def test_ps1_ram_total_mib_is_mib_integer():
    d = _fixture()
    raw = d["dimensions"]["compute"]["static"]["ram_total_mib"]
    # bare integer (no units / commas) — the contract the .ps1 must emit
    assert isinstance(raw, int)
    mib = MATRIX.coerce_to_mib(raw)
    assert mib == raw
    # ≥ ram_gib_min*1024 when the floor is set (W4 follow-up); if absent, anticipate the
    # dev-tier floor (8 GiB) so the fixture is provably above any plausible restored value.
    floor_gib = _win1_baseline().get("compute_floor", {}).get("ram_gib_min", 8)
    assert mib >= int(floor_gib) * 1024


def test_harness_config_winram_floor_present():
    config = yaml.safe_load(CONFIG.read_text())
    for machine in ("licensed-win-1", "licensed-win-2"):
        floor = config["workstations"][machine]["compute_floor"]
        assert floor["cores_min"] == 8
        assert floor["ram_gib_min"] == 15


# ════════════════════════════════════════════════════════════════════════════
# 5. field-key parity: fixture key-tree == collect-equality.sh --stdout key-tree
# ════════════════════════════════════════════════════════════════════════════
def _key_tree(node):
    """Recursive set of dotted key paths (structure only, values ignored). Lists are
    summarized by their elements' merged key-trees, so order/length differences in the
    repo/solver lists don't break parity."""
    out = set()
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(k)
            for sub in _key_tree(v):
                out.add(f"{k}.{sub}")
    elif isinstance(node, list):
        for item in node:
            out |= _key_tree(item)
    return out


def _sh_stdout(env_extra: dict, tmp_path: Path, machine: str = "licensed-win-1") -> dict:
    """Run collect-equality.sh --stdout against a minimal non-git WORKSPACE_HUB."""
    ws = tmp_path / "workspace-hub"
    (ws / ".claude" / "state").mkdir(parents=True)
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    env = {"WORKSPACE_HUB": str(ws), "PATH": BASH_PATH, "HOME": str(tmp_path)}
    # The OS-override seam is double-gated: it only applies when the explicit test-enable flag is
    # set (so ambient production env can't spoof the OS). Tests that force the windows branch via
    # EQ_OS_OVERRIDE must also set EQ_TEST_ENABLE_OS_OVERRIDE=1.
    if "EQ_OS_OVERRIDE" in env_extra:
        env["EQ_TEST_ENABLE_OS_OVERRIDE"] = "1"
    env.update(env_extra)
    res = subprocess.run(
        ["bash", str(SH), "--stdout", "--machine", machine],
        env=env, capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    return yaml.safe_load(res.stdout)


def test_ps1_field_parity_with_sh_stdout(tmp_path):
    # The .ps1's delegation target IS collect-equality.sh, so its emission must carry the same
    # field keys as the live .sh --stdout (minus OS-dependent values). Drive the .sh through the
    # windows EQ_* seam so the compute fields are populated exactly as the .ps1 would populate them.
    sh = _sh_stdout(
        {"EQ_OS_OVERRIDE": "windows", "EQ_CORES": "16", "EQ_RAM_TOTAL_MIB": "65277",
         "EQ_RAM_AVAIL_MIB": "41203", "EQ_DISK_AVAIL_GB": "742",
         "EQ_GPU_MODEL": "NVIDIA RTX A2000 12GB"},
        tmp_path)
    fixture_keys = _key_tree(_fixture())
    sh_keys = _key_tree(sh)
    # The fixture must not invent keys the live collector doesn't emit, and must not be missing
    # any the collector emits. (generated_at is emitted by both.)
    assert fixture_keys == sh_keys, (
        f"only-in-fixture: {sorted(fixture_keys - sh_keys)} | only-in-sh: {sorted(sh_keys - fixture_keys)}")


# ════════════════════════════════════════════════════════════════════════════
# 6. W5 EQ_* validation: bad values fall back to "unknown"; good values flow
# ════════════════════════════════════════════════════════════════════════════
def _compute(sh: dict) -> tuple[dict, dict]:
    c = sh["dimensions"]["compute"]
    return c["static"], c["headroom"]


def test_sh_eq_overrides_good_values_flow(tmp_path):
    sh = _sh_stdout(
        {"EQ_OS_OVERRIDE": "windows", "EQ_CORES": "32", "EQ_RAM_TOTAL_MIB": "131072",
         "EQ_RAM_AVAIL_MIB": "90000", "EQ_DISK_AVAIL_GB": "1024",
         "EQ_GPU_MODEL": "NVIDIA RTX 4090"},
        tmp_path)
    static, headroom = _compute(sh)
    assert static["cores"] == 32
    assert static["ram_total_mib"] == 131072
    assert static["gpu_model"] == "NVIDIA RTX 4090"
    assert headroom["ram_avail_mib"] == 90000
    assert headroom["disk_avail_gb"] == 1024


def test_sh_eq_overrides_bad_values_fallback_unknown(tmp_path):
    # W5: empty, non-numeric, negative, unit-suffixed → "unknown" (clean fallback, never 0/garbage).
    sh = _sh_stdout(
        {"EQ_OS_OVERRIDE": "windows", "EQ_CORES": "", "EQ_RAM_TOTAL_MIB": "abc",
         "EQ_RAM_AVAIL_MIB": "-5", "EQ_DISK_AVAIL_GB": "16GB", "EQ_GPU_MODEL": ""},
        tmp_path)
    static, headroom = _compute(sh)
    assert static["cores"] == "unknown"
    assert static["ram_total_mib"] == "unknown"
    assert headroom["ram_avail_mib"] == "unknown"
    assert headroom["disk_avail_gb"] == "unknown"
    # empty gpu → "none" (the existing default), not an empty scalar
    assert static["gpu_model"] == "none"


def test_sh_eq_override_newline_fallback_unknown(tmp_path):
    # A trailing newline (e.g. "12\n" from a stray CIM line) must NOT be accepted as 12.
    sh = _sh_stdout(
        {"EQ_OS_OVERRIDE": "windows", "EQ_CORES": "12\n"},
        tmp_path)
    static, _ = _compute(sh)
    assert static["cores"] == "unknown"


def test_sh_eq_bad_compute_grades_missing_evidence(tmp_path):
    # Defense-in-depth: a garbled EQ_* set must grade MISSING-EVIDENCE (fail-closed), never a
    # false CONFORMS/BELOW-BASELINE off a bogus 0. Proves the "unknown" fallback reaches the matrix.
    sh = _sh_stdout(
        {"EQ_OS_OVERRIDE": "windows", "EQ_CORES": "abc", "EQ_RAM_TOTAL_MIB": "abc"},
        tmp_path)
    verdict = MATRIX.cold_verdict("compute", sh, _win1_baseline(),
                                  ["assetutilities", "digitalmodel", "worldenergydata", "assethold"])
    assert verdict == "MISSING-EVIDENCE"


# ════════════════════════════════════════════════════════════════════════════
# 7. The .ps1 companion exists and documents the W1/W3 owner-side contract
# ════════════════════════════════════════════════════════════════════════════
def test_ps1_collector_exists():
    assert PS1.exists(), f"missing {PS1}"


def test_ps1_documents_w1_commit_is_wrappers_job():
    # W1: the collector must NOT commit/push; that is equality-report.ps1's job (#2815).
    text = PS1.read_text()
    assert "#2815" in text or "equality-report.ps1" in text
    # W3: a freshness preflight that fails fast without writing a STALE report.
    assert "fetch" in text.lower()
    assert "Resolve-EqualityMachineLabel" in text
    assert "Unknown Windows equality collector host" in text


def test_eq_os_override_ignored_without_test_flag(tmp_path):
    # SECURITY (Codex code-review MAJOR): EQ_OS_OVERRIDE must NOT spoof the OS in production. It
    # only applies behind the explicit EQ_TEST_ENABLE_OS_OVERRIDE=1 flag. Without the flag the
    # override is ignored, so the collector reports the REAL OS instead of the injected value.
    ws = tmp_path / "workspace-hub"
    (ws / ".claude" / "state").mkdir(parents=True)
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    env = {"WORKSPACE_HUB": str(ws), "PATH": BASH_PATH, "HOME": str(tmp_path),
           "EQ_OS_OVERRIDE": "unknown"}  # deliberately NO test-enable flag
    res = subprocess.run(["bash", str(SH), "--stdout", "--machine", "licensed-win-1"],
                         env=env, capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    d = yaml.safe_load(res.stdout)
    assert d["os"] != "unknown"                                      # real OS, override ignored
