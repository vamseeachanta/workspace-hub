"""Offline structural checks; no browser interaction is exercised.

Expected payloads are independent literals from the format example documented
in html_review_layer.md. Byte expectations are literal concatenations, not
outputs computed by the injector.
"""

import copy
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from scripts.review import html_review_layer as layer


# Synthetic format example; version 1 is defined in html_review_layer.md.
EXAMPLE_JSON = '''{
  "schema_version": 1,
  "source_ref": "reports/example.html",
  "comments": [{
    "quote": "Design basis",
    "section": "basis",
    "source_ref": "reports/example.html",
    "comment": "Explain this assumption.",
    "timestamp": "2026-10-15T00:00:00Z"
  }]
}'''
EXAMPLE = {
    "schema_version": 1,
    "source_ref": "reports/example.html",
    "comments": [{
        "quote": "Design basis",
        "section": "basis",
        "source_ref": "reports/example.html",
        "comment": "Explain this assumption.",
        "timestamp": "2026-10-15T00:00:00Z",
    }],
}
SOURCE = (
    b'<!doctype html>\r\n<html><head><meta charset="utf-8"></head>'
    b'<body><section id="basis"><h1>Design basis</h1>'
    b'<p>Pressure &amp; temperature: \xce\x94.</p></section>\r\n</body></html>\r\n'
)


@pytest.fixture
def paths(tmp_path):
    source = tmp_path / "report.html"
    source.write_bytes(SOURCE)
    return source, tmp_path / "review.html"


def inject(paths, **kwargs):
    source, output = paths
    layer.inject(source, output, source_ref="reports/example.html", **kwargs)
    return output.read_bytes()


class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_source_bytes_unchanged(paths):
    rendered = inject(paths)
    assert paths[0].read_bytes() == SOURCE
    before, after = SOURCE.split(b"</body>")
    assert rendered.startswith(before)
    assert rendered.endswith(b"</body>" + after)


@pytest.mark.parametrize("alias", ["same", "relative", "symlink", "hardlink"])
def test_injector_refuses_same_destination(paths, alias):
    source, output = paths
    if alias == "same":
        output = source
    elif alias == "relative":
        output = source.parent / "." / source.name
    elif alias == "symlink":
        output.symlink_to(source)
    else:
        import os
        os.link(source, output)
    with pytest.raises(ValueError, match="alias"):
        layer.inject(source, output, source_ref="reports/example.html")
    assert source.read_bytes() == SOURCE


def test_existing_output_is_not_overwritten(paths):
    paths[1].write_bytes(b"existing review")
    with pytest.raises(FileExistsError):
        inject(paths)
    assert paths[1].read_bytes() == b"existing review"
    assert paths[0].read_bytes() == SOURCE


def test_comment_payload_roundtrip():
    assert layer.loads_payload(EXAMPLE_JSON) == EXAMPLE
    assert json.loads(layer.dumps_payload(EXAMPLE)) == EXAMPLE
    assert layer.loads_payload(layer.dumps_payload(EXAMPLE)) == EXAMPLE


@pytest.mark.parametrize("quote,section", [("Selected words", ""), ("", "basis")])
def test_quote_or_section_payload(quote, section):
    payload = copy.deepcopy(EXAMPLE)
    payload["comments"][0].update(quote=quote, section=section)
    assert layer.loads_payload(json.dumps(payload)) == payload


def test_json_integer_version_accepts_equivalent_number():
    # JSON has one number type: 1.0 and 1 denote the documented version.
    text = EXAMPLE_JSON.replace('"schema_version": 1,', '"schema_version": 1.0,')
    assert layer.loads_payload(text) == EXAMPLE


def malformed_payloads():
    yield None
    yield []
    yield {**EXAMPLE, "schema_version": True}
    yield {**EXAMPLE, "schema_version": "1"}
    yield {**EXAMPLE, "schema_version": 0}  # Not the documented version.
    yield {**EXAMPLE, "extra": "unknown"}
    yield {**EXAMPLE, "comments": {}}
    yield {**EXAMPLE, "comments": [None]}
    yield {**EXAMPLE, "source_ref": " "}
    for key in EXAMPLE:
        payload = copy.deepcopy(EXAMPLE)
        del payload[key]
        yield payload
    for key in EXAMPLE["comments"][0]:
        payload = copy.deepcopy(EXAMPLE)
        del payload["comments"][0][key]
        yield payload
    for changes in (
        {"quote": " ", "section": ""}, {"quote": None}, {"section": []},
        {"source_ref": "other.html"}, {"comment": "\t"}, {"comment": 1},
        {"extra": "unknown"}, {"timestamp": "2026-02-30T00:00:00Z"},
        {"timestamp": "2026-10-15"}, {"timestamp": "2026-10-15T00:00:00+00:00"},
        {"timestamp": "0000-01-01T00:00:00Z"},
    ):
        payload = copy.deepcopy(EXAMPLE)
        payload["comments"][0].update(changes)
        yield payload


