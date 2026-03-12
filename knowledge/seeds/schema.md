# Knowledge Seeds — Resource Catalog Schema

## When to use this schema

Use this schema for doc-research WRKs that download and catalogue domain reference documents
(e.g. naval architecture, electrical engineering, structural analysis). Each domain gets its
own `knowledge/seeds/<domain>-resources.yaml` file following this structure.

This is separate from the `entries[]` pattern used by `career-learnings.yaml` style files.

## Required top-level fields

```yaml
category: <domain-slug>          # e.g. naval-architecture
subcategory: references
created_at: "YYYY-MM-DD"
```

## Standard sections

### `textbooks[]` — downloadable PDFs

```yaml
textbooks:
  - title: "Full title of the book"
    author: "Author or organisation"
    year: YYYY                          # integer or ~ if unknown
    local_path: "/mnt/ace/docs/_standards/<DIR>/subdir/filename.pdf"
    source_url: "https://..."
    size_mb: N                          # integer, approximate
    topics: [topic1, topic2]
    notes: "optional free-text"         # omit if empty
```

### `online_portals[]` — non-downloadable resources

```yaml
online_portals:
  - title: "Portal name"
    url: "https://..."
    notes: "What is available here"
```

### `pending_manual[]` — WAF-blocked or borrow-only items

```yaml
pending_manual:
  - title: "Book title"
    url: "https://..."
    notes: "Reason: archive.org borrow-only / eagle.org WAF block / paywalled"
```

## Bulk section variant

For 10+ files of the same type (e.g. ship plan PDFs), use `count` and `local_dir`
instead of per-file entries to keep the file readable:

```yaml
ship_plans:
  count: 107
  local_dir: "/mnt/ace/docs/_standards/SNAME/ship-plans"
  source_base_url: "https://maritime.org/doc/plans"
  notes: "Individual filenames listed in download script PLANS array"
```

## Minimal example

```yaml
category: example-domain
subcategory: references
created_at: "2026-01-01"

textbooks:
  - title: "Introduction to Example Engineering"
    author: "J. Smith"
    year: 2005
    local_path: "/mnt/ace/docs/_standards/ExampleDomain/intro-example-eng.pdf"
    source_url: "https://example.org/intro.pdf"
    size_mb: 12
    topics: [fundamentals, circuits]
```
