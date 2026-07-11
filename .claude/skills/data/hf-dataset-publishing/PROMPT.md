# Copy-paste prompt — Publish analysis results to Hugging Face

Fill in `<analysis>`, `<repo>`, and `<projection>`, then paste this to any agent. It runs the
full proven flow: reshape → dataset card + provenance → data-quality sanity-check → publish →
verify. It honors license routing, the withhold-and-file-issue data-quality gate, and the
keep-separate-from-`-runs` convention.

---

Save the results of **`<analysis>`** (from the **`<repo>`** repo) to Hugging Face as a
queryable, viewer-renderable dataset named **`aceengineer/<repo>-<projection>`**. Use the
`data/hf-dataset-publishing` skill and its bundled `publish_analysis_to_hf.py`. Do the following,
in order, and report each step:

**0. Auth (do NOT print the token).** Confirm `hf auth whoami` succeeds (expect
`user=<u>`, orgs include `aceengineer`). The CLI is `hf` — do NOT use the deprecated
`huggingface-cli`.

**1. Reshape → flat parquet tables (one per entity).** Load the `<analysis>` output. Build one
`pandas.DataFrame` per entity type (e.g. fields / wells / countries). Keep SCALAR columns only —
flatten a few useful nested scalars, skip list/dict columns. Sanitize non-finite floats
(`NaN`/`inf`) to genuine nulls. Write each table as `<table>.parquet` into a clean output folder.

**2. Dataset card `README.md`.** Write YAML frontmatter with `license:` (per routing below),
`pretty_name`, `tags`, and a `configs:` block — one `config_name` + `data_files` entry per
parquet table. In the body: what it is; a table of configs + row counts; **provenance** (source
file **sha256** hashes + a `schema_version`); the data basis + units; and a note that nulls are
genuine (non-finite values were coerced to null).

**3. DATA-QUALITY GATE — sanity-check the actual VALUES, not just row counts.**
> Faithful to source != correct.
Run a domain plausibility check on the numbers. If any values are implausible (e.g. absurd
breakevens on producing fields), **withhold those columns**, file a `cat:data` / bug issue in
`<repo>`, note the withholding + issue link in the card, and continue with the safe columns.
Never silently omit — missing/withheld data must be visible in the card.

**4. License / public-vs-private routing** (cite `.claude/rules/codes-standards-data-routing.md`):
- Public-domain **federal** data (BSEE/NOAA/USGS) → **public**, `license: cc-by-4.0`.
- **Vendor-licensed / private / client** data → **NOT public**; private repo only with explicit
  owner sign-off.
- **Synthetic / own-analysis** → publisher's choice.
- Unsure of provenance → default **private** and ask the owner before going public.

**5. Publish.** Run the bundled helper (dry-run first):
```
python3 publish_analysis_to_hf.py --repo-id aceengineer/<repo>-<projection> --folder <out> [--public] --dry-run
python3 publish_analysis_to_hf.py --repo-id aceengineer/<repo>-<projection> --folder <out> [--public]
```
(Omit `--public` for anything non-federal/non-synthetic — the helper defaults to PRIVATE.)

**6. Verify the render surface.** `HfApi.list_repo_files` to confirm parquet + README landed,
then poll the datasets-server: `https://datasets-server.huggingface.co/is-valid?dataset=<id>` and
`.../rows?dataset=<id>&config=<table>&split=train&offset=0&length=10`. **Indexing lags a few
minutes on a brand-new dataset** ("server is busier than usual") — poll, don't assume failure.

**Conventions & guardrails you MUST honor:**
- Name it `aceengineer/<repo>-<projection>` (datasets on the org are free).
- Do **NOT** publish into `aceengineer/<repo>-runs` — that is the separate contract-managed
  algorithm-run ledger (workspace-hub#3433). Projections get their own dataset.
- Never print/echo/commit the HF token.
- Sandbox: `python3 -c "..."` is DENIED — use `python3 - <<'EOF'` heredocs. `base64 -d` is
  DENIED — fetch repo files via `gh api -H "Accept: application/vnd.github.raw"
  "repos/<owner>/<repo>/contents/<path>?ref=main"`. Verify via `gh api` / `HfApi` /
  datasets-server API, not the lagging `raw.githubusercontent.com` / HF CDN.

**Report back:** the dataset URL, the configs + row counts, any withheld columns + the issue you
filed, and the `/is-valid` result.
