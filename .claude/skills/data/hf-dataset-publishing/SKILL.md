---
name: hf-dataset-publishing
description: >-
  Save/publish analysis or computation results from ANY ecosystem repo to Hugging Face as a
  queryable, viewer-renderable dataset. Use when the user wants to "save results to hugging
  face", "publish dataset to HF", "hugging face data saving", "save analysis results",
  "hf dataset", "make results queryable", or "render via datasets-server API". Reshapes nested
  results into flat parquet tables, writes a dataset card with a viewer `configs:` block and
  provenance, applies license/public-vs-private routing, enforces a domain data-quality gate
  (faithful-to-source != correct), publishes to `aceengineer/<repo>-<projection>`, and verifies
  via the datasets-server API.
---

# Publishing Analysis Results to Hugging Face

Turn the results of any analysis/computation (from any repo in this ecosystem) into a
**queryable, auto-rendered Hugging Face dataset**. HF's datasets-server auto-indexes parquet
tables and exposes them both in the in-browser viewer and via a REST API — so a published
dataset becomes a live, linkable, machine-queryable projection of your results.

This skill encodes a workflow that was executed end-to-end on 2026-07-11. Follow THIS, not
generic HF docs.

## When to use

- You have analysis output (JSON, dicts, dataframes, a results folder) and want to save it
  somewhere queryable and viz-renderable, not just a file on disk.
- You want a shareable, indexable surface for a set of computed results (per field / per well /
  per country / per run-summary, etc.).
- Someone says "publish this to Hugging Face" / "save these results as an HF dataset".

