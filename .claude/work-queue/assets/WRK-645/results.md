# WRK-645 Results

## Experiment goal

Test whether Claude CLI can write a markdown review artifact directly to disk during a non-interactive run, and whether that path is more reliable than stdout capture.

## Target setup

- Real target: `WRK-624` via compact plan bundle
- Control target: minimal markdown review input
- Output mode: Claude instructed to write review markdown to a fixed file path under `assets/WRK-645/raw/`
- Tools enabled: `Read,Edit,Write`
- CLI mode: `claude -p`

## Runs

| Run | Target | Expected artifact | Result |
|---|---|---|---|
| R1 | `WRK-624` compact bundle | `raw/claude-written-review.md` | no file created, no stdout review, timeout/no-output pattern |
| R2 | minimal control target | `raw/claude-written-review-control.md` | no file created, no stdout review, timeout/no-output pattern |

## Interpretation

The file-write strategy does not improve reliability on the tested Claude CLI path.

Key observations:
- Claude CLI has no native `--output-file` style option for review content.
- Prompt-instructed file writing through enabled tools did not create the requested markdown artifact.
- The failure persisted even on a trivial control target, which means this is not only a heavy-payload issue.
- For this path, file-write review capture is currently less reliable than the minimal stdout smoke-test path validated in `WRK-642`.

## Conclusion

Do not adopt prompt-driven file-write review capture as a workflow transport strategy for Claude at this time.

The current best-supported paths remain:
1. stdout/schema capture for minimal control checks
2. deterministic `NO_OUTPUT` classification for failed real review runs
3. continued investigation through other provider invocation shapes rather than file-write instructions
