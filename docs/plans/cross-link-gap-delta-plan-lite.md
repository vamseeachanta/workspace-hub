# Offline cross-link gap delta: Plan-lite

## Scope

Validation will remain limited to the standalone comparison of two explicitly
supplied local JSONL snapshots. Discovery, scoring, ingest and storage behaviour
will remain outside this change.

## Intended validation

- Both snapshots will be validated before any delta is emitted. Invalid JSONL,
  duplicate keys, repeated identities, non-finite values and invalid identity
  components will be rejected without reflecting input content or paths.
- Identity comparison will use the directed tuple `(source_wiki, source_page,
  target_wiki, target_page)`, matching the existing producer. Added and removed
  identities will follow set difference; shared identities will be compared
  literally, ignoring only the top-level `discovered` field.
- Deterministic output will be checked against literal expected records and
  byte-identical output after input records and object keys are reordered.
  Payload fields, list order and JSON scalar types will retain their meaning.
- Offline tests will use synthetic local fixtures, verify input preservation,
  and cover empty snapshots, malformed inputs and command-line errors. They
  will require neither discovery nor access to referenced pages.

## Checks

The focused suite will run with an external temporary directory and disabled
pytest cache:

```sh
uv run --no-project --with pytest python -m pytest tests/data/test_cross_link_gap_delta.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/cross-link-gap-delta-tests"
```

Python syntax, whitespace, publication content and applicable direct file checks
will also be checked. Hosted failures will be inspected separately from the
focused suite; unrelated failures will be reported with their baseline evidence.

## Limits

Validation will cover snapshot comparison only. It will not establish that
referenced pages exist, qualify discovery scores or bound snapshot memory use.
