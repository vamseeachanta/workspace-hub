# Read-only duplicate inventory and plan

The pipeline records content evidence and writes a proposed dedupe plan. It never
deletes, moves, renames, links or writes scanned files. Removal requires a separate
explicit decision by the maintainer. Runtime inputs choose roots and free-text
labels; the tool does not discover a system name.

## Pipeline

Use Python 3.11 or later; runtime code uses only the standard library.

~~~sh
python -I scripts/dedupe/hash_inventory.py --config A.config.json --label A --out A.manifest.jsonl --cache A.cache.json
python -I scripts/dedupe/hash_inventory.py --config B.config.json --label B --out B.manifest.jsonl --cache B.cache.json --max-seconds 60
python -I scripts/dedupe/merge_manifests.py A.manifest.jsonl B.manifest.jsonl --out groups.json
python -I scripts/dedupe/dedupe_plan.py groups.json --policy policy.json --out plan.md --out-json plan.json
~~~

The example budget of 60 seconds is a user-selected illustration, not an acceptance
limit. Inventory exits successfully only for a complete scan; an incomplete
inventory exits with status 1 after saving results. Invalid input or output
failure exits with status 2. These are application conventions, not measurements.
A budget is cooperative: it is checked during traversal and between reads. It
cannot interrupt a blocked filesystem operation. Re-running the same command with
its cache resumes hashing; traversal still runs again.

All outputs, including caches, must be outside scanned roots. Inventory rejects
overlapping roots, symlink roots, destinations within roots and existing output
hard links to scanned files. Each command also rejects destinations that alias its
inputs or each other. Keep merge and plan outputs outside the original roots too:
portable manifests intentionally omit absolute root locations, so those later
commands cannot rediscover root boundaries.

## Schema and performance conventions

