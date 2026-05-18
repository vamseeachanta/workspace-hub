# Report Follow-up Issue Backlog (#2729)

These are body/command drafts only. They do not self-approve implementation work.

## report validator

```bash
gh issue create --title "feat(report): implement report evidence bundle validator for #2729" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/report-validator.md
```

Body draft: validate `report-evidence-bundle.schema.yaml`, published claim bindings, output residency, legal scan result, and sanitization gate before publication.

## artifact index

```bash
gh issue create --title "feat(report): build report artifact index by output residency" --label enhancement --label domain:documentation --label cat:documentation --body-file docs/architecture/follow-up-bodies/report-artifact-index.md
```

Body draft: index raw outputs, evidence bundles, HTML deliverables, limited PDFs, chatbots/query surfaces, and report-derived learning by issue/source/output residency.

## publication pipeline

```bash
gh issue create --title "feat(report): enforce publication pipeline gates for #2729" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/report-publication-pipeline.md
```

Body draft: wire content/report generation to `report-publication-gates.md` and fail closed on missing evidence bundle, legal scan, sanitization, or output-residency compatibility.
