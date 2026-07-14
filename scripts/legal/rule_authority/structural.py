"""Closed-encoding detection for structurally private authority artifacts."""
# AUTHORITY_FORENSIC_DEFINITION: detector signatures, never authority data.

from __future__ import annotations

import base64
from dataclasses import dataclass

PRIVATE_MARKERS = (
    b"legal-rule-private-report-v1",
    b"legal-rule-coverage-v1",
    b"core.repositoryformatversion",
    b"PACK\x00\x00\x00\x02",
    b"\xfftOc",
)
DEFINITION_SENTINEL = b"AUTHORITY_FORENSIC_DEFINITION"
CANONICAL_MARKERS = {
    b"legal-rule-registry-v1": frozenset({
        "config/legal-rule-registry.json", "schemas/legal-rule-registry.schema.json"}),
    b"legal-rule-policy-v1": frozenset({
        "config/legal-rule-authority-policy.json", "schemas/legal-rule-policy.schema.json"}),
    b"legal-rule-map-v1": frozenset({"schemas/legal-rule-map.schema.json"}),
    b"legal-rule-authority-manifest-v1": frozenset({
        "schemas/legal-rule-authority-manifest.schema.json"}),
    b"legal-rule-active-anchor-v1": frozenset({
        "schemas/legal-rule-active-anchor.schema.json"}),
    b"legal-rule-generation-ledger-v1": frozenset({
        "schemas/legal-rule-generation-ledger.schema.json"}),
    b"legal-rule-complete-v1": frozenset({"schemas/legal-rule-complete.schema.json"}),
}


@dataclass(frozen=True)
class SensitiveArtifacts:
    """Private bytes known to the current authenticated authority."""

    key: bytes
    decoded_patterns: tuple[bytes, ...]
    exact_artifacts: tuple[bytes, ...]
    prohibited_basenames: frozenset[str]
    digests: tuple[bytes, ...] = ()
    individual_values: tuple[bytes, ...] = ()


def _sensitive_encodings(sensitive: SensitiveArtifacts) -> tuple[bytes, ...]:
    encoded = [sensitive.key, base64.b64encode(sensitive.key)]
    for pattern in sensitive.decoded_patterns:
        encoded.append(pattern)
        encoded.append(base64.b64encode(pattern))
    for digest in sensitive.digests:
        encoded.extend((digest, digest.hex().encode("ascii"), base64.b64encode(digest)))
    encoded.extend(sensitive.individual_values)
    encoded.extend(sensitive.exact_artifacts)
    return tuple(value for value in encoded if value)


def _has_private_bytes(payload: bytes, sensitive: SensitiveArtifacts,
                       *, definitions: bool = False) -> bool:
    candidates = _sensitive_encodings(sensitive)
    if not definitions:
        candidates = (*PRIVATE_MARKERS, *candidates)
    return any(candidate in payload for candidate in candidates)


def _definition_surface(path: str, payload: bytes) -> bool:
    allowed = (path == "docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md" or
               path.startswith("scripts/legal/rule_authority/") or
               path.startswith("scripts/legal/tests/test_rule_authority_"))
    return allowed and DEFINITION_SENTINEL in b"\n".join(payload.splitlines()[:5])


def _misplaced_public_marker(path: str, payload: bytes) -> bool:
    for marker, canonical_paths in CANONICAL_MARKERS.items():
        if marker in payload and path not in canonical_paths:
            return True
    return False


def contains_sensitive(path: bytes, payload: bytes,
                       sensitive: SensitiveArtifacts) -> bool:
    """Detect closed sensitive encodings without decoding hostile Git paths."""
    basename = path.rsplit(b"/", 1)[-1]
    prohibited = {name.encode("ascii") for name in sensitive.prohibited_basenames}
    public_path = path.decode("ascii", errors="surrogateescape")
    definitions = _definition_surface(public_path, payload)
    return (basename in prohibited or _has_private_bytes(path, sensitive) or
            _has_private_bytes(payload, sensitive, definitions=definitions) or
            (not definitions and _misplaced_public_marker(public_path, payload)))


def scan_blobs(blobs: dict[str, bytes], sensitive: SensitiveArtifacts) -> list[str]:
    """Return paths containing closed-form private artifacts, never their values."""
    findings = []
    for path, payload in blobs.items():
        if contains_sensitive(path.encode("utf-8"), payload, sensitive):
            findings.append(path)
    return sorted(findings)
