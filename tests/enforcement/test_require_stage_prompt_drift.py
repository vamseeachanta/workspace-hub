from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "require-stage-prompt-drift.sh"


def run_script(env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def read_log(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def test_missing_base_ref_skips_cleanly(tmp_path: Path) -> None:
    log_file = tmp_path / "drift-log.jsonl"
    result = run_script(
        {
            "STAGE_PROMPT_DRIFT_BASE_REF": "refs/heads/definitely-missing-ref",
            "STAGE_PROMPT_DRIFT_SCRIPT": "/bin/false",
            "STAGE_PROMPT_DRIFT_LOG": str(log_file),
        }
    )

    assert result.returncode == 0
    assert "base ref not found" in result.stderr.lower()
    assert '"verdict":"skip"' in read_log(log_file)


def test_strict_mode_blocks_on_detected_drift(tmp_path: Path) -> None:
    fake = REPO_ROOT / ".tmp-stage-prompt-drift-fail.py"
    log_file = tmp_path / "drift-log.jsonl"
    fake.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "Path(sys.argv[sys.argv.index('--output-md') + 1]).write_text('# Stage prompt drift check\\n- WRK-9\\n', encoding='utf-8')\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    try:
        result = run_script(
            {
                "STAGE_PROMPT_DRIFT_BASE_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_HEAD_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_SCRIPT": str(fake),
                "STAGE_PROMPT_DRIFT_STRICT": "1",
                "STAGE_PROMPT_DRIFT_LOG": str(log_file),
            }
        )
    finally:
        fake.unlink(missing_ok=True)

    assert result.returncode == 1
    assert "fail" in result.stderr.lower()
    assert "Remediation:" in result.stderr
    assert '"verdict":"fail"' in read_log(log_file)


def test_advisory_mode_warns_but_allows_push(tmp_path: Path) -> None:
    fake = REPO_ROOT / ".tmp-stage-prompt-drift-fail.py"
    log_file = tmp_path / "drift-log.jsonl"
    fake.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "Path(sys.argv[sys.argv.index('--output-md') + 1]).write_text('# Stage prompt drift check\\n- WRK-9\\n', encoding='utf-8')\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    try:
        result = run_script(
            {
                "STAGE_PROMPT_DRIFT_BASE_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_HEAD_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_SCRIPT": str(fake),
                "STAGE_PROMPT_DRIFT_STRICT": "0",
                "STAGE_PROMPT_DRIFT_LOG": str(log_file),
            }
        )
    finally:
        fake.unlink(missing_ok=True)

    assert result.returncode == 0
    assert "warning" in result.stderr.lower()
    assert "Remediation:" in result.stderr
    assert '"verdict":"warning"' in read_log(log_file)


def test_script_enables_stub_generation_by_default(tmp_path: Path) -> None:
    fake = REPO_ROOT / ".tmp-stage-prompt-drift-args.py"
    log_file = tmp_path / "drift-log.jsonl"
    args_file = tmp_path / "argv.txt"
    fake.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        f"Path({str(args_file)!r}).write_text(' '.join(sys.argv[1:]), encoding='utf-8')\n"
        "Path(sys.argv[sys.argv.index('--output-md') + 1]).write_text('# Stage prompt drift check\\n', encoding='utf-8')\n"
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    try:
        result = run_script(
            {
                "STAGE_PROMPT_DRIFT_BASE_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_HEAD_REF": "HEAD",
                "STAGE_PROMPT_DRIFT_SCRIPT": str(fake),
                "STAGE_PROMPT_DRIFT_LOG": str(log_file),
            }
        )
    finally:
        fake.unlink(missing_ok=True)

    assert result.returncode == 0
    assert "--write-evidence-stubs" in args_file.read_text(encoding="utf-8")
