"""Tests for bounded ACMA wiki-unblock helper (#2245)."""

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from acma_wiki_unblock import (  # noqa: E402
    TARGET_SPECS,
    build_handoff_payload,
    preview_is_usable,
    resolve_target_records,
    summary_output_path,
    write_summary_artifact,
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def _write_ledger(path: Path) -> None:
    path.write_text(
        """
- id: OCIMF-TANDEM-MOORING
  title: OCIMF Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities
  domain: marine
  doc_path: /mnt/ace/acma-codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf
- id: CSA-Z276.1-20
  title: CSA Z276.1-20 Marine Structures Associated with LNG Facilities
  domain: marine
  doc_path: /mnt/ace/acma-codes/CSA/276.1-20 marine structures associated with LNG facilities.pdf
- id: CSA-Z276.18
  title: CSA Z276.18 LNG Production, Storage, and Handling
  domain: marine
  doc_path: /mnt/ace/acma-codes/CSA/Z276.18 LNG Production, storage, and handling.pdf
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_resolve_target_records_returns_exact_three_targets(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.yaml"
    index_path = tmp_path / "index.jsonl"
    _write_ledger(ledger_path)
    _write_jsonl(
        index_path,
        [
            {
                "path": spec["doc_path"],
                "content_hash": f"sha256:{i}",
                "source": "acma_codes",
                "domain": None,
                "summary": None,
                "ext": "pdf",
            }
            for i, spec in enumerate(TARGET_SPECS, start=1)
        ]
        + [
            {
                "path": "/mnt/ace/acma-codes/CSA/out-of-scope.pdf",
                "content_hash": "sha256:extra",
                "source": "acma_codes",
                "domain": None,
                "summary": None,
                "ext": "pdf",
            }
        ],
    )

    resolved = resolve_target_records(index_path=index_path, ledger_path=ledger_path)

    assert len(resolved) == 3
    assert {record.standard_id for record in resolved} == {
        "OCIMF-TANDEM-MOORING",
        "CSA-Z276.1-20",
        "CSA-Z276.18",
    }
    assert {record.path for record in resolved} == {spec["doc_path"] for spec in TARGET_SPECS}
    assert all(record.domain == "marine" for record in resolved)


def test_resolve_target_records_errors_when_any_target_missing(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.yaml"
    index_path = tmp_path / "index.jsonl"
    _write_ledger(ledger_path)
    _write_jsonl(
        index_path,
        [
            {
                "path": TARGET_SPECS[0]["doc_path"],
                "content_hash": "sha256:1",
                "source": "acma_codes",
                "domain": None,
                "summary": None,
                "ext": "pdf",
            }
        ],
    )

    with pytest.raises(ValueError, match="Missing target index records"):
        resolve_target_records(index_path=index_path, ledger_path=ledger_path)


def test_summary_output_path_uses_local_override_directory(tmp_path: Path) -> None:
    result = summary_output_path(tmp_path, "sha256:abc123")
    assert result == tmp_path / "sha256:abc123.json"


def test_build_handoff_payload_names_exact_artifact_refs(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.yaml"
    index_path = tmp_path / "index.jsonl"
    summaries_dir = tmp_path / "summaries"
    _write_ledger(ledger_path)
    _write_jsonl(
        index_path,
        [
            {
                "path": spec["doc_path"],
                "content_hash": f"sha256:{i}",
                "source": "acma_codes",
                "domain": None,
                "summary": None,
                "ext": "pdf",
            }
            for i, spec in enumerate(TARGET_SPECS, start=1)
        ],
    )
    resolved = resolve_target_records(index_path=index_path, ledger_path=ledger_path)
    results = [
        write_summary_artifact(record, summaries_dir=summaries_dir, text_extractor=lambda _path, t=record.title: t)
        for record in resolved
    ]

    payload = build_handoff_payload(results)

    assert payload["issue"] == 2245
    assert payload["downstream_issue"] == 2227
    assert payload["ready_for_2227"] is True
    assert len(payload["targets"]) == 3
    assert {item["domain"] for item in payload["targets"]} == {"marine"}
    assert all(item["summary_artifact"].endswith(".json") for item in payload["targets"])
    assert all("content_hash" in item for item in payload["targets"])


def test_preview_is_usable_rejects_garbled_or_empty_text() -> None:
    title = "CSA Z276.18 LNG Production, Storage, and Handling"
    assert preview_is_usable(title, "") is False
    assert preview_is_usable(title, "monen kuunnella cannikka camoin pyctyvat vaatteitaan") is False
    assert preview_is_usable(title, "LNG production, storage, and handling requirements for marine terminals") is True


def test_write_summary_artifact_marks_blocker_for_unusable_preview(tmp_path: Path) -> None:
    summaries_dir = tmp_path / "summaries"
    record = TARGET_SPECS[0]
    target = type("Target", (), {
        "standard_id": record["id"],
        "title": record["title"],
        "path": record["doc_path"],
        "content_hash": "sha256:blocker",
        "source": "acma_codes",
        "domain": "marine",
        "ext": "pdf",
    })()

    result = write_summary_artifact(
        target,
        summaries_dir=summaries_dir,
        text_extractor=lambda _path: "monen kuunnella cannikka camoin pyctyvat vaatteitaan",
    )

    payload = json.loads(Path(result.summary_artifact).read_text(encoding="utf-8"))
    assert result.ready_for_2227 is False
    assert result.blocker is not None
    assert payload["ready_for_2227"] is False
    assert payload["blocker"]
    assert payload["summary"] == ""
