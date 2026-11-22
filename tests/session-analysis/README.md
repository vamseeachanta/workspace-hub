# Synthetic ingestion fixture

## Plan-lite

The acceptance check will exercise one ingestion script,
`scripts/analysis/ingest-codex-sessions.sh`, using the adjacent synthetic JSONL
fixture. It will pass explicit date, input and output arguments from an unrelated
temporary working directory, then repeat with spaces in the parent path.

Acceptance will require the complete expected event, three message turns,
unchanged source and copied bytes, and an exact inventory of created files.
The fixture will also be checked against ignore rules in a tracked checkout.
Production ingestion changes, historical records, broader fixture inventory and
network services are outside this scope.

## Fixture and oracle

`fixtures/rollout-synthetic.jsonl` and `test_ingest_fixture_portability.py` are
tracked repository files. Confirm their tracking with:

```sh
git ls-files --error-unmatch tests/session-analysis/fixtures/rollout-synthetic.jsonl tests/session-analysis/test_ingest_fixture_portability.py
```

The fixture contains five rows: metadata, user message, assistant message,
tool event and user message. Only the three message rows count as turns.
The test declares the full expected event independently of the ingestion script;
the metadata supplies the date and the fixture basename supplies the identifier.

## Acceptance command

```sh
uv run --no-project --with pytest python -m pytest tests/session-analysis/test_ingest_fixture_portability.py -q -rA -p no:cacheprovider --basetemp="$TMPDIR/ingestion-fixture-tests"
```

Set `TMPDIR` to designated scratch storage before running. The suite contains
two tests, covering ordinary and spaced parent paths. A passing focused suite
does not establish that unrelated repository tests or hosted checks pass.
