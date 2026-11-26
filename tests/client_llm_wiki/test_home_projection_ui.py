"""Regression tests for the local dashboard review controls."""
from pathlib import Path
import subprocess

from .test_home_projection import hp, record


def test_file_picker_inputs_preserve_clean_and_dirty_review_state():
    result = subprocess.run(
        ["node", str(Path(__file__).with_name("home_projection_review_test.cjs"))],
        capture_output=True, text=True, timeout=15,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert result.returncode == 0, result.stderr


def test_section_headings_do_not_shadow_review_control_ids():
    data = record()
    for section, ident in zip(data["sections"], ("review-panel", "review-load")):
        section["id"] = ident
    dashboard = hp.render(data)["dashboard.html"]
    for section in data["sections"]:
        ident = section["id"]
        assert dashboard.count(f' id="{ident}"') == 1
        assert f'<option value="{ident}">' in dashboard
