# Engineering calculation source-gate TDD

Use this reference when executing approved engineering-calculation issues that depend on standards, licensed workbooks, off-repo corpora, or citation sidecars.

## Durable lesson

Do not let implementation pass by only removing old placeholder names or adding report-label checks. A source-gated calculation must prove that the actual numerical path uses the approved source route and fails closed when that route is unavailable.

## Required TDD pattern

1. Start with a RED test that fails against the current placeholder/simplified formula path.
   - Bad: only assert `OLD_CONSTANT_NAME` is absent from source.
   - Good: assert calculation calls a source adapter / resolver and raises a source/citation error when the workbook/cache/citation registry is missing.
2. Add an independent oracle before production code uses it.
   - Prefer hand calculation, issue-thread artifact, locked review fixture, or source-derived value captured outside the production path.
   - Do not compute expected values by calling the same production function under test.
3. Test the numerical path, not just the report text.
   - Assert selected coefficient IDs/families, units, sign convention, reference area/length, and at least one representative force/moment value.
   - Include a negative test that would fail if a trigonometric placeholder or constant fallback is silently used.
4. Test license boundaries separately.
   - Repo-bound artifacts may contain pointer/provenance/citation metadata and issue-specific outputs.
   - They must not serialize a reusable licensed coefficient corpus unless explicit license approval exists.
5. Keep report presentation tests as secondary checks.
   - Report terms, headings, DOCX/PDF text extraction, SVG metadata, and chart labels verify packaging.
   - They do not prove calculation correctness by themselves.

## Review checklist

Before leaving implementation for validation/review, ask:

- Would tests fail if the approved workbook/off-repo source were replaced by an inline simplified formula?
- Would tests fail if the citation sidecar or code_id resolution were missing?
- Is at least one default-case sample checked with an independent oracle?
- Are sign/unit/reference-area/reference-length assumptions asserted at the data/model boundary?
- Are licensed raw workbooks/PDFs and reusable extracted corpora kept out of tracked outputs?

If any answer is no, stay in the TDD loop. Do not proceed to closeout on string-removal or presentation-only tests.
