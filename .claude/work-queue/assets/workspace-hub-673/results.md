# WRK-646 Results

## Experiment goal

Test whether avoiding large stdin entirely and letting Claude read the compact plan bundle from a file via the `Read` tool improves non-interactive review reliability.

## Runs

| Run | Invocation | Result |
|---|---|---|
| R1 | Short prompt + `Read` tool, no `--add-dir`, `--output-format text` | no output within observation window; inconclusive because absolute-path read allowance was incomplete |
| R2 | Short prompt + `Read` tool + `--add-dir`, `--output-format text` | no output within bounded window; no substantive review returned |

## Comparison to prior experiments

- `WRK-642`: minimal stdout/schema control succeeded, real review targets failed under stdin-heavy path
- `WRK-644`: smaller provider-specific compact bundle still returned `NO_OUTPUT`
- `WRK-645`: prompt-driven file-write strategy failed on both real and trivial control targets
- `WRK-646`: temp-file `Read` path did not produce a substantive review within the bounded run window

## Interpretation

The temp-file `Read` path did not provide a clear improvement in this workspace.

It removed the large-stdin payload from the invocation, which was the main reason to test it. But under the actual CLI runs performed here, Claude still did not return a usable review artifact on the real `WRK-624` target within the bounded execution window.

That means one of two things is true:
1. large stdin is not the only dominant failure factor in this environment, or
2. the file-read path still requires a different invocation shape to become reliable

## Conclusion

Do not replace the current Claude transport path with the temp-file `Read` variant based on this evidence.

The result is negative for adoption and inconclusive for root-cause isolation. The workflow should continue to rely on explicit `NO_OUTPUT` classification rather than treating the file-read variant as a solved transport fix.
