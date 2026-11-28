# Knowledge map: writing

Verified 2026-11-27T15:41:54Z against workspace-hub `origin/main`. Machine-readable form:
`writing.yaml`. The newsletter and article pipeline, per-machine toolchain and the 20 recorded
deviations are held in the private repository: `fleet-ops docs/knowledge-maps/writing.yaml`.

## 1 Scope

This map indexes how engineering text is written, reviewed, verified and issued: reports,
calculation notes, client deliverables, articles, newsletters, wiki pages, proposals and
correspondence. Each genre is given with its surface, governing rules, skills, templates,
review chain, lint command and approval path.

## 2 Register

The register is set by `.claude/rules/engineering-register.md`, stated canonically in
`config/agents/SHARED_SOUL.md` (section "Engineering register"). The full guide with quoted
exemplars is the private `llm-wiki` page `engineering/concepts/engineering-report-house-style`.

- The subject is the analysis, result, component, document or company, never a person. The
  proposal genre is the only written exemption.
- Every conclusion is bound to its criterion, comparator and governing case.
- `should` and `is recommended` carry advice; `shall` and `must` carry requirements.
- `-`, `n/a`, `TBD`, `Not Evaluated` and a true zero are distinct.
- Method is written in report-present passive, completed events in the past tense, findings in
  the simple present. Captions sit below tables and figures; units sit in the header.

Lint: `uv run python scripts/enforcement/check-engineering-register.py PATH...`
(`--self-test` runs 15 fixtures; it passed on 2026-11-27). Verbatim standards text and quoted
list items are excluded by design.

## 3 Surface and claims

The surface is named before the first line is written (`.claude/rules/report-audience-and-surface.md`).

| Surface | Client identifiers | Cost models, host names | Defects in own tooling |
|---|---|---|---|
| Internal | allowed | allowed | allowed |
| Client deliverable | required | never | never |
| Hosted (any URL) | redacted | never | never |

Table 1 – Content permitted per surface

Claim vocabulary (`report-claim-discipline` skill):

- Plausibility verdicts are `implausible` or `not_implausible`; review packs add `not_evaluated`.
- `validated` and `passed` are not written without a named referent. Without one, the claim is
  a verified prediction with a numerical-uncertainty band and a statement that modelling error
  lies outside it.
- `acceptable`, `conservative` and `safe` are not written without the criterion that makes them so.
- A causal claim about tool behaviour requires a source read and a check of existing output;
  otherwise it is labelled a hypothesis (`mechanism-before-publication.md`).
- Every artifact that encodes a calculation names one comparator the producing system did not
  make; `archived-run` is a regression guard only (`reproducibility-is-not-correctness.md`).

## 4 Citations and standards

- Standards-derived constants emit a `Citation` sidecar with `code_id`, `publisher`,
  `revision`, `section`, `source_sibling` and `source_project`; resolution fails closed with
  `CitationResolutionError` (`.claude/rules/calc-citation-contract.md`,
  `docs/standards/calc-output-citation.md`).
- References are grouped as model and data, solver and programs (with versions), and standards
  and methods (with clause). A missing revision or URL is written `TBA`, never invented.
- Maintainer ruling of 28 Oct 2026 (`codes-standards-data-routing.md`): internal work has no
  gates. Outward work quotes the clauses and values used with standard, edition and clause,
  rebuilds charts as "Reconstructed from [standard], Figure X" with digitising uncertainty,
  and keeps original PDFs and whole sections off public surfaces. Each job cites the applicable
  CFR and other regulators.

## 5 PDF and SVG

- PDF-bound and logo SVG carries no `<pattern>`, `clip-path`, `<filter>`, `<mask>` or
  `<foreignObject>` (`.claude/rules/svg-pdf-portability.md`).
- Verification: `pdftocairo -png -r 200 out.pdf check` and `pdftoppm -png -r 200 out.pdf check`;
  the two rasters must agree.
- Headless Chrome drops `file://` images (embed as base64 data URIs) and hangs without
  `--virtual-time-budget`.
- No Level-2 SVG portability script exists yet; the check is manual.

## 6 Review and approval

1. The author drafts; a second provider reviews (`docs/standards/AI_REVIEW_ROUTING_POLICY.md`:
   Codex reviews Claude work, Claude reviews Codex work, Agy optional for a plain-English pass).
   Review is advisory and fixes real defects; it is not a merge gate.
2. A commentable local HTML copy is produced with `tools/html-review/make_review_copy.py`;
   comment JSON is saved beside the page and read back each round
   (`docs/standards/review-and-communication-standard.md` section 3).
3. Before issue, the reviewer records the outgoing bundle per
   `docs/standards/FINAL_REPORT_VERIFICATION.md`: audience, artifact digests, identifier
   decision, rights, secret evidence, reviewer, date and verdict. `legal-sanity-scan` is retired.
4. Repository text merges on green required checks (`merge-authorization.md`).
5. The owner approves client-facing emails and messages, spending, and outward publication.
   Owner decisions go on a local HTML decision board (`human-decision-boards.md`).

## 7 Genres

| Genre | Surface | Templates and skills | Lint | Approval |
|---|---|---|---|---|
| Engineering report | internal / client / hosted | conventions draft P3 (`engineering-reporting-conventions-proposed.html`), `reformat-engineering-report-prompt.md`, `engineering-report-generator`, `html-report-verify`, `md-to-pdf`, `docx` | register lint | owner before client issue |
| Calculation note | internal / client | `scripts/reporting/generate-calc-report.py` (YAML), digitalmodel `reporting/calc_report.py` (typed), `calculation-report` | register lint; citation resolver | owner before client issue |
| Client deliverable | client | as report; cold read; Cairo and Poppler check | register lint | owner only |
| Article | hosted | house rules private | register lint; private document-rules check | owner publishes |
| Newsletter | hosted | house rules private | as article | owner publishes |
| Wiki page | private wiki sibling | `llm-wiki-page-shape-contract`, `llm-wiki-public-private-routing` | `check-wiki-sibling-frontmatter.py`; register lint | merge on green |
| Proposal | client | none located | register lint (first person exempt) | owner |
| Correspondence and agent text | varies | `review-and-communication-standard.md` section 5 | none | owner for client-facing |

Table 2 – Genre index

Four report skeletons coexist (conventions draft P3, the typed seven-section model, the
llm-wiki house-style skeleton and a private house skeleton). The canonical system is an owner
decision tracked in workspace-hub issue 3810; until it is settled, a new report uses the system
its target repository already uses.

## 8 Open questions

- The canonical report system (issue 3810).
- Whether articles and newsletters join proposals as a first-person exemption in the register rule.
- Whether the typed `Confidence` level `validated` requires a named referent field.
- When `svg-pdf-portability.md` receives its Level-2 script.