@pytest.mark.parametrize("payload", list(malformed_payloads()))
def test_malformed_payload_refused_without_writes(paths, payload):
    with pytest.raises(ValueError):
        layer.loads_payload(json.dumps(payload))
    with pytest.raises(ValueError):
        layer.dumps_payload(payload)
    with pytest.raises(ValueError):
        inject(paths, payload=payload)
    assert paths[0].read_bytes() == SOURCE
    assert not paths[1].exists()


def test_bad_json_refused():
    with pytest.raises(ValueError):
        layer.loads_payload('{"comments":')


def test_payload_source_mismatch_refused(paths):
    payload = {**EXAMPLE, "source_ref": "other.html", "comments": []}
    with pytest.raises(ValueError, match="source"):
        inject(paths, payload=payload)
    assert paths[0].read_bytes() == SOURCE
    assert not paths[1].exists()


def test_injection_before_real_closing_body(paths):
    prefix = (
        b'<html><body><!-- </body> -->'
        b'<script>const sample = "</body>";</script>'
        b'<p title="</body>">text</p>'
    )
    suffix = b'</BoDy  ></html><!-- </body> -->'
    paths[0].write_bytes(prefix + suffix)
    rendered = inject(paths)
    assert rendered.startswith(prefix)
    assert rendered.endswith(suffix)
    assert rendered.index(b'id="hrl-root"') > len(prefix)


@pytest.mark.parametrize("tag", ["textarea", "title", "xmp", "iframe", "noembed", "noframes", "noscript"])
def test_body_lookalikes_in_text_elements(paths, tag):
    # WHATWG HTML text-element parsing: end-tag text is not a body end token.
    prefix = f'<html><body><{tag}>example </body></{tag}>'.encode()
    suffix = b'</body></html>'
    paths[0].write_bytes(prefix + suffix)
    rendered = inject(paths)
    assert rendered.startswith(prefix)
    assert rendered.endswith(suffix)


def test_body_lookalikes_in_templates(paths):
    prefix = b'<html><body><template><template></body></template></template>'
    suffix = b'</body></html>'
    paths[0].write_bytes(prefix + suffix)
    rendered = inject(paths)
    assert rendered.startswith(prefix)
    assert rendered.endswith(suffix)


@pytest.mark.parametrize("source", [
    b"<p>fragment</p>", b"<body></body></body>", b"\xff</body>",
    b"<body><plaintext>example</body>", b'<body><p id="hrl-custom">text</p></body>',
])
def test_unsupported_source_refused(paths, source):
    paths[0].write_bytes(source)
    with pytest.raises(ValueError):
        inject(paths)
    assert paths[0].read_bytes() == source
    assert not paths[1].exists()


def test_repeated_injection_is_refused(paths):
    rendered = inject(paths)
    output = paths[1].with_name("again.html")
    with pytest.raises(ValueError, match="already|reserved"):
        layer.inject(paths[1], output, source_ref="reports/example.html")
    assert paths[1].read_bytes() == rendered
    assert not output.exists()


@pytest.mark.parametrize("reference", ["", " \t", "\ufeff", "\x85", "\x1c", None])
def test_empty_source_reference_refused(paths, reference):
    with pytest.raises(ValueError):
        layer.inject(*paths, source_ref=reference)
    assert paths[0].read_bytes() == SOURCE
    assert not paths[1].exists()


def test_empty_comments_and_original_resource_references(paths):
    original = b'<html><head><script src="existing.js"></script></head><body></body></html>'
    paths[0].write_bytes(original)
    payload = {"schema_version": 1, "source_ref": "reports/example.html", "comments": []}
    rendered = inject(paths, payload=payload)
    assert paths[0].read_bytes() == original
    assert rendered.startswith(original.split(b"</body>")[0])
    assert layer.loads_payload(layer.dumps_payload(payload)) == payload


