"""JSON for HTML script data (WHATWG HTML, parsing, script data states)."""
import json


def script_json(value, **kwargs):
    """Encode data without HTML-significant characters; decoded JSON is unchanged.

    RFC 8259 section 7 permits Unicode escapes. WHATWG script data end tag
    open/name states recognize a literal less-than sign even in JSON strings.
    Unicode separator escapes also permit use in older JavaScript consumers.
    This serializes data only, not JavaScript code or HTML attribute values.
    """
    kwargs['allow_nan'] = False
    text = json.dumps(value, **kwargs)
    for char, escaped in (('<', r'\u003c'), ('>', r'\u003e'), ('&', r'\u0026'),
                          ('\u2028', r'\u2028'), ('\u2029', r'\u2029')):
        text = text.replace(char, escaped)
    return text