These conventions implement the issue specification (#4224).
The initial format version is 1. Numeric example inputs below are constructed
fixtures; they impose no acceptance limits.

Configuration:

~~~json
{
  "roots": ["example/A"],
  "min_size_bytes": 0,
  "exclude": ["*.tmp", "cache", "cache/*"],
  "follow_symlinks": false
}
~~~

- roots: nonempty ordered array of existing, nonoverlapping directories. Manifest
  root is the zero-based index in this array; path is relative to that root.
  Manifest paths use forward slashes as separators; legal POSIX colons and
  backslashes remain literal filename characters when read on other systems.
  Labels should uniquely identify a root configuration when merging inventories.
- min_size_bytes: nonnegative integer, inclusive; default 0 includes empty files.
  A previous large-file survey used 200 MB; this is an example threshold only,
  not the default or a recommendation. Supply the desired byte count explicitly.
- exclude: optional case-sensitive fnmatch globs on relative POSIX paths;
  default empty. A matched directory is pruned. An asterisk can match a slash.
- follow_symlinks: only false is accepted. Symlinks, directory junctions, other
  reparse points and special files are skipped.

Staged hashing:

1. Group all files in a run by exact byte size. Size singletons are not opened.
2. For size collisions, hash the concatenation of the first and last **64 KiB**
   using SHA-256. A KiB here is 1024 bytes. When a file is shorter than a sampling
   window, its whole content appears twice in this sample input.
3. For collisions in both size and sample digest, hash the entire file with
   **1 MiB** reads (1024 × 1024 bytes), using SHA-256.

The window and read chunk sizes are application-selected performance defaults
defined by this README, not correctness thresholds. Sampling can reject
duplicates, but cannot prove them. SHA-256 follows [FIPS 180-4 (2015), section 6.2](https://doi.org/10.6028/NIST.FIPS.180-4);
its 256-bit output is represented by 64 hexadecimal digits (256 / 4).
The chunked hashlib read/update approach follows the existing
scripts/data/document-index/cross-drive-dedup-audit.py helper. That helper's fixed
root configuration prevents importing it into this generic tool; its code remains
unchanged. Other inspected dedupe helpers operate on document sections or a
database and require extra dependencies.

JSONL begins with a manifest header, followed by one object per observed file:

~~~json
{"type":"manifest","version":1,"label":"A","complete":true,"errors":[]}
{"label":"A","root":0,"path":"one","size":3,"mtime":1,"sha256":null,"sample_sha256":null,"stage":"size"}
~~~

mtime is integer nanoseconds since the filesystem epoch (st_mtime_ns), avoiding
floating-point cache-key rounding. The value 1 in this schema example is synthetic.
stage is size, sample or full; sha256 is non-null only for successful full
hashes. sample_sha256 is null until sampled. Metadata-read failures use null size
and mtime plus an error class name. Read failures preserve known size and mtime.
A file changed while hashing is invalidated; a final metadata pass also checks
earlier records. No exception text or absolute source path is emitted in errors.
Directory errors are in header errors. Any error or budget stop sets
complete to false; a budget stop also sets stop_reason to budget.

### Cache and atomic output

The cache is local runtime evidence, not a portable manifest or authentication
mechanism. Keys contain root index, relative path, size and nanosecond mtime.
Entries additionally check device, inode and ctime to reduce accidental stale
reuse. A context digest binds the ordered root locations, format, algorithm and
sampling window. Changed metadata triggers rehashing; previously sampled files
can advance to a full hash if new collisions appear. Finished samples and hashes
are cached even when the budget expires. Reuse assumes a trusted local cache.

Each output is written to an adjacent tool-owned temporary file, flushed, synced
and replaced using [Python 3.11 os.replace](https://docs.python.org/3.11/library/os.html#os.replace).
This is the sole allowed filesystem replacement. Failure before replacement keeps
the previous destination intact and may leave a .partial file for diagnosis.
The cache, manifest and two plan formats are individually atomic, not a multi-file
transaction. A successful cache save can therefore precede a failed manifest save.

### Merged groups and totals

groups.json has across_labels, within_label, candidate_groups, totals,
errors, scan_errors and incomplete_labels.

Only error-free full hashes from complete manifests form verified groups, keyed
on (size, sha256). An incomplete manifest's full hash is never promoted to
verified evidence. Its entries can appear only in size/sample candidate groups.
If any entry of a size lacks a sample, candidates use size alone; otherwise
candidate groups use (size, sample_sha256). Candidates can include complete
records to expose possible cross-inventory matches. They never enter verified
totals or removal proposals.

For each verified group, retaining one copy gives (file_count - 1) × size bytes
of theoretical reclaimable content. totals.verified covers every verified group;
totals.across_labels covers groups spanning labels; totals.within_label covers
groups confined to one label. All report groups, files, bytes_reclaimable.
per_label instead counts duplicates among that label's copies, even inside a
cross-label group; these local totals overlap the other categories and must not
be added to them. They are not filesystem free-space predictions.

The independent fixture in tests/dedupe/test_merge.py uses three labels:
three equal size-10 files across A/A/B give (3−1)×10 = 20 bytes; two equal size-4
files within C give (2−1)×4 = 4 bytes. Total: two groups, five files, 24 bytes.
Local savings are A=10, B=0 and C=4 bytes.

### Policy and verification commands

~~~json
{
  "keep_preference": [
    {"labels": ["A", "B"]},
    {"path_prefixes": ["archive/", "documents/"]},
    "shorter_path",
    "older_mtime"
  ],
  "protect": ["retained/*", "B:0/legal/*"]
}
~~~

keep_preference is an ordered list of criteria. Earlier labels or prefixes rank
first; unmatched entries rank after matched entries. Prefix matching is literal.
shorter_path ranks by character count, older_mtime by smaller nanosecond mtime.
The final deterministic tie-break is label, root index, relative path.
An empty preference list uses only that final tie-break.

protect globs match either a relative path or label:root/path. If any copies
are protected, choose the keeper among those copies using the ordered preferences;
every other protected copy is retained. If all copies are protected, no removal
candidates are proposed. Otherwise every verified, unprotected non-keeper becomes
a REMOVAL CANDIDATE with a reason. Candidate groups are counted but excluded.
Malformed verified groups, including incomplete evidence, are rejected.

Plan root bindings use ordinal shell variables starting at ROOT_1. Bind these
yourself to the original root locations before using the quoted sha256sum
commands. Every candidate has a command hashing both keeper and candidate, plus
the expected digest. Compare both actual results to that digest immediately before
any independently authorized action. For roots on separate systems, run the two
hashes at their respective roots and compare the results manually. The tool does
not transfer files, execute commands or require sha256sum to generate a plan.
Markdown commands containing line separators are withheld because Markdown
readers can normalize filename characters. The exact command remains in JSON;
inspect it without newline normalization before independent verification.

## Worked temporary-tree example

Run the following from the repository root. The temporary directory is supplied
by the calling environment. All output is a sibling of the scanned directories.

~~~sh
python - <<'PY'
import json
import os
from pathlib import Path

example = Path(os.environ["TMPDIR"]) / "dedupe-example"
for label in ("A", "B"):
    root = example / label
    root.mkdir(parents=True, exist_ok=True)
    for name in ("one", "two"):
        (root / name).write_bytes(b"abc")
    config = {"roots": [str(root)], "follow_symlinks": False}
    (example / (label + ".config.json")).write_text(
        json.dumps(config), encoding="utf-8", newline="\n"
    )
(example / "policy.json").write_text(json.dumps({
    "keep_preference": [{"labels": ["A", "B"]}, "shorter_path", "older_mtime"],
    "protect": []
}), encoding="utf-8", newline="\n")
PY
example="$TMPDIR/dedupe-example"
python -I scripts/dedupe/hash_inventory.py --config "$example/A.config.json" --label A --out "$example/A.manifest.jsonl" --cache "$example/A.cache.json"
python -I scripts/dedupe/hash_inventory.py --config "$example/B.config.json" --label B --out "$example/B.manifest.jsonl" --cache "$example/B.cache.json"
python -I scripts/dedupe/merge_manifests.py "$example/A.manifest.jsonl" "$example/B.manifest.jsonl" --out "$example/groups.json"
python -I scripts/dedupe/dedupe_plan.py "$example/groups.json" --policy "$example/policy.json" --out "$example/plan.md" --out-json "$example/plan.json"
~~~

Manifest excerpt (mtime is replaced below by a descriptive placeholder):

~~~text
{"label":"A","root":0,"path":"one","size":3,"mtime":<filesystem nanoseconds>,"sha256":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","stage":"full",...}
~~~

The digest is the [NIST SHA-256 worked example, “One Block Message Sample”](https://csrc.nist.gov/CSRC/media/Projects/Cryptographic-Standards-and-Guidelines/documents/examples/SHA256.pdf)
for abc. There are four copies of three bytes: one group, four files,
(4−1)×3 = 9 bytes of theoretical savings and three removal candidates.

Plan excerpt:

~~~text
**Nothing has been deleted. Removal needs a separate explicit decision by the maintainer. Recheck both files immediately before any action.**

Keep: ["A", 0, "one"].
REMOVAL CANDIDATE: ["B", 0, "one"]. Reason: keep preference: label order.
Expected SHA-256 for both: ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
    sha256sum -- "${ROOT_1}"/one "${ROOT_2}"/one
~~~

A and B each have two equal files so both inventories can fully hash them.
If each label instead has only one file of a size, those files remain size-only
candidates across inventories. To verify them, run a combined local inventory of
the relevant roots, or collect additional full hashes in a separately reviewed
workflow; this tool does not silently read another root.

## Tests and limits

~~~sh
uv run --no-project --with pytest python -m pytest tests/dedupe -q -rA -p no:cacheprovider
uv run --no-project --with ruff ruff check scripts/dedupe tests/dedupe
~~~

Expected values come from the cited NIST example or independent constructed
fixtures and hand calculations written in test docstrings. The pipeline test
snapshots the entire temporary input tree before and after execution and compares
names, sizes, mtimes and independently computed content hashes. The static test
inspects every package module for mutation calls and permits only the explicitly
named atomic output replacement.

Hard links and bind mounts are not detected or discounted as duplicate copies.
Theoretical byte totals may therefore overstate physical savings. Output
hard-link rejection is a safety check, not hard-link inventory accounting.
Hash equality is evidence of content equality, not metadata equality; it assumes
SHA-256 collision resistance. Empty files can be duplicates with zero savings.
Reads may update access times under filesystem policy; the tool does not set them.
The files are not a filesystem snapshot: concurrent edits after validation, or
deliberate changes preserving metadata, require immediate human re-verification.
Optional nonsymlink/nonblocking open flags are used where the platform provides
them; weaker platforms cannot give the same race resistance. No cross-system
transport, path discovery or authentication is provided. Inventories and grouping
are held in memory; a very large directory can exceed the cooperative budget
while its entries are being listed and sorted.
