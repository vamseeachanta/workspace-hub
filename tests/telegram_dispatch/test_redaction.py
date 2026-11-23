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


def test_token_validation_failure_redacts_token_material_in_reason() -> None:
    credential = "".join(["123456789", ":", "ABCDEFGHIJKLMNOPQRSTUVWXYZ12"])

    message = module.format_token_validation_failure(
        credential,
        reason=f"invalid token {credential}",
    )

    assert credential not in message
    assert "ABCDEFGHIJKLMNOPQRSTUVWXYZ12" not in message
    assert "invalid token [REDACTED]" in message


def test_short_invalid_token_echo_in_reason_is_redacted() -> None:
    credential = "".join(["987654321", ":", "ZYXWV"])

    message = module.format_token_validation_failure(
        credential,
        reason=f"invalid token {credential}",
    )

    assert credential not in message
    assert "ZYXWV" not in message
    assert "invalid token [REDACTED]" in message


def test_token_validation_failure_redacts_partial_token_fragments_in_reason() -> None:
    credential = "".join(["987654321", ":", "ZYXWV"])

    message = module.format_token_validation_failure(
        credential,
        reason="invalid bot 987654321 suffix ZYXWV",
    )

    assert "987654321" not in message
    assert "ZYXWV" not in message
    assert "invalid bot [REDACTED] suffix [REDACTED]" in message


def test_token_validation_failure_redacts_long_secret_chunks_in_reason() -> None:
    credential = "".join(["123456789", ":", "ABCDEFGHIJKLMNOPQRSTUVWXYZ12"])

    message = module.format_token_validation_failure(
        credential,
        reason="invalid token fragment ABCD or QRST",
    )

    assert "ABCD" not in message
    assert "QRST" not in message


def test_telegram_identifier_fields_are_redacted_from_status() -> None:
    payload = {
        "allowed_user_ids": "12345,67890",
        "chat_id": "-1009876543210",
        "invite_link": "https://t.me/+abcdefghijklmnop",
        "phone_number": "+155****4567",
        "safe_status": "ready",
    }

    rendered = module.render_status(payload)

    assert "12345" not in rendered
    assert "67890" not in rendered
    assert "-1009876543210" not in rendered
    assert "t.me/+" not in rendered
    assert "+155****4567" not in rendered
    assert "ready" in rendered


def test_telegram_identifier_values_are_redacted_from_freeform_strings() -> None:
    payload = {
        "message": (
            "chat_id=-1009876543210 allowlist=12345,67890 allowed_user_ids=24680,13579 "
            "invite=https://t.me/+abcdefghijklmnop phone=+155****4567"
        ),
        "safe_status": "ready",
    }

    rendered = module.render_status(payload)

    assert "-1009876543210" not in rendered
    assert "12345" not in rendered
    assert "67890" not in rendered
    assert "24680" not in rendered
    assert "13579" not in rendered
    assert "t.me/+" not in rendered
    assert "+155****4567" not in rendered
    assert "ready" in rendered


def test_redaction_preserves_safe_long_slugs() -> None:
    payload = {
        "evidence_type": "telegram-hermes-host-local-readiness",
        "producer": "scripts/readiness/telegram_hermes_readiness.py",
    }

    rendered = module.render_status(payload)

    assert "telegram-hermes-host-local-readiness" in rendered
    assert "scripts/readiness/telegram_hermes_readiness.py" in rendered


def test_token_fragment_redaction_does_not_corrupt_common_words_or_marker() -> None:
    credential = "".join(["123456789", ":", "failACTEhostABCDEFGH"])

    message = module.format_token_validation_failure(
        credential,
        reason="failed host validation ACTE ABCD",
    )

    assert "ABCDEFGH" not in message
    assert "ABCD" not in message
    assert "failed host validation ACTE [REDACTED]" in message


def test_render_status_redacts_contextual_token_fragments() -> None:
    payload = {
        "status": "fail",
        "failures": [
            "remote evidence leaked bot token tail ZYXWV",
            "remote evidence leaked token fragment ABCD",
        ],
    }

    rendered = module.render_status(payload)

    assert "ZYXWV" not in rendered
    assert "ABCD" not in rendered
    assert "bot token tail [REDACTED]" in rendered
    assert "token fragment [REDACTED]" in rendered


def test_render_status_redacts_untrusted_remote_fragment_values() -> None:
    payload = {
        "status": "fail",
        "failures": ["remote evidence leaked fragment ZYXWV"],
        "warnings": ["remote evidence leaked fragment ABCD"],
        "missing_data": ["remote evidence leaked fragment LMNO"],
    }

    rendered = module.render_status(payload)

    assert "ZYXWV" not in rendered
    assert "ABCD" not in rendered
    assert "LMNO" not in rendered
    assert "fragment [REDACTED]" in rendered
