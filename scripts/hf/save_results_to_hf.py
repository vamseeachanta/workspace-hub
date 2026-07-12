#!/usr/bin/env python3
# ABOUTME: Generic tool to save ANY repo/algorithm's results to a Hugging Face dataset.
# ABOUTME: Auto-discovers tables from arbitrary nested JSON/CSV/parquet, reshapes to
# ABOUTME: parquet, writes a viewer-ready dataset card with provenance, publishes, verifies.
"""
save_results_to_hf.py — one command to publish analysis/computation results to Hugging Face.

    python save_results_to_hf.py --repo-id aceengineer/<repo>-<projection> \
        --input results.json [more.csv data.parquet a_dir/ ...] \
        [--public] [--license cc-by-4.0] [--title "..."] \
        [--source-repo owner/repo] [--algorithm "name@version"] [--dry-run]

Design goals (why this is generic):
  * Accepts arbitrary nested JSON, CSV/TSV, parquet, or directories of those.
  * Auto-discovers tables: every list-of-dicts and dict-of-dicts (recursing through
    wrapper dicts) becomes a table; nested scalars flatten to dotted columns; anything
    deeper is JSON-stringified (lossless).
  * Sanitizes NaN/inf -> null. Writes parquet (HF datasets-server auto-renders it).
  * Emits a dataset card with a viewer `configs:` block + sha256 provenance.
  * PRIVATE by default (fail-safe); --public only for redistributable data.
  * Verifies via list_repo_files + the datasets-server /is-valid API.

DATA-QUALITY REMINDER (printed at the end): faithful-to-source != correct. A generic
tool cannot judge domain plausibility — it prints per-column stats so YOU can eyeball
outliers; withhold implausible columns + file an issue before trusting a public dataset.
See workspace-hub/.claude/skills/data/hf-dataset-publishing/ and the license routing rule
.claude/rules/codes-standards-data-routing.md before going --public.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path


def _flatten(rec, prefix="", out=None):
    """Recursively flatten nested dicts into dotted keys; JSON-stringify lists/other."""
    out = {} if out is None else out
    for k, v in rec.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            _flatten(v, key + ".", out)
        elif isinstance(v, list):
            out[key] = json.dumps(v, ensure_ascii=False)  # lossless, viewer shows text
        else:
            out[key] = v
    return out


def _is_list_of_dicts(v):
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, dict) for x in v)


def _is_dict_of_dicts(v):
    return isinstance(v, dict) and len(v) > 0 and all(isinstance(x, dict) for x in v.values())


def discover_tables(obj, name=""):
    """Return {table_name: [row_dict, ...]} for every table-like structure found."""
    tables = {}

    def walk(v, nm):
        if _is_list_of_dicts(v):
            tables[nm or "records"] = [_flatten(r) for r in v]
        elif _is_dict_of_dicts(v):
            rows = []
            for k, r in v.items():
                fr = _flatten(r)
                rows.append({"_id": k, **fr})
            tables[nm or "records"] = rows
            # also recurse in case a value hides deeper tables (rare) — skip to avoid dup
        elif isinstance(v, dict):
            for k, sub in v.items():
                walk(sub, f"{nm}.{k}" if nm else k)
        # scalars / list-of-scalars at the top level are ignored (not a table)

    walk(obj, name)
    return tables


def _sanitize_df(df):
    import numpy as np
    # inf -> NaN so parquet stores it as null; keep native dtypes (numeric stays numeric,
    # so parquet nulls are native AND numeric_stats can profile columns). json.loads already
    # turned any literal NaN token into float('nan'), which parquet writes as null.
    return df.replace([np.inf, -np.inf], np.nan)


def _sha256(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def ingest(inputs):
    """Yield (table_name, DataFrame, source_path) for every input."""
    import pandas as pd
    paths = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            paths += [q for q in p.rglob("*") if q.suffix.lower() in
                      (".json", ".csv", ".tsv", ".parquet")]
        else:
            paths.append(p)
    for p in paths:
        s = p.suffix.lower()
        if s == ".json":
            obj = json.loads(p.read_text())
            tabs = discover_tables(obj, p.stem)
            if not tabs:  # flat object -> single one-row table
                tabs = {p.stem: [_flatten(obj)] if isinstance(obj, dict) else []}
            for nm, rows in tabs.items():
                yield _clean_name(nm), pd.DataFrame(rows), str(p)
        elif s in (".csv", ".tsv"):
            yield _clean_name(p.stem), pd.read_csv(p, sep="\t" if s == ".tsv" else ","), str(p)
        elif s == ".parquet":
            yield _clean_name(p.stem), pd.read_parquet(p), str(p)


def _clean_name(nm):
    return "".join(c if (c.isalnum() or c in "-_") else "_" for c in nm).strip("_").lower() or "table"


def build_card(repo_id, tables_meta, source_hashes, license_, title, source_repo,
               algorithm, card_note=None):
    cfg = "\n".join(f"- config_name: {t}\n  data_files: {t}.parquet" for t in tables_meta)
    rows = "\n".join(f"| `{t}` | {m['rows']} | {m['cols']} |" for t, m in tables_meta.items())
    prov = "\n".join(f"- `{Path(sp).name}` — sha256 `{h[:16]}…`" for sp, h in source_hashes.items())
    pretty = title or repo_id.split("/")[-1]
    # Data-quality gate disclosures (withheld columns/tables + issue links) MUST be
    # visible in the card per the gate — never silently omit. Caller supplies via --card-note.
    note_block = f"\n## Data-quality notes\n\n{card_note}\n" if card_note else ""
    return f"""---
