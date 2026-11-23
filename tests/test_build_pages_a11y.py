"""Accessibility baseline in the Pages builder stylesheet (wh#3401 / #3402).

The shared STYLE emitted into public/assets/style.css by scripts/build_pages.py
must carry a consistent keyboard-focus indicator and an .sr-only helper, so every
generated hub page is keyboard-accessible from one source. Purple brand kept.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _style() -> str:
    spec = importlib.util.spec_from_file_location(
        "build_pages_a11y", ROOT / "scripts" / "build_pages.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.STYLE


def test_style_has_focus_visible():
    assert ":focus-visible" in _style()


def test_style_has_sr_only():
    assert ".sr-only" in _style()


def test_style_keeps_purple_brand():
    # per-repo identity: wh stays purple, not recoloured to another repo's brand
    assert "--brand:#5b3fd6" in _style()
