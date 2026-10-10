"""Static regression checks for agent-preflight receipt redaction."""
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "windows" / "agent-preflight.ps1"


def test_serialized_receipt_uses_json_specific_secret_redaction():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "[switch]$SerializedJson" in text
    assert "Hide-Secrets -Text ($receipt | ConvertTo-Json -Depth 6) -SerializedJson" in text
