# Private find catalog

The catalog joins owner metadata in one SQLite FTS5 database. Source payloads
remain with their owners. Every returned record carries its source, owner ID,
locator, domain, exposure class, units when supplied, and observed provenance.
Catalog presence does not qualify a record for engineering calculations.

Run from the repository root with a configuration stored outside Git:

```sh
uv run --no-project --with pyyaml python scripts/data/find_catalog/cli.py inventory
uv run --no-project --with pyyaml python scripts/data/find_catalog/cli.py build
uv run --no-project --with pyyaml python scripts/data/find_catalog/cli.py find \
  "RAO heave" --domain marine --source response-atlas --exposure internal
```

Set `FIND_CATALOG_CONFIG` to the private YAML configuration, or pass `--config`
before the command. No default index or source path is embedded in the code.

The configuration has `version: 1`, a `database` path and a nonempty `sources`
list. Relative paths resolve beside that configuration; environment variables
are expanded and unresolved variables are rejected. Each source requires:

| Key | Meaning |
| --- | --- |
| `id` | Source selector; reuse the registered source ID where one exists |
| `kind` | One adapter from the table below |
| `path` | Private configured metadata file or directory |
| `domain` | Fallback domain when the owner metadata supplies none |
| `exposure` | `public`, `internal` or `restricted`; no automatic promotion |
| `owner` | Optional authoritative owner; defaults to the source selector |
| `revision` | Optional pinned owner revision; otherwise `unknown` |
| `sha256` | Optional expected metadata-file SHA-256; disagreement aborts import |

Table 1. Configuration fields. `id` selects a source, while each owner's native
dataset, atlas or standard ID is retained separately in results.

| Adapter | Input shape |
| --- | --- |
| `energy_catalog` | YAML catalog with `modules` and per-module `datasets` |
| `atlas_manifests` | Atlas root with `*/*/manifest.yaml`, each with `atlas_id` |
| `riser_manifest` | YAML manifest with named `tables`, `file` and optional digests |
| `standards_registry` | JSON `standards` list or mapping with owner code IDs |
| `wiki_pages` | Wiki root containing `*/wiki/**/*.md`; title and body are searchable |
| `ace_manifest` | Store root with `*/MANIFEST.tsv`, or one TSV manifest; comment lines are ignored |

Table 2. Native metadata adapters. Configure the existing source catalog and
domain index as the source of ownership and domain choices; this projection
does not allocate datasets or replace either registry.

`inventory` records the actual parsed baseline before `build`. Counts are per
configured source, including zero entries; advertised catalog totals are not
used. Missing inputs, malformed structured manifests, duplicate record keys and
digest mismatches abort a rebuild. The previous catalog remains unchanged.

Page search reads Markdown directly and has no graph dependency. This restores
keyword discovery through `find` even when an older wiki query surface gates
`pages search` on a graph artifact. It does not claim that the separate wiki CLI
has been changed. Domain filters use page frontmatter or the wiki directory.
Pages with malformed frontmatter remain searchable with an explicit metadata
warning; they remain unverified.

Queries match every token, ignoring case and treating punctuation as separators.
Ranking uses FTS5 BM25 with title weighting, then stable source/ID/locator ties.
The JSON result includes a bounded excerpt and private owner-relative locators.
Filters can be combined; `--limit` accepts 0 through 1000. An empty result is a
successful lookup, while configuration and catalog failures exit with code 2.

For a synthetic lookup, a `response-atlas` source contains atlas `response-01`,
titled “Semisubmersible RAO”, with heave response and frequency in rad/s.
`find "RAO heave" --source response-atlas` returns that ID, its manifest locator,
the declared units, exposure and observed manifest SHA-256. The engineer can
then resolve the manifest through its configured owner; no result table is
copied into this repository.

The database is created with owner-only file permissions and atomically
replaced after an integrity check. Paths within Git trees, including worktrees
and symlink aliases, are rejected. Search opens the database read-only. Source
files are never written. Exposure filters are discovery selectors, not access
controls or anonymization; output stays private until the exposure layer is
applied. Semantic search and domain-database ingestion are outside this phase.
