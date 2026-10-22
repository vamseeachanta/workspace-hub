"""Isolated reconciliation tests; no upgrades or real scheduler calls.

Independent truth table: a successful child returns zero; an exit seven is
propagated; timeout returns 124 (GNU Coreutils, timeout invocation, Exit status,
https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html).
The seven is an arbitrary synthetic failure input, not an acceptance limit.
"""
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/cron/harness-update.sh"


@pytest.mark.parametrize("mode,child_status,timeout_status,expected", [
    ("false", 0, 0, 0),
    ("false", 7, 0, 7),
    ("false", 0, 124, 124),
    ("true", 0, 0, 0),
    ("true", 7, 0, 7),
])
def test_reconciler_result(tmp_path, mode, child_status, timeout_status, expected):
    """Five enumerated cases cover success, failure, timeout and dry-run status."""
    installer = tmp_path / "scripts/cron/setup-cron.sh"
    installer.parent.mkdir(parents=True)
    installer.write_text(f'printf "%s\\n" "$*" > "$TRACE"\nexit {child_status}\n')
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    timeout = fake_bin / "timeout"
    timeout.write_text(
        '#!/bin/bash\nprintf "%s\\n" "$1" > "$BUDGET_TRACE"\n'
        f'if [ "{timeout_status}" != 0 ]; then exit {timeout_status}; fi\n'
        'shift\nexec "$@"\n'
    )
    timeout.chmod(0o755)
    source = SCRIPT.read_text()
    function = re.search(r"^sync_crontab\(\) \{.*?^\}", source, re.MULTILINE | re.DOTALL).group()
    driver = tmp_path / "driver.sh"
    driver.write_text(
        'set -uo pipefail\nlog() { printf "%s\\n" "$*"; }\n'
        'record() { :; }\n' + function + '\nsync_crontab\n'
    )
    env = {**os.environ, "WORKSPACE_HUB": str(tmp_path), "DRY_RUN": mode,
           "PATH": str(fake_bin) + os.pathsep + os.environ["PATH"],
           "TRACE": str(tmp_path / "trace"), "CRON_RECONCILE_TIMEOUT": "9s",
           "BUDGET_TRACE": str(tmp_path / "budget")}
    result = subprocess.run(["bash", str(driver)], env=env, text=True, capture_output=True, check=False)
    assert result.returncode == expected
    assert f"cron_reconcile_status={expected}" in result.stdout
    assert (tmp_path / "budget").read_text().strip() == "9s"
    if timeout_status == 0:
        assert (tmp_path / "trace").read_text().strip() == ("--dry-run" if mode == "true" else "")
    # The reconciliation status must survive summary and notification commands.
    assert 'sync_crontab || cron_status=$?' in source
    assert source.rstrip().endswith('exit "$cron_status"')


def test_direct_installer_gate_is_unchanged():
    """The transitive caller retains the sole direct installer's authority check."""
    source = (ROOT / "scripts/cron/setup-cron.sh").read_text()
    assert '"$CANONICAL_MACHINE" != "$PHYSICAL_MACHINE"' in source
    assert 'APPLY_ARGS+=(--apply)' in source
