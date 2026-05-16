"""TDD tests for #2720 Telegram/Hermes status redaction."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "telegram_dispatch" / "redaction.py"
spec = importlib.util.spec_from_file_location("telegram_dispatch_redaction", MODULE_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["telegram_dispatch_redaction"] = module
spec.loader.exec_module(module)


def test_status_redacts_tokens_and_env_values() -> None:
    fake_telegram_credential = "".join(["123456789", ":", "ABCDEF", "ghijkl", "MNOPQR", "stuvwx"])
    fake_gateway_credential = "".join(["ghp_", "ABCDEF", "ghijkl", "MNOPQR", "stuvwx", "3456"])
    fake_anthropic_credential = "".join(["sk-ant", "-", "ABCDEF", "ghijkl", "MNOPQR", "stuvwx", "7890"])
    payload = {
        "host_id": "dev-primary",
        "telegram_token": fake_telegram_credential,
        "env": {
            "HERMES_GATEWAY_TOKEN": fake_gateway_credential,
            "ANTHROPIC_API_KEY": fake_anthropic_credential,
            "SAFE_FLAG": "enabled",
        },
        "message": f"credential={fake_telegram_credential} path=/mnt/local-analysis/workspace-hub",
    }

    redacted = module.redact_status(payload)
    rendered = module.render_status(redacted)

    assert fake_telegram_credential not in rendered
    assert fake_gateway_credential not in rendered
    assert fake_anthropic_credential not in rendered

    assert "ghp_" not in rendered
    assert "sk-ant" not in rendered
    assert "[REDACTED]" in rendered
    assert "dev-primary" in rendered
    assert "enabled" in rendered


def test_expired_or_invalid_bot_token_does_not_leak() -> None:
    credential = "".join(["987654321", ":", "ZYXWV"])

    message = module.format_token_validation_failure(credential, reason="expired")

    assert credential not in message

    assert "ZYXWV" not in message
    assert "expired" in message
    assert "[REDACTED]" in message
