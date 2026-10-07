# Context extraction — full procedure (drive-file-search Step 1–2 detail)

Everything below is executable by any runtime (Claude, Codex, Gemini) with only
`bash`, `git`, `gh`, and `python`. Every signal is **fail-soft**: if a command
errors or a file is absent, drop that signal and continue with the rest.

## Step 1 — Extract work context

### (a) Repo + issue

```bash
repo=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")   # "" if not a git repo
# only if an issue number N is already known in-session:
gh issue view N --json title,labels
```

- `terms_issue` = significant words of the issue title: strip stopwords
  (the/a/of/for/and/...), strip numbers-only tokens.
- Note labels that hint at a domain or category (`cat:*`, domain words).

### (b) Engineering domain — reuse the generated map, never a hand-copied list

Read `.claude/hooks/ecosystem-domain-map.json` (generated from
`llm-wiki/data/domain-database-index.yml`; 12 domains, each with `keywords[]`).
Pick the **first domain whose `keywords[]` match** the task description or issue
title — word-boundary, case-insensitive (the same matching posture as
`.claude/hooks/ecosystem-data-nudge.sh`). Record the domain id and the specific
keyword(s) that matched. Do not copy keyword lists into any other file; read the
map live so the skill never drifts from the generated source.

### (c) Artifact-type hints — task type → file-type expectation

| Task type | Expected extensions |
|---|---|
| calcs / analysis | xlsx, py, csv |
| CAD / geometry | dwg, ipt, step, sldprt, iges |
| standards / code question | pdf |
| simulation | dat, sim, yml, owr |

Hints are **presentation garnish only**: they boost hint-matching extensions
within equal-score groups at display time (Step 5 of SKILL.md); they never change
the query and never re-rank across different scores.

Return: `(repo, terms_issue, domain, matched_keywords, hints)`.

## Step 2 — Assemble the query (2–5 terms, ONE CLI call)

```
terms = dedupe(top matched domain keyword(s) + 1–3 significant issue-title words)
```

`--domain` vocabulary guard: map ids (`mooring`, `riser`, ...) are NOT guaranteed
to be registry `domains:` values (the live registry uses `engineering`, `marine`,
`drilling`, `cad`, `standards`, `literature`). Only pass `--domain <d>` if `<d>`
appears in a `domains:` list in `config/drive-index-registry.yml`. Otherwise
**fold the domain word into the query terms — the safe default**: an entry with
`domains:` absent matches ALL queries, and an unknown `--domain` yields an empty
selection with exit 0 (silent-empty, not an error). A grep-level check of the
registry can false-positive on comments or other keys, so the guard is
best-effort; prefer folding whenever in doubt.

## Worked mock walkthrough (dry-runnable without the live drives)

**Context:** working in `digitalmodel` on a mooring fatigue calc; the in-session
issue title is "Mooring line fatigue screening".

1. **Extract** — (a) `repo = digitalmodel`; issue title terms → `line`, `fatigue`,
   `screening` (stopwords dropped). (b) The map's `mooring` domain matches on
   keywords `mooring` and `mooring line`. (c) Task type = calc → hints
   `xlsx, py, csv`.
2. **Assemble** — `mooring` is not a `domains:` value in the live registry
   (`engineering, marine, drilling, cad, standards, literature`), so fold it in.
   Terms: `"mooring line fatigue screening"`. No `--domain` flag.
3. **Run the ONE command:**

   ```bash
   uv run python scripts/data/drive-index-search/search.py \
     "mooring line fatigue screening" --json --limit 20
   ```

4. **Parse** — for this dry run, treat `references/mock-envelope.json` as the
   stdout envelope (exit 0). It contains 5 results across 2 source indexes and
   one `coverage_gaps` entry (`dde_literature_catalog`, reason `unreachable` —
   opaque free text, quoted verbatim, never interpreted).
5. **Present** (top 5 shown; scores are all distinct, so artifact-type hints
   reorder nothing here — they would only reorder within an equal-score group):

   ```
   Related files on the shared drives for "mooring line fatigue screening":

   1. /mnt/ace/projects/example-fpso/mooring/line-fatigue-screening.xlsx
      why: matched mooring/line/fatigue/screening; rank_basis fts_bm25 (score 0.94);
      .xlsx matches the calc hint
      source: ace_knowledge — built 2026-03-26 (may lag recent drive changes)

   2. /mnt/ace/projects/example-fpso/mooring/fatigue-postprocess.py
      why: matched mooring/line/fatigue/screening; rank_basis fts_bm25 (score 0.87);
      .py matches the calc hint
      source: ace_knowledge — built 2026-03-26

   3. /mnt/dde/literature/fatigue/chain-fatigue-review.pdf
      why: matched mooring/fatigue/screening; rank_basis token_match (score 0.75)
      source: master_document_index — frozen 2026-04-17; dde results may be stale

   4. /mnt/ace/projects/example-semisub/mooring/line-tension-summary.csv
      why: matched mooring/line; rank_basis token_match (score 0.62);
      .csv matches the calc hint
      source: master_document_index — frozen 2026-04-17

   5. /mnt/ace/standards/example-org/offshore-mooring-design-practice.pdf
      why: matched mooring/line; rank_basis token_match (score 0.58)
      source: master_document_index — frozen 2026-04-17

   NOT searched: index dde_literature_catalog ("unreachable") — results exclude the
   dde literature catalog; to restore: scripts/setup/canonical-drive-links.sh (PR #3341).

   Next actions:
   1. open/read one of the listed files (bounded read of that file only)
   2. record chosen paths as "Documents consulted" in the active plan's
      Resource Intelligence section
   3. refine terms and re-run once
   ```

Presentation notes demonstrated above:

- `canonical_path` is always shown (`/mnt/<drive>/...`); `raw_path` (e.g. the
  `/mnt/remote/...` alias on result 3) is never shown — it exists in the envelope
  only for de-identification checks and dedup.
- Freshness caveats come from the registry entry's `freshness/built_at`; if an
  entry has no freshness metadata, say "freshness unknown" — never invent a date.
- The `coverage_gaps` `reason` ("unreachable") is quoted verbatim as opaque free
  text — no enum exists, so never pattern-match or paraphrase it.
- Before quoting any of these paths into a public artifact (issue/plan/PR/commit),
  apply the De-identification guardrail in SKILL.md — the mock paths here are
  fictional and already de-identified.
