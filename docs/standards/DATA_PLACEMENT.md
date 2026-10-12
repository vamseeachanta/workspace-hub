# Data Placement Standard

> Single source for generated data, bulky artifacts, cold reference files and lightweight metadata placement.

## Owner Decisions

- L01: "Manifest and fetch only, one content-addressed layout, no history rewrite; retire the Git LFS tier". Owner note: "if too superseded or not used, delete them. If we need them save them to [the primary Linux workstation's data disk]".
- L02 owner note: "what is the important.. do we have redundancy to download data if so.. maintain scripts; if no redundancy for certain data, we need to maintain 2nd copy on [the second Linux workstation]".
- L03: "Keep the contract: originals stay in Git; only derived, generated and regenerable files move".
- L04: "Adopt both as proposed": a tracked non-source file over 1 MB that no code or test references moves regardless of age; a referenced file unchanged for 90 days moves with fetch on demand; under 1 MB stays; public manifests carry relative paths and digests only.
- L05: "Pilot on assetutilities and the strategy repo, then digitalmodel, then the rest".
- L06: "Remove them from the tree now, ahead of the size work; keep copies on the data disk" for published reference PDFs and project-coded presentation material found in a public repo.

## Decision Rule

One mechanism: manifest and fetch. The repository keeps a committed manifest with repo-relative path, bytes, SHA-256 and disposition, plus one fetch script. The bytes live outside Git. No symlinks back into the repo, and no Git LFS.

One layout: content-addressed blobs live at `${ACE_DATA_ROOT}/data/<repo>/blobs/sha256/<first two hex>/<sha256>.<ext>`. The repository's external data root also contains `${ACE_DATA_ROOT}/data/<repo>/MANIFEST.tsv` and a dated verification file beside it.

Data already stored under the earlier per-topic archive layout stays where it is and remains recorded in its own manifest; new moves use the one layout. No conversion duty is introduced.

Private material, including anything client-derived, quarantined or from a private repository, goes under `${ACE_DATA_ROOT}/data/_private/<repo>/` with owner-only directory permissions. A public manifest records private material only as a count and total size; it carries no host names, mount paths, private locators or payload details.

| Criterion | In git repo | Manifest-and-fetch outside Git |
|---|---|---|
| Size | < 10 MB total and below the cold-file rule | >= 10 MB, or will grow past it |
| File count | < 1000 files | >= 1000 files |
| Cold non-source files | Under 1 MB, or still actively referenced within the cold rule | MOVE or DELETE disposition per the cold rule |
| Content type | Source, configs, schemas, scripts, ledgers, small indexes, tests, required originals | Generated outputs, summaries, extracted content, large indexes, cold references |
| Volatility | Changes with human intent | Changes with pipeline runs or can be fetched/restored |
| Sensitivity | Public and non-client metadata | Private payloads under the private layout only |

If a directory will exceed either threshold, 10 MB or 1000 files, it belongs outside Git under the manifest-and-fetch layout. The threshold triggers storage placement; the manifest stays committed.

## Cold Rule

A tracked non-source file over 1 MB that no code or test references moves regardless of age. A referenced file unchanged for 90 days moves with fetch on demand. Under 1 MB stays. Public manifests carry relative paths and digests only.

Heavy text counts: any tracked file over 1 MB that is not source code needs a stated consumer, whether binary or text. Solver text inputs and listings, JSONL indexes, rendered HTML with embedded libraries, images and archives are evaluated the same way.

## Dispositions

| Disposition | Meaning |
|---|---|
| KEEP | The file remains in Git because it is source, a required original, under threshold or actively consumed. |
| SHRINK | A large test fixture is replaced by a cut-down fixture, while the original is stored outside Git. |
| MOVE | The bytes move to the content-addressed layout and are restored through the fetch script. |
| DELETE-REDOWNLOADABLE | The file is removed from Git because the maintained fetch script can reacquire it. |
| DELETE-SUPERSEDED | The file is removed because a newer retained artifact or source makes it obsolete. |
| QUARANTINE-PRIVATE | The file is removed from public surfaces and retained only under the private layout when rights or sensitivity require it. |

## Originals

Client originals stay committed in the owning private repo. Only derived, generated and regenerable files move. Vendor-licensed standards and codes still follow the licensed-location exclusion in the agent data-handling contract and are not committed to Git.

## Repository Manifest

The committed manifest is the reviewable contract for moved bytes. Each payload row records:

- repo-relative path that a consumer expects;
- byte count;
- SHA-256 digest;
- disposition;
- relative content-addressed blob path or `private-summary`;
- whether the file is re-downloadable;
- second-copy status when the file cannot be re-downloaded.

