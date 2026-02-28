# WRK-647 Results

## Goal

Validate the patched `submit-to-claude.sh` wrapper against the correct `WRK-624` plan spec target.

## Invocation

- File: `specs/wrk/WRK-624/plan.md`
- Mode: `--compact-plan`
- Wrapper path: patched temp-file transport with `Read` tool only
- Prompt: `Review this implementation plan.`
- Timeout: 120s
- Retries: 1

## Outcome

- The patched wrapper exercised the new transport path:
  - review content written to temp file
  - short prompt passed to `claude -p`
  - `Read` enabled
  - `--add-dir` set to the temp run directory
- Claude returned a renderable structured review artifact.
- Validator classification of the resulting artifact: VALID
- Exit code: `0`

## Review result summary

- Verdict: `REQUEST_CHANGES`
- Claude's review focused on compact-bundle truncation and missing visible context in the review input.
- This is a meaningful, schema-valid review output, which is a clear improvement over the prior `NO_OUTPUT` behavior.

## Comparison to earlier experiments

- `WRK-642`: minimal control succeeded, real review targets failed under stdin-heavy transport.
- `WRK-644`: compact bundle + older transport still produced `NO_OUTPUT`.
- `WRK-646`: direct temp-file `Read` tests were not operationally successful.
- `WRK-647`: patched wrapper returned a valid Claude review on the real `WRK-624` target.

## Conclusion

The patched wrapper is validated as an effective transport improvement for this target.

The remaining issue is no longer transport failure. It is review content quality and bundle sufficiency. Claude can now review the compact plan bundle, but the bundle may still be too lossy for a full Route C review.
