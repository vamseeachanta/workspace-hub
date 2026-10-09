# make_comment_gif.py
"""Record the report comment tutorial using headless Microsoft Edge.

Run:
    python make_comment_gif.py
"""

from __future__ import annotations

import io
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import expect, sync_playwright


HERE = Path(__file__).resolve().parent

URL = (HERE / "example-report-review.html").resolve().as_uri() + "#s3-2"
OUTPUT = HERE / "how-to-comment.gif"
FRAME_DIR = OUTPUT.parent / "gif-frames"
WIDTH, HEIGHT = 1280, 800
OUTPUT_WIDTH = 960
CAPTION_HEIGHT = 108
MAX_BYTES = 8_000_000

COMMENT = "Add the reference draft to the table caption."
SECOND_COMMENT = (
    "Convert this to sub-bullets: one bullet per draft, "
    "with the speed and the % change."
)
APPEND_TEXT = " Also give the units."
RESULTS_QUOTE = (
    "Resistance increases by about 30 % from ballast to the loaded "
    "draft at 12 kn in this example."
)

CAP_OPEN = "1. Open the report in Edge or Chrome (not an e-mail preview)"
CAP_SELECT = "2. Select the text you want to comment on"
CAP_CLICK = "3. Click Comment"
CAP_TYPE = "4. Type your comment, then Add"
CAP_ADDED = "The passage is highlighted; hover shows the comment"
CAP_STRUCTURE = (
    "You can ask for structure changes: 'convert to sub-bullets', "
    "'make this a table', 'move to Appendix'"
)
CAP_SECOND = "Second comment added (2)"
CAP_EDIT = (
    "Edit any comment in the list at any time; changes are kept automatically"
)
CAP_SAVE = (
    "5. Save comments: the first time, choose the folder that holds the report"
)


def font(size):
    for filename in ("segoeui.ttf", "arial.ttf"):
        path = Path("C:/Windows/Fonts") / filename
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def wrap(text, typeface, max_width):
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if current and draw.textlength(candidate, font=typeface) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return lines


def centered_lines(image, lines, typeface, top, spacing, color="white"):
    draw = ImageDraw.Draw(image)
    for index, line in enumerate(lines):
        draw.text(
            (WIDTH / 2, top + index * spacing),
            line, font=typeface, fill=color, anchor="mt",
        )


def card(blocks):
    image = Image.new("RGB", (WIDTH, HEIGHT), "#1F5A7A")
    layouts = []
    for text, size in blocks:
        typeface = font(size)
        layouts.append((wrap(text, typeface, WIDTH - 160), typeface, size + 13))
    total = sum(len(lines) * spacing for lines, _, spacing in layouts)
    total += 36 * (len(layouts) - 1)
    top = (HEIGHT - total) / 2
    for lines, typeface, spacing in layouts:
        centered_lines(image, lines, typeface, top, spacing)
        top += len(lines) * spacing + 36
    return image


def ideas_card():
    rows = [
        'Reword: "Replace with: …"',
        'Structure: "Convert to sub-bullets" · "Make this a table" · "Merge with 4.1"',
        'Values: "Should be 6.50 m, see drawing rev B"',
        'Scope: "Delete, not needed" · "Move to Appendix"',
        'Add: "Add a note on the trim sign convention"',
        'Question: "Why is C4 lower than C3?"',
        'Confirm: "Agreed, no change"',
    ]
    image = Image.new("RGB", (WIDTH, HEIGHT), "#1F5A7A")
    draw = ImageDraw.Draw(image)
    body = font(30)
    layouts = [wrap(row, body, WIDTH - 160) for row in rows]
    total = 90 + sum(len(lines) * 42 + 16 for lines in layouts)
    if total > HEIGHT - 100:
        raise RuntimeError("Ideas card does not fit")
    top = (HEIGHT - total) / 2
    draw.text((80, top), "Ideas for comments", font=font(48),
              fill="white", anchor="lt")
    top += 90
    for lines in layouts:
        for line in lines:
            draw.text((80, top), line, font=body, fill="white", anchor="lt")
            top += 42
        top += 16
    return image


