#!/usr/bin/env python3
"""Build bounded context packs for the index-level other bucket.

This issue's approved execution input is ``data/document-index/index.jsonl``.
That file is not present in this checkout, so this helper uses the mounted
``/mnt/ace/docs/master-index.jsonl`` project archive as a deterministic
fallback for generating candidate packs and exact file-path allowlists.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

HUB_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = HUB_ROOT / "data" / "document-index" / "registry.yaml"
AUDIT_PATH = HUB_ROOT / "data" / "document-index" / "data-audit-report.md"
LOCAL_INDEX_PATH = HUB_ROOT / "data" / "document-index" / "index.jsonl"
FALLBACK_INDEX_PATH = Path("/mnt/ace/docs/master-index.jsonl")
REPORT_PATH = HUB_ROOT / "docs" / "reports" / "index-other-bucket-bounded-packs.md"
MANIFEST_PATH = HUB_ROOT / "data" / "document-index" / "index-other-bucket-pack-manifest.yaml"

DOC_CODE_MAP = {
    "CAL": "calculation",
    "REP": "report",
    "DWG": "drawing",
    "SPE": "specification",
    "PRC": "procedure",
    "MOM": "minutes-of-meeting",
    "LET": "correspondence",
    "MTR": "material-record",
    "PLN": "plan",
    "SCH": "schedule",
    "RFQ": "procurement",
    "INV": "invoice",
    "PO": "purchase-order",
    "DAT": "data-file",
}

EXTENSION_CLASS_MAP = {
    "pdf": "pdf-doc",
    "doc": "word-doc",
    "docx": "word-doc",
    "xls": "spreadsheet",
    "xlsx": "spreadsheet",
    "xlsm": "spreadsheet",
    "ppt": "presentation",
    "pptx": "presentation",
    "csv": "tabular-data",
    "msg": "email",
    "eml": "email",
    "mpp": "schedule",
}


@dataclass(frozen=True)
class PackSpec:
    pack_id: str
    path_prefix: str
    allowed_doc_classes: tuple[str, ...]
    proposed_domain: str
    proposed_status: str
    triage_action: str
    priority: int
    rationale: str


ACTIONABLE_PACK_SPECS = (
    PackSpec(
        pack_id="ace-project-pipeline-9427-itt-reclassify",
        path_prefix=(
            "disciplines/production/projects/9427_2pipeline_engg/"
            "05_reports/9427_2pipeline_engg/1. ITT-20230419T095814Z-001"
        ),
        allowed_doc_classes=("pdf-doc", "specification", "word-doc", "procedure", "report"),
        proposed_domain="pipeline",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=1,
        rationale=(
            "ITT, FEED, EPC, and deliverable-list documents are already grouped "
            "under a single pipeline-engg subtree and can be written back as a "
            "bounded pipeline reference pack."
        ),
    ),
    PackSpec(
        pack_id="ace-project-drilling-3824-calculation-allowlist",
        path_prefix=(
            "disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/"
            "00_inbox/3824 - BP Macondo Containment Riser Analysis/CAL"
        ),
        allowed_doc_classes=("calculation", "spreadsheet"),
        proposed_domain="drilling",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=2,
        rationale=(
            "Macondo containment riser calculation workbooks are tightly clustered "
            "under the CAL subtree and represent a clean drilling-domain allowlist."
        ),
    ),
    PackSpec(
        pack_id="ace-project-drilling-31057-calculation-allowlist",
        path_prefix=(
            "disciplines/drilling/projects/31057_eni_riser_and_subsea_structures_analysis/"
            "00_inbox/31057 - ENI Riser and Subsea Structures Analysis/CAL"
        ),
        allowed_doc_classes=("calculation", "spreadsheet"),
        proposed_domain="drilling",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=3,
        rationale=(
            "The ENI riser calculation subtree contains explicit CAL-coded workbooks "
            "and is small enough for exact allowlist writeback in #2247."
        ),
    ),
    PackSpec(
        pack_id="ace-project-misc-614-sewol-calculation-allowlist",
        path_prefix="disciplines/misc/projects/614_sewol/00_inbox/614 Sewol/CAL",
        allowed_doc_classes=("calculation", "spreadsheet"),
        proposed_domain="naval-architecture",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=4,
        rationale=(
            "Sewol CAL workbooks are strongly engineering-specific and bounded to a "
            "single salvage-analysis subtree suitable for targeted reclassification."
        ),
    ),
    PackSpec(
        pack_id="ace-project-misc-614-sewol-report-allowlist",
        path_prefix="disciplines/misc/projects/614_sewol/05_reports/614 Sewol/REP",
        allowed_doc_classes=("report",),
        proposed_domain="naval-architecture",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=5,
        rationale=(
            "The Sewol REP subtree is a small set of report-coded deliverables and is "
            "the cleanest report-only pack in the salvage archive."
        ),
    ),
    PackSpec(
        pack_id="ace-project-misc-2100-package-engineering-calcs",
        path_prefix=(
            "disciplines/misc/projects/2100_blk31_slor_design/"
            "00_inbox/2100 BLK31 SLOR Design/300 Package Engineering"
        ),
        allowed_doc_classes=("calculation", "spreadsheet", "report"),
        proposed_domain="installation",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=6,
        rationale=(
            "The 2100 package-engineering inbox subtree is a bounded calculation-heavy "
            "installation pack rather than a mixed correspondence archive."
        ),
    ),
    PackSpec(
        pack_id="ace-project-drilling-3824-component-data-summarize-first",
        path_prefix=(
            "disciplines/drilling/projects/3824_bp_macondo_containment_riser_analysis/"
            "05_reports/3824 - BP Macondo Containment Riser Analysis/Component Data"
        ),
        allowed_doc_classes=(
            "pdf-doc",
            "word-doc",
            "presentation",
            "procedure",
            "calculation",
            "specification",
        ),
        proposed_domain="drilling",
        proposed_status="reference",
        triage_action="summarize_first",
        priority=7,
        rationale=(
            "Component-data files are engineering-relevant but mixed enough that #2247 "
            "should summarize and normalize them before committing authoritative "
            "domain/path writeback."
        ),
    ),
    PackSpec(
        pack_id="ace-project-misc-2100-bp-documents-summarize-first",
        path_prefix=(
            "disciplines/misc/projects/2100_blk31_slor_design/"
            "05_reports/2100 BLK31 SLOR Design/BP Documents"
        ),
        allowed_doc_classes=("pdf-doc", "specification", "report", "word-doc", "plan"),
        proposed_domain="installation",
        proposed_status="reference",
        triage_action="summarize_first",
        priority=8,
        rationale=(
            "BP document drops are bounded but mixed vendor/client material. They are "
            "good candidates for summary-first normalization before domain writeback."
        ),
    ),
)

REMAIN_MISCELLANEOUS_RULES = (
    {
        "selection_rule": (
            "path_prefix=disciplines/knowledge_skills/projects/ri/00_inbox/ri "
            "AND doc_class=email"
        ),
        "candidate_count": 31156,
        "reason": (
            "Legacy RI inbox email pool is extremely large, mixed, and operationally "
            "expensive to normalize. Keep miscellaneous until a dedicated email/"
            "thread normalization issue exists."
        ),
    },
    {
        "selection_rule": (
            "path_prefix=disciplines/knowledge_skills/projects/ri/05_reports/ri "
            "AND doc_class=pdf-doc"
        ),
        "candidate_count": 90798,
        "reason": (
            "The RI report/pdf archive is a legacy bulk dump with mixed provenance and "
            "insufficient project boundaries for #2247-style bounded writeback."
        ),
    },
)


def classify_doc_class(file_path: str) -> str:
    """Return a deterministic document class from a relative file path."""
    name = Path(file_path).name
    ext = Path(file_path).suffix.lower().lstrip(".")
    upper_name = name.upper()
    lower_name = name.lower()

    for code, doc_class in DOC_CODE_MAP.items():
        if f"-{code}-" in upper_name or f"_{code}_" in upper_name:
            return doc_class

    if "minutes" in lower_name or "meeting" in lower_name:
        return "minutes-of-meeting"
    if "invoice" in lower_name:
        return "invoice"
    if "proposal" in lower_name or "bid" in lower_name or "quote" in lower_name:
        return "proposal"
    if "rfq" in lower_name or "request for quotation" in lower_name:
        return "procurement"
    if "report" in lower_name:
        return "report"
    if "calc" in lower_name:
        return "calculation"
    if "spec" in lower_name:
        return "specification"
    if "procedure" in lower_name:
        return "procedure"

    return EXTENSION_CLASS_MAP.get(ext, "other-file")


def extract_other_count_from_audit(markdown_text: str) -> int | None:
    """Extract the authoritative `other` bucket count from the audit report."""
    match = re.search(r"\|\s*other\s*\|\s*([\d,]+)\s*\|", markdown_text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def choose_execution_index() -> tuple[Path, str]:
    """Select the best available index surface for pack generation."""
    if LOCAL_INDEX_PATH.exists():
        return LOCAL_INDEX_PATH, "repo-local"
    if FALLBACK_INDEX_PATH.exists():
        return FALLBACK_INDEX_PATH, "mounted-master-index"
    raise FileNotFoundError(
        "Neither data/document-index/index.jsonl nor /mnt/ace/docs/master-index.jsonl is available."
    )


def iter_relative_paths(index_path: Path) -> Iterable[str]:
    """Yield relative file paths from the selected execution index."""
    with index_path.open() as handle:
        for line in handle:
            record = json.loads(line)
            if "file_path" in record:
                yield record["file_path"]
            elif "path" in record:
                yield record["path"]


def collect_pack_records(index_path: Path, pack_spec: PackSpec) -> list[str]:
    """Collect exact file-path allowlists for a configured pack."""
    record_keys: list[str] = []
    allowed = set(pack_spec.allowed_doc_classes)
    prefix = pack_spec.path_prefix
    for relative_path in iter_relative_paths(index_path):
        if not relative_path.startswith(prefix):
            continue
        if classify_doc_class(relative_path) not in allowed:
            continue
        record_keys.append(relative_path)
    return sorted(record_keys)


def build_manifest(index_path: Path, execution_mode: str) -> dict[str, Any]:
    """Build the machine-readable handoff manifest."""
    registry = yaml.safe_load(REGISTRY_PATH.read_text())
    audit_text = AUDIT_PATH.read_text()
    manifest_packs = []

    for pack_spec in ACTIONABLE_PACK_SPECS:
        record_keys = collect_pack_records(index_path, pack_spec)
        manifest_packs.append(
            {
                "pack_id": pack_spec.pack_id,
                "selection_rule": {
                    "path_prefix": pack_spec.path_prefix,
                    "allowed_doc_classes": list(pack_spec.allowed_doc_classes),
                    "execution_index_mode": execution_mode,
                    "execution_index_path": str(index_path),
                },
                "candidate_count": len(record_keys),
                "record_keys_kind": "file_path",
                "record_keys": record_keys,
                "proposed_domain": pack_spec.proposed_domain,
                "proposed_status": pack_spec.proposed_status,
                "triage_action": pack_spec.triage_action,
                "writeback_target": "#2247",
                "priority": pack_spec.priority,
                "rationale": pack_spec.rationale,
                "provenance_note": (
                    "Generated from the mounted master index because the repo-local "
                    "data/document-index/index.jsonl artifact is absent in this checkout."
                ),
            }
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issue": {
            "number": 2249,
            "title": "feat(doc-intel): triage index-level other bucket into bounded context packs",
            "downstream_handoff_issue": 2247,
        },
        "authoritative_other_bucket": {
            "registry_yaml_count": int(registry["by_domain"]["other"]),
            "data_audit_report_count": extract_other_count_from_audit(audit_text),
            "reconciled_live_index_count": None,
            "reconciliation_status": "blocked-missing-repo-local-index",
        },
        "input_artifacts": {
            "requested_live_index": str(LOCAL_INDEX_PATH),
            "requested_live_index_present": LOCAL_INDEX_PATH.exists(),
            "execution_index_path": str(index_path),
            "execution_index_mode": execution_mode,
            "registry_yaml": str(REGISTRY_PATH),
            "data_audit_report": str(AUDIT_PATH),
            "mounted_source_registry": str(HUB_ROOT / "data" / "document-index" / "mounted-source-registry.yaml"),
        },
        "handoff_contract": {
            "consumer_issue": 2247,
            "required_fields": [
                "pack_id",
                "selection_rule",
                "candidate_count",
                "record_keys",
                "proposed_domain",
                "proposed_status",
                "triage_action",
                "writeback_target",
                "provenance_note",
            ],
            "writeback_expectation": (
                "#2247 should resolve each exact file-path allowlist against the "
                "authoritative index, then write back domain/path metadata only for the "
                "allowlisted records."
            ),
        },
        "packs": manifest_packs,
        "remain_miscellaneous_for_now": REMAIN_MISCELLANEOUS_RULES,
    }


def render_report(manifest: dict[str, Any]) -> str:
    """Render the human-readable report."""
    packs = manifest["packs"]
    authoritative = manifest["authoritative_other_bucket"]
    input_artifacts = manifest["input_artifacts"]

    lines = [
        "# Index-Level `other` Bucket — Bounded Context Packs",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Scope",
        "",
        "This report packages bounded candidate packs for issue #2247 using exact file-path allowlists.",
        "The approved execution input for #2249 was `data/document-index/index.jsonl`, but that artifact is absent in this checkout.",
        "To keep the issue moving without writing outside the owned paths, this run used the mounted fallback index at "
        f"`{input_artifacts['execution_index_path']}` and treated the output as a candidate-pack handoff rather than a fully reconciled authoritative writeback list.",
        "",
        "## Input Reconciliation",
        "",
        f"- `registry.yaml` index-level `other` count: `{authoritative['registry_yaml_count']}`",
        f"- `data-audit-report.md` index-level `other` count: `{authoritative['data_audit_report_count']}`",
        f"- Repo-local `data/document-index/index.jsonl` present: `{input_artifacts['requested_live_index_present']}`",
        f"- Execution surface used for this run: `{input_artifacts['execution_index_mode']}` at `{input_artifacts['execution_index_path']}`",
        "- Result: the authoritative 44,705-count baseline is corroborated by the repo audit artifacts but could not be re-counted locally because the repo-local live index file is missing.",
        "",
        "## Immediate Execution Packs",
        "",
        "| Priority | Pack ID | Action | Proposed Domain | Candidate Count | Selection Boundary |",
        "|---|---|---|---|---:|---|",
    ]

    for pack in sorted(packs, key=lambda item: item["priority"]):
        lines.append(
            f"| {pack['priority']} | `{pack['pack_id']}` | `{pack['triage_action']}` | "
            f"`{pack['proposed_domain']}` | {pack['candidate_count']} | "
            f"`{pack['selection_rule']['path_prefix']}` |"
        )

    lines.extend(
        [
            "",
            "## Pack Details",
            "",
        ]
    )

    for pack in sorted(packs, key=lambda item: item["priority"]):
        lines.extend(
            [
                f"### `{pack['pack_id']}`",
                "",
                f"- Action: `{pack['triage_action']}`",
                f"- Proposed domain: `{pack['proposed_domain']}`",
                f"- Candidate count: `{pack['candidate_count']}`",
                f"- Selection rule: `{pack['selection_rule']['path_prefix']}` with doc classes `{', '.join(pack['selection_rule']['allowed_doc_classes'])}`",
                f"- #2247 writeback target: `{pack['writeback_target']}`",
                f"- Rationale: {pack['rationale']}",
                "- Example records:",
            ]
        )
        for example_path in pack["record_keys"][:3]:
            lines.append(f"  - `{example_path}`")
        lines.append("")

    lines.extend(
        [
            "## Remain Miscellaneous For Now",
            "",
            "| Selection Rule | Candidate Count | Reason |",
            "|---|---:|---|",
        ]
    )
    for rule in manifest["remain_miscellaneous_for_now"]:
        lines.append(
            f"| `{rule['selection_rule']}` | {rule['candidate_count']} | {rule['reason']} |"
        )

    lines.extend(
        [
            "",
            "## #2247 Handoff Contract",
            "",
            "- Consume `data/document-index/index-other-bucket-pack-manifest.yaml` as the canonical allowlist artifact.",
            "- Resolve each `record_keys` file-path allowlist against the authoritative index on the #2247 execution machine.",
            "- Write back only the allowlisted records for each pack.",
            "- Preserve `provenance_note` so the fallback execution surface used here is visible in downstream review.",
            "",
            "Expected authoritative writeback fields for each allowlisted record:",
            "",
            "- `domain`",
            "- `path_category`",
            "- `path_subcategory`",
            "- `review_note`",
            "- `provenance_note`",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument("--manifest-path", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()

    index_path, execution_mode = choose_execution_index()
    manifest = build_manifest(index_path=index_path, execution_mode=execution_mode)
    report_text = render_report(manifest)

    args.manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    args.report_path.write_text(report_text, encoding="utf-8")

    pack_counts = Counter(pack["triage_action"] for pack in manifest["packs"])
    print(
        "wrote",
        args.report_path,
        args.manifest_path,
        f"packs={len(manifest['packs'])}",
        dict(pack_counts),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
