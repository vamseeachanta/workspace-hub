# Provider Autofeed Health Recovery

Use this reference when a provider autofeed/continuous-throughput monitor has over-launched duplicate lanes, accumulated orphaned provider processes, or produced raw process counts without durable artifacts.

## Session pattern captured

A 15-minute autofeed monitor was paused after producing overlapping Claude/Codex/Gemini lanes. Reconciliation found useful earlier Claude governance artifacts, but a controlled live tick with the patched monitor launched 9 lanes and produced no durable useful output:

- Claude lanes: alive, but 0-byte logs and missing/0-byte result files after several minutes.
- Codex lanes: alive, but 0-byte logs and missing/0-byte result files after several minutes.
- Gemini Pro lanes: `RESOURCE_EXHAUSTED` / `An unexpected critical error occurred`; stub result files existed but were not useful.

Conclusion: do not resume recurring autofeed merely because the classifier is patched. If the provider launch surface is unhealthy, switch from target-count dispatch to provider-health recovery.

## Safe recovery sequence

1. **Pause the recurring feeder first**
   - Disable/pause the Hermes cron or scheduler before launching replacements.
   - Preserve the cron ID/name/state in the status report.

2. **Reconcile current lanes before new work**
   - Inspect process trees, logs, result files, and run-dir mtimes.
   - Treat active process count as weak evidence; durable result artifacts win.
   - Write a reconciliation artifact under the monitor/run log directory.

3. **Kill only after evidence capture and explicit scope**
   - For orphaned/stale process trees, record PID, command line, elapsed time, last log tail, and result/log mtimes first.
   - Prefer `TERM` to process group, wait, then targeted child cleanup if roots leave orphaned children.
   - Never silently kill foreign PIDs or unrelated provider sessions.

4. **Patch monitor in dry-run mode first**
   - Add or verify `DRY_RUN=1` so the monitor can classify and plan launches without starting providers.
   - Run `bash -n` before any live tick.
   - Validate dry-run output reports skipped launches and does not spawn provider processes.

5. **Run exactly one controlled live tick**
   - Keep cron paused.
   - Launch one manual tick only.
   - Inspect after 1-3 minutes: root PIDs, child PIDs, log sizes/mtimes, result sizes/mtimes, and failure signatures.
   - If the tick produces no durable output or only provider-capacity/sandbox errors, clean it up and keep cron paused.

6. **Resume only after health proof**
   - Require at least one provider to prove durable output through a minimal health probe or controlled tick.
   - Consider resuming at a slower cadence (30m/60m) instead of the failed 15m cadence.

## Classifier rules that prevented false positives

Use signature-first classification before freshness/size checks:

- `Reading additional input from stdin` -> Codex stdin stall.
- `bwrap: loopback: Failed RTM_NEWADDR` -> Codex sandbox no-exec.
- `stream-json requires --verbose` -> Claude invocation error.
- `No capacity available for model gemini-2.5`, `RESOURCE_EXHAUSTED`, or `An unexpected critical error occurred` -> Gemini capacity/critical failure.

Then count useful-active only when:

- result file age is below the freshness window and size is greater than a STARTED-stub threshold, or
- log file age is below the freshness window and size is above a meaningful threshold.

Also:

- Infer log path from result path when child process command lines only include result paths.
- Deduplicate child processes by result path so `timeout`, `node`, provider binary, and `tee` children do not inflate provider counts.
- Classify duplicate child PIDs as duplicates, not independent useful lanes.

## Provider invocation gotchas

- Claude: text output can avoid fragile `stream-json` / `--verbose` coupling, but 0-byte log + no result after a few minutes is not useful. Probe separately with a minimal exact result-file write before trusting the monitor.
- Codex: stdin-file form and `--output-last-message` may still produce 0-byte logs/results if the sandbox/CLI is broken. Include a text-only fallback instruction, but do not count the lane useful without output.
- Gemini: run from `/mnt/local-analysis`, set `GEMINI_CLI_TRUST_WORKSPACE=true`, include the workspace via `--include-directories`, and explicitly tell the prompt to write to the result path. Do not flash-fallback in the same tick after Pro capacity failure.

## Decision rule

If a controlled live tick yields useful-active counts of zero for all providers, or only capacity/sandbox/no-output signatures, keep recurring autofeed paused and switch to provider-health probes:

1. one minimal Claude exact-result write probe;
2. one minimal Codex text-only audit probe;
3. Gemini backoff until Pro capacity returns;
4. only then resume recurring autofeed at reduced cadence.
