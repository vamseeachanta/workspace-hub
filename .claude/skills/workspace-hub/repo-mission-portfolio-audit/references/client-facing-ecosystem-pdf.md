# Client-facing ecosystem PDF checklist

Session-derived pattern from building a one-page repo-ecosystem PDF for an engineering consulting prospect.

## Target artifact

- One-page Letter landscape PDF.
- Flowchart explains how the repo ecosystem turns a client/prospect question into governed work, reusable engineering assets, and a client-ready pack.
- Every repo label is a clickable GitHub link.
- Public-facing enough to send externally; no client-specific confidential details.

## Tier-1 repos to show

Use eight Tier-1 repos unless live workspace docs supersede this:

1. `workspace-hub` — AI control plane; issue/plan/review gates; cross-repo standards.
2. `digitalmodel` — engineering calculations; offshore/subsea workflows; OrcaFlex/AQWA/FEA outputs.
3. `assetutilities` — shared utilities; units/config/CLI helpers; report/data plumbing.
4. `worldenergydata` — energy datasets; BSEE/EIA/drilling inputs; data prep pipelines.
5. `llm-wiki` — knowledge storehouse; public methodology corpus; retrieval context for agents.
6. `aceengineer-website` — public proof surface; brochures/case studies; client-facing credibility.
7. `aceengineer-strategy` — private GTM operations; prospect/pilot tracking; proposal strategy notes.
8. `assethold` — business evidence; finance/portfolio analytics; budget and decision support.

## Layout requirements that improved legibility

- Put the repo name in each flowchart block title, not only in the side panel.
- Keep role labels short: e.g., `workspace-hub — AI control plane`, `llm-wiki — Knowledge storehouse`.
- Use a right-side repo links block with compact cards: repo link plus exactly three purpose bullets.
- Include `llm-wiki` between control plane and computation/data layers because it feeds reusable knowledge/retrieval context.
- Add a short prospect-review panel: pick one representative problem, build a starter pack, review with senior-engineer judgment before production.

## Verification checklist

For Chrome-generated PDFs, verify all of the following before delivery:

```bash
PDF="docs/gtm/sendable-bundles/YYYY-MM-DD/repo-ecosystem-flowchart.pdf"
pdfinfo "$PDF" | sed -n '1,18p'              # should show Pages: 1 and landscape Letter size
pdftotext "$PDF" - | grep -E 'llm-wiki|Tier-1 repo links|workspace-hub|digitalmodel'
strings "$PDF" | grep -E 'https://github.com/.*/(workspace-hub|digitalmodel|assetutilities|worldenergydata|llm-wiki|aceengineer-website|aceengineer-strategy|assethold)'
```

Then open the PDF visually and confirm:

- single page (`1 / 1`), landscape;
- no content cut off;
- flowchart and repo links block are readable;
- `llm-wiki` appears both in the flowchart and repo links block.