def caption(image, text):
    image = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle(
        (0, HEIGHT - CAPTION_HEIGHT, WIDTH, HEIGHT), fill=(12, 25, 35, 235)
    )
    typeface = font(27)
    lines = wrap(text, typeface, WIDTH - 80)
    if len(lines) > 2:
        raise RuntimeError(f"Caption exceeds the reserved bar: {text}")
    top = HEIGHT - CAPTION_HEIGHT + (CAPTION_HEIGHT - len(lines) * 37) / 2
    centered_lines(overlay, lines, typeface, top, 37)
    return Image.alpha_composite(image, overlay).convert("RGB")


CURSOR_JS = """
() => {
    const cursor = document.createElement("div");
    cursor.id = "tutorial-cursor";
    cursor.style.cssText = `
        position:fixed;left:0;top:0;width:32px;height:40px;
        pointer-events:none;z-index:2147483647;
    `;
    cursor.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg"
           width="32" height="40" viewBox="0 0 32 40"
           style="position:absolute;left:0;top:0;overflow:visible">
        <path d="M2 2 L2 30 L9 23 L15 36 L21 33 L15 21 L26 21 Z"
              fill="white" stroke="#102633" stroke-width="2"
              stroke-linejoin="round"/>
      </svg>`;
    const ripple = document.createElement("div");
    ripple.id = "tutorial-ripple";
    ripple.style.cssText = `
        position:fixed;pointer-events:none;z-index:2147483646;
        border:3px solid #FFB347;border-radius:50%;
        transform:translate(-50%,-50%);display:none;
        box-sizing:border-box;background:rgba(255,179,71,.16);
    `;
    document.body.append(ripple, cursor);
}
"""

PRESENTATION_CSS = """
html { scroll-behavior: auto !important; }
#rv-panel { bottom: 120px !important; max-height: 550px !important; }
"""

# Preserve sentence selection; allow the second beat to select a whole paragraph.
SELECTION_JS = r"""
({selector, whole}) => {
    const p = document.querySelector(selector);
    if (!p) throw new Error("Selection paragraph is missing: " + selector);
    const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let text = "", node;
    while ((node = walker.nextNode())) {
        nodes.push({node, start:text.length, end:text.length + node.length});
        text += node.data;
    }
    const start = text.search(/\S/);
    if (start < 0) throw new Error("Section paragraph is empty");
    let sentence;
    if (whole) {
        sentence = text.slice(start);
    } else if (Intl.Segmenter) {
        sentence = Array.from(
            new Intl.Segmenter("en", {granularity:"sentence"})
                .segment(text.slice(start))
        )[0].segment;
    } else {
        const rest = text.slice(start);
        sentence = (rest.match(/^[\s\S]*?[.!?](?=\s|$)/) || [rest])[0];
    }
    const quote = sentence.trimEnd();
    const end = start + quote.length;
    function boundary(offset, isEnd) {
        for (const part of nodes) {
            if (offset >= part.start &&
                (offset < part.end || (isEnd && offset === part.end))) {
                return {node:part.node, offset:offset-part.start};
            }
        }
        throw new Error("Cannot map selection to text nodes");
    }
    const a = boundary(start, false), b = boundary(end, true);
    const range = document.createRange();
    range.setStart(a.node, a.offset);
    range.setEnd(b.node, b.offset);
    const rects = Array.from(range.getClientRects())
        .filter(r => r.width > 0 && r.height > 0);
    if (!rects.length) throw new Error("Selection has no visible geometry");
    window.__tutorialSelection = {range, quote};
    return {
        quote,
        rects: rects.map(r => ({
            left:r.left, right:r.right, top:r.top, bottom:r.bottom
        }))
    };
}
"""

SNAP_SELECTION_JS = """
() => {
    const selection = getSelection();
    selection.removeAllRanges();
    selection.addRange(window.__tutorialSelection.range);
}
"""

