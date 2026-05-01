#!/usr/bin/env python3
"""Backfill recommended `sources` frontmatter on Elements wiki source pages."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAGES = [
    ("knowledge/wikis/asset-management/wiki/sources/elements-assethold-casa-grande-77017.md", "/mnt/ace/assethold/casa-grande-77017"),
    ("knowledge/wikis/engineering/wiki/sources/elements-digitalmodel-qgis.md", "/mnt/ace/digitalmodel/tools/qgis"),
    ("knowledge/wikis/engineering/wiki/sources/elements-doris-university.md", "/mnt/ace/doris/training"),
    ("knowledge/wikis/engineering-standards/wiki/sources/elements-doris-codes-specs.md", "/mnt/ace/doris/codes"),
    ("knowledge/wikis/lng-projects/wiki/sources/elements-acma-projects-31522-woodfibre.md", "/mnt/ace/acma-projects/31522-woodfibre-lng"),
    ("knowledge/wikis/lng-projects/wiki/sources/elements-doris-62092-sesa.md", "/mnt/ace/doris/62092_sesa"),
    ("knowledge/wikis/marine-engineering/wiki/sources/elements-digitalmodel-riser-toolbox.md", "/mnt/ace/digitalmodel/references/riser-toolbox"),
    ("knowledge/wikis/marine-engineering/wiki/sources/elements-digitalmodel-suction-pile-sizing.md", "/mnt/ace/digitalmodel/references/suction-pile-sizing"),
]


def patch_page(rel_path: str, source_root: str) -> bool:
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    if "\nsources:\n" in text[: text.find("\n---", 3) if text.find("\n---", 3) != -1 else 400]:
        return False
    marker = "last_updated: 2026-04-28\n"
    replacement = marker + "sources:\n" + f"  - {source_root}\n"
    if marker not in text:
        raise RuntimeError(f"missing marker in {path}")
    path.write_text(text.replace(marker, replacement, 1), encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for rel, src in PAGES:
        if patch_page(rel, src):
            print(f"patched {rel}")
            changed += 1
        else:
            print(f"already-ok {rel}")
    print(f"changed={changed}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
