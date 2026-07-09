"""Tracked brand.css as the single source for the Pages builder (wh#3401 / #3402).

The generator must READ its stylesheet from the tracked docs/assets/brand.css
(not an embedded Python string), so non-generated pages can link the same file
and the brand lives in one editable place. Purple identity + a11y baseline kept.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "docs" / "assets" / "brand.css"


def _style() -> str:
    spec = importlib.util.spec_from_file_location(
        "build_pages_brand", ROOT / "scripts" / "build_pages.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.STYLE


def test_brand_css_is_tracked_and_present():
    assert BRAND.exists(), "docs/assets/brand.css must exist as the tracked source"


def test_generator_reads_the_tracked_brand_css():
    # single source: the generator's STYLE is exactly the tracked file's content
    assert _style() == BRAND.read_text(encoding="utf-8")


def test_brand_css_keeps_identity_and_a11y():
    css = BRAND.read_text(encoding="utf-8")
    assert "--brand:#5b3fd6" in css  # wh stays purple
    assert ":focus-visible" in css  # a11y baseline retained
    assert ".sr-only" in css
