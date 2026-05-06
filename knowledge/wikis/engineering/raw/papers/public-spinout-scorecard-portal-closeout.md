# Public llm-wiki spinout scorecard + portal closeout pattern

Use when maximizing a public `llm-wiki` repository that was spun out of a private/control-plane workspace.

## Problem shape

- The public repo should be improved without copying private raw files, vendor PDFs, vendor-derivative text, credentials, or private mount paths.
- Some issues may be approval-gated (`status:plan-review`); do not execute them without explicit user approval.
- The public repo is the artifact/content storehouse; pipeline/orchestration usually remains in `workspace-hub` or another control-plane repo.

## Safe high-leverage move

1. Clone/orient in the public repo and read README/provenance/licensing first.
2. Inspect issue labels and separate:
   - safe/approved implementation anchors,
   - approval-gated plan-review items,
   - control-plane-only work.
3. Generate a deterministic repo-local scorecard from committed markdown metadata only:
   - domain count,
   - markdown content pages,
   - curated synthesis pages,
   - source-summary pages,
   - missing frontmatter/index entries,
   - orphan curated pages,
   - navigation/cross-link health.
4. Write both:
   - `docs/reports/<name>.md` for human triage,
   - `docs/reports/<name>.json` for repeatable automation.
5. For the largest source-heavy domain, prefer adding a faceted `wiki/portal.md` and an `index.md` link before touching stale `overview.md` text. Overview rewrites can overlap approval-gated issue scopes.

## Public artifact hygiene gates

Before commit/push, verify the exact staged files:

```bash
git diff --cached --check
uv run python -m py_compile scripts/<scorecard_script>.py
uv run python -m json.tool docs/reports/<scorecard>.json >/dev/null

# Scan exact staged files, not the whole repo, for private path strings and common secrets.
git diff --cached --name-only -z \
  | xargs -0 grep -InE '(/mnt/(ace|local-analysis)|AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY|api[_-]?key|token|password|secret)' \
  || true
```

Then manually inspect staged diffs for:

- raw archive paths accidentally preserved in generated prose,
- vendor-derived copied text rather than summaries/metadata,
- root clutter or generated outputs outside agreed report/tooling locations,
- markdown local links that point to missing files,
- trailing blank lines/whitespace failures.

If generated prose mentions a private source root, replace with generic wording such as `non-public source material` before committing.

## Closeout discipline

- Commit and push in the same window.
- Prove local HEAD equals remote branch.
- Post issue comments using body files, including:
  - commit hash,
  - changed artifacts,
  - validation evidence,
  - raw-data/vendor-derivative boundary statement,
  - what remains in the approval queue.
- Do not close broad umbrella issues unless the whole scope is complete; evidence comments can close the loop for incremental deliverables.

## Example result shape

- A dependency-free `scripts/llm_wiki_strengthening_scorecard.py` that reads public markdown metadata only.
- A generated `docs/reports/llm-wiki-strengthening-scorecard.{md,json}`.
- A generated `wikis/<large-domain>/wiki/portal.md` with frontmatter, corpus snapshot, faceted links, and representative curated/source pages.
- A small `index.md` link to the portal.
