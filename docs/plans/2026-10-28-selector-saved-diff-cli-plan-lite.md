# Saved-diff selector CLI: Plan-lite

## Scope

The regression slice will exercise `scripts/ci/hub_test_select.py` through its
`json` and `explain` commands with `--root` and `--diff-file`. Fixtures will use
saved NUL-delimited name-status records and an independent two-file inventory.
Live Git collection and changes to selector behavior will remain outside scope.

## Literal expectations

- A rename from `scripts/data/old.py` to `tests/skills/test_beta.py` will select
  `tests/data` and `tests/skills`, with exactly `tests/data/test_alpha.py` and
  `tests/skills/test_beta.py` in the selected file list.
- Deleting `docs/guide.md` will select no families or files and print no pytest
  command.
- An incomplete rename or missing final NUL after a valid selecting record will
  fail with empty standard output and the literal generic diagnostic.
- Both output modes will match independently enumerated JSON or text, including
  the printed command. Every invocation will preserve directory membership and
  file bytes; fixture modules will reject import or execution.

## Offline validation

Validation will run the existing 27 cases in `tests/ci/test_hub_test_select.py`
and the six CLI cases in `tests/ci/test_hub_test_select_cli.py` with:

```sh
uv run --offline --no-project --with pytest python -m pytest tests/ci/test_hub_test_select.py tests/ci/test_hub_test_select_cli.py -q -rA -p no:cacheprovider
```

The invocation will use an external temporary base. The complete `tests/ci/`
suite, whitespace checks, engineering-register checks and a secret scan will
provide additional validation. Offline success will establish the saved-diff
contract only; it will not establish live Git coverage or green hosted checks.

The pull request comment will supply this Plan-lite section for the description.
Updating the description will remain a maintainer action.