def test_embedded_payload_uses_safe_json(paths):
    payload = copy.deepcopy(EXAMPLE)
    hostile = '</script><img src="remote" onerror="alert()">&\u2028\u2029'
    payload["comments"][0]["comment"] = hostile
    rendered = inject(paths, payload=payload).decode()
    data = rendered.split('<script id="hrl-data" type="application/json">')[1].split('</script>')[0]
    assert json.loads(data)["payload"] == payload
    assert hostile not in rendered
    assert not any(tag == "img" for tag, attrs in Elements(rendered).tags)


def test_controls_inline_print_hidden_and_no_network_resources(paths):
    rendered = inject(paths).decode()
    added = rendered[len(SOURCE.split(b"</body>")[0].decode()):]
    tags = Elements(added).tags
    for tag, attrs in tags:
        assert tag not in {"link", "iframe", "img", "object", "embed", "base"}
        assert not ({"src", "href", "srcset", "action"} & attrs.keys())
        assert not any(name.startswith("on") for name in attrs)
    assert '@media print' in added
    assert '#hrl-root { display: none !important; }' in added
    for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "@import", "url("):
        assert forbidden not in added
    for required in ("getSelection", "localStorage", "JSON.parse", "JSON.stringify", "Blob", "textContent"):
        assert required in added
    assert "innerHTML" not in added
    assert {"hrl-comment", "hrl-section", "hrl-export", "hrl-import"} <= {
        attrs.get("id") for tag, attrs in tags
    }


def test_cli_copy_and_invalid_import(paths, tmp_path):
    fixture = tmp_path / "comments.json"
    fixture.write_text(EXAMPLE_JSON, encoding="utf-8", newline="\n")
    command = [sys.executable, str(ROOT / "scripts/review/html_review_layer.py"),
               str(paths[0]), str(paths[1]), "--source-ref", "reports/example.html",
               "--comments", str(fixture)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert paths[0].read_bytes() == SOURCE
    assert b'id="hrl-root"' in paths[1].read_bytes()
    fixture.write_text('{"unexpected":true}', encoding="utf-8", newline="\n")
    command[3] = str(tmp_path / "invalid.html")
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode != 0
    assert not (tmp_path / "invalid.html").exists()
    assert paths[0].read_bytes() == SOURCE


# The explicit blank set includes Python/ECMAScript whitespace and the BOM.
BLANK_CODEPOINTS = (
    *range(0x09, 0x0E), *range(0x1C, 0x21), 0x85, 0xA0, 0x1680,
    *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F, 0x205F, 0x3000, 0xFEFF,
)


def whitespace_vectors():
    for text, accepted in [
        ("", False),
        *((chr(codepoint), False) for codepoint in BLANK_CODEPOINTS),
        ("".join(map(chr, BLANK_CODEPOINTS)), False),
        ("\u200b", True), ("\u180e", True), ("\x00", True),
        ("\ufeffText\x85", True),
    ]:
        for field in ("source_ref", "comment", "quote", "section"):
            payload = copy.deepcopy(EXAMPLE)
            if field == "source_ref":
                payload["source_ref"] = text
                payload["comments"][0]["source_ref"] = text
            else:
                payload["comments"][0][field] = text
                if field in ("quote", "section"):
                    other = "section" if field == "quote" else "quote"
                    payload["comments"][0][other] = ""
            yield payload, accepted


@pytest.mark.parametrize("runtime", ["python", "javascript"])
def test_shared_whitespace_contract(runtime):
    vectors = list(whitespace_vectors())
    if runtime == "python":
        results = []
        for payload, _ in vectors:
            try:
                assert layer.loads_payload(layer.dumps_payload(payload)) == payload
            except ValueError:
                results.append(False)
            else:
                results.append(True)
    else:
        # Execute the shipped validator, without a browser or replacement logic.
        validator = "  const exactKeys" + layer._SCRIPT.split("  const exactKeys", 1)[1]
        validator = validator.split("  let payload =", 1)[0]
        program = validator + """
const fs = require("node:fs");
const vectors = JSON.parse(fs.readFileSync(0, "utf8"));
let source;
const results = vectors.map(value => {
  source = value.source_ref;
  try {
    return JSON.stringify(validate(value)) === JSON.stringify(value);
  } catch { return false; }
});
process.stdout.write(JSON.stringify(results));
"""
        result = subprocess.run(
            ["node", "-e", program], input=json.dumps([p for p, _ in vectors]),
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        results = json.loads(result.stdout)
    assert results == [accepted for _, accepted in vectors]
