import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "scripts" / "email" / "fixture-redaction-check.py"


def run_hook(path: Path):
    return subprocess.run(
        [sys.executable, str(HOOK), str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_fixture_redaction_rejects_real_domains(tmp_path):
    fixture = tmp_path / "bad.yaml"
    fixture.write_text(
        "sender: person@aceengineer.com\nphone: 713-555-0181\n",
        encoding="utf-8",
    )

    result = run_hook(fixture)

    assert result.returncode == 1
    assert "real email/domain" in result.stderr


def test_fixture_redaction_allows_placeholder_domains(tmp_path):
    fixture = tmp_path / "good.yaml"
    fixture.write_text(
        "sender: client@example.com\nreply_to: broker@test.invalid\n",
        encoding="utf-8",
    )

    result = run_hook(fixture)

    assert result.returncode == 0, result.stderr
