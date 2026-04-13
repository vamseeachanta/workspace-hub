#!/usr/bin/env python3
"""Bounded helper for #2245 ACMA wiki-unblock artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
HUB_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_INDEX_PATH = HUB_ROOT / "data/document-index/index.jsonl"
DEFAULT_LEDGER_PATH = HUB_ROOT / "data/document-index/standards-transfer-ledger.yaml"
DEFAULT_SUMMARIES_DIR = HUB_ROOT / "data/document-index/summaries"
DEFAULT_HANDOFF_PATH = HUB_ROOT / "docs/reports/acma-wiki-unblock-2245-handoff.yaml"

TARGET_SPECS = [
    {
        "id": "OCIMF-TANDEM-MOORING",
        "title": "OCIMF Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities",
        "domain": "marine",
        "doc_path": "/mnt/ace/acma-codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities.pdf",
    },
    {
        "id": "CSA-Z276.1-20",
        "title": "CSA Z276.1-20 Marine Structures Associated with LNG Facilities",
        "domain": "marine",
        "doc_path": "/mnt/ace/acma-codes/CSA/276.1-20 marine structures associated with LNG facilities.pdf",
    },
    {
        "id": "CSA-Z276.18",
        "title": "CSA Z276.18 LNG Production, Storage, and Handling",
        "domain": "marine",
        "doc_path": "/mnt/ace/acma-codes/CSA/Z276.18 LNG Production, storage, and handling.pdf",
    },
]


@dataclass(frozen=True)
class TargetRecord:
    standard_id: str
    title: str
    path: str
    content_hash: str
    source: str
    domain: str
    ext: str


@dataclass(frozen=True)
class ArtifactResult:
    record: TargetRecord
    summary_artifact: str
    ready_for_2227: bool
    blocker: str | None


def summary_output_path(summaries_dir: Path, content_hash: str) -> Path:
    return summaries_dir / f"{content_hash}.json"


def _load_target_specs_from_ledger(ledger_path: Path) -> list[dict]:
    wanted = {spec["id"] for spec in TARGET_SPECS}
    with ledger_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or []

    if isinstance(loaded, dict):
        ledger = loaded.get("standards", [])
    else:
        ledger = loaded

    result = [entry for entry in ledger if isinstance(entry, dict) and entry.get("id") in wanted]
    if len(result) != len(TARGET_SPECS):
        missing = sorted(wanted - {entry.get("id") for entry in result})
        raise ValueError(f"Missing target ledger entries: {', '.join(missing)}")
    return result


def resolve_target_records(index_path: Path, ledger_path: Path) -> list[TargetRecord]:
    ledger_entries = _load_target_specs_from_ledger(ledger_path)
    wanted_by_path = {entry["doc_path"]: entry for entry in ledger_entries}
    found: dict[str, TargetRecord] = {}

    with index_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            path = record.get("path")
            if path not in wanted_by_path:
                continue
            entry = wanted_by_path[path]
            found[path] = TargetRecord(
                standard_id=entry["id"],
                title=entry.get("title") or Path(path).stem,
                path=path,
                content_hash=record.get("content_hash", ""),
                source=record.get("source", ""),
                domain=entry.get("domain", "marine"),
                ext=record.get("ext", ""),
            )

    missing_paths = sorted(set(wanted_by_path) - set(found))
    if missing_paths:
        raise ValueError(f"Missing target index records: {missing_paths}")

    missing_hash = [record.path for record in found.values() if not record.content_hash]
    if missing_hash:
        raise ValueError(f"Target records missing content_hash: {missing_hash}")

    return [found[spec["doc_path"]] for spec in TARGET_SPECS]


def extract_text_preview(path: Path, max_pages: int = 3, max_chars: int = 5000) -> str:
    result = subprocess.run(
        ["pdftotext", "-f", "1", "-l", str(max_pages), "-q", str(path), "-"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return ""
    return result.stdout[:max_chars]


def summarise_text(title: str, text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return title
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 40:
            return sentence[:280]
    return cleaned[:280]


def preview_is_usable(title: str, text: str) -> bool:
    cleaned = re.sub(r"\s+", " ", text).strip().lower()
    if not cleaned:
        return False
    title_tokens = {
        token.lower()
        for token in re.findall(r"[a-zA-Z]{3,}", title)
        if token.lower() not in {"guidelines", "associated", "conventional", "tankers", "facilities"}
    }
    if not title_tokens:
        return len(cleaned) >= 80
    return any(token in cleaned for token in title_tokens)


def write_summary_artifact(
    record: TargetRecord,
    summaries_dir: Path,
    text_extractor: Callable[[Path], str] = extract_text_preview,
) -> ArtifactResult:
    summaries_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = summary_output_path(summaries_dir, record.content_hash)
    preview = text_extractor(Path(record.path))
    usable = preview_is_usable(record.title, preview)
    blocker = None
    if not usable:
        blocker = "pdftotext preview was empty or did not contain usable title/domain-aligned text; bounded helper cannot produce a reliable reusable summary from this source file on this machine"

    payload = {
        "path": record.path,
        "sha256": record.content_hash,
        "source": record.source,
        "title": record.title,
        "discipline": record.domain,
        "domain": record.domain,
        "summary": summarise_text(record.title, preview) if usable else "",
        "text_preview": preview[:1000],
        "extraction_method": "pdftotext_p3" if preview else "title_fallback",
        "issue": 2245,
        "downstream_issue": 2227,
        "ready_for_2227": usable,
        "blocker": blocker,
    }
    artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ArtifactResult(
        record=record,
        summary_artifact=str(artifact_path),
        ready_for_2227=usable,
        blocker=blocker,
    )


def build_handoff_payload(results: list[ArtifactResult]) -> dict:
    return {
        "issue": 2245,
        "downstream_issue": 2227,
        "generated_from": "scripts/data/document-index/acma_wiki_unblock.py",
        "ready_for_2227": all(result.ready_for_2227 for result in results),
        "targets": [
            {
                **asdict(result.record),
                "summary_artifact": result.summary_artifact,
                "ready_for_2227": result.ready_for_2227,
                "blocker": result.blocker,
            }
            for result in results
        ],
    }


def write_handoff_payload(results: list[ArtifactResult], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_handoff_payload(results)
    output_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return output_path


def run(index_path: Path, ledger_path: Path, summaries_dir: Path, handoff_path: Path) -> dict:
    records = resolve_target_records(index_path=index_path, ledger_path=ledger_path)
    results = [write_summary_artifact(record, summaries_dir=summaries_dir) for record in records]
    handoff_file = write_handoff_payload(results, output_path=handoff_path)
    return {
        "records": [asdict(result.record) for result in results],
        "summary_paths": [result.summary_artifact for result in results],
        "ready_for_2227": all(result.ready_for_2227 for result in results),
        "blockers": [
            {"standard_id": result.record.standard_id, "blocker": result.blocker}
            for result in results
            if result.blocker
        ],
        "handoff_path": str(handoff_file),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare bounded ACMA summary/classification artifacts for #2245")
    parser.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--ledger-path", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--summaries-dir", type=Path, default=DEFAULT_SUMMARIES_DIR)
    parser.add_argument("--handoff-path", type=Path, default=DEFAULT_HANDOFF_PATH)
    args = parser.parse_args()

    result = run(
        index_path=args.index_path,
        ledger_path=args.ledger_path,
        summaries_dir=args.summaries_dir,
        handoff_path=args.handoff_path,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
