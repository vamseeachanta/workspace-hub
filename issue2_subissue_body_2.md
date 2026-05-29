Parent: #2

## Objective
Create a small, approved, cited knowledge pack from the `llm-wiki-acma` repo ecosystem for the first Oil & Gas Q&A POC.

## Scope
- Inventory approved Markdown/HTML/report/manifests in the repo.
- Start with repo docs and report-layer artifacts; avoid raw `sources/` data unless explicitly approved.
- Create a machine-readable manifest with source IDs, file paths, repo revision, privacy classification, and allowed use.
- Produce a small retrieval corpus suitable for local RAG/search.
- Include enough domain material to answer a few representative Oil & Gas questions with citations.

## Deliverable
HTML-first report plus machine-readable manifest under `reports/teams-bot/issue-2/`, e.g.:
- `knowledge-pack.html`
- `knowledge-pack-manifest.json`
- optional `knowledge-pack-index.jsonl`

## Acceptance criteria
- [ ] Each indexed source has a stable source ID and repo path.
- [ ] Raw/private data access posture is documented.
- [ ] Each chunk can be traced back to an approved artifact.
- [ ] Test questions return cited source IDs.
- [ ] No client-sensitive raw text is exposed outside the private repo/report layer.
