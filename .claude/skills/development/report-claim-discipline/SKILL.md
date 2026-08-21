---
name: report-claim-discipline
description: >
  What an engineering report may CLAIM, and to whom. Governs audience/surface
  routing, verdict vocabulary (never "validated" without a referent), explicit
  confidence, TBA as a deliverable-shaping tool, reference categories and URL
  policy, provenance of derived quantities, and PDF production traps. The other
  reporting skills cover pipelines and verification; this one covers content.
type: reference
version: 1.0.0
category: development
last_updated: 2026-08-20
related_skills:
  - calculation-report
  - engineering-report-generator
  - html-report-verify
  - reporting-workflow
tags: [reporting, claims, provenance, confidence, client-deliverable, pdf, redaction]
---

# Report Claim Discipline

Every other reporting skill in this tree covers **mechanics** — YAML schemas, generator
pipelines, DOM verification, fixture proofs. None covers **what may be claimed in a
report, and to whom.** That is this skill.

Use it *before* generating: these are content decisions, and most of them are
unrecoverable once a document has been issued or published.

## 1. Name the surface first

Internal page, client deliverable, and hosted artifact are three different documents.
The same fact is redacted on one and required on another, and **the discriminator is
the surface, not the sensitivity of the fact**.

Full table and the reasoning: `.claude/rules/report-audience-and-surface.md`.
Do not proceed until you can name the row.

## 2. Never write "validated" without a referent

Verification asks *am I solving the equations right* and is answerable from the
simulation alone. Validation asks *am I solving the right equations* and is answerable
only against a measurement of the thing being modelled. **Losing the referent does not
weaken validation — it deletes it.**

Where no experiment or benchmark exists for the specific artefact, the honest claim is:

> a **verified prediction** with a stated **numerical**-uncertainty band, plus an
> explicit statement that **modelling error is not inside that band** and is not
> bounded by anything in the report.

Verdict vocabulary is `implausible` / `not_implausible`. Never "passed", never
"validated". **A plausibility band cannot confirm; it can only fail to contradict.**
Presenting a referent-free number with a pass stamp is manufacturing a grade.

Worked precedent, already implemented — read these rather than re-deriving the argument:

- `digitalmodel/src/digitalmodel/solvers/openfoam/validation/referent_free_resistance.py`
  — scores a run for a hull with no published coefficient; never loads a referent,
  never returns a validation verdict. Its module docstring states the category
  difference once, plainly.
- `digitalmodel/docs/domains/openfoam/referent-free-resistance-validation-2026-08-19.md`
  — the design note, including the item-by-item table of what survives the loss of
  the referent and what does not.

Corollary worth remembering: a criterion invented *after* looking at the answer is not
a criterion.

## 3. Confidence is explicit, never defaulted

The house typed format (`digitalmodel/src/digitalmodel/reporting/calc_report.py`)
requires a `Confidence` on every `ResultBlock` — `validated` / `analytical` /
`pending` — and deliberately refuses to default one.

Record why: **a default is invisible, and an invisible default is how a pending number
acquires the appearance of a measured one.** Three levels is deliberately coarse; what
a reader needs is whether a number is measured, inferred, or not yet available.

Anything not supplied by the client goes in the assumption ledger with its basis. Never
silent.

## 4. TBA is a deliverable-shaping tool, not a placeholder

Populate the Results section **before the numbers exist** — one row per quantity that
will be delivered, with its unit and its confidence, value reading `TBA`.

- An empty Results section communicates nothing.
- A populated one communicates exactly what is coming, and sets client expectations
  *before* delivery rather than at it.
- It forces agreement on the deliverable list while disagreeing is still cheap.

Same discipline for references: **TBA a missing detail rather than omitting the
reference or inventing the detail.** A reference with `revision: TBA` is honest; a
reference with a guessed revision is a fabrication that looks like traceability.

## 5. References: three categories, URLs where applicable

Group references into three categories:

| Category | Must carry |
|---|---|
| **Model and data** | input geometry and datasets, with provenance and hashes |
| **Solver and programs** | names **and versions** |
| **Standards and methods** | publisher, designation, revision, clause |

`Reference.url` is **optional by design**. Many legitimate sources have no public URL —
a purchased standard, a client-supplied model — and a mandatory field invites a
fabricated one. **A fabricated link is worse than no link, because it looks like
traceability.**

