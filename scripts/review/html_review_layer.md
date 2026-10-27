# HTML review copy

The standalone injector creates a new review copy of trusted UTF-8 HTML. It
preserves the input file and copies its bytes around one insertion immediately
before the real closing body tag. No existing report producer is changed.

```sh
python scripts/review/html_review_layer.py report.html review.html \
  --source-ref reports/example.html
python scripts/review/html_review_layer.py report.html review-with-comments.html \
  --source-ref reports/example.html --comments review-comments.json
```

Use an explicit portable reference suitable for export. It is never inferred
from an absolute file name. Output must be a new path; aliases (including hard
links and symlinks), existing destinations, missing or multiple closing body
tags, and reserved `hrl-` element IDs are refused. Reinject from the original
source into a new destination to start another copy.

Select text and click **Comment**, or choose **Select section**, click a section
and click **Comment**. A section reference is its closest section, article, main
or identified ancestor's ID, then its first heading, then the document title or
the label `Document`. Section references are descriptive hints, not stable DOM
locators. Saving adds a comment and attempts local storage. **Export JSON** saves
portable comments; **Import JSON** validates the entire file before replacing
comments and requires an exact source-reference match. Invalid imports retain
the existing comments. Local storage is keyed by source-byte digest and source
reference; if it is unavailable, export remains the persistence route.

## Format

Version `1` is defined here. The following independent synthetic example is also
the literal fixture for the Python round-trip tests:

```json
{
  "schema_version": 1,
  "source_ref": "reports/example.html",
  "comments": [{
    "quote": "Design basis",
    "section": "basis",
    "source_ref": "reports/example.html",
    "comment": "Explain this assumption.",
    "timestamp": "2026-10-15T00:00:00Z"
  }]
}
```

All shown keys are required; additional keys are refused. The root is an object,
`schema_version` is the JSON number `1` (equivalently `1.0`, never a boolean),
`source_ref` is a nonblank string and
`comments` is an array (possibly empty). Every record is an object whose fields
are strings. `quote` or `section` must be nonblank; either may be empty when the
other is supplied. `comment` must be nonblank. Each record's `source_ref` must
equal the root reference. String contents are preserved, including whitespace.
Timestamps are valid calendar times in the exact UTC form
`YYYY-MM-DDTHH:MM:SSZ`, using years `0001` through `9999`, whole seconds and no
leap seconds. These choices define the format, rather than engineering values.
JSON object names should be unique; the standard JSON parsers retain the last
value when names repeat. Python `loads_payload`, `dumps_payload` and
`validate_payload` expose the same data contract used by the inline controls.

## Limits and verification

Only the injected layer is self-contained: inline CSS, script and data, with no
network requests or external resources. Existing HTML content, scripts and
resource references remain intact. This is not a sanitizer or sandbox; use only
trusted source HTML. Imported text is rendered through `textContent`; embedded
data uses the existing `script_json` serializer. The controls are hidden by
inline print CSS.

The copy requires a browser allowing inline JavaScript. Restrictive content
security policies, unusual markup or CSS, browser file-origin storage policies,
download handling, selection and actual print rendering are not verified.
Source files declaring a different character encoding and obsolete `plaintext`
elements are unsupported. This uses a conservative token parser, not a complete
HTML tree builder; malformed documents and foreign-content parsing are outside
the supported contract. Imports
match the source reference but do not authenticate a revision or author; check
the quoted context before applying an edit. There is no automatic pickup,
cross-repository rollout, producer integration or publication operation.

Focused checks are synthetic, offline Python checks of byte preservation,
alias refusal, insertion structure, payload validation and round trips,
script-data escaping, print rules, CLI behavior and absence of added resource
references. They do not execute the inline JavaScript or test browser behavior.