**Do NOT use this** to record algorithm-run identity/replay ledgers — that is the separate
`aceengineer/<repo>-runs` contract (workspace-hub#3433). See Conventions below.

## Prerequisites (environment-backed auth)

- CLI is **`hf`** (`huggingface-cli` is DEPRECATED — do not use it).
- Token lives at `~/.cache/huggingface/token`. Verify:
  ```bash
  hf auth whoami          # expect: user=<u> and orgs include aceengineer
  ```
- Python libs available: `huggingface_hub` (1.21+), `pandas`, `pyarrow`.
- **Never print, echo, log, or commit the token.** Secrets stay in env / token-file only.

## The 4-step workflow

### Step 1 — Reshape nested results → flat tabular tables (one per entity)

Load the analysis output and build **one `pandas.DataFrame` per entity type** (e.g. `fields`,
`wells`, `countries`). For each table select SCALAR columns only:

- Flatten a few useful nested scalars (e.g. `econ.breakeven -> econ_breakeven`).
- SKIP list/dict-valued columns (they don't render in the tabular viewer).
- **Sanitize NaN/inf.** The source JSON may carry literal `NaN`/`Infinity` tokens that break
  strict JSON consumers. Parquet stores genuine nulls natively, so coerce non-finite floats to
  null and write **parquet** — which is exactly what the HF datasets-server auto-renders.

```python
import math, pandas as pd, numpy as np

def clean(df: pd.DataFrame) -> pd.DataFrame:
    # non-finite floats -> genuine null (parquet-native)
    return df.replace([np.inf, -np.inf], np.nan)

df_fields = clean(pd.DataFrame(field_rows))         # one row per field
df_fields.to_parquet("out/fields.parquet", index=False)
```

CSV is an acceptable fallback if parquet is unavailable, but parquet is preferred (native nulls
+ auto-render).

### Step 2 — Dataset card `README.md` with YAML frontmatter

The frontmatter MUST include `license:` (see routing rule), `pretty_name`, `tags`, and a
**`configs:`** block listing each parquet table as its own viewer config:

```yaml
---
license: cc-by-4.0
pretty_name: World Energy Data — Explorer Projection
tags:
  - energy
  - oil-and-gas
  - analysis-results
configs:
  - config_name: fields
    data_files: fields.parquet
  - config_name: wells
    data_files: wells.parquet
  - config_name: countries
    data_files: countries.parquet
---
```

The card **body** must cover:

- **What it is** — one-paragraph description of the projection and its source analysis.
- **A table of configs + row counts** (e.g. `fields — 56 rows`).
- **Provenance** — source file **sha256** hashes + a `schema_version`. This is how a consumer
  proves which analysis run produced the data.
- **Data basis** — what the numbers mean, units, and the note that **nulls are genuine** (not
  missing-by-accident) because non-finite values were coerced to null.
- Any **withheld columns** (see the data-quality gate) with a link to the filed issue.

### Step 3 — Publish

```python
from huggingface_hub import HfApi
api = HfApi()
repo_id = "aceengineer/<repo>-<projection>"          # e.g. aceengineer/worldenergydata-explorer
api.create_repo(repo_id=repo_id, repo_type="dataset",
                private=<per routing>, exist_ok=True)
api.upload_folder(folder_path="out", repo_id=repo_id, repo_type="dataset",
                  commit_message="Publish <projection> analysis projection")
```

The bundled `publish_analysis_to_hf.py` does exactly this (plus auth check + verify) — prefer it
over hand-rolling.

### Step 4 — Verify (the render-via-API surface)

```python
api.list_repo_files(repo_id=repo_id, repo_type="dataset")   # confirm parquet + README landed
```

Then hit the **datasets-server API** (the surface that powers the in-browser viewer):

```
https://datasets-server.huggingface.co/is-valid?dataset=<repo_id>
https://datasets-server.huggingface.co/rows?dataset=<repo_id>&config=<table>&split=train&offset=0&length=10
```

**Indexing lag is normal.** A brand-new dataset returns *"server is busier than usual / retry
later"* for a few minutes before `/rows` and the in-browser viewer come up. **Poll — do not
assume failure.** Once `/is-valid` reports valid and `/rows` returns data, the viewer is live.

## Conventions the skill MUST encode

- **Naming:** `aceengineer/<repo>-<projection>` — e.g. `worldenergydata-explorer`. Datasets on
  the `aceengineer` org are **free**.
- **Keep SEPARATE from the run-dataset contract.** `aceengineer/<repo>-runs` is
  workspace-hub#3433's contract-managed **algorithm-run ledger** (run-identity + replay).
  Analysis-result projections are a different artifact and get their **own** dataset. Do **not**
  dump projections into `-runs`.
- **License / public-vs-private routing** (cite `.claude/rules/codes-standards-data-routing.md`):
  - Public-domain **federal** data (BSEE / NOAA / USGS) → **public**, `license: cc-by-4.0`.
  - **Vendor-licensed / private / client** data → must **NOT** be published to a public HF
    dataset. A **private** repo is OK only with **explicit owner** sign-off.
  - **Synthetic / own-analysis** output → publisher's choice.
  - If unsure of the source's provenance, default to **private** and ask the owner.

## DATA-QUALITY GATE (load-bearing — do not skip)

> **Faithful to source != correct.**

Row counts matching the source proves nothing about whether the numbers are right. Before
publishing, run a **domain plausibility check on the actual values** — publishing to a new,
labeled, queryable surface is a natural audit trigger, so audit here.

- If values are **implausible**, **withhold those columns**, file a `cat:data` / bug issue, and
  **note the withholding in the card** (with the issue link).
- Real case (2026-07-11): economics columns showed **$380 breakevens on producing fields** —
  clearly wrong. Those columns were **withheld** pending **worldenergydata#971** rather than
  published as fact.
- **Honesty principle:** missing/withheld data → **visible provenance/placeholder**, never
  silent omission.

## Sandbox gotchas (each cost real cycles)

- `python3 -c "..."` is **DENIED** → use a heredoc: `python3 - <<'EOF' ... EOF`.
- `base64 -d` is **DENIED** → fetch repo file content raw instead of decoding the contents API:
  ```bash
  gh api -H "Accept: application/vnd.github.raw" \
    "repos/<owner>/<repo>/contents/<path>?ref=main"
  ```
- Post-publish, **`raw.githubusercontent.com` and the HF CDN can lag** → verify via `gh api` /
  `HfApi` / the datasets-server API, not the raw CDN.
- Org **Gradio/Docker Spaces need a paid HF plan** (datasets are free). Relevant only if this
  data later gets a viz **Space** — the dataset itself costs nothing.

## Bundled resources

- **`publish_analysis_to_hf.py`** — reusable helper: verifies `hf auth whoami`, creates the
  dataset repo, uploads a prepared folder (parquet + README), then polls the datasets-server
  `/is-valid` to report readiness. Parameterized `--repo-id / --folder / --private`, with a
  `--dry-run`. Run `python3 publish_analysis_to_hf.py --help`.
- **`PROMPT.md`** — a copy-paste, parameterized prompt to hand any agent so it runs this whole
  flow (reshape → card+provenance → sanity-check → publish → verify) while honoring license
  routing, the withhold-and-file-issue data-quality gate, and the keep-separate-from-`-runs`
  convention.
