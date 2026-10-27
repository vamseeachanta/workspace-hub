"""Add offline review controls to an explicit HTML copy; never edit the source.

Usage: python scripts/review/html_review_layer.py report.html review.html \
    --source-ref reports/example.html [--comments comments.json]

See html_review_layer.md for the portable format and trust/encoding limits.
Only the standard library is required. No producer integrations are installed.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.lib.script_json import script_json


# Version and timestamp precision are defined in html_review_layer.md, Format.
SCHEMA_VERSION = 1
_TIMESTAMP = re.compile(r"(?!0000)[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_PAYLOAD_KEYS = {"schema_version", "source_ref", "comments"}
_COMMENT_KEYS = {"quote", "section", "source_ref", "comment", "timestamp"}


def _substantive(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_payload(payload: object, source_ref: str | None = None) -> dict:
    """Validate the complete format before any state or output is changed."""
    if not isinstance(payload, dict) or payload.keys() != _PAYLOAD_KEYS:
        raise ValueError("invalid payload fields")
    version = payload["schema_version"]
    if isinstance(version, bool) or not isinstance(version, (int, float)) or version != SCHEMA_VERSION:
        raise ValueError("unsupported schema version")
    reference = payload["source_ref"]
    if not _substantive(reference) or (source_ref is not None and reference != source_ref):
        raise ValueError("invalid or mismatched source reference")
    if not isinstance(payload["comments"], list):
        raise ValueError("comments must be an array")
    for comment in payload["comments"]:
        if not isinstance(comment, dict) or comment.keys() != _COMMENT_KEYS:
            raise ValueError("invalid comment fields")
        if not all(isinstance(value, str) for value in comment.values()):
            raise ValueError("comment fields must be strings")
        if not (_substantive(comment["quote"]) or _substantive(comment["section"])):
            raise ValueError("a quote or section is required")
        if comment["source_ref"] != reference or not _substantive(comment["comment"]):
            raise ValueError("invalid comment or source reference")
        timestamp = comment["timestamp"]
        if not _TIMESTAMP.fullmatch(timestamp):
            raise ValueError("timestamp must be a UTC calendar time to seconds")
        try:
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as exc:
            raise ValueError("invalid calendar timestamp") from exc
    return payload


def loads_payload(text: str) -> dict:
    """Read exported JSON, refusing malformed records as a whole."""
    return validate_payload(json.loads(text))


def dumps_payload(payload: object) -> str:
    """Write portable JSON after complete validation; preserve string contents."""
    return json.dumps(validate_payload(payload), ensure_ascii=False, allow_nan=False) + "\n"


class _BodyEnd(HTMLParser):
    """Locate real end tags, ignoring lookalikes in comments and script text."""

    # WHATWG HTML text and scripting-enabled noscript parsing. Explicitly list
    # these for consistent behavior across supported Python parser versions.
    CDATA_CONTENT_ELEMENTS = ("script", "style", "textarea", "title", "xmp",
                              "iframe", "noembed", "noframes", "noscript")

    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.ends: list[int] = []
        self.reserved = False
        self.template_depth = 0
        self.lines = text.split("\n")
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == "template":
            self.template_depth += 1  # Nesting depth increases by one element.
        if tag == "plaintext":
            raise ValueError("plaintext elements are unsupported")
        if any(name == "id" and value and value.startswith("hrl-") for name, value in attrs):
            self.reserved = True

    def handle_endtag(self, tag):
        if tag == "template" and self.template_depth:
            self.template_depth -= 1
        if tag == "body" and not self.template_depth:
            line, column = self.getpos()
            # HTMLParser uses one-based lines and zero-based columns.
            self.ends.append(sum(len(value) + 1 for value in self.lines[:line - 1]) + column)


_CONTROLS = r'''
<style id="hrl-style">
/* Layout values are presentation choices, not engineering quantities. */
#hrl-root { position: fixed; inset: auto 1rem 1rem auto; z-index: 2147483647;
  width: min(28rem, 90vw); max-height: 70vh; overflow: auto; padding: 1rem;
  background: white; color: black; border: 1px solid currentColor;
  font: 1rem sans-serif; text-align: left; }
#hrl-root button, #hrl-root textarea, #hrl-root input { font: inherit; }
#hrl-root textarea { display: block; width: 100%; box-sizing: border-box; }
#hrl-root li { white-space: pre-wrap; overflow-wrap: anywhere; }
@media print {
  #hrl-root { display: none !important; }
}
</style>
<aside id="hrl-root" aria-label="Report review">
  <strong>Report review</strong>
  <p>Select text, or choose Select section and click a section.</p>
  <button id="hrl-section" type="button" aria-pressed="false">Select section</button>
  <button id="hrl-comment" type="button" disabled>Comment</button>
  <p id="hrl-target"></p>
  <form id="hrl-form" hidden>
    <label for="hrl-text">Requested edit</label>
    <textarea id="hrl-text" required></textarea>
    <button type="submit">Save comment</button>
    <button id="hrl-cancel" type="button">Cancel</button>
  </form>
  <button id="hrl-export" type="button">Export JSON</button>
  <label for="hrl-import">Import JSON (replaces comments)</label>
  <input id="hrl-import" type="file" accept="application/json,.json">
  <p id="hrl-status" role="status" aria-live="polite"></p>
  <ol id="hrl-comments"></ol>
</aside>
'''

_SCRIPT = r'''
<script id="hrl-script">
(() => {
  "use strict";
  const embedded = JSON.parse(document.getElementById("hrl-data").textContent);
  const root = document.getElementById("hrl-root");
  const control = name => document.getElementById("hrl-" + name);
  const status = message => { control("status").textContent = message; };
  const source = embedded.payload.source_ref;
  const exactKeys = (value, keys) => value !== null && typeof value === "object" &&
    !Array.isArray(value) && Object.keys(value).sort().join(",") === keys.sort().join(",");
  // Mirrors html_review_layer.md, Format: all fields required; no unknown keys.
  function validate(value) {
    if (!exactKeys(value, ["schema_version", "source_ref", "comments"]) ||
        value.schema_version !== 1 || value.source_ref !== source ||
        typeof value.source_ref !== "string" || !value.source_ref.trim() ||
        !Array.isArray(value.comments)) throw Error("Invalid review payload or source reference.");
    for (const item of value.comments) {
      if (!exactKeys(item, ["quote", "section", "source_ref", "comment", "timestamp"]) ||
          !Object.values(item).every(field => typeof field === "string") ||
          !(item.quote.trim() || item.section.trim()) || !item.comment.trim() ||
          item.source_ref !== source ||
          !/^(?!0000)[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/.test(item.timestamp)) {
        throw Error("Invalid comment record.");
      }
      const time = new Date(item.timestamp);
      if (!Number.isFinite(time.getTime()) ||
          time.toISOString().replace(".000Z", "Z") !== item.timestamp) {
        throw Error("Invalid calendar timestamp.");
      }
    }
    return value;
  }
  let payload = validate(embedded.payload);
  let target = null;
  let choosingSection = false;
  let editingTarget = null;
  function render() {
    control("comments").replaceChildren();
    for (const item of payload.comments) {
      const row = document.createElement("li");
      row.textContent = [item.section, item.quote, item.comment, item.timestamp].filter(Boolean).join("\n");
      control("comments").appendChild(row);
    }
  }
  function persist() {
    try {
      localStorage.setItem(embedded.storage_key, JSON.stringify(payload));
      status("Comments saved locally. Export JSON to share them.");
    } catch {
      status("Local storage unavailable. Export JSON to retain comments.");
    }
  }
  try {
    const saved = localStorage.getItem(embedded.storage_key);
    if (saved !== null) payload = validate(JSON.parse(saved));
  } catch {
    status("Stored comments unavailable or invalid; embedded comments retained.");
  }
  render();
  function sectionFor(element) {
    const section = element.closest("section, article, main, [id]") || document.body;
    const heading = section.querySelector("h1, h2, h3, h4, h5, h6");
    return section.id || (heading && heading.textContent.trim()) || document.title || "Document";
  }
  function select(value) {
    target = value;
    control("comment").disabled = !target;
    control("target").textContent = target ? (target.quote || target.section) : "";
  }
  function captureSelection() {
    if (root.contains(document.activeElement) || choosingSection) return;
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    const range = selection.getRangeAt(0); // Selection API: first range index.
    if (root.contains(range.startContainer) || root.contains(range.endContainer) ||
        range.intersectsNode(root)) return;
    const element = range.startContainer.nodeType === Node.ELEMENT_NODE ?
      range.startContainer : range.startContainer.parentElement;
    if (element && selection.toString().trim()) {
      select({quote: selection.toString(), section: sectionFor(element)});
    }
  }
  document.addEventListener("mouseup", captureSelection);
  document.addEventListener("keyup", captureSelection);
  control("section").addEventListener("click", () => {
    choosingSection = !choosingSection;
    control("section").setAttribute("aria-pressed", String(choosingSection));
    status(choosingSection ? "Click a report section." : "Section selection cancelled.");
  });
  document.addEventListener("click", event => {
    if (!choosingSection || root.contains(event.target)) return;
    event.preventDefault();
    event.stopPropagation();
    select({quote: "", section: sectionFor(event.target)});
    choosingSection = false;
    control("section").setAttribute("aria-pressed", "false");
    status("Section selected. Choose Comment to request an edit.");
  }, true);
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      choosingSection = false;
      control("section").setAttribute("aria-pressed", "false");
    }
  });
  control("comment").addEventListener("click", () => {
    if (!target) return;
    editingTarget = {...target};
    control("form").hidden = false;
    control("text").focus();
  });
  control("cancel").addEventListener("click", () => {
    control("form").hidden = true;
    editingTarget = null;
  });
  control("form").addEventListener("submit", event => {
    event.preventDefault();
    const comment = control("text").value;
    if (!editingTarget || !comment.trim()) return;
    // Format uses UTC seconds; Date supplies milliseconds which are removed.
    const timestamp = new Date().toISOString().replace(/\.[0-9]{3}Z$/, "Z");
    const next = {...payload, comments: [...payload.comments,
      {...editingTarget, source_ref: source, comment, timestamp}]};
    try { payload = validate(next); } catch (error) { status(error.message); return; }
    control("text").value = "";
    control("form").hidden = true;
    editingTarget = null;
    render();
    persist();
  });
  control("export").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(validate(payload)) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "review-comments.json";
    link.click();
    URL.revokeObjectURL(url);
  });
  control("import").addEventListener("change", async event => {
    const [file] = event.target.files;
    if (!file) return;
    try {
      const imported = validate(JSON.parse(await file.text()));
      payload = imported;
      render();
      persist();
    } catch {
      status("Import refused: invalid JSON, schema, or source reference. Comments retained.");
    } finally {
      event.target.value = "";
    }
  });
})();
</script>
'''


_UNSET = object()


def inject(source: Path, output: Path, *, source_ref: str, payload: object = _UNSET) -> None:
    """Create a new copy with controls immediately before the real body end.

    Refuse aliases, existing output, reserved IDs, unsupported HTML and invalid
    payloads. Source bytes outside the insertion are copied without re-encoding.
    """
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or (output.exists() and source.samefile(output)):
        raise ValueError("source and output alias each other")
    if not _substantive(source_ref):
        raise ValueError("source reference is required")
    if payload is _UNSET:
        payload = {"schema_version": SCHEMA_VERSION, "source_ref": source_ref, "comments": []}
    validate_payload(payload, source_ref)
    original = source.read_bytes()
    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("source must be UTF-8 HTML") from exc
    parsed = _BodyEnd(text)
    if parsed.reserved:
        raise ValueError("review layer already present or reserved hrl- ID in source")
    if len(parsed.ends) != 1:  # Format requires exactly one real closing body.
        raise ValueError("source must contain exactly one closing body tag")
    offset = len(text[:parsed.ends[0]].encode("utf-8"))
    digest = hashlib.sha256(original).hexdigest()
    data = {"payload": payload, "storage_key": "html-review:" + digest + ":" + source_ref}
    markup = _CONTROLS + '<script id="hrl-data" type="application/json">' + script_json(data) + '</script>\n' + _SCRIPT
    result = original[:offset] + markup.encode("utf-8") + original[offset:]
    # Exclusive creation also refuses symlinks and races with another writer.
    with output.open("xb") as destination:
        destination.write(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-ref", required=True, help="portable source reference, never inferred from a local path")
    parser.add_argument("--comments", type=Path, help="validated exported JSON to embed")
    args = parser.parse_args(argv)
    try:
        payload = loads_payload(args.comments.read_text(encoding="utf-8")) if args.comments else _UNSET
        inject(args.source, args.output, source_ref=args.source_ref, payload=payload)
    except (OSError, ValueError) as exc:
        # Do not echo local file names or imported values in diagnostics.
        parser.exit(1, f"Review copy refused ({type(exc).__name__}); check inputs and destination.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
