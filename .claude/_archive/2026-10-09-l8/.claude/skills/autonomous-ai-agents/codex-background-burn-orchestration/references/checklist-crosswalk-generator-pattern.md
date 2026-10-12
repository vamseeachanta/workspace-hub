# Checklist Crosswalk Generator Pattern

Use this when a Codex burn / launch-bundle run is already terminal but the user or harness repeats a long checklist and asks for unchecked items to be worked without self-marking boxes.

## Pattern

1. Treat the latest prompt as a request for fresh evidence, not implicit authorization to launch more work.
2. Re-open the manifest and prior evidence artifacts from the run directory.
3. Re-refresh live state:
   - `gh issue view ...` rich JSON plus a lean TSV fallback for state/url/updated/closed.
   - `git status --short --branch`, `git rev-parse HEAD`, recent commits, and `git ls-remote` twice for remote-branch finality.
   - two narrow `ps` scans scoped to the run directory that avoid matching the scan command itself.
   - Hermes/background process registry if available.
4. Produce both JSON and Markdown crosswalk files under `monitoring-evidence/` with:
   - inventory counts (`requested`, `identified`, `accessible`, `pre_existing_launched`, `launched_this_turn`, `terminal`, `succeeded`, `blocked_partial`, `failed`, `running`, `omitted`, `unknown`);
   - bundle table with repo, issues, session/run handle, status, branch, HEAD, remote branch, dirty status, prompt/log hashes;
   - requirement-class rows mapping checklist item numbers to evidence classes;
   - current terminal classification recomputed from live issue state and git/process evidence, not blindly copied from an older manifest (for example, classify mixed closed/open issue bundles as `blocked_partial` even when all local processes are terminal);
   - retrospective impossibilities separated from human/governance blockers;
   - `new_user_supplied_bundle_refs`, `launched_this_turn`, and `launched_new_continuation` explicitly set so judges can distinguish prior launches from current-turn action.
5. Run a refined post-redaction secret scan and write a hash manifest after all artifact writes.
   - When selecting the "latest prior evidence" artifact, exclude companion files such as `*-hashes.json` and secret-scan outputs; otherwise a hash manifest can be misreported as the prior evidence JSON. Prefer an explicit predicate like `name.startswith("checklist-crosswalk-evidence-") and name.endswith(".json") and not name.endswith("-hashes.json")`.
   - Scope the secret scan to the generated evidence artifacts and any intentionally included prompt/log excerpts, not huge dependency caches or already-redacted historical scans. Classify known redacted/synthetic examples (for example `[REDACTED]`, `sk-abc...`, `token=secret`) separately from real candidates so the report does not create false blockers.
6. Remove any temporary evidence-generator scripts after artifact creation, or store reusable generators under the skill's `scripts/` directory instead of leaving one-off scripts in the run directory. Include cleanup proof in the final note when the run directory is being judged for residue.
7. If no new bundle IDs or approval override were supplied and remaining work is `blocked_partial`, stop with exact required user decisions.
8. After context compaction or a handoff summary, treat all in-chat status as stale. Re-open the latest on-disk non-companion evidence JSON, verify its hash/path, and then create a fresh timestamped crosswalk artifact from live process/git/GitHub checks. Even if the previous artifact is only minutes old, repeated judge/checklist prompts need a new evidence artifact or a clear `new_launches_this_turn=0` reconciliation for the current turn.
9. When using Hermes process tools, record both the narrow shell `ps` scan and the Hermes background registry result (including an empty `process(action="list")` response) so the judge can distinguish “no active tracked session” from “not checked”.

## Robust implementation note

For large evidence-gathering scripts, prefer writing a deterministic temporary Python script and invoking it with the terminal/shell. Inside the script, use `subprocess.run(..., capture_output=True, timeout=...)` and normalize every command result to `{cmd, workdir, exit_code, output}`. This avoids brittle nested tool-wrapper assumptions and gives stable evidence records even when individual commands time out.

Do not turn wrapper quirks or transient command failures into durable negative claims about the tool; capture the robust command-normalization pattern instead.