# Discover the actual page storage key by its two known comments, without
# assuming that the page's lexical KEY constant is exposed on window.
STORAGE_KEYS_JS = """
expected => {
    function matches(value) {
        if (!value || typeof value !== "object") return false;
        if (Array.isArray(value) &&
            value.length === expected.length &&
            value.every((item, i) => item && item.comment === expected[i]))
            return true;
        return Object.values(value).some(matches);
    }
    return Object.keys(localStorage).filter(key => {
        try { return matches(JSON.parse(localStorage.getItem(key))); }
        catch { return false; }
    });
}
"""

SAVE_STUB_JS = """
() => {
    // In-memory stand-in for the unavailable native folder dialog.
    window.__rvSaved = [];
    window.showDirectoryPicker = async () => ({
        name: "review", kind: "directory",
        queryPermission: async () => "granted",
        requestPermission: async () => "granted",
        getFileHandle: async (n, o) => {
            // The folder holds this page, so the page's folder check passes.
            if (n === decodeURIComponent(location.pathname.split("/").pop()))
                return { getFile: async () => ({ text: async () => document.documentElement.outerHTML }) };
            if (!(o && o.create))
                throw new DOMException("not found", "NotFoundError");
            return { createWritable: async () => ({
                write: async text => {
                    window.__rvSaved.push({name:n, payload:JSON.parse(text)});
                },
                close: async () => {}
            }) };
        },
    });
}
"""


class Recorder:
    def __init__(self, page):
        self.page = page
        self.frames = []
        self.durations = []
        self.position = (70.0, 100.0)

    def add(self, image, duration):
        self.frames.append(image.convert("RGB"))
        self.durations.append(duration)

    def capture(self, text, duration=120):
        with Image.open(io.BytesIO(self.page.screenshot())) as raw:
            self.add(caption(raw, text), duration)

    def position_cursor(self, x, y):
        self.page.mouse.move(x, y)
        self.page.evaluate(
            """([x,y]) => {
                const c = document.getElementById("tutorial-cursor");
                c.style.left = x + "px";
                c.style.top = y + "px";
            }""", [x, y],
        )
        self.position = (x, y)

    def move(self, x, y, steps, text):
        start_x, start_y = self.position
        for index in range(1, steps + 1):
            fraction = index / steps
            self.position_cursor(
                start_x + (x - start_x) * fraction,
                start_y + (y - start_y) * fraction,
            )
            self.capture(text)

    def ripple(self, text):
        for diameter, opacity in ((16, 1), (34, 0.75), (54, 0.4)):
            self.page.evaluate(
                """([x,y,d,o]) => {
                    const r = document.getElementById("tutorial-ripple");
                    Object.assign(r.style, {
                        left:x+"px", top:y+"px",
                        width:d+"px", height:d+"px",
                        opacity:String(o), display:"block"
                    });
                }""", [*self.position, diameter, opacity],
            )
            self.capture(text)
        self.page.evaluate(
            "document.getElementById('tutorial-ripple').style.display='none'"
        )

    def click(self, selector, text):
        target = self.page.locator(selector)
        expect(target).to_be_visible()
        target.scroll_into_view_if_needed()
        box = target.bounding_box()
        if box is None:
            raise RuntimeError(f"No bounding box for {selector}")
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT - CAPTION_HEIGHT):
            raise RuntimeError(f"Target is outside the unobscured viewport: {selector}")
        self.move(x, y, 3, text)
        self.page.mouse.down()
        self.capture(text)
        self.page.mouse.up()
        self.ripple(text)


