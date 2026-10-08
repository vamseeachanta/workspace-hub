"""Browser tests of the review layer: select -> Comment -> Add -> edit -> Save beside the page.

Save must write the comments JSON into the folder that holds the page and never trigger a download.
The native folder dialog cannot be driven headless, so `showDirectoryPicker` is stubbed with an
origin-private (OPFS) directory that holds a copy of the page. OPFS is unavailable on file:// pages,
so the generated page is served from a local http.server bound to 127.0.0.1.

Needs Playwright and Microsoft Edge (channel "msedge"); skipped when either is missing.
Run: python -m pytest tools/html-review/tests -q
"""
import functools
import http.server
import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "make_review_copy.py"
SAMPLE = HERE.parent / "demo" / "example-report.html"
PAGE_NAME = "example-report-review.html"
EXPORT = "example-report-review.json"  # named after the page: <page stem>.json

playwright = pytest.importorskip("playwright.sync_api")

# Stub picker: returns an OPFS sub-folder named by window.__rvPick. setup() copies this page into it.
PICKER_JS = """
window.showDirectoryPicker = async () => {
  window.__rvActive = navigator.userActivation.isActive;  // transient activation when the picker is called
  const root = await navigator.storage.getDirectory();
  return root.getDirectoryHandle(window.__rvPick || "page-folder", {create: true});
};
"""


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    root = tmp_path_factory.mktemp("review")
    out = root / PAGE_NAME
    subprocess.run([sys.executable, str(TOOL), str(SAMPLE), str(out), "test-comments-v1", "test-comments"], check=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=str(root))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}/{PAGE_NAME}"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture()
def browser():
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge", headless=True)
        except Exception as exc:  # Edge not installed
            pytest.skip(f"msedge not available: {exc}")
        yield b
        b.close()


def open_page(browser, url):
    context = browser.new_context(viewport={"width": 1300, "height": 900}, accept_downloads=True)
    context.add_init_script(PICKER_JS)
    page = context.new_page()
    page.errors, page.downloads = [], []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.on("download", lambda d: page.downloads.append(d.suggested_filename))
    page.goto(url + "#s3-2")
    # The page folder holds a copy of the page itself; "wrong-folder" holds nothing.
    page.evaluate("""async name => {
      const root = await navigator.storage.getDirectory();
      const dir = await root.getDirectoryHandle("page-folder", {create: true});
      const w = await (await dir.getFileHandle(name, {create: true})).createWritable();
      await w.write(await (await fetch(location.href)).text()); await w.close();
      await root.getDirectoryHandle("wrong-folder", {create: true});
    }""", PAGE_NAME)
    return page


def read_folder(page, folder):
    return page.evaluate("""async folder => {
      const dir = await (await navigator.storage.getDirectory()).getDirectoryHandle(folder);
      const out = {};
      for await (const [name, h] of dir.entries()) if (name.endsWith(".json")) out[name] = await (await h.getFile()).text();
      return out;
    }""", folder)


def add_comment(page):
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


def test_usage_requires_all_arguments():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True)
    assert r.returncode != 0 and "usage" in (r.stderr + r.stdout)


def test_save_writes_beside_page_and_reloads(server, browser):
    page = open_page(browser, server)
    add_comment(page)
    page.click("#rv-save")
    page.wait_for_function("document.querySelector('#rv-status').textContent.startsWith('Saved')")
    assert page.evaluate("window.__rvActive") is True, "picker called without transient user activation"
    saved = json.loads(read_folder(page, "page-folder")[EXPORT])
    assert saved["page"] == "example-report.html"
    assert saved["report_version"]
    assert saved["comments"][0]["comment"].endswith("Also give the units.")
    assert saved["comments"][0]["section"].startswith("#s3-2")
    # Reopen with browser storage cleared: the comments come back from the JSON beside the page.
    page.evaluate("localStorage.clear()")
    page.reload()
    page.wait_for_function("document.querySelector('#rv-count').textContent === '1'")
    assert "Loaded 1 saved comment" in page.inner_text("#rv-status")
    assert not page.downloads, page.downloads
    assert not page.errors, page.errors


def test_wrong_folder_is_refused(server, browser):
    page = open_page(browser, server)
    add_comment(page)
    page.evaluate("window.__rvPick = 'wrong-folder'")
    page.click("#rv-save")
    page.wait_for_function("/Nothing was saved/.test(document.querySelector('#rv-status').textContent)")
    assert "does not hold this page" in page.inner_text("#rv-status")
    assert read_folder(page, "wrong-folder") == {}
    assert page.inner_text("#rv-count") == "1"
    # Choosing the right folder afterwards saves there.
    page.evaluate("window.__rvPick = 'page-folder'")
    page.click("#rv-save")
    page.wait_for_function("document.querySelector('#rv-status').textContent.startsWith('Saved')")
    assert EXPORT in read_folder(page, "page-folder")
    assert not page.downloads, page.downloads
    assert not page.errors, page.errors


def test_no_file_system_access_never_downloads(server, browser):
    page = open_page(browser, server)
    add_comment(page)
    page.evaluate("window.showDirectoryPicker = undefined")
    page.click("#rv-save")
    page.wait_for_timeout(500)
    status = page.inner_text("#rv-status")
    assert "Nothing was saved" in status and "kept in this tab" in status
    assert not page.downloads, page.downloads
    assert not page.errors, page.errors


def test_other_revision_export_is_left_unchanged(server, browser):
    page = open_page(browser, server)
    other = json.dumps({"page": "example-report.html", "report_version": "older", "comments": []})
    page.evaluate("""async ([name, text]) => {
      const dir = await (await navigator.storage.getDirectory()).getDirectoryHandle("page-folder");
      const w = await (await dir.getFileHandle(name, {create: true})).createWritable(); await w.write(text); await w.close();
    }""", [EXPORT, other])
    add_comment(page)
    page.click("#rv-save")
    page.wait_for_function("/different report revision/.test(document.querySelector('#rv-status').textContent)")
    files = read_folder(page, "page-folder")
    assert files[EXPORT] == other
    siblings = [n for n in files if n != EXPORT]
    assert len(siblings) == 1 and siblings[0].startswith("example-report-review-"), files
    assert json.loads(files[siblings[0]])["comments"][0]["comment"].endswith("Also give the units.")
    assert siblings[0] in page.inner_text("#rv-status")
    assert not page.downloads, page.downloads
    assert not page.errors, page.errors
