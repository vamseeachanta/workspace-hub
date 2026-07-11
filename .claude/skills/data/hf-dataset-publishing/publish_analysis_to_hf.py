#!/usr/bin/env python3
"""
publish_analysis_to_hf.py
=========================

Reusable helper to publish a PREPARED folder of analysis results (parquet tables + a
dataset-card README.md) to Hugging Face as a queryable, viewer-renderable dataset, then verify
readiness via the datasets-server API.

This script does NOT reshape your data or write the card — that is Steps 1 & 2 of the workflow
(see SKILL.md), which are analysis-specific and must include your own provenance + data-quality
gate. This script is Steps 3 & 4: create repo -> upload folder -> verify render surface.

Prerequisites
-------------
- CLI `hf` authenticated (token at ~/.cache/huggingface/token); `hf auth whoami` must succeed.
  (`huggingface-cli` is DEPRECATED — this script uses the `hf` CLI + the huggingface_hub API.)
- Python libs: huggingface_hub (1.21+). Only stdlib is used otherwise.
- Your `--folder` already contains: one or more `*.parquet` tables and a `README.md` whose YAML
  frontmatter has a `configs:` block mapping each table to a viewer config.

Naming convention
-----------------
Repo id MUST be `aceengineer/<repo>-<projection>` (e.g. `aceengineer/worldenergydata-explorer`).
Do NOT publish analysis projections into `aceengineer/<repo>-runs` — that is the separate
contract-managed algorithm-run ledger (workspace-hub#3433).

License / public-vs-private routing
----------------------------------
Per `.claude/rules/codes-standards-data-routing.md`:
  - Public-domain federal data (BSEE/NOAA/USGS) -> public, license cc-by-4.0.
  - Vendor-licensed / private / client data -> NEVER public; private repo only with explicit
    owner sign-off.
  - Synthetic / own-analysis -> publisher's choice.
This script defaults to `--private` OFF only when you pass `--public` explicitly; otherwise it
creates a PRIVATE repo (fail-safe).

Usage
-----
    python3 publish_analysis_to_hf.py \
        --repo-id aceengineer/worldenergydata-explorer \
        --folder ./out \
        --public \
        --commit-message "Publish explorer analysis projection"

    # Preview everything without touching HF:
    python3 publish_analysis_to_hf.py --repo-id aceengineer/foo-bar --folder ./out --dry-run

Security
--------
Never print, echo, or log the HF token. This script only ever reads it implicitly through the
huggingface_hub client / `hf` CLI, which pick it up from ~/.cache/huggingface/token or the
HF_TOKEN env var.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATASETS_SERVER = "https://datasets-server.huggingface.co"


# --------------------------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------------------------
def verify_auth() -> str:
    """Run `hf auth whoami` and return the resolved username. Exit if not authenticated.

    Note: token is NEVER printed. We only surface the username/orgs from whoami output.
    """
    try:
        proc = subprocess.run(
            ["hf", "auth", "whoami"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        sys.exit(
            "ERROR: `hf` CLI not found. Install huggingface_hub (>=1.21) which ships the `hf` "
            "command. (`huggingface-cli` is deprecated.)"
        )
    except subprocess.TimeoutExpired:
        sys.exit("ERROR: `hf auth whoami` timed out.")

    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0 or "not logged in" in out.lower():
        sys.exit(
            "ERROR: not authenticated with Hugging Face.\n"
            "Fix: ensure a token exists at ~/.cache/huggingface/token (or export HF_TOKEN), "
            "then re-run `hf auth whoami`.\n"
            f"whoami said: {out}"
        )
    print(f"[auth] {out}")
    return out


# --------------------------------------------------------------------------------------------
# Folder validation
# --------------------------------------------------------------------------------------------
def validate_folder(folder: Path) -> list[Path]:
    """Confirm the folder holds a README.md and at least one parquet/csv table."""
    if not folder.is_dir():
        sys.exit(f"ERROR: --folder is not a directory: {folder}")

    readme = folder / "README.md"
    if not readme.is_file():
        sys.exit(
            f"ERROR: no README.md dataset card in {folder}. Step 2 of the workflow requires a "
            "card with a YAML `configs:` block. See SKILL.md."
        )

    tables = sorted(list(folder.glob("*.parquet")) + list(folder.glob("*.csv")))
    if not tables:
        sys.exit(f"ERROR: no *.parquet or *.csv tables found in {folder}.")

    # Light sanity check: does the card mention a configs: block?
    card = readme.read_text(errors="replace")
    if "configs:" not in card:
        print(
            "[warn] README.md has no `configs:` block — the HF viewer may not expose each table "
            "as its own config. See SKILL.md Step 2."
        )

    print(f"[folder] {folder}  ->  {len(tables)} table(s): "
          + ", ".join(t.name for t in tables))
    return tables


# --------------------------------------------------------------------------------------------
# Publish
# --------------------------------------------------------------------------------------------
def publish(repo_id: str, folder: Path, private: bool, commit_message: str) -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    print(f"[create_repo] {repo_id} (private={private}) exist_ok=True")
    api.create_repo(
        repo_id=repo_id,
        repo_type="dataset",
        private=private,
        exist_ok=True,
    )
    print(f"[upload_folder] {folder}  ->  {repo_id}")
    api.upload_folder(
        folder_path=str(folder),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=commit_message,
    )
    files = api.list_repo_files(repo_id=repo_id, repo_type="dataset")
    print("[uploaded files]")
    for f in sorted(files):
        print(f"    {f}")


# --------------------------------------------------------------------------------------------
# Verify via datasets-server API
# --------------------------------------------------------------------------------------------
def _get_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": "publish_analysis_to_hf"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": str(e)}
        return e.code, body
    except Exception as e:  # noqa: BLE001
        return None, {"error": str(e)}


def verify_render(repo_id: str, poll_seconds: int = 300, interval: int = 20) -> bool:
    """Poll the datasets-server /is-valid endpoint until the dataset indexes.

    A brand-new dataset returns "server is busier than usual / retry later" for a few minutes.
    Poll — do not assume failure.
    """
    q = urllib.parse.urlencode({"dataset": repo_id})
    url = f"{DATASETS_SERVER}/is-valid?{q}"
    deadline = time.time() + poll_seconds
    print(f"[verify] polling {url}")
    while time.time() < deadline:
        status, body = _get_json(url)
        if status == 200 and isinstance(body, dict):
            # e.g. {"preview": true, "viewer": true, "search": false, "statistics": false}
            if any(body.get(k) for k in ("preview", "viewer", "valid")):
                print(f"[verify] READY: {body}")
                print(f"[verify] viewer:  https://huggingface.co/datasets/{repo_id}/viewer")
                print(f"[verify] rows API: {DATASETS_SERVER}/rows?dataset="
                      f"{urllib.parse.quote(repo_id)}&config=<table>&split=train&offset=0&length=10")
                return True
            print(f"[verify] not ready yet: {body}")
        else:
            # 400/500 during indexing lag is expected right after publish.
            print(f"[verify] indexing lag (status={status}): {body}. retrying in {interval}s...")
        time.sleep(interval)
    print(
        "[verify] TIMEOUT — dataset not confirmed valid within window. This is often just a "
        "longer indexing lag; check the viewer URL in a few minutes:\n"
        f"    https://huggingface.co/datasets/{repo_id}/viewer"
    )
    return False


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(
        description="Publish a prepared analysis-results folder to Hugging Face as a dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--repo-id", required=True,
                   help="aceengineer/<repo>-<projection>  (NOT ...-runs)")
    p.add_argument("--folder", required=True, type=Path,
                   help="Folder holding prepared *.parquet tables + README.md dataset card")
    vis = p.add_mutually_exclusive_group()
    vis.add_argument("--public", action="store_true",
                     help="Create a PUBLIC dataset (only for public-domain federal / synthetic "
                          "data per the routing rule). Default is PRIVATE (fail-safe).")
    vis.add_argument("--private", action="store_true",
                     help="Create a PRIVATE dataset (default).")
    p.add_argument("--commit-message", default="Publish analysis projection",
                   help="Commit message for the upload.")
    p.add_argument("--no-verify", action="store_true",
                   help="Skip the datasets-server /is-valid poll after upload.")
    p.add_argument("--poll-seconds", type=int, default=300,
                   help="Max seconds to poll for indexing (default 300).")
    p.add_argument("--dry-run", action="store_true",
                   help="Validate auth + folder + naming, print the plan, but do NOT create or "
                        "upload anything.")
    args = p.parse_args()

    # Fail-safe default: private unless --public is explicitly passed.
    private = not args.public

    # Naming guardrails.
    if not args.repo_id.startswith("aceengineer/"):
        print(f"[warn] repo-id '{args.repo_id}' is not under the aceengineer/ org.")
    if args.repo_id.endswith("-runs"):
        sys.exit(
            "ERROR: repo-id ends with '-runs'. That namespace is the contract-managed "
            "algorithm-run ledger (workspace-hub#3433). Analysis projections get their own "
            "'<repo>-<projection>' dataset. Rename and re-run."
        )

    print("=" * 78)
    print("Hugging Face analysis-result dataset publisher")
    print(f"  repo-id : {args.repo_id}")
    print(f"  folder  : {args.folder}")
    print(f"  private : {private}  ({'PUBLIC' if not private else 'PRIVATE'})")
    print(f"  dry-run : {args.dry_run}")
    print("=" * 78)

    verify_auth()
    validate_folder(args.folder)

    if args.dry_run:
        print("\n[dry-run] Plan:")
        print(f"  1. create_repo({args.repo_id}, repo_type=dataset, private={private}, exist_ok=True)")
        print(f"  2. upload_folder({args.folder} -> {args.repo_id})")
        if not args.no_verify:
            print(f"  3. poll {DATASETS_SERVER}/is-valid?dataset={args.repo_id}")
        print("[dry-run] No changes made.")
        return 0

    publish(args.repo_id, args.folder, private, args.commit_message)

    if not args.no_verify:
        verify_render(args.repo_id, poll_seconds=args.poll_seconds)

    print(f"\nDone. Dataset: https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
