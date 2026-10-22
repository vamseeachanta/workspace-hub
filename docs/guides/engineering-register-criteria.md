# Sentence-scoped criteria in the engineering register checker

The engineering register checker accepts a governing criterion before or after
an unsupported adjective (R3) or a negated intensifier (R5) in the same sentence.
A bare claim still produces a finding. This corrects the clause-order defect
described in issue #3835 (2026).

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Explain sentence-scoped criteria and a worked example so clause order does not conceal a supplied reason. |

## Method and scope

The checker first blanks code, quotations, link targets and other excluded
regions while preserving character offsets. It separates the remaining prose
at full stops, question marks, exclamation marks and blank paragraphs. Dots
between digits in reference numbers and decimal values stay within the sentence,
as does a soft line wrap.

Each resulting span receives one shared criterion-vocabulary test. When a
criterion is present, both R3 and R5 accept claims within that span, regardless
of clause order. Otherwise, their candidate patterns report bare claims at the
original line numbers. Their existing following-clause explanation forms still
apply: R3 accepts immediate explanatory punctuation or conjunctions; R5 accepts
a following colon or long dash within the sentence.

The criterion vocabulary is unchanged: named comparisons, references and reason
markers such as `against`, `per`, `criterion`, `because` and `since`. Matching
starts at word boundaries so `Table` inside `acceptable` cannot qualify the
claim itself. The previous character windows no longer limit the distance between
a claim and its criterion
within a sentence. A criterion in either adjacent sentence does not qualify a
bare claim.

No engineering equation, coefficient or numerical acceptance limit is involved.
The source for the behavior is issue #3835, acceptance criteria and minimal pairs
(2026), together with the existing criterion and explanation forms in
[the checker](../../scripts/enforcement/check-engineering-register.py).
The governing prose rule is recorded in
[the engineering register](../../.claude/rules/engineering-register.md).

## Worked example

Save these four input lines as `example.md`:

```text
Because the agent no longer reads FETCH_HEAD, manual pulls are safe.
Since the mill certificate is absent, the grade is not obviously correct.
Manual pulls are safe now.
The grade is not obviously correct.
```

Run:

```sh
uv run --no-project python scripts/enforcement/check-engineering-register.py example.md
```

Hand classification gives the answer independently of the implementation:

| Input line | Method | Expected finding |
| --- | --- | --- |
| First | `Because` supplies the same-sentence reason before the claim. | None |
| Second | `Since` supplies the same-sentence reason before the hedge. | None |
| Third | No criterion accompanies the adjective. | R3 |
| Fourth | No criterion accompanies the hedge. | R5 |

The command returns exit status `1` and reports findings on lines `3` and `4`,
followed by `1 file(s) checked, 2 violation(s)`. These counts are the sum of the
hand classifications in the table. Moving either supplied reason after its
claim leaves that line free of findings. Moving it into a separate sentence
leaves the claim bare and produces its finding.

The example is exercised through the command entry point in
[the regression tests](../../tests/enforcement/test_check_engineering_register.py).
The tests also cover both clause orders, both adjacent-sentence directions,
soft wraps, blank paragraphs, excluded inline code, long sentences, existing
explanation forms and original finding locations.

## Known limits

Sentence detection is a punctuation heuristic. Abbreviation full stops still
split spans; Markdown list items without punctuation or blank lines can share a
span. The vocabulary test recognises supplied wording, not whether a reason is
technically valid or actually governs every claim in a compound sentence.
These limits require reading the prose; the checker does not establish
engineering acceptance. Locale-independent self-test fixture writing is tracked
separately in issue #3834 and is outside this change.
