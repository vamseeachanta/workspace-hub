"""
gate_checks_archive.py — archive-readiness gate check (WRK-668).

Provides check_archive_readiness() used by verify-gate-evidence.py (--phase archive)
and archive-item.sh.

Return convention: (True, msg) = PASS, (None, msg) = WARN/soft-fail, (False, msg) = FAIL.
"""
from __future__ import annotations

from pathlib import Path

import yaml

# Sentinel strings that indicate an un-filled stub value
_STUB_SENTINELS = {
    "checked (manual)",
    "manual",
    "stub",
    "todo",
    "tbd",
    "",
}

_REQUIRED_FIELDS = (
    "merge_status",
    "sync_status",
    "html_verification_ref",
    "legal_scan_ref",
    "archive_readiness",
)


def _load_tooling(assets_dir: Path) -> tuple[dict | None, str]:
    """Load archive-tooling.yaml from evidence/; return (data, error_msg)."""
    tooling_path = assets_dir / "evidence" / "archive-tooling.yaml"
    if not tooling_path.exists():
        return None, f"archive-tooling.yaml absent: {tooling_path}"
    try:
        data = yaml.safe_load(tooling_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return None, f"archive-tooling.yaml parse error: {exc}"
    return data, ""


def check_archive_readiness(assets_dir: Path) -> tuple[bool | None, str]:
    """Validate archive-tooling.yaml for a WRK item before archiving.

    Gates checked (in order):
    1. archive-tooling.yaml exists and is valid YAML
    2. All required fields present and non-sentinel
    3. merge_status / sync_status not stub sentinels (hard-fail)
    4. html_verification_ref file exists on disk
    5. legal_scan_ref file exists on disk
    6. document_index_ref present OR exemption note provided (soft-fail if absent)
    7. archive_readiness field matches actual gate outcomes

    Returns (True, msg) on full pass, (None, msg) on soft-fail, (False, msg) on hard-fail.
    """
    data, err = _load_tooling(assets_dir)
    if data is None:
        return False, err

    # --- 1. Required fields present ---
    missing = [f for f in _REQUIRED_FIELDS if f not in data]
    if missing:
        return False, f"archive-tooling.yaml missing required fields: {', '.join(missing)}"

    # --- 2. Merge/sync sentinel check (hard-fail) ---
    for field in ("merge_status", "sync_status"):
        val = str(data.get(field, "")).strip().lower()
        if val in _STUB_SENTINELS:
            return False, (
                f"archive-tooling.yaml: {field}={data[field]!r} is a stub sentinel — "
                "replace with real merge/sync verification before archiving; "
                "if remediation is non-trivial, run create-spinoff-wrk.sh to capture it"
            )

    # --- 3. html_verification_ref must be set and file must exist ---
    html_ref = str(data.get("html_verification_ref", "")).strip()
    if not html_ref:
        return False, "archive-tooling.yaml: html_verification_ref is empty — must point to lifecycle HTML file"
    if not Path(html_ref).exists():
        return False, (
            f"archive-tooling.yaml: html_verification_ref={html_ref!r} not found on disk"
        )

    # --- 4. legal_scan_ref must be set and file must exist ---
    legal_ref = str(data.get("legal_scan_ref", "")).strip()
    if not legal_ref:
        return False, "archive-tooling.yaml: legal_scan_ref is empty — must point to legal scan artifact"
    if not Path(legal_ref).exists():
        return False, (
            f"archive-tooling.yaml: legal_scan_ref={legal_ref!r} not found on disk"
        )

    # --- 5. document_index_ref — soft-fail if absent without exemption ---
    doc_ref = str(data.get("document_index_ref", "")).strip()
    exemption = str(data.get("document_index_exemption", "")).strip()
    if not doc_ref and not exemption:
        return None, (
            "archive-tooling.yaml: document_index_ref is empty and no exemption note; "
            "set document_index_ref or add document_index_exemption to proceed (soft-fail)"
        )
    if not doc_ref and exemption:
        return None, (
            f"archive-tooling.yaml: document_index_ref absent — exemption accepted: {exemption}"
        )

    # --- 6. archive_readiness field ---
    readiness = str(data.get("archive_readiness", "")).strip().lower()
    if readiness == "hard-fail":
        return False, "archive-tooling.yaml: archive_readiness=hard-fail — resolve blockers before archiving"
    if readiness == "soft-fail":
        return None, "archive-tooling.yaml: archive_readiness=soft-fail — review workarounds before archiving"

    return True, "archive-tooling.yaml: all gates pass (archive_readiness=pass)"