Public manifests carry relative paths and digests only: no host names, mount paths or private locators.

## Fetch and Verification

The repository provides one fetch script that reads the manifest, restores missing bytes on demand, verifies SHA-256 and exits clearly when a file is unavailable. A removal PR merges only after the stored copy is verified, and after the second copy is verified for data that cannot be re-downloaded.

Data that cannot be re-downloaded gets a verified second copy on a second machine's own disk, not a network view of the primary disk, recorded in the manifest. Re-downloadable public data keeps a maintained fetch script instead of a second copy.

## Windows and CI Access

A Windows workstation has no mount of the data disk and fetches on demand over ssh/rsync from the host named in an environment variable; this works from Git Bash. A hosted CI runner cannot reach the store, so the fetch script is a clear no-op with a message there, and any test that needs a fetched file skips with a visible reason. A symlink is not an option on either.

## What Belongs in the Repo

- Configuration files.
- Schema definitions and registries.
- Lightweight JSON indexes and shard metadata below the thresholds.
- Seed data for knowledge bases below the thresholds.
- Extracted calculation code and tests.
- Pipeline checkpoints below the thresholds.
- `.gitkeep` placeholders for empty directories.
- Required client-supplied and measured originals in the owning private repository.
- Compressed state archives produced by the oversized state-file recovery runbook, when kept for consumer-compatible zero-loss state history.

## What Uses Manifest and Fetch

- Generated summaries and extracted text above threshold.
- Bulk document content when source rights allow external storage.
- Large search indexes, including BM25 pickles and JSONL indexes.
- Runtime JSONL logs and notification data.
- Any pipeline output that can be regenerated from source.
- Published reference PDFs and project-coded presentation material removed from public repositories under L06.

## Current Misplaced Data — Relocation Plan

Audit date: 2026-03-31. Items below exceed thresholds and should use the manifest-and-fetch layout.

| Directory | Size | Files | Git-tracked? | Target | Status |
|---|---|---|---|---|---|
| `data/document-index/summaries/` | ~1.5 GB | ~717K | No (gitignored) | `${ACE_DATA_ROOT}/data/workspace-hub/blobs/sha256/` | Pending manifest-and-fetch conversion |
| `data/doc-intelligence/` | 295 MB | ~9K | No (gitignored) | `${ACE_DATA_ROOT}/data/workspace-hub/blobs/sha256/` | Pending manifest-and-fetch conversion |
| `data/standards/promoted/` | 28 MB | varies | No (gitignored) | `${ACE_DATA_ROOT}/data/workspace-hub/blobs/sha256/` | Pending manifest-and-fetch conversion |

### Already Correct or Pending

- `data/document-index/shards/` - 17 MB tracked, over the 10 MB directory threshold; pending manifest-and-fetch review even though the files are lightweight JSON indexes.
- `knowledge/seeds/` - 144 KB, small seed files (correct in repo).
- `knowledge/dark-intelligence/xlsx-poc-v2/` - tracked code/tests, YAML data gitignored (correct split).
- `knowledge-base/` - 380 KB runtime JSONL, already gitignored.

### Relocation Steps (follow-up, not done yet)

For each directory in the relocation plan:

1. Build a manifest with repo-relative path, bytes, SHA-256 and disposition for each payload.
2. Copy each payload into the content-addressed blob layout under `${ACE_DATA_ROOT}/data/<repo>/blobs/sha256/<first two hex>/`.
3. Write or update `${ACE_DATA_ROOT}/data/<repo>/MANIFEST.tsv` and a dated verification file beside it.
4. Add or update the committed manifest and the repository's one fetch script.
5. Verify stored copies by SHA-256; verify the second copy for data that cannot be re-downloaded.
6. Remove the Git-tracked payload only after verification; do not rewrite history.

Removal shrinks the checkout and every worktree, not the clone. Partial clone is the route for clone size.

## Gitignore and Guard Coverage

Moved payload patterns should be covered by `.gitignore` after the committed manifest and fetch script exist. The expected gate in every repository is a `check-added-large-files --maxkb=1000` pre-commit check with an explicit allow-list. This standard states the gate; it does not add the hook here.

## For AI Agents

Before writing output to `data/` or `knowledge/`:

1. Check whether the target is source, a required original, derived/generated/regenerable data, or private material.
2. If output will exceed 10 MB, 1000 files or the cold-file rule, write the bytes to the manifest-and-fetch layout and commit only the manifest/fetch updates.
3. Do not create symlinks back into the repository.
4. If the external data root is unavailable, fail or skip with a visible reason; do not silently substitute a local path.
