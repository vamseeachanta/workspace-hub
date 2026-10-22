"""Solver discovery truth tables with controlled imports and install roots."""

from __future__ import annotations

import subprocess
from pathlib import Path

from collector_support import PROBE_LIB, collector_env
from collector_support import bash_path as _bash_path

# ── probe-solvers.sh unit semantics (#2849 / PR #2850 decision 2026-05-28) ──────
# present ≠ licensed: install/import/env presence classifies as `present`; `licensed`
# requires a real license signal (none available locally → never emitted here).


def _probe(fn: str, env_extra: dict | None = None, fake_import_ok: bool = False,
           tmp_path: Path | None = None) -> str:
    """Source probe-solvers.sh and echo the result of one probe function.

    fake_import_ok=True shims a `python` on PATH whose `import OrcFxAPI` succeeds,
    so the OrcFxAPI SDK-present path is exercised without the real SDK installed.
    """
    assert tmp_path is not None
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "TEST_ROOT": str(tmp_path)}
    path_prefix = ""
    if fake_import_ok:
        assert tmp_path is not None
        binp = tmp_path / "bin"
        binp.mkdir(exist_ok=True)
        py = binp / "python"
        py.write_text("#!/usr/bin/env bash\nexit 0\n")  # any args → success (import ok)
        py.chmod(0o755)
        path_prefix = f"{_bash_path(binp)}:"
    env["PATH"] = path_prefix + env["PATH"]
    if env_extra:
        env.update(env_extra)
    res = subprocess.run(
        ["bash", "-c", f'source "{_bash_path(PROBE_LIB)}"; {fn}'],
        env=collector_env(env), capture_output=True, text=True, timeout=30, check=False)
    assert res.returncode == 0, res.stderr
    return res.stdout.strip()


def test_probe_orcaflex_import_ok_is_present_not_licensed(tmp_path):
    # `import OrcFxAPI` success → present (NOT licensed). Load-bearing decision.
    assert _probe("probe_orcaflex", fake_import_ok=True, tmp_path=tmp_path) == "present"
    assert _probe("probe_orcaflex_evidence", fake_import_ok=True, tmp_path=tmp_path) == "import"


def test_probe_orcawave_import_ok_is_present_not_licensed(tmp_path):
    assert _probe("probe_orcawave", fake_import_ok=True, tmp_path=tmp_path) == "present"


def test_probe_orcawave_env_only_is_present(tmp_path):
    owp = tmp_path / "ow"; owp.mkdir()
    assert _probe("probe_orcawave", env_extra={"ORCAWAVE_PATH": str(owp)}, tmp_path=tmp_path) == "present"


def test_probe_ansys_license_env_does_not_upgrade_to_licensed(tmp_path):
    # A license-server env var is recorded as evidence but never upgrades status to licensed.
    # No ANSYS root on the test host → absent regardless of env (real signal still needed).
    assert _probe("probe_ansys",
                  env_extra={"ANSYSLI_SERVERS": "1055@licsrv"}, tmp_path=tmp_path) == "absent"


def test_probe_never_emits_licensed_locally(tmp_path):
    # No real license probe exists locally → no probe emits `licensed` on this host.
    for fn in ("probe_orcaflex", "probe_orcawave", "probe_aqwa", "probe_ansys"):
        assert _probe(fn, fake_import_ok=True, tmp_path=tmp_path) != "licensed"


