#!/usr/bin/env python3
"""Brand-token drift guard — workspace-hub#3402 (epic #3401).

The self-contained report pages under docs/reports/*.html are copied verbatim into
public/ and each carries a *frozen inline copy* of the hub brand tokens. This guard
fails if a page that DECLARES the brand (defines --brand) diverges from the
canonical docs/assets/brand.css values — so the purple identity stays consistent
even though each page inlines its own copy.

Pages that do NOT declare --brand (dark scorecards and other intentional designs)
are exempt — they are not claiming the hub brand.

Run locally and in CI (see .github/workflows/enforcement-gate.yml):
    python scripts/enforcement/check-brand-token-drift.py
Exit 0 = consistent, 1 = drift.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRAND_CSS = ROOT / "docs" / "assets" / "brand.css"
REPORTS = ROOT / "docs" / "reports"

TOKEN_RE = re.compile(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})")


def norm(hexv: str) -> str:
    """Normalise a hex colour for comparison (#fff -> #ffffff, lowercased)."""
    h = hexv.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", h):
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def root_tokens(text: str) -> dict[str, str]:
    """Extract the first :root{} custom-property map from CSS/HTML text."""
    m = re.search(r":root\s*\{([^}]*)\}", text, re.DOTALL)
    if not m:
        return {}
    return {name: norm(val) for name, val in TOKEN_RE.findall(m.group(1))}


def find_violations(canon: dict[str, str], pages: dict[str, dict[str, str]]):
    """pages: {label: token_map}. A page is checked only if it declares --brand;
    every canonical token it also defines must match. Returns [(label, name, got, want)]."""
    out = []
    for label, toks in pages.items():
        if "brand" not in toks:  # not a brand page -> exempt
            continue
        for name, val in toks.items():
            if name in canon and val != canon[name]:
                out.append((label, name, val, canon[name]))
    return out


def main() -> int:
    if not BRAND_CSS.exists():
        print(f"brand guard: {BRAND_CSS} missing", file=sys.stderr)
        return 1
    canon = root_tokens(BRAND_CSS.read_text(encoding="utf-8"))
    pages = {
        str(p.relative_to(ROOT)): root_tokens(p.read_text(encoding="utf-8", errors="ignore"))
        for p in sorted(REPORTS.glob("*.html"))
    }
    checked = [lbl for lbl, t in pages.items() if "brand" in t]
    violations = find_violations(canon, pages)
    if violations:
        print("BRAND-TOKEN DRIFT — report pages that declare --brand must match "
              "docs/assets/brand.css:\n")
        for label, name, got, want in violations:
            print(f"  ✗ {label}: --{name} = {got} (brand.css: {want})")
        print("\nFix the page's :root to the canonical values, or update "
              "docs/assets/brand.css if the brand deliberately changed.")
        return 1
    print(f"brand guard OK — {len(checked)} brand-declaring report page(s) match "
          f"docs/assets/brand.css ({len(canon)} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
