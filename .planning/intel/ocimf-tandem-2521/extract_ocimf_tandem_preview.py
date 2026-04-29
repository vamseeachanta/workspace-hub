#!/usr/bin/env python3
"""Generate the #2521 OCIMF Tandem preview artifact without committing raw PDF text.

The source PDF is a scanned document: pdftotext returns an empty preview. This
helper renders the first few pages to temporary PNGs, OCRs them with tesseract,
then writes a bounded JSON preview/summary artifact and updates the existing
#2245/#2227 handoff for only the OCIMF-TANDEM-MOORING target. CSA targets remain
blocked/split to #2522.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = Path(
    "/mnt/ace/acma-codes/OCIMF/OCIMF-Tandem Mooring and Offloading Guidelines "
    "for Conventional Tankers at FPSO Facilities.pdf"
)
OCIMF_DOC_KEY = "sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af"
SUMMARY_PATH = REPO_ROOT / "data/document-index/summaries" / f"{OCIMF_DOC_KEY}.json"
HANDOFF_PATH = REPO_ROOT / "docs/reports/acma-wiki-unblock-2245-handoff.yaml"
TITLE = "OCIMF Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities"


def run_cmd(args: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False, timeout=timeout)


def normalize_ocr_text(text: str) -> str:
    text = text.replace("F{P)SO", "F(P)SO").replace("F(P)SO Facilities'is", "F(P)SO Facilities' is")
    text = re.sub(r"@Copyright OCIMF 2000", "Copyright OCIMF 2009", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def ocr_first_pages(pdf_path: Path, pages: int = 3) -> str:
    with tempfile.TemporaryDirectory(prefix="ocimf_tandem_ocr_") as tmp:
        prefix = Path(tmp) / "page"
        render = run_cmd(["pdftoppm", "-f", "1", "-l", str(pages), "-r", "200", "-png", str(pdf_path), str(prefix)], timeout=90)
        if render.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {render.stderr.strip()}")
        chunks: list[str] = []
        for image in sorted(Path(tmp).glob("page-*.png")):
            ocr = run_cmd(["tesseract", str(image), "stdout", "--psm", "6"], timeout=90)
            if ocr.returncode != 0:
                raise RuntimeError(f"tesseract failed for {image.name}: {ocr.stderr.strip()}")
            chunks.append(ocr.stdout)
    return normalize_ocr_text("\n\n".join(chunks))


def build_summary(preview: str) -> str:
    # Curated only from first-page OCR: avoids raw full-text ingestion while giving #2227 usable evidence.
    return (
        "OCR preview identifies the source as OCIMF's first-edition 2009 Tandem Mooring and Offloading "
        "Guidelines for Conventional Tankers at F(P)SO Facilities, issued by the Oil Companies International "
        "Marine Forum. The visible table of contents covers scope, purpose, applicable codes and standards, "
        "FPSO/FSO offloading philosophy, subsea mooring arrangements, basis of design, tandem mooring "
        "configuration, and equipment including single/dual hawser systems, chafe chain, fairlead, weak link, "
        "hawser handling, storage, and retirement."
    )


def write_summary(preview: str) -> None:
    if len(preview) < 200:
        raise ValueError(f"OCR preview too short for #2521 acceptance: {len(preview)} chars")
    payload = {
        "path": str(SOURCE_PATH),
        "sha256": OCIMF_DOC_KEY,
        "source": "acma_codes",
        "title": TITLE,
        "discipline": "marine",
        "domain": "marine",
        "summary": build_summary(preview),
        "text_preview": preview[:1200],
        "extraction_method": "ocr_tesseract_first_pages",
        "issue": 2521,
        "downstream_issue": 2227,
        "ready_for_2227": True,
        "blocker": None,
        "provenance": {
            "source_of_record": str(SOURCE_PATH),
            "raw_pdf_committed_to_git": False,
            "ocr_scope": "first 3 pages only; temporary render images deleted after OCR",
        },
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_handoff() -> None:
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))
    handoff["generated_from"] = ".planning/intel/ocimf-tandem-2521/extract_ocimf_tandem_preview.py"
    # Keep top-level false until CSA split/Branch-B state is reconciled; #2521 only unblocks OCIMF.
    handoff["ready_for_2227"] = False
    for target in handoff.get("targets", []):
        sid = target.get("standard_id")
        if sid == "OCIMF-TANDEM-MOORING":
            target["summary_artifact"] = str(SUMMARY_PATH)
            target["ready_for_2227"] = True
            target["blocker"] = None
        elif sid in {"CSA-Z276.1-20", "CSA-Z276.18"}:
            target["ready_for_2227"] = False
            target["blocker"] = "CSA content readiness intentionally split to #2522; not claimed by #2521 OCIMF-only unblocker"
    HANDOFF_PATH.write_text(yaml.safe_dump(handoff, sort_keys=False), encoding="utf-8")


def main() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(SOURCE_PATH)
    preview = ocr_first_pages(SOURCE_PATH)
    write_summary(preview)
    update_handoff()
    print(f"wrote {SUMMARY_PATH}")
    print(f"updated {HANDOFF_PATH}")
    print(f"preview_chars={len(preview)}")


if __name__ == "__main__":
    main()