Only `http`/`https` may be linkified. A `javascript:` or `data:` URL in a citation
field is an injection vector and no legitimate reference needs one. The typed renderer
already enforces this (`_ref_body` in `calc_report.py`); any other renderer must too.

For standards-derived *constants*, the citation sidecar contract is separate and
mandatory: `.claude/rules/calc-citation-contract.md`.

## 6. Say when a quantity was derived

Where the report states a quantity that was **computed from client-supplied input**
rather than taken from a specification, say so, and say from what.

This is the difference between a report that can be **reviewed** and one that must be
**trusted**. It lets the client check our numbers against their own — which is the
entire point of issuing a calculation rather than an answer.

## 7. Revision history is the trail behind the current revision

The header already tells a reader which revision they hold. What a reviewer holding an
**earlier** copy needs is *what changed since theirs*.

Render the history table when entries are present; **omit the section entirely on a
first issue** rather than showing an empty table. An empty revision table is visual
noise that implies a lost history.

## 8. PDF production traps on this fleet

| Trap | Fix |
|---|---|
| Headless Chrome `--print-to-pdf` **drops `file://` images** | embed every image as a base64 `data:` URI before printing |
| Headless Chrome on a display-less host **hangs** | always pass `--virtual-time-budget` |
| Cairo mis-paints constructs Poppler renders fine | verify with **both** `pdftocairo -png` and `pdftoppm -png` and confirm they **agree** — the reader most likely uses a Cairo-based viewer (Evince/GNOME Document Viewer) |

The SVG authoring side of this — no `<pattern>`, `clipPath`, `<filter>`, `<mask>` in
PDF-bound SVG — is already covered and is not restated here:
`.claude/rules/svg-pdf-portability.md`.

## Which report system?

⚠ There are currently **two independent calculation-report systems** in this ecosystem
with different formats and different design systems:

- **YAML → script**, documented by [`calculation-report`](../../data/calculation-report/SKILL.md)
  (`scripts/reporting/generate-calc-report.py`, warm-parchment design system).
- **Typed Python models**, `digitalmodel/src/digitalmodel/reporting/calc_report.py` —
  fixed seven-section order (Objective, Design data, Analysis methodology, Results,
  Validation status, Way forward, References and provenance) with the required
  `Confidence` taxonomy.

Which is canonical is an **owner decision**, tracked at
[workspace-hub#3810](https://github.com/vamseeachanta/workspace-hub/issues/3810). Until
it is decided: check which system the target repo already uses before adding a report,
and do not introduce a third.

The claim rules in this skill are **system-independent** — they apply to whichever
renderer you use, and to hand-written HTML.

## Pre-issue checklist

- [ ] Surface named (internal / client deliverable / hosted) and content matched to it
- [ ] No cost model, host name, per-run rate or self-criticism in a client or hosted document
- [ ] Hosted artifact sanitised of client identifiers; client deliverable *carries* them
- [ ] No "validated" or "passed" anywhere without a named referent
- [ ] Every result block carries an explicit confidence; none defaulted
- [ ] Results section populated — pending quantities present as `TBA` with unit and confidence
- [ ] References grouped in the three categories; solver **versions** present; no invented URL or revision
- [ ] Derived quantities flagged as derived, with their input source
- [ ] Revision history rendered if present, omitted entirely if first issue
- [ ] PDF verified in **both** Cairo and Poppler and they agree; images embedded as data URIs

## What this skill does NOT cover

Deliberately, so it stays short — go to the mechanics skills for these:

- YAML schema and validation gate → [`calculation-report`](../../data/calculation-report/SKILL.md)
- Plotly/HTML generation patterns → [`engineering-report-generator`](../engineering-report-generator/SKILL.md)
- DOM/visual/artifact-bundle verification → [`html-report-verify`](../html-report-verify/SKILL.md)
- Generate → verify → test → iterate loop → [`reporting-workflow`](../workflows/reporting-workflow/SKILL.md)
- Cold-outreach demo collateral → [`gtm-parametric-demo-reports`](../../business/gtm-parametric-demo-reports/SKILL.md)
- Fixture-backed reporting proof baselines → [`orcaflex-reporting-fixture-proof-pattern`](../../digitalmodel/orcaflex-reporting-fixture-proof-pattern/SKILL.md)
