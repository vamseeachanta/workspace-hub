"""Promotion-ledger schema validation, readiness classification, and reporting.

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2747
Plan:  docs/plans/2026-05-21-issue-2747-acma-private-wiki-promotion-ledger.md
Templates: templates/client-llm-wiki/ledgers/

Design notes:
- `confidence.overall` is an operator-set field (see ledgers/README.md). The
  readiness classification returned by ``classify_readiness`` is a DERIVED
  surface and intentionally separate. This preserves the operator's judgment
  while letting downstream dashboards/reports compute "scored != approved".
- Validation is fail-closed: any missing required field, missing residency or
  provenance, missing score metadata, missing gate state, or missing revision
  lineage raises ``LedgerValidationError``. Downstream consumers cannot treat
  the absence of those fields as a benign default.
- Public output residency requires the full clearance gate set + a non-empty
  rationale. The DATA-CYCLE.md contract bars raw-to-public flows; this is the
  programmatic backstop.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping


READINESS_LABELS = (
    "not-started",
    "partial",
    "usable-with-caveats",
    "client-ready",
    "needs-human-review",
)

# Confidence dimensions required on every entry (eight + overall).
CONFIDENCE_DIMENSIONS = (
    "raw_source_presence",
    "readability_or_ocr_quality",
    "extraction_completeness",
    "metadata_completeness",
    "citation_quality",
    "privacy_redaction_classification",
    "engineering_domain_confidence",
    "report_readiness",
)

ALLOWED_SOURCE_CLASSES = {
    "raw-data",
    "readable-raw-data",
    "private-wiki",
    "public-derivative",
}

ALLOWED_INPUT_RESIDENCY = {"private-client", "private-internal", "public-eligible"}
ALLOWED_OUTPUT_RESIDENCY = {"readable-local", "private-wiki", "public-llm-wiki"}
ALLOWED_RATIONALE_BUCKETS = {
    "not_started",
    "mechanical",
    "model",
    "human_review",
    "mixed",
}
ALLOWED_PROMOTION_STATUS = {
    "not_started",
    "partial",
    "usable_with_caveats",
    "client_ready",
    "needs_human_review",
}

REQUIRED_GATE_KEYS = (
    "reviewer_clearance",
    "legal_clearance",
    "sanitization_review",
    "public_release_clearance",
    "private_release_clearance",
)

PUBLIC_GATES = (
    "reviewer_clearance",
    "legal_clearance",
    "sanitization_review",
    "public_release_clearance",
)
PRIVATE_GATES = ("reviewer_clearance", "private_release_clearance")

# Classification thresholds — derived only, never written back onto the entry.
LOW_DIMENSION_CAP = 0.3      # any sub-field below this caps readiness
PARTIAL_OVERALL_MAX = 0.5    # overall <= this and ungated => partial
USABLE_OVERALL_MAX = 0.75    # overall in (PARTIAL_OVERALL_MAX, this] and ungated
READY_OVERALL_MIN = 0.75     # >= this AND all private gates => client-ready


class LedgerValidationError(ValueError):
    """Raised when a ledger document fails fail-closed validation."""


# --------------------------------------------------------------------------- #
# Structural validation                                                       #
# --------------------------------------------------------------------------- #


def validate_structure(doc: Any) -> None:
    """Shallow structural check used for example/template files.

    Permits placeholder ``null`` values inside entries (the example YAML uses
    these). Full semantic validation lives in ``validate``.
    """
    if not isinstance(doc, Mapping):
        raise LedgerValidationError("ledger root must be a mapping")
    for key in ("ledger_version", "client", "entries"):
        if key not in doc:
            raise LedgerValidationError(f"ledger missing top-level key '{key}'")
    if not isinstance(doc["entries"], list):
        raise LedgerValidationError("ledger 'entries' must be a list")
    seen_ids: set[str] = set()
    for idx, entry in enumerate(doc["entries"]):
        if not isinstance(entry, Mapping):
            raise LedgerValidationError(f"entry #{idx} must be a mapping")
        if "source_id" not in entry:
            raise LedgerValidationError(f"entry #{idx} missing source_id")
        sid = entry["source_id"]
        if sid in seen_ids:
            raise LedgerValidationError(f"duplicate source_id '{sid}'")
        seen_ids.add(sid)


# --------------------------------------------------------------------------- #
# Full semantic validation                                                    #
# --------------------------------------------------------------------------- #


def validate(doc: Any) -> None:
    """Fail-closed validation of a ledger document.

    Raises ``LedgerValidationError`` on the first defect encountered.
    Returns ``None`` on success.
    """
    validate_structure(doc)
    for idx, entry in enumerate(doc["entries"]):
        _validate_entry(entry, idx)


def _require(entry: Mapping, key: str, idx: int, hint: str = "") -> Any:
    if key not in entry:
        raise LedgerValidationError(
            f"entry #{idx} ({entry.get('source_id', '?')}) missing required field '{key}'"
            + (f" — {hint}" if hint else "")
        )
    return entry[key]


def _validate_entry(entry: Mapping, idx: int) -> None:
    sid = entry.get("source_id", "?")

    # Identity + provenance
    _require_nonblank_string(_require(entry, "source_id", idx), f"entry #{idx} source_id")
    sid = entry["source_id"]
    _require_nonblank_string(
        _require(entry, "source_doc_key", idx, "needed for #2389 doc-intel join"),
        f"entry {sid} source_doc_key",
    )
    _require_nonblank_string(_require(entry, "source_path", idx), f"entry {sid} source_path")
    sc = _require(entry, "source_class", idx)
    if sc not in ALLOWED_SOURCE_CLASSES:
        raise LedgerValidationError(
            f"entry {sid} source_class '{sc}' not in {sorted(ALLOWED_SOURCE_CLASSES)}"
        )

    input_res = _require(entry, "input_residency", idx)
    output_res = _require(entry, "output_residency", idx)
    if input_res not in ALLOWED_INPUT_RESIDENCY:
        raise LedgerValidationError(
            f"entry {sid} input_residency '{input_res}' invalid"
        )
    if output_res not in ALLOWED_OUTPUT_RESIDENCY:
        raise LedgerValidationError(
            f"entry {sid} output_residency '{output_res}' invalid"
        )

    # Extraction provenance
    extraction = _require(entry, "extraction", idx)
    if not isinstance(extraction, Mapping):
        raise LedgerValidationError(f"entry {sid} extraction must be a mapping")
    if "version" not in extraction:
        raise LedgerValidationError(
            f"entry {sid} extraction.version is required (revision lineage anchor)"
        )
    _require_nonnegative_int(extraction["version"], f"entry {sid} extraction.version")
    for k in ("method", "tool_version", "extracted_at"):
        if k not in extraction:
            raise LedgerValidationError(f"entry {sid} extraction.{k} key missing")
        _require_nonblank_string(extraction[k], f"entry {sid} extraction.{k}")

    # Confidence (8 + overall)
    conf = _require(entry, "confidence", idx)
    if not isinstance(conf, Mapping):
        raise LedgerValidationError(f"entry {sid} confidence must be a mapping")
    for dim in CONFIDENCE_DIMENSIONS:
        if dim not in conf:
            raise LedgerValidationError(
                f"entry {sid} confidence.{dim} missing (must be 0.0–1.0)"
            )
        _require_unit_float(conf[dim], f"entry {sid} confidence.{dim}")
    if "overall" not in conf:
        raise LedgerValidationError(f"entry {sid} confidence.overall missing")
    _require_unit_float(conf["overall"], f"entry {sid} confidence.overall")

    # Score metadata
    sm = _require(entry, "score_metadata", idx)
    if not isinstance(sm, Mapping):
        raise LedgerValidationError(f"entry {sid} score_metadata must be a mapping")
    for k in ("scored_by", "scored_with", "scored_at", "rationale_bucket"):
        if k not in sm:
            raise LedgerValidationError(f"entry {sid} score_metadata.{k} missing")
    for k in ("scored_by", "scored_with", "scored_at"):
        _require_nonblank_string(sm[k], f"entry {sid} score_metadata.{k}")
    bucket = sm["rationale_bucket"]
    if bucket not in ALLOWED_RATIONALE_BUCKETS:
        raise LedgerValidationError(
            f"entry {sid} score_metadata.rationale_bucket '{bucket}' invalid"
        )

    # Promotion + gates
    promotion = _require(entry, "promotion", idx)
    if not isinstance(promotion, Mapping):
        raise LedgerValidationError(f"entry {sid} promotion must be a mapping")
    for k in ("status", "private_wiki_allowed", "public_llm_wiki_allowed",
              "rationale", "gates"):
        if k not in promotion:
            raise LedgerValidationError(f"entry {sid} promotion.{k} missing")
    status = promotion["status"]
    if status not in ALLOWED_PROMOTION_STATUS:
        raise LedgerValidationError(
            f"entry {sid} promotion.status '{status}' invalid"
        )
    for k in ("private_wiki_allowed", "public_llm_wiki_allowed"):
        _require_bool(promotion[k], f"entry {sid} promotion.{k}")
    gates = promotion["gates"]
    if not isinstance(gates, Mapping):
        raise LedgerValidationError(f"entry {sid} promotion.gates must be a mapping")
    for gk in REQUIRED_GATE_KEYS:
        if gk not in gates:
            raise LedgerValidationError(
                f"entry {sid} promotion.gates.{gk} missing"
            )
        _require_bool(gates[gk], f"entry {sid} promotion.gates.{gk}")

    _enforce_private_output_gates(promotion, sid)
    _enforce_public_output_gates(entry, promotion, output_res, sid)

    # Revision lineage
    lineage = _require(entry, "revision_lineage", idx)
    if not isinstance(lineage, Mapping):
        raise LedgerValidationError(f"entry {sid} revision_lineage must be a mapping")
    if "current_extraction_version" not in lineage:
        raise LedgerValidationError(
            f"entry {sid} revision_lineage.current_extraction_version missing"
        )
    if "previous_extraction_versions" not in lineage:
        raise LedgerValidationError(
            f"entry {sid} revision_lineage.previous_extraction_versions missing"
        )
    if not isinstance(lineage["previous_extraction_versions"], list):
        raise LedgerValidationError(
            f"entry {sid} revision_lineage.previous_extraction_versions must be a list"
        )
    _require_nonnegative_int(
        lineage["current_extraction_version"],
        f"entry {sid} revision_lineage.current_extraction_version",
    )
    if lineage["current_extraction_version"] != extraction["version"]:
        raise LedgerValidationError(
            f"entry {sid} revision_lineage.current_extraction_version "
            f"({lineage['current_extraction_version']}) must equal "
            f"extraction.version ({extraction['version']})"
        )
    _validate_previous_versions(
        lineage["previous_extraction_versions"], extraction["version"], sid
    )


def _enforce_private_output_gates(promotion: Mapping, sid: str) -> None:
    """Require explicit private clearance before allowing private-wiki use."""
    if not promotion["private_wiki_allowed"]:
        return
    gates = promotion["gates"]
    for gk in PRIVATE_GATES:
        if gates[gk] is not True:
            raise LedgerValidationError(
                f"entry {sid} allows private wiki output but gate '{gk}' is not cleared"
            )
    rationale = promotion.get("rationale") or ""
    if not rationale.strip():
        raise LedgerValidationError(
            f"entry {sid} allows private wiki output but promotion.rationale is empty"
        )


def _enforce_public_output_gates(
    entry: Mapping, promotion: Mapping, output_res: str, sid: str
) -> None:
    if output_res == "public-llm-wiki" and promotion["public_llm_wiki_allowed"] is not True:
        raise LedgerValidationError(
            f"entry {sid} declares public output residency but public_llm_wiki_allowed is not true"
        )
    public_declared = output_res == "public-llm-wiki" or promotion["public_llm_wiki_allowed"] is True
    if not public_declared:
        return
    gates = promotion["gates"]
    for gk in PUBLIC_GATES:
        if gates[gk] is not True:
            raise LedgerValidationError(
                f"entry {sid} declares public output but gate '{gk}' is not cleared"
            )
    rationale = promotion.get("rationale") or ""
    if not rationale.strip():
        raise LedgerValidationError(
            f"entry {sid} declares public output but promotion.rationale is empty"
        )


def _require_unit_float(value: Any, label: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise LedgerValidationError(f"{label} must be a number")
    if not (0.0 <= float(value) <= 1.0):
        raise LedgerValidationError(f"{label} must be in range 0.0–1.0 (got {value})")


def _require_nonblank_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LedgerValidationError(f"{label} must be a non-empty string")


def _require_bool(value: Any, label: str) -> None:
    if not isinstance(value, bool):
        raise LedgerValidationError(f"{label} must be a boolean")


def _require_nonnegative_int(value: Any, label: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise LedgerValidationError(f"{label} must be a non-negative integer")


def _validate_previous_versions(
    previous_versions: list[Any], current_version: int, sid: str
) -> None:
    seen_versions: set[int] = set()
    for idx, prior in enumerate(previous_versions):
        if not isinstance(prior, Mapping):
            raise LedgerValidationError(
                f"entry {sid} revision_lineage.previous_extraction_versions[{idx}] must be a mapping"
            )
        for key in ("version", "method", "extracted_at"):
            if key not in prior:
                raise LedgerValidationError(
                    f"entry {sid} revision_lineage.previous_extraction_versions[{idx}].{key} missing"
                )
        _require_nonnegative_int(
            prior["version"],
            f"entry {sid} revision_lineage.previous_extraction_versions[{idx}].version",
        )
        if prior["version"] >= current_version:
            raise LedgerValidationError(
                f"entry {sid} revision_lineage.previous_extraction_versions[{idx}].version "
                f"({prior['version']}) must be less than current extraction.version ({current_version})"
            )
        if prior["version"] in seen_versions:
            raise LedgerValidationError(
                f"entry {sid} revision_lineage.previous_extraction_versions has duplicate "
                f"version {prior['version']}"
            )
        seen_versions.add(prior["version"])
        _require_nonblank_string(
            prior["method"],
            f"entry {sid} revision_lineage.previous_extraction_versions[{idx}].method",
        )
        _require_nonblank_string(
            prior["extracted_at"],
            f"entry {sid} revision_lineage.previous_extraction_versions[{idx}].extracted_at",
        )


# --------------------------------------------------------------------------- #
# Readiness classification (derived; never mutates the entry)                 #
# --------------------------------------------------------------------------- #


def classify_readiness(entry: Mapping) -> str:
    """Return one of READINESS_LABELS based on confidence + gate state.

    The classification is intentionally separate from ``promotion.status``.
    The operator's ``promotion.status`` records their *intent*; this function
    reports what the ledger *evidences*. They can diverge, and when they do
    the dashboard exposes the gap.
    """
    extraction = entry.get("extraction") or {}
    not_extracted = (
        not extraction.get("method")
        and not extraction.get("tool_version")
        and not extraction.get("extracted_at")
    )

    conf = entry.get("confidence") or {}
    dims = [conf.get(d, 0.0) for d in CONFIDENCE_DIMENSIONS]
    overall = conf.get("overall", 0.0)
    has_low_dim = any(float(d) < LOW_DIMENSION_CAP for d in dims)

    promotion = entry.get("promotion") or {}
    gates = promotion.get("gates") or {}
    public_cleared = (
        promotion.get("public_llm_wiki_allowed") is True
        and all(gates.get(k) is True for k in PUBLIC_GATES)
    )
    private_cleared = (
        promotion.get("private_wiki_allowed") is True
        and all(gates.get(k) is True for k in PRIVATE_GATES)
    )

    if not_extracted and all(float(d) == 0.0 for d in dims):
        return "not-started"

    # A single weak dimension caps readiness — operator must remediate or
    # mark "needs-human-review" explicitly. Mirrors README §"Combining sub-fields".
    if has_low_dim:
        return "needs-human-review"

    if private_cleared or public_cleared:
        if float(overall) >= READY_OVERALL_MIN:
            return "client-ready"
        # Cleared but weak score — surface for human review rather than autopromote.
        return "needs-human-review"

    if float(overall) <= PARTIAL_OVERALL_MAX:
        return "partial"
    if float(overall) <= USABLE_OVERALL_MAX:
        return "usable-with-caveats"
    # Score is high enough but no clearance recorded — must not slip into
    # client-ready. The release gate is load-bearing per the plan adversarial
    # review (`feedback_never_offer_to_self_label_plan_approved` family).
    return "needs-human-review"


# --------------------------------------------------------------------------- #
# Dashboard / report summary                                                  #
# --------------------------------------------------------------------------- #


def summarize(doc: Mapping) -> dict:
    """Return a dashboard-shaped summary of a ledger document.

    Shape::

        {
          "counts": {<label>: int, ...},
          "ready":  [<entry>, ...],          # only client-ready
          "blocked":[<entry>, ...],          # everything else (with readiness label attached)
          "groups": {<label>: [<entry>, ...]},
        }

    The ``blocked`` list explicitly surfaces low-confidence / partial /
    needs-human-review items so they cannot be missed before client use.
    """
    entries: Iterable[Mapping] = doc.get("entries") or ()
    counts = {label: 0 for label in READINESS_LABELS}
    groups: dict[str, list[dict]] = {label: [] for label in READINESS_LABELS}

    for entry in entries:
        label = classify_readiness(entry)
        counts[label] += 1
        decorated = dict(entry)
        decorated["readiness"] = label
        groups[label].append(decorated)

    ready = list(groups["client-ready"])
    blocked: list[dict] = []
    for label in READINESS_LABELS:
        if label == "client-ready":
            continue
        blocked.extend(groups[label])

    return {
        "counts": counts,
        "ready": ready,
        "blocked": blocked,
        "groups": groups,
    }
