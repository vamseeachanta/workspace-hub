# Data-layer path-class examples for architecture plans

Use this reference when drafting or revising data-layer, llm-wiki, RAG/chatbot, document-intelligence, or report-source inventory plans.

## Pattern learned

For data architecture issues, do not stop at abstract source classes like "raw data", "private staging", or "public repo content". Add concrete, reviewable path-class examples so the user can quickly relate the taxonomy to real storage and add more categories.

Also separate generic private/local source data from **client-private source data**. Client roots need a stronger default than ordinary staging paths: they promote only into dedicated private client wiki repositories/corpora, while public `llm-wiki` remains separate. Reports may combine private client retrieval with public `llm-wiki` retrieval only at report/runtime, with source classes and citations kept distinct.

## Example path classes

| Path / pattern | Typical contents | Layer posture | Public/private default |
|---|---|---|---|
| `/mnt/ace/` raw PDFs → generated `.md` files | Raw standards/literature/project PDFs and first-pass markdown extraction outputs | D-L1 raw/source data → D-L2 raw-like extraction output | Private/local source data |
| `/mnt/ace/raw-processed/` | Index files, markdown, uncurated llm-wiki drafts/staging packs, extraction manifests, source cards, RAG chunks | D-L2 raw-like structured/staging data | Private/local source data |
| `/mnt/local-analysis/<repo>/` | Tier-1 repo checkouts: workspace-hub, digitalmodel, assetutilities, worldenergydata, llm-wiki, assethold, aceengineer-website, aceengineer-strategy | D-L3 curated knowledge/data or repo-backed execution/report metadata, depending on path | Public-facing only when explicitly curated/sanitized and repo policy allows |
| `/mnt/ace/<client-or-project-root>/` | Client/project raw documents, emails/exports, project archives, working datasets, extraction outputs tied to a client | D-L1 client raw/source → D-L2/D-L3 private client knowledge | Private-client by default; never promote directly into public `llm-wiki` |
| `/mnt/local-analysis/<client>-llm-wiki/` | Private client-specific wiki/corpus, curated source cards, manifests, retrieval chunks, insight-report evidence packs | D-L3 private client wiki/corpus | Private repo/corpus required unless explicit sanitization/publication approval exists |

## Client data handling model

When the user identifies concrete client roots, add a separate `Client data handling model` section rather than folding them into the generic `/mnt/ace/` row.

Recommended mapping pattern:

| Raw client root | Private wiki/corpus target | Rule |
|---|---|---|
| `/mnt/ace/rock-oil-field` | `/mnt/local-analysis/rock-oil-field-llm-wiki` | Private-client corpus; no public promotion by default |
| `/mnt/ace/client-projects` | `/mnt/local-analysis/client-projects-llm-wiki` | Private-client corpus; no public promotion by default |
| `/mnt/ace/doris` | `/mnt/local-analysis/doris-llm-wiki` | Private-client corpus; no public promotion by default |
| `/mnt/ace/acma-projects` | `/mnt/local-analysis/acma-projects-llm-wiki` | Private-client corpus; no public promotion by default |
| `/mnt/ace/frontier-deepwater` | `/mnt/local-analysis/frontier-deepwater-llm-wiki` | Private-client corpus; no public promotion by default |
| `/mnt/ace/saipem` and similar roots | `/mnt/local-analysis/<client>-llm-wiki` | Private-client corpus; no public promotion by default |

Report-time combination rule:
- A client insight report may query both a private client wiki/corpus and public `llm-wiki`.
- The report layer must preserve distinct citations/source classes (for example `private-client` vs `public-llm-wiki`).
- Do not merge raw/private client materials into public `llm-wiki` as an implementation shortcut.
- Sanitized public derivatives require an explicit approval/sanitization gate and provenance back to the private source class.

## Required drafting moves

1. Add a `Concrete example path classes for user review` table near the initial source inventory.
2. Include path/pattern, example contents, proposed layer level, public/private posture, and notes.
3. If a path was user-provided but does not exist in the current runtime, record it as an intended/example staging path rather than pretending it was verified.
4. Add a separate `Client data handling model` section when client/project roots are in scope.
5. Map every named client root to a dedicated private `/mnt/local-analysis/<client>-llm-wiki` target or mark the target as planned if it does not yet exist.
6. Add an acceptance criterion that the final data-source inventory must include concrete path classes and client-private wiki targets.
7. Add a TDD expectation that client roots cannot route into public `llm-wiki` and that report-time combination rules preserve public/private citation separation.
8. For public-facing repo paths under `/mnt/local-analysis/<repo>/`, explicitly state that raw private source data does not become public just because a sanitized derivative lands in a public repo.

## Verification note

A lightweight path probe is useful evidence, but absence on the current machine is not a reason to remove a user-provided canonical/intended path. Capture the distinction: `exists in this runtime`, `missing in this runtime but user-provided/intended`, `planned private target repo/corpus`, or `repo/path pattern to be resolved during implementation`.

When the repo has unrelated dirty/untracked state, commit only the plan/supporting-doc files intentionally changed for the issue. Verify the target plan file is clean/synced after commit/push rather than claiming the entire worktree is clean.