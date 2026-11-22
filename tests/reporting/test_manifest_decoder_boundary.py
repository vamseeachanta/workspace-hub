"""Manifest decoder failures must not retain untrusted input.

Python json.loads documents JSONDecodeError for invalid JSON and
UnicodeDecodeError for unsupported byte encodings:
https://docs.python.org/3/library/json.html#json.loads
JSONDecodeError.doc retains the input document. Resource error meanings:
https://docs.python.org/3/library/exceptions.html#RecursionError
https://docs.python.org/3/library/exceptions.html#OverflowError
https://docs.python.org/3/library/exceptions.html#MemoryError
Resource failures are injected; no allocation or arithmetic exhaustion is used.
"""

import traceback

import pytest
import report_provenance
from report_provenance import ProvenanceError, load_manifest


SENTINEL = "untrusted-decoder-sentinel"
PUBLIC_ERROR = "invalid or ambiguous JSON manifest"


@pytest.fixture
def deep_manifest():
    # Test-design budget, not a production acceptance limit: 2,048 arrays.
    # Grammar: '[' repeated depth times, 'null', then depth closing ']'.
    # Hand calculation: 2 * 2,048 delimiter bytes + 4 literal bytes = 4,100.
    depth = 2048
    byte_budget = 4100
    raw = b"[" * depth + b"null" + b"]" * depth
    assert len(raw) == depth * (len(b"[") + len(b"]")) + len(b"null")
    assert len(raw) <= byte_budget
    return raw


def assert_public_error(error):
    assert type(error) is ProvenanceError
    assert str(error) == PUBLIC_ERROR
    assert error.__cause__ is None
    assert error.__context__ is None
    assert SENTINEL not in "".join(traceback.format_exception(error))


@pytest.mark.parametrize("error_type", [RecursionError, OverflowError, MemoryError])
def test_decoder_resource_errors_are_provenance_errors(monkeypatch, error_type, deep_manifest):
    def fail_decode(raw, **kwargs):
        assert raw == deep_manifest
        raise error_type(SENTINEL)

    monkeypatch.setattr(report_provenance.json, "loads", fail_decode)
    with pytest.raises(ProvenanceError) as caught:
        load_manifest(deep_manifest)
    assert_public_error(caught.value)


@pytest.mark.parametrize("raw", [
    b'{"value": "untrusted-decoder-sentinel",',
    # UTF-8 permits no FF octet (RFC 3629, section 4).
    b'{"value": "untrusted-decoder-sentinel\xff"}',
    b'{"value": "untrusted-decoder-sentinel", "value": null}',
    b'{"untrusted-decoder-sentinel": NaN}',
    b'{"untrusted-decoder-sentinel": Infinity}',
    b'{"untrusted-decoder-sentinel": -Infinity}',
], ids=["syntax", "utf8", "duplicate", "nan", "infinity", "negative-infinity"])
def test_manifest_decode_error_retains_no_input(raw):
    with pytest.raises(ProvenanceError) as caught:
        load_manifest(raw)
    assert_public_error(caught.value)


def test_bounded_deep_nesting(deep_manifest):
    # JSON permits no trailing '!': expect syntax or depth rejection, depending
    # on decoder capacity. Do not depend on a runtime-specific nesting threshold.
    # The malformed fixture adds one literal byte to the budget: 4,101 bytes.
    with pytest.raises(ProvenanceError) as caught:
        load_manifest(deep_manifest + b"!")
    assert_public_error(caught.value)


@pytest.mark.parametrize("input_type", [str, bytes, bytearray])
def test_valid_manifest_unchanged(input_type):
    # Independent literal oracle: json's conversion table maps objects to dicts,
    # arrays to lists, true/false/null to True/False/None. The decimal 1.25 is
    # exactly 5/4; the integer is a literal with no derived numeric threshold.
    # https://docs.python.org/3/library/json.html#json.JSONDecoder
    raw = (
        '{"schema":"report-provenance-v1","report_id":"example",'
        '"revision":"initial","repository_url":"https://example.org/reference",'
        '"sources":[],"prerequisites":[],"values":[true,false,null,1.25,'
        '12345678901234567890],"text":"\\u03bb"}'
    )
    expected = {
        "schema": "report-provenance-v1", "report_id": "example",
        "revision": "initial", "repository_url": "https://example.org/reference",
        "sources": [], "prerequisites": [],
        "values": [True, False, None, 1.25, 12345678901234567890], "text": "λ",
    }
    value = raw if input_type is str else input_type(raw.encode())
    assert load_manifest(value) == expected