def select_sentence(recorder):
    page = recorder.page
    geometry = page.evaluate(
        SELECTION_JS, {"selector": "#s3-2 ~ p", "whole": False}
    )
    rects = geometry["rects"]
    if len(geometry["quote"]) > 600:
        raise RuntimeError("First sentence exceeds the review layer's quote limit")
    for rect in rects:
        if not (
            0 <= rect["left"] < rect["right"] <= WIDTH
            and 0 <= rect["top"] < rect["bottom"] < HEIGHT - CAPTION_HEIGHT
        ):
            raise RuntimeError("First sentence does not fit in the visible report area")
    first = rects[0]
    recorder.move(first["left"] + 1, (first["top"] + first["bottom"]) / 2,
                  3, CAP_SELECT)
    page.mouse.down()
    for index, rect in enumerate(rects):
        y = (rect["top"] + rect["bottom"]) / 2
        if index:
            recorder.move(rect["left"] + 1, y, 1, CAP_SELECT)
        recorder.move(rect["right"] - 1, y, 3, CAP_SELECT)
    page.evaluate(SNAP_SELECTION_JS)
    page.mouse.up()
    expect(page.locator("#rv-btn")).to_be_visible()
    if page.evaluate("getSelection().toString().trim()") != geometry["quote"].strip():
        raise RuntimeError("Selected text differs from the first sentence")
    recorder.capture(CAP_SELECT, 1100)


def select_structure(recorder):
    page = recorder.page
    selector = "#s4 p:nth-of-type(2)"
    page.evaluate("getSelection().removeAllRanges()")
    page.locator(selector).evaluate(
        "element => element.scrollIntoView({block:'center', behavior:'instant'})"
    )
    recorder.capture(CAP_STRUCTURE, 600)
    geometry = page.evaluate(SELECTION_JS, {"selector": selector, "whole": True})
    if " ".join(geometry["quote"].split()) != RESULTS_QUOTE:
        raise RuntimeError("Section 4 second paragraph differs from the sample")
    if len(geometry["quote"]) > 600:
        raise RuntimeError("Second paragraph exceeds the review layer's quote limit")
    panel = page.locator("#rv-panel").bounding_box()
    if panel is None:
        raise RuntimeError("Review panel has no bounding box")
    rect = geometry["rects"][0]
    y = (rect["top"] + rect["bottom"]) / 2
    left = rect["left"] + 1
    right = min(rect["right"] - 1, panel["x"] - 12, left + 230)
    if not (0 <= left < right < WIDTH and 0 <= y < HEIGHT - CAPTION_HEIGHT):
        raise RuntimeError("No unobscured left-hand paragraph drag is available")
    for x in (left, right):
        if not page.evaluate(
            """([selector,x,y]) => {
                const p = document.querySelector(selector);
                return p.contains(document.elementFromPoint(x,y));
            }""", [selector, x, y],
        ):
            raise RuntimeError("Paragraph drag would hit an overlay")
    recorder.move(left, y, 3, CAP_STRUCTURE)
    page.mouse.down()
    recorder.move(right, y, 3, CAP_STRUCTURE)
    # Drag only in the exposed left area, then snap to the whole paragraph.
    page.evaluate(SNAP_SELECTION_JS)
    page.mouse.up()
    expect(page.locator("#rv-btn")).to_be_visible()
    if page.evaluate("getSelection().toString().trim()") != geometry["quote"]:
        raise RuntimeError("The whole second paragraph was not selected")
    recorder.capture(CAP_STRUCTURE, 800)


def type_comment(recorder, text, caption_text):
    previous = 0
    for beat in range(1, 9):
        end = math.ceil(len(text) * beat / 8)
        for character in text[previous:end]:
            recorder.page.keyboard.insert_text(character)
        previous = end
        recorder.capture(caption_text, 180)
    expect(recorder.page.locator("#rv-text")).to_have_value(text)


def show_first_highlight(recorder):
    page = recorder.page
    highlight = page.locator("mark.rv-hl").filter(
        has_not=page.locator("#rv-panel")
    ).first
    expect(highlight).to_be_visible()
    expect(highlight).to_have_attribute("title", COMMENT)
    page.evaluate("getSelection().removeAllRanges()")
    box = highlight.bounding_box()
    if box is None:
        raise RuntimeError("Highlighted passage has no bounding box")
    recorder.move(
        box["x"] + min(box["width"] / 2, 100),
        box["y"] + box["height"] / 2, 3, CAP_ADDED,
    )
    # Assert the real native title; do not fabricate headless tooltips.
    page.wait_for_timeout(800)
    recorder.capture(CAP_ADDED, 2000)