license: {license_}
pretty_name: {pretty}
tags:
- analysis-results
configs:
{cfg}
---

# {pretty}

Analysis/computation results published for query + visualization via the Hugging Face
datasets-server API. Generated by `scripts/hf/save_results_to_hf.py`.

## Tables

| config | rows | cols |
|---|---|---|
{rows}
{note_block}
## Provenance

- Source repo: `{source_repo or 'n/a'}`  ·  algorithm: `{algorithm or 'n/a'}`
- Schema version: `1.0.0`
- Source snapshots (sha256):

{prov}

Nulls are genuine missing values (non-finite floats were coerced to null). Load a table:
`pandas.read_parquet(hf_hub_download("{repo_id}", "<config>.parquet", repo_type="dataset"))`.
"""


def numeric_stats(name, df):
    import pandas as pd
    num = df.select_dtypes(include="number")
    lines = []
    for c in num.columns:
        col = pd.to_numeric(num[c], errors="coerce")
        # mean + negative-count surface wrong-sign / impossible-ratio errors that a
        # min/max alone hides (a sign flip mid-distribution, a rate > 1, etc.).
        neg = int((col < 0).sum())
        mean = col.mean()
        lines.append(f"    {name}.{c}: min={col.min()} max={col.max()} mean={mean} "
                     f"neg={neg} nulls={int(col.isna().sum())}")
    return lines


def main():
    ap = argparse.ArgumentParser(description="Publish any repo/algorithm's results to a HF dataset.")
    ap.add_argument("--repo-id", required=True, help="aceengineer/<repo>-<projection> (NOT <repo>-runs)")
    ap.add_argument("--input", nargs="+", required=True, help="json/csv/tsv/parquet files or dirs")
    ap.add_argument("--public", action="store_true", help="publish PUBLIC (default: private fail-safe)")
    ap.add_argument("--license", default="cc-by-4.0")
    ap.add_argument("--title", default=None)
    ap.add_argument("--source-repo", default=None)
    ap.add_argument("--algorithm", default=None)
    ap.add_argument("--card-note", default=None,
                    help="Markdown appended to the card as a 'Data-quality notes' section "
                         "(REQUIRED to disclose any withheld column/table + issue link per the gate)")
    ap.add_argument("--withhold", default=None,
                    help="comma-separated column names the data-quality gate flagged implausible: "
                         "DROP them from every table before publishing (preserves source provenance — "
                         "do NOT hand-edit inputs) and auto-disclose them in the card")
    ap.add_argument("--withhold-issue", default=None,
                    help="URL of the cat:data/bug issue filed for the withheld columns (shown in the card)")
    ap.add_argument("--out", default=None, help="staging dir (default: temp)")
    ap.add_argument("--dry-run", action="store_true", help="build + report, do NOT publish")
    args = ap.parse_args()
    withhold = {c.strip() for c in (args.withhold or "").split(",") if c.strip()}

    if args.repo_id.rstrip("/").endswith("-runs"):
        sys.exit("REFUSED: '-runs' is the contract-managed algorithm-run ledger (wh#3433). "
                 "Use a distinct projection name.")

    import tempfile
    import pandas as pd
    out = Path(args.out or tempfile.mkdtemp(prefix="hf_results_"))
    out.mkdir(parents=True, exist_ok=True)

    tables_meta, source_hashes, stat_lines = {}, {}, []
    withheld_hits = {}  # col -> [tables it was dropped from]
    for name, df, src in ingest(args.input):
        if df.empty:
            print(f"  skip empty table: {name}")
            continue
        df = _sanitize_df(df)
        dropped = [c for c in df.columns if c in withhold]
        if dropped:
            df = df.drop(columns=dropped)
            for c in dropped:
                withheld_hits.setdefault(c, []).append(name)
        base = name
        i = 1
        while base in tables_meta:  # de-dup names
            i += 1; base = f"{name}_{i}"
        df.to_parquet(out / f"{base}.parquet", index=False)
        tables_meta[base] = {"rows": len(df), "cols": df.shape[1]}
        source_hashes[src] = _sha256(src)
        stat_lines += numeric_stats(base, df)
        drop_msg = f"  (withheld: {dropped})" if dropped else ""
        print(f"  table {base}: {len(df)} rows x {df.shape[1]} cols  (from {Path(src).name}){drop_msg}")

    if not tables_meta:
        sys.exit("No tables discovered from the inputs.")

    # Fail-closed: a withheld column that never matched any table is almost certainly a
    # typo — better to stop than to publish thinking a bad column was dropped when it wasn't.
    unmatched = withhold - set(withheld_hits)
    if unmatched:
        sys.exit(f"--withhold names no column in any table: {sorted(unmatched)}. Check the names.")

    # Auto-disclose withheld columns in the card (never silently omit — the gate's core promise).
    card_note = args.card_note
    if withheld_hits:
        issue = f" — see {args.withhold_issue}" if args.withhold_issue else " (file a cat:data issue)"
        wl = "\n".join(f"- `{c}` withheld from: {', '.join(sorted(set(t)))}" for c, t in withheld_hits.items())
        wblock = ("**Withheld columns** (dropped by the data-quality gate as implausible; the "
                  f"source retains them){issue}:\n\n{wl}")
        card_note = f"{card_note}\n\n{wblock}" if card_note else wblock

    card = build_card(args.repo_id, tables_meta, source_hashes, args.license,
                      args.title, args.source_repo, args.algorithm, card_note)
    (out / "README.md").write_text(card)
    print(f"\nstaged {len(tables_meta)} tables + README.md in {out}")
    print("\n--- numeric column stats (EYEBALL for implausible values — faithful != correct) ---")
    print("\n".join(stat_lines) or "    (no numeric columns)")

    if args.dry_run:
        print(f"\n[dry-run] would publish to {args.repo_id} "
              f"({'PUBLIC' if args.public else 'PRIVATE'}). Nothing uploaded.")
        return

    from huggingface_hub import HfApi
    from huggingface_hub.utils import HfHubHTTPError
    api = HfApi()
    who = api.whoami()
    print(f"\nauth ok: {who.get('name')}  (orgs: {[o['name'] for o in who.get('orgs', [])]})")
    # whoami confirms IDENTITY, not WRITE scope. A read-only token passes every step
    # above and only fails here — catch it and give a clear, actionable diagnosis
    # instead of an opaque 401/403 traceback.
    try:
        api.create_repo(repo_id=args.repo_id, repo_type="dataset",
                        private=not args.public, exist_ok=True)
        info = api.upload_folder(
            folder_path=str(out), repo_id=args.repo_id, repo_type="dataset",
            commit_message=f"results via save_results_to_hf.py ({args.source_repo or 'n/a'})")
    except HfHubHTTPError as e:
        code = getattr(getattr(e, "response", None), "status_code", None)
        if code in (401, 403):
            sys.exit(f"AUTH: the HF token lacks WRITE scope for {args.repo_id} (HTTP {code}). "
                     "Create a WRITE token at https://huggingface.co/settings/tokens and retry.")
        raise
    rev = getattr(info, "oid", None) or getattr(info, "commit_id", None)
    print(f"published: https://huggingface.co/datasets/{args.repo_id}  "
          f"({'PUBLIC' if args.public else 'PRIVATE'})  revision={rev}")
    # Verify the bytes actually landed (don't just trust the upload return).
    files = set(api.list_repo_files(repo_id=args.repo_id, repo_type="dataset", revision=rev))
    expected = {"README.md"} | {f"{t}.parquet" for t in tables_meta}
    missing = expected - files
    if missing:
        sys.exit(f"VERIFY FAILED: expected files missing at revision {rev}: {sorted(missing)}")
    print(f"verified {len(expected)} files on the remote at revision {rev}.")
    print(f"is-valid (indexing lags a few min — poll, don't assume failure): "
          f"https://datasets-server.huggingface.co/is-valid?dataset={args.repo_id}")
    for t in tables_meta:
        print(f"  rows[{t}]: https://datasets-server.huggingface.co/rows"
              f"?dataset={args.repo_id}&config={t}&split=train&offset=0&length=10")
    print("\nREMINDER: sanity-check the values above. Withhold implausible columns (--withhold) + file a "
          "cat:data issue before trusting a public dataset (faithful-to-source != correct).")


if __name__ == "__main__":
    main()
