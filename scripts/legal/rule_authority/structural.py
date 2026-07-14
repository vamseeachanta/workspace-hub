"""Closed-encoding detection for structurally private authority artifacts."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import PurePosixPath

PRIVATE_MARKERS = (
    b"legal-rule-map-v1",
    b"legal-rule-authority-manifest-v1",
    b"legal-rule-active-anchor-v1",
    b"legal-rule-generation-ledger-v1",
    b"legal-rule-complete-v1",
    b"PACK\x00\x00\x00\x02",
    b"\xfftOc",
)
PUBLIC_MARKERS = {
    b"legal-rule-registry-v1": "config/legal-rule-registry.json",
    b"legal-rule-policy-v1": "config/legal-rule-authority-policy.json",
}


@dataclass(frozen=True)
class SensitiveArtifacts:
    """Private bytes known to the current authenticated authority."""

    key: bytes
    decoded_patterns: tuple[bytes, ...]
    exact_artifacts: tuple[bytes, ...]
    prohibited_basenames: frozenset[str]


def _sensitive_encodings(sensitive: SensitiveArtifacts) -> tuple[bytes, ...]:
    encoded = [sensitive.key, base64.b64encode(sensitive.key)]
    for pattern in sensitive.decoded_patterns:
        encoded.append(base64.b64encode(pattern))
    encoded.extend(sensitive.exact_artifacts)
    return tuple(value for value in encoded if value)


def _has_private_bytes(payload: bytes, sensitive: SensitiveArtifacts) -> bool:
    candidates = (*PRIVATE_MARKERS, *_sensitive_encodings(sensitive))
    return any(candidate in payload for candidate in candidates)


def _misplaced_public_marker(path: str, payload: bytes) -> bool:
    for marker, canonical_path in PUBLIC_MARKERS.items():
        if marker in payload and path != canonical_path:
            return True
    return False


def scan_blobs(blobs: dict[str, bytes], sensitive: SensitiveArtifacts) -> list[str]:
    """Return paths containing closed-form private artifacts, never their values."""
    findings = []
    for path, payload in blobs.items():
        basename = PurePosixPath(path).name
        if (basename in sensitive.prohibited_basenames or
                _has_private_bytes(payload, sensitive) or
                _misplaced_public_marker(path, payload)):
            findings.append(path)
    return sorted(findings)
