# feat(report): enforce publication pipeline gates for #2729

Parent: #2729

Wire content/report generation to `docs/architecture/report-publication-gates.md` and fail closed when publication evidence is incomplete.

Publication must require:

- evidence bundle validation
- canonical legal scan evidence
- sanitization gate evidence
- source/command/checksum/review bindings for published claims
- output-residency compatibility
- explicit promotion decision for public or more-public outputs

Acceptance criteria:

- pipeline gate has TDD coverage for allow/reject cases
- generated HTML/PDF/chatbot/public-page outputs cannot publish without evidence bundle validation
- missing legal scan or sanitization evidence blocks publication
- closeout docs record the validator command and evidence path
