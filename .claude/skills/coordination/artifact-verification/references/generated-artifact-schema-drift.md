# Generated Artifact Schema Drift Recovery

Use this when a task restores generated artifacts from a patch/archive and validation then explodes with broad schema-version or missing-field failures.

## Symptom Pattern

- Targeted tests or validators fail across many generated records.
- Failures repeat the same fields on most nodes/edges/rows, such as missing required schema fields or wrong schema version.
- The current checkout already contains generator/validator code, but the artifact files came from an archived patch, stash, old worker output, or copied report directory.
- Public-safety grep or presence checks may pass, but semantic/schema validation fails at scale.

## Preferred Recovery

1. Inspect the current generator and validator CLI from the checked-out code, not from old notes.
2. Treat restored generated outputs as bootstrap material only.
3. Rerun the current generator from the repo root to overwrite artifacts.
4. Rerun the current validator against the regenerated outputs.
5. Only then decide whether test expectations, fixture data, or validator rules need edits.

## Do Not

- Do not commit recovered generated artifacts just because file presence checks pass.
- Do not edit validators to accept stale artifacts before proving the generator contract.
- Do not close the issue while artifacts are only restored-from-patch unless they are regenerated or verified byte-for-byte compatible with the current generator contract.

## Example Evidence to Capture

- Generator command and exit status.
- Validator command and exit status.
- `git diff --stat` after regeneration.
- Public-safety scan output for generated artifacts.
- Targeted tests proving fixture behavior and canonical artifact parity.
