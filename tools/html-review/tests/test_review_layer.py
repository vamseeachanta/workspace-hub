"""Browser test of the review layer: select -> Comment -> Add -> edit in list -> Save (download fallback).

Needs Playwright and Microsoft Edge (channel "msedge"); skipped when either is missing.
Run: python -m pytest tools/html-review/tests -q
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "make_review_copy.py"
SAMPLE = HERE.parent / "demo" / "example-report.html"

playwright = pytest.importorskip("playwright.sync_api")


@pytest.fixture(scope="module")
def review_page(tmp_path_factory):
    out = tmp_path_factory.mktemp("review") / "example-report-review.html"
    subprocess.run([sys.executable, str(TOOL), str(SAMPLE), str(out), "test-comments-v1", "test-comments"], check=True)
    return out


def test_usage_requires_all_arguments():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True)
    assert r.returncode != 0 and "usage" in (r.stderr + r.stdout)


def test_comment_edit_and_save(review_page):
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception as exc:  # Edge not installed
            pytest.skip(f"msedge not available: {exc}")
        page = browser.new_page(viewport={"width": 1300, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(review_page.as_uri() + "#s3-2")
        para = page.locator("#s3-2 ~ p").first
        para.scroll_into_view_if_needed()
        box = para.bounding_box()
        page.mouse.move(box["x"] + 2, box["y"] + 8)
        page.mouse.down()
        page.mouse.move(box["x"] + 300, box["y"] + 8, steps=10)
        page.mouse.up()
        assert page.is_visible("#rv-btn"), "Comment button did not appear after a selection"
        page.click("#rv-btn")
        page.fill("#rv-text", "Replace with: eight conditions over two drafts.")
        page.click("#rv-add")
        assert page.inner_text("#rv-count") == "1"
        assert page.locator("mark.rv-hl").count() == 1
        page.locator('#rv-list textarea[data-i="0"]').click()
        page.keyboard.press("End")
        page.keyboard.type(" Also give the units.")
        page.evaluate("window.showDirectoryPicker = undefined")  # headless: no folder dialog -> download fallback
        with page.expect_download() as dl:
            page.click("#rv-save")
        saved = json.loads(Path(dl.value.path()).read_text(encoding="utf-8"))
        browser.close()
    assert saved["page"] == "example-report.html"
    assert saved["report_version"]
    assert saved["comments"][0]["comment"].endswith("Also give the units.")
    assert saved["comments"][0]["section"].startswith("#s3-2")
    assert not errors, errors
