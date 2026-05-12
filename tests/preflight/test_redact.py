from __future__ import annotations

from scripts.preflight.redact import redact_text, strip_url_secret


def test_redacts_github_tokens_jwts_and_generic_api_keys() -> None:
    raw = (
        "Token: gho_abcdefghijklmnopqrstuvwxyz123456 "
        "jwt eyJabcDEF12345.eyJabcDEF12345.signatureXYZ12345 "
        "key sk-abcdefghijklmnopqrstuvwxyz123456"
    )

    redacted = redact_text(raw)

    assert "gho_" not in redacted
    assert "eyJabc" not in redacted
    assert "sk-" not in redacted
    assert "[REDACTED:gh-token]" in redacted


def test_strips_query_string_from_provider_base_url() -> None:
    assert (
        strip_url_secret("https://example.invalid/v1?token=secret&x=1")
        == "https://example.invalid/v1"
    )
