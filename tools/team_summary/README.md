# Client team summary generator

One command turns a client's facts file into its team summary PDF (workspace-hub#3967).

```bash
uv run --group dev python tools/team_summary/build.py \
  --data <client-wiki>/reports/team-summary/summary.yml \
  --out  <client-wiki>/reports/team-summary/team-summary.pdf \
  --wiki-root <client-wiki>
```

## Contract

| Lives where | What |
|---|---|
| workspace-hub (this folder) | Schema, template and generator. Client-agnostic; no client data. |
| `llm-wiki-<client>/reports/team-summary/summary.yml` | The facts. Every item carries a `source` path in that wiki. |
| `llm-wiki-<client>/reports/team-summary/team-summary.pdf` | The one canonical PDF, overwritten in place. Git history is the change history. No dated copies. |

- The summary is regenerated daily and published to one stable link on the client Space.
- Sections are fixed: learn or solve, top 3 priorities, outstanding issues, decisions and blockers,
  by area (empty areas omitted), current deliverables, sources. This is an operational summary, so
  the ten-section formal report standard (#3925) does not apply.
- The PDF is a client deliverable surface: follow `.claude/rules/report-audience-and-surface.md`
  and `docs/standards/FINAL_REPORT_VERIFICATION.md` before the first publication to a new audience.
- Renderer: headless Chrome (Linux, Windows) or Edge (Windows). Override with `TEAM_SUMMARY_BROWSER`.

## Review links

An item may point to the document that needs a response. These fields are optional and existing
`summary.yml` files remain valid.

| Field | Where | Meaning |
|---|---|---|
| `review.link_base` | Top level | URL prefix used to link wiki-relative document paths in the PDF. When omitted, paths render as plain text. |
| `review.copies_dir` | Top level | Wiki-relative folder for generated HTML review copies and saved comment JSON files. |
| `review.return_to` | Top level | Short instruction for where saved comment JSON files go back. |
| `review.doc` | Priority, issue, blocker, area item or deliverable | Wiki-relative document path that needs input, approval, a conclusion or comments. |
| `review.ask` | Priority, issue, blocker, area item or deliverable | One of `input`, `approval`, `conclusion`, `comments`; controls the rendered label. |

Use `--make-review-copies` with `--wiki-root` to generate commentable copies for reviewed HTML
documents under `review.copies_dir`. The generator links those copies and never deletes saved comment
JSON files.

`example/summary.yml` is synthetic and drives the tests in `tests/team_summary/`.
