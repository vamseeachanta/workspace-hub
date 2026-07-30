# Copy-paste prompt — Save analysis results to Hugging Face

Fill in `<analysis>`, `<input>`, `<repo>`, `<projection>`, then paste to any agent. It uses the
generic tool `scripts/hf/save_results_to_hf.py` (auto-discovers tables, reshapes, cards, publishes,
verifies) and the `data/hf-dataset-publishing` skill. The agent's judgment is only needed for the
license call and the data-quality gate.

---

Save the results of **`<analysis>`** from the **`<repo>`** repo to Hugging Face as a queryable
dataset `aceengineer/<repo>-<projection>`, using `scripts/hf/save_results_to_hf.py` and the
`data/hf-dataset-publishing` skill. Do this in order, reporting each step:

**0. Auth (never print the token).** Confirm `hf auth whoami` (expect `orgs` includes `aceengineer`).
The CLI is `hf` — not the deprecated `huggingface-cli`.

**1. Dry-run first** — auto-discover the tables and see the data-quality stats:
```
python scripts/hf/save_results_to_hf.py \
  --repo-id aceengineer/<repo>-<projection> \
  --input <files-or-dirs: json/csv/parquet> \
  --source-repo <repo> --algorithm "<name@version>" \
  --dry-run
```
Report the discovered tables (rows × cols) and the printed **per-column numeric stats**.

**2. DATA-QUALITY GATE — eyeball the stats (faithful-to-source != correct).** If any value is
implausible for the domain (absurd min/max, wrong sign, impossible ratio), do NOT publish it as-is:
drop/withhold that source column, **file a `cat:data`/bug issue in `<repo>`**, and note the
withholding. Never silently omit — a withheld column must be visible in the card.

**3. License / public-vs-private** (`.claude/rules/codes-standards-data-routing.md`):
- Public-domain **federal** (BSEE/NOAA/USGS) → add `--public --license cc-by-4.0`.
- **Vendor-licensed / private / client** → keep PRIVATE (omit `--public`); public only with explicit
  owner sign-off.
- **Synthetic / own analysis** → your call. Unsure of provenance → PRIVATE, and ask.

**4. Publish** — same command without `--dry-run` (add `--public` only per step 3):
```
python scripts/hf/save_results_to_hf.py --repo-id aceengineer/<repo>-<projection> \
  --input <...> --source-repo <repo> --algorithm "<name@version>" [--public]
```

**5. Verify.** The script prints the dataset URL + the datasets-server `/is-valid` link. Then poll
`https://datasets-server.huggingface.co/rows?dataset=aceengineer/<repo>-<projection>&config=<table>&split=train&offset=0&length=10`
— indexing lags a few minutes on a brand-new dataset ("server is busier than usual"); poll, don't
assume failure.

**Guardrails you MUST honor:**
- Name it `aceengineer/<repo>-<projection>`. The tool **refuses `-runs` targets** (that's the
  wh#3433 contract-managed algorithm-run ledger) — do not work around that.
- Never print / echo / commit the HF token.
- Sandbox: `python3 -c "..."` is DENIED → use `python3 - <<'EOF'` heredocs. `base64 -d` is DENIED →
  fetch repo files with `gh api -H "Accept: application/vnd.github.raw" "repos/<owner>/<repo>/contents/<path>?ref=main"`.
  Verify via `gh api` / `HfApi` / datasets-server — not the lagging `raw.githubusercontent.com` / HF CDN.

**Report back:** the dataset URL, the tables + row counts, any withheld columns + the issue filed,
and the `/is-valid` result.