def add_second_comment(recorder):
    page = recorder.page
    select_structure(recorder)
    recorder.click("#rv-btn", CAP_STRUCTURE)
    expect(page.locator("#rv-text")).to_be_visible()
    expect(page.locator("#rv-text")).to_be_focused()
    type_comment(recorder, SECOND_COMMENT, CAP_STRUCTURE)
    recorder.capture(CAP_STRUCTURE, 500)
    recorder.click("#rv-add", CAP_STRUCTURE)
    expect(page.locator("#rv-count")).to_have_text("2")
    expect(page.locator('#rv-list textarea[data-i="1"]')).to_have_value(SECOND_COMMENT)
    marks = page.locator("#s4 p:nth-of-type(2) mark.rv-hl")
    expect(marks.first).to_be_visible()
    for mark in marks.all():
        expect(mark).to_have_attribute("title", SECOND_COMMENT)
    page.evaluate("getSelection().removeAllRanges()")
    recorder.capture(CAP_SECOND, 900)


def edit_first_comment(recorder):
    page = recorder.page
    keys = page.evaluate(STORAGE_KEYS_JS, [COMMENT, SECOND_COMMENT])
    if not keys:
        raise RuntimeError("Cannot discover the page's stored two-comment record")
    selector = '#rv-list textarea[data-i="0"]'
    textarea = page.locator(selector)
    expect(textarea).to_have_value(COMMENT)
    textarea.scroll_into_view_if_needed()
    recorder.click(selector, CAP_EDIT)
    expect(textarea).to_be_focused()
    page.keyboard.press("Control+End")
    for chunk in (" Also", " give", " the", " units."):
        # Native keyboard input fires the list's automatic-save input handler.
        page.keyboard.type(chunk)
        recorder.capture(CAP_EDIT, 220)
    expect(textarea).to_have_value(COMMENT + APPEND_TEXT)
    updated_keys = page.evaluate(
        STORAGE_KEYS_JS, [COMMENT + APPEND_TEXT, SECOND_COMMENT]
    )
    if not set(keys).intersection(updated_keys):
        raise RuntimeError("The existing localStorage record did not keep the edit")
    expect(page.locator("#rv-count")).to_have_text("2")
    recorder.capture(CAP_EDIT, 900)


def verify_private_save(page):
    expect(page.locator("#rv-status")).to_contain_text(
        "Saved 2 comments to ", timeout=15000
    )
    result = page.evaluate("() => window.__rvSaved || []")
    matching = [
        item for item in result
        if len(item["payload"].get("comments", [])) == 2
        and item["payload"]["comments"][0].get("comment") == COMMENT + APPEND_TEXT
        and item["payload"]["comments"][1].get("comment") == SECOND_COMMENT
    ]
    if len(matching) != 1:
        raise RuntimeError("Stand-in folder did not receive exactly one matching saved JSON")
    if matching[0]["name"] not in page.locator("#rv-status").inner_text():
        raise RuntimeError("Saved filename does not match the displayed status")


def write_outputs(recorder):
    duration = sum(recorder.durations)
    if not 32_000 <= duration <= 42_000:
        raise RuntimeError(f"Storyboard duration is outside 32–42 seconds: {duration} ms")
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    expected_names = set()
    for index, frame in enumerate(recorder.frames):
        filename = f"{index:02d}.png"
        expected_names.add(filename)
        frame.save(FRAME_DIR / filename)
    for path in FRAME_DIR.iterdir():
        if (path.is_file() and re.fullmatch(r"\d+\.png", path.name)
                and path.name not in expected_names):
            path.unlink()
    size = (OUTPUT_WIDTH, round(HEIGHT * OUTPUT_WIDTH / WIDTH))
    reduced = [frame.resize(size, Image.Resampling.LANCZOS) for frame in recorder.frames]
    for colors in (128, 96, 64):
        palettes = [
            frame.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                           dither=Image.Dither.NONE)
            for frame in reduced
        ]
        palettes[0].save(
            OUTPUT, save_all=True, append_images=palettes[1:],
            duration=recorder.durations, loop=0, optimize=True, disposal=2,
        )
        if OUTPUT.stat().st_size <= MAX_BYTES:
            break
    else:
        raise RuntimeError("GIF exceeds 8 MB even with 64-color frames")
    with Image.open(OUTPUT) as saved:
        if saved.size != size or saved.info.get("loop") != 0:
            raise RuntimeError("GIF dimensions or looping metadata are incorrect")
        stored_duration = 0
        for index in range(saved.n_frames):
            saved.seek(index)
            saved.load()
            stored_duration += saved.info.get("duration", 0)
        if stored_duration != duration:
            raise RuntimeError("Encoded GIF duration differs from the storyboard")
        encoded_frames = saved.n_frames
    print(f"Frames: {len(recorder.frames)} PNGs; {encoded_frames} GIF frames")
    print(f"Total duration: {duration / 1000:.2f} seconds")
    print(f"File size: {OUTPUT.stat().st_size:,} bytes")
    print(f"GIF: {OUTPUT}")
    print(f"Inspection frames: {FRAME_DIR}")


