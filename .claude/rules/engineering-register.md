# Engineering Register — Universal

Every repository in this ecosystem is engineering. One register applies to all
output: issued reports, wiki pages, commit messages, chat replies, email, and the
text one agent writes for another.

The register was **derived, not prescribed** — recovered by reading the reports
this practice and its peers have issued, including a reviewer-commented draft
whose 31 comments show what a checker actually changed before issue. Full guide
with a quoted exemplar per rule: `llm-wiki`
`wikis/engineering/wiki/concepts/engineering-report-house-style.md`.

Canonical statement for agents: `config/agents/SHARED_SOUL.md`, section
"Engineering register". All five provider runtimes are built from it.

## Governing rules

- The subject is the analysis, result, component, document or company — not a
  person. First-person plural belongs to proposals and qualifications.
- Bind every conclusion to its criterion, comparator and governing case.
- State plainly when something is not established: name the missing evidence, say
  what cannot be calculated, mark the affected result approximate, and condition
  acceptance on obtaining the evidence. A generic disclaimer is not a limitation.
- `should` and `is recommended` carry advice. `shall` and `must` denote
  requirements, not emphasis.
- `-`, `n/a`, `TBD`, `Not Evaluated` and a true zero mean different things.
- Never write `acceptable`, `conservative` or `safe` without the criterion that
  makes it so.
- Tense: report-present passive for method, past for completed events, simple
  present for findings.
- Captions below tables and figures. Units in the header. Three decimals for
  thickness and corrosion allowance.

## Enforcement

`scripts/enforcement/check-engineering-register.py PATH...` — Level 2.
`--self-test` runs 15 fixtures.

Two exclusions are deliberate and load-bearing:

- **Verbatim third-party transcriptions are not checked.** Standards, papers and
  source extracts carry their own author's register. The first run over the wiki
  returned 1,489 findings, none actionable, because it was linting the text of
  NACE and NORSOK. A linter that flags transcribed sources teaches people to
  ignore it.
- **A list item that is only a quoted phrase is a citation.** A style guide must
  be able to list the constructions it bans. `<!-- register-lint: ignore -->`
  suppresses a line that must carry an example.

A negated intensifier is a **hedge, not an intensifier**, and is reported
separately as R5. "Not obviously correct" admits something is unproven, which is
what the register asks for; the first version of R1.2 flagged that admission
while passing the bare assertion "X is correct". The remedy for R5 differs from
R1.2: supply the criterion, do not delete the word. (Raised by a peer session
against `llm-wiki-risersintl`, where three of four `obviously` findings were the
negated form.)

The unsupported-adjective rule accepts a criterion **named**, **cited**, or
**explained in the following clause**. Its first version recognised only the
first two forms and flagged two pages that had given their reason; the rule was
wrong, not the pages.
