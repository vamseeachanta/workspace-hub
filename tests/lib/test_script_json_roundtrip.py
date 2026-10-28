"""Synthetic script-data vectors with independent JSON and HTML oracles.

Basis: RFC 8259 sections 6 and 7 (finite numbers and escaped strings),
WHATWG HTML parsing, script data end tag open/name states (case-insensitive
closing tags), and Unicode Character Database names for separator characters.
The expected document events are enumerated by hand from the literal template;
expected payloads are literal input objects, never serializer-produced fixtures.
"""

import json
from html.parser import HTMLParser
from unicodedata import lookup

import pytest

from lib.script_json import script_json


class DocumentProbe(HTMLParser):
    """Record document order, including text relative to script boundaries."""

    def __init__(self):
        super().__init__()
        self.events = []

    def handle_starttag(self, tag, attrs):
        self.events.append(("start", tag, attrs))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))

    def handle_data(self, data):
        self.events.append(("text", data))


def parse_document(encoded):
    document = DocumentProbe()
    document.feed(
        '<html><body><script type="application/json" id="payload">'
        + encoded
        + '</script><p id="sentinel">Still visible</p></body></html>'
    )
    document.close()
    return document.events


def assert_document_intact(encoded):
    # Hand enumeration: the only script ends before the trailing paragraph.
    assert parse_document(encoded) == [
        ("start", "html", []),
        ("start", "body", []),
        ("start", "script", [("type", "application/json"), ("id", "payload")]),
        ("text", encoded),
        ("end", "script"),
        ("start", "p", [("id", "sentinel")]),
        ("text", "Still visible"),
        ("end", "p"),
        ("end", "body"),
        ("end", "html"),
    ]


@pytest.fixture
def nested_payload():
    # Construct Unicode separators at runtime from their UCD character names.
    separators = lookup("LINE SEPARATOR") + lookup("PARAGRAPH SEPARATOR")
    return {
        "nested": [
            {"closing_tags": [
                '</script><span id="breakout">injected</span>',
                '</ScRiPt><script id="extra">injected</script>',
                '</SCRIPT><img src="synthetic">',
            ]},
            {"punctuation": '< > & "quoted" \'single\' \\ backslash',
             "unicode": "café " + separators},
            [True, False, None, [], {}],
        ],
        '</sCrIpT><b id="key-breakout">': {separators: "key preserved"},
    }


@pytest.mark.parametrize("ensure_ascii", [True, False])
def test_script_data_cannot_create_html_elements(nested_payload, ensure_ascii):
    encoded = script_json(nested_payload, ensure_ascii=ensure_ascii)

    assert_document_intact(encoded)
    for character in ("<", ">", "&", lookup("LINE SEPARATOR"),
                      lookup("PARAGRAPH SEPARATOR")):
        assert character not in encoded


def test_document_probe_detects_unescaped_breakout():
    # Literal unsafe JSON is a positive control for the HTML parsing oracle.
    unsafe = """{"text":"</sCrIpT><span id='breakout'>injected</span>"}"""
    assert json.loads(unsafe) == {
        "text": "</sCrIpT><span id='breakout'>injected</span>"
    }
    assert ("start", "span", [("id", "breakout")]) in parse_document(unsafe)


@pytest.mark.parametrize("ensure_ascii", [True, False])
def test_script_json_nested_roundtrip(nested_payload, ensure_ascii):
    encoded = script_json(nested_payload, ensure_ascii=ensure_ascii)
    events = parse_document(encoded)
    assert_document_intact(encoded)
    script_text, sentinel_text = [
        event_text for kind, *details in events if kind == "text"
        for event_text in details
    ]

    assert json.loads(script_text) == nested_payload
    assert sentinel_text == "Still visible"
    if ensure_ascii:
        assert encoded.isascii()
    else:
        assert "café" in encoded


@pytest.mark.parametrize("ensure_ascii", [True, False])
@pytest.mark.parametrize("options", [{}, {"allow_nan": False}, {"allow_nan": True}],
                         ids=["default", "strict-request", "permissive-request"])
@pytest.mark.parametrize("nonfinite", [float("nan"), float("inf"), float("-inf")],
                         ids=["nan", "positive-infinity", "negative-infinity"])
def test_script_json_rejects_nonfinite(nonfinite, options, ensure_ascii):
    # RFC 8259 section 6 excludes NaN and both infinities from JSON numbers.
    with pytest.raises(ValueError):
        script_json({"nested": [{"value": nonfinite}]},
                    ensure_ascii=ensure_ascii, **options)