def prepare_page(page):
    page.set_default_timeout(10000)
    page.goto(URL, wait_until="load")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="load")
    page.evaluate("document.fonts.ready")
    expect(page.locator("#rv-count")).to_have_text("0")
    expect(page.locator("#rv-panel")).to_be_visible()
    expect(page.locator("#rv-folder")).not_to_have_text("")
    page.add_style_tag(content=PRESENTATION_CSS)
    page.locator("#s3-2 ~ p").first.scroll_into_view_if_needed()
    page.evaluate(
        """() => {
            const h = document.getElementById("s3-2");
            window.scrollTo(0, window.scrollY + h.getBoundingClientRect().top - 90);
        }"""
    )
    page.evaluate(CURSOR_JS)


def record_first_comment(recorder):
    page = recorder.page
    recorder.add(card([
        ("How to comment on an engineering report", 50),
        ("select text, Comment, Add, Save", 31),
    ]), 2500)
    recorder.capture(CAP_OPEN, 1500)
    select_sentence(recorder)
    recorder.capture(CAP_CLICK, 1000)
    recorder.click("#rv-btn", CAP_CLICK)
    expect(page.locator("#rv-text")).to_be_visible()
    expect(page.locator("#rv-text")).to_be_focused()
    recorder.capture(CAP_TYPE, 650)
    type_comment(recorder, COMMENT, CAP_TYPE)
    recorder.capture(CAP_TYPE, 1000)
    recorder.click("#rv-add", CAP_TYPE)
    expect(page.locator("#rv-count")).to_have_text("1")
    show_first_highlight(recorder)


def record_save_and_cards(recorder):
    page = recorder.page
    page.evaluate(SAVE_STUB_JS)
    recorder.capture(CAP_SAVE, 1400)
    recorder.click("#rv-save", CAP_SAVE)
    verify_private_save(page)
    recorder.capture(CAP_SAVE, 2300)
    recorder.add(ideas_card(), 5000)
    recorder.add(card([
        (
            "Comments are saved beside the report as a .json "
            "file and reloaded next time.", 35,
        ),
        (
            "Choose the folder that holds the report; any other "
            "folder is refused. If saving is not possible, use Copy "
            "and paste into your reply.", 29,
        ),
        ("Folder... changes where comments are saved", 29),
    ]), 3000)


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        try:
            # Fresh nonpersistent context isolates real comments and folder handles.
            context = browser.new_context(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=1, accept_downloads=False,
            )
            page = context.new_page()
            errors, downloads = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("download", lambda download: downloads.append(download.suggested_filename))
            prepare_page(page)
            recorder = Recorder(page)
            recorder.position_cursor(70, 100)
            record_first_comment(recorder)
            add_second_comment(recorder)
            edit_first_comment(recorder)
            record_save_and_cards(recorder)
            if downloads:
                raise RuntimeError(f"Unexpected download fallback: {downloads}")
            if errors:
                raise RuntimeError("Browser errors:\n" + "\n".join(errors))
        finally:
            browser.close()
    write_outputs(recorder)


if __name__ == "__main__":
    main()
