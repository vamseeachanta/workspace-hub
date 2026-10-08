# HTML review: select-to-comment layer for reports and decision boards

Tracking issue: [3920](https://github.com/vamseeachanta/workspace-hub/issues/3920). The layer lets a reviewer comment directly on any local HTML report or decision board. The comments come back as a JSON file that an agent picks up and applies.

## Use

```bash
python tools/html-review/make_review_copy.py SRC.html OUT-review.html STORAGE_KEY EXPORT_NAME
```

- `SRC.html` is left unchanged. `OUT-review.html` is the same page with the review layer injected. A page without `<body>`, such as an artifact-style page, is wrapped automatically.
- `STORAGE_KEY` names the browser storage slot. Bump it per review round, e.g. `…-v2`.
- `EXPORT_NAME` is the saved file name without `.json`, e.g. `report-comments-r2`.

## What the reviewer does

1. Open the review copy in **Edge or Chrome**, from disk. E-mail, Teams and SharePoint previews block scripts; a `<noscript>` note says so.
2. Select text, click **Comment**, type the edit, then **Add**. The passage is highlighted, and hovering shows the comment.
3. Edit any comment in the list at any time; changes are kept automatically.
4. **Save comments**:
   - The JSON is always written beside the page, in the folder that holds it, never to Downloads.
   - The first save asks once for a folder. Choose the folder that holds the review page. The page checks that the folder contains the page itself (same file name and revision) and refuses any other folder.
   - Later saves write `EXPORT_NAME.json` there directly, merging comments already in that file. The folder is remembered per page location, so copies of the page in different folders each save beside themselves.
   - On opening, if the browser still has write permission for that folder, comments saved beside the page are loaded and merged.
   - **Folder…** changes the folder (with the same check).
   - If the folder cannot be written (no File System Access API, permission refused, dialog cancelled, wrong folder), nothing is saved. The comments stay in the tab and in browser storage, and the status line says why.
   - **Copy** puts the JSON on the clipboard for an e-mail reply.
5. **Voice**: on Windows 10 or 11, click in a comment box and press **Windows key + H** to dictate.

Each saved file records:
- `page`, `report_version` (source SHA-256 prefix and modification time), `report_folder` and `exported_at`;
- for every comment: `quote`, `section` (nearest heading), `data_src` (for traced values), `comment` and `at`.

Comments also carry a stable `id`, and `edited_at` once edited here; `deleted_ids` retains deletion records. Save, Load and folder merge all merge rather than replace:
- A comment already present here keeps its local text; an incoming copy with the same `id` is ignored. No time comparison is made.
- Deletion records are combined, and deleted comments are not restored.
- An imported deletion record does not remove a comment edited here (`edited_at` set in this browser's own record). The edit is kept and the status line reports how many were kept; delete it here if the deletion is intended. `edited_at` arriving in an imported file is ignored, so an edit made elsewhere gains no protection.

Comments stored in this browser for other revisions are announced on open but not merged. A review copy generated from that revision can Save or Copy them. If stored comments for this revision cannot be read, the unreadable record is copied to `KEY|revision|unreadable` before anything overwrites it; if that copy fails, browser storage for the revision is left unchanged for the session and the status line asks for Save or Copy. If the folder's `EXPORT_NAME.json` belongs to another revision or cannot be read or merged, Save leaves it unchanged and writes `EXPORT_NAME-<revision>.json` (the first 12 characters of the source SHA-256) in the same folder, merging that file if it exists; the status line names the file. If that file cannot be merged either, nothing is saved. Save, Load and folder merge require the same page and report revision. Browser storage is kept per revision (`KEY|revision`); the bare `KEY` entry (a legacy array or another revision's record) is read once, adopted only if it matches this revision, and never overwritten. Legacy exported files with matching revision metadata are accepted.

## Ideas for comments (shown in the GIFs)

- Reword: "Replace with: …"
- Structure: "Convert to sub-bullets", "Make this a table", "Merge with 4.1"
- Values: "Should be 6.50 m, see drawing rev B"
- Scope: "Delete, not needed", "Move to Appendix"
- Add: "Add a note on …"
- Question: "Why is C4 lower than C3?"
- Confirm: "Agreed, no change"

## Tutorial GIFs (generic; safe to send to any client)

| File | Content |
|---|---|
| `demo/how-to-comment.gif` | Select, Comment, type, Add; a second comment asking for sub-bullets; editing a comment; the ideas card; Save (about 36 s) |
| `demo/how-to-comment-voice.gif` | The same flow using Windows voice typing (Win+H); the toolbar is an illustration (about 39 s) |

Both GIFs are recorded against `demo/example-report.html`, a sample report with illustrative values. They contain no client content.

Regenerate:

```bash
python tools/html-review/make_review_copy.py tools/html-review/demo/example-report.html tools/html-review/demo/example-report-review.html example-report-comments-v1 example-report-comments
python tools/html-review/demo/make_comment_gif.py
python tools/html-review/demo/make_voice_gif.py
```

Requirements:
- Python with `playwright`, `Pillow` and `imageio`, and Microsoft Edge installed. Playwright drives `channel="msedge"`; no Playwright browser download is needed.
- The scripts write frames to `demo/gif-frames*/`, which git ignores, for inspection.
- The native folder dialog and the real Windows voice toolbar cannot be recorded headless. The scripts stub the folder with an in-memory handle and draw a neutral "listening" overlay, labelled as an illustration.

## Test

Offline integrity regressions require Python and Node:

```bash
python -m unittest discover -s tools/html-review/tests -p test_integrity.py -v
```

These tests cover revision rejection, edit/deletion preservation (including an imported deletion of a locally edited comment), unreadable-storage preservation, the revision-suffixed sibling for a mismatched or malformed folder export, refusal of a folder without the page, no write when permission is refused or the API is missing, loading on open, absence of any download code in the layer, imported-text escaping, parameter encoding, source overwrite rejection, and that the committed demo review copy matches the current generator with no absolute folder path.

```bash
python -m pytest tools/html-review/tests -q
```

The browser tests are skipped when Playwright or Edge is missing. They serve the review page from a local `http.server` on 127.0.0.1, because the origin-private file system used to stand in for the folder dialog is unavailable on `file://` pages, and fail on any download event. They cover:
- select, Comment, Add and highlight, and editing a comment in the list;
- Save beside the page, the saved JSON fields, and reloading them on open with browser storage cleared;
- refusal of a folder that does not hold the page;
- no save and no download without the File System Access API;
- an other-revision export left unchanged, with comments written to the revision-suffixed sibling.

## Provenance and known limits

- The GIF recording scripts were drafted by Codex from a written brief, then run, debugged and frame-checked by the preparing Claude session (2026-09-29).
- Browsers cannot write beside a page silently. The first Save always asks for a folder, and later sessions may ask again for permission. There is no download fallback: when the folder cannot be written, the comments stay in the tab until Save succeeds or Copy is used.
- The native folder dialog and permission prompt are not exercised by the tests; they are stubbed.
- The highlight marks the first 80 characters of a quote.
