# Weekly-review source-lookup query pack

This pack covers local source discovery for issue 2121.
It exercises `lookup_data` in `scripts/knowledge/doc-key-lookup.py` against
synthetic files only. It does not integrate a live weekly review or establish
engineering readiness, source rights, freshness or answer quality.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-25 | Synthetic source lookup and negative controls are specified to make discovery independently testable. |
| 1 | 2026-10-26 | Scope, acceptance checks and limits are consolidated in Plan-lite for review. |

## Plan-lite

The pack will cover synthetic source-key and wiki-key discovery, an absent key,
and a broken source mapping that retains its wiki match. Its two affected paths
will be `docs/document-intelligence/weekly-review-query-pack.md` and
`scripts/knowledge/tests/test_weekly_review_query_pack.py`.

Acceptance will require the three pack tests and the two existing tests in
`scripts/knowledge/tests/test_phase4_tools.py` to pass without failures or skips.
The checks will execute the documented example against temporary stores and
assert literal identities, empty results and the retained-wiki mapping gap.

The scope will remain synthetic discovery. It will not establish live weekly-review
integration, freshness, source qualification, answer quality or general join
validation. The remaining questions below will stay explicitly unanswered.

## Questions and answer contract

| Question identifier | Question | Source of truth | Expected answer fields |
| --- | --- | --- | --- |
| SOURCE-KEY | Which indexed source has the supplied key? | Temporary `data/document-index/index.jsonl`: exact `content_hash` match | `lookup.query`, `lookup.lookup_type`, `lookup.index_records`: `content_hash`, `path`, `source`, `domain`, `status` |
| WIKI-KEY | Which wiki page references that key? | Temporary `knowledge/wikis/engineering/wiki/sources/alpha.md`: key in page text | `lookup.wiki_pages`: `domain`, `page`, `title` |
| MISSING-KEY | Is an absent key explicitly unanswered? | Empty results across the temporary index, wiki and ledger | `status: unanswered`, all result lists empty |

The expected source identity is `synthetic-alpha`, with locator
`synthetic/sources/alpha.txt`, domain `engineering`, and index status `indexed`.
The expected wiki identity is
`knowledge/wikis/engineering/wiki/sources/alpha.md`, titled `Synthetic alpha`.
The empty synthetic ledger is `data/document-index/standards-transfer-ledger.yaml`.
No standards entry is expected. These literal identities are fixture design
inputs, not values obtained from the lookup implementation. Paths returned on
Windows use the native separator.

The public test string is exactly `abc` encoded as UTF-8, without a newline.
Its SHA-256 digest is
`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
The independent fixture calculation is `printf abc | sha256sum`; the Python
example computes it again with `hashlib.sha256`. This is a test vector, not a
hash of an external document. The prefixed form is the fixture `doc_key`.
The digest algorithm and import depth in the tests follow Python's `hashlib`
API and this repository's `scripts/knowledge/tests` directory layout respectively;
collection counts below come from the stated pytest commands.

## Executable worked example

Run from the repository root with Python. The same fenced block is executed by
`test_documented_query_pack_executes`; the tests supply `fixture_root` and
`lookup_script`. All lookup path constants are replaced before the first query.
The empty ledger is valid with or without optional YAML support. The production
lookup functions are used directly; no search algorithm is reimplemented.

```python
import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


def query_pack(query):
    with patch.multiple(
        lookup,
        REPO_ROOT=fixture_root,
        INDEX_JSONL=fixture_root / "data/document-index/index.jsonl",
        STD_LEDGER=fixture_root / "data/document-index/standards-transfer-ledger.yaml",
        WIKIS_DIR=fixture_root / "knowledge/wikis",
        WIKI_DOMAINS=["engineering"],
    ):
        result = lookup.lookup_data(query, by="key")
    if not any(result[name] for name in ("index_records", "wiki_pages", "standards_ledger")):
        status = "unanswered"
    elif result["index_records"] and result["wiki_pages"]:
        status = "answered"
    else:
        status = "source-mapping-gap"
    return {"status": status, "lookup": result}


# A supplied root must be a disposable directory, never a document store.
# Keep the temporary-directory object alive for the lifetime of this example.
if "fixture_root" not in globals():
    temporary = TemporaryDirectory()
    fixture_root = Path(temporary.name)
lookup_script = globals().get("lookup_script", Path("scripts/knowledge/doc-key-lookup.py"))
spec = importlib.util.spec_from_file_location("query_pack_lookup", lookup_script)
lookup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lookup)
key = "sha256:" + hashlib.sha256(b"abc").hexdigest()
index = fixture_root / "data/document-index/index.jsonl"
index.parent.mkdir(parents=True, exist_ok=True)
index.write_text(json.dumps({
    "content_hash": key, "path": "synthetic/sources/alpha.txt",
    "source": "synthetic-alpha", "domain": "engineering", "status": "indexed",
}) + "\n", encoding="utf-8")
(fixture_root / "data/document-index/standards-transfer-ledger.yaml").write_text(
    "standards: []\n", encoding="utf-8"
)
page = fixture_root / "knowledge/wikis/engineering/wiki/sources/alpha.md"
page.parent.mkdir(parents=True, exist_ok=True)
page.write_text('---\ntitle: "Synthetic alpha"\n---\n' + key + "\n", encoding="utf-8")
answer = query_pack(key)
print(json.dumps(answer, indent=2))
```

`status` is an example-level discovery classification; `lookup_data` itself
returns no answer-status field. `answered` requires both source and wiki results
for this small fixture. Exact identities, counts and fields are independently
asserted in the test; this classification alone is not a general join validator.
The broken-mapping control changes the index key while retaining the matching
wiki. Its expected status is `source-mapping-gap`, even though output is nonempty.
The absent query `absent-synthetic-key` must produce `unanswered` and empty lists.

## Verification and remaining gaps

Run `python -m pytest scripts/knowledge/tests/test_weekly_review_query_pack.py scripts/knowledge/tests/test_phase4_tools.py -q -rA`.
The starting baseline is two passing tests in `test_phase4_tools.py`; the ending
selection is five passing tests: the same baseline plus the three named pack tests.
The initial test-first run fails because this document has not yet been created.
No real document store or network is required by the pack tests. Fixtures are
created beneath pytest's temporary root and are not saved as authoritative data.

Questions outside this pack remain unanswered:

- What changed since the previous weekly review? No dated snapshot comparison is included.
- Which sources are stale, licensed, authoritative or ready for engineering use? No qualification evidence is checked.
- Which findings contradict each other or require action? No semantic synthesis is performed.
- Which missing source should be acquired next? No acquisition priority is calculated.
- Are production indexes, ledgers and wikis complete and mutually consistent? Only a synthetic key and a broken mapping are exercised.
- Do standards, path queries, duplicate identities or optional ledger parsers behave equivalently? No such coverage is claimed.

The verification lesson is that a wiki match without its indexed source remains
a mapping gap; nonempty lookup output alone cannot establish an answered question.
