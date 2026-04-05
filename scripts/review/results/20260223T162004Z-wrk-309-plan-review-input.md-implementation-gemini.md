I will start by verifying the existence of the target files and directories mentioned in the plan.
I'll check the existence of each script individually to avoid PowerShell parameter errors.
I'll ensure the `scripts/lib` directory exists before creating the resolver script.
I'll create the `scripts/lib/python-resolver.sh` file with a robust logic to identify the available Python executable.
I'll now read the `scripts/cron/comprehensive-learning-nightly.sh` file to identify the `python3` calls.
I'll now read the `scripts/operations/compliance/normalize_work_queue_metadata.sh` script to identify and update its `python3` calls.
I'll now read the `scripts/operations/compliance/validate_work_queue_schema.sh` script to identify and update its `python3` calls.
I'll now read the `scripts/test/lib/invoke-pytest.sh` script to identify and update its `python3` calls.
I'll now read the `scripts/development/ai-workflow/auto-fix-loop.sh` script to identify and update its `python3` calls.
I'll now read the `scripts/ai/assessment/auto-sync-usage.sh` script to identify and update its `python3` calls.
I'll now read the `scripts/utilities/doc-to-context/doc2context.sh` script to identify and update its `python3` calls.
I'll start by updating the `scripts/cron/comprehensive-learning-nightly.sh` script to use the portable Python resolver.
I'll now update `scripts/operations/compliance/normalize_work_queue_metadata.sh` to use the portable Python resolver.
I'll now update `scripts/operations/compliance/validate_work_queue_schema.sh` to use the portable Python resolver.
I'll now update `scripts/test/lib/invoke-pytest.sh` to use the portable Python resolver.
I'll now update `scripts/development/ai-workflow/auto-fix-loop.sh` to use the portable Python resolver.
I'll now update `scripts/ai/assessment/auto-sync-usage.sh` to use the portable Python resolver. I'll source it at the top and replace all `python3` calls.
I'll now replace all occurrences of `python3` with `${PYTHON}` in `scripts/ai/assessment/auto-sync-usage.sh`.
I'll search for all `python3` occurrences in `scripts/ai/assessment/auto-sync-usage.sh` to ensure accurate replacement.
I'll read `scripts/ai/assessment/auto-sync-usage.sh` again to identify all `python3` calls for accurate replacement.
I'll replace the `python3` calls in `scripts/ai-assessment/auto-sync-usage.sh` one by one to ensure accuracy.
I'll now replace the `python3 -c` calls in `scripts/ai-assessment/auto-sync-usage.sh` with `${PYTHON} -c`.
I'll continue replacing the remaining `python3 -c` calls in `scripts/ai-assessment/auto-sync-usage.sh` with `${PYTHON} -c`.
I'll replace the final `python3 -c` call in `scripts/ai-assessment/auto-sync-usage.sh` with `${PYTHON} -c`.
I'll now update `scripts/utilities/doc-to-context/doc2context.sh` by sourcing the portable Python resolver at the top and then replacing all `python3` calls.
I'll now replace all `python3` calls in `scripts/utilities/doc-to-context/doc2context.sh` with `${PYTHON}`.
I'll now read `.claude/hooks/check-encoding.sh` to understand its current structure and prepare for refactoring it into batch mode.
I'll now refactor `.claude/hooks/check-encoding.sh` into batch mode, processing all files in a single Python invocation to improve efficiency.
I'll now verify the changes by running `bash .claude/hooks/check-encoding.sh` and assessing its performance.
I'll debug the `check-encoding.sh` script to identify the cause of the exit code 1 by running it with `bash -x`.
I'll investigate whether `uv run` is functioning correctly by executing a simple Python command.
I'll debug the `BAD_REPORT` command by running the pipeline separately to identify the source of the non-zero exit code.
I'll retry the pipeline debugging by running it inside `bash -c` to correctly execute the bash script.
I'll verify if any files exist in the target directories to ensure the `collect_files` command has something to process.
I'll refactor `check-encoding.sh` to capture the file list first, then process it with `uv run`, avoiding potential pipe issues.
I'll test the updated `.claude/hooks/check-encoding.sh` script to verify it functions correctly.
I'll create a file with UTF-16 encoding to verify that `check-encoding.sh` correctly identifies bad encodings.
I'll now rerun the `check-encoding.sh` script to confirm it correctly identifies the newly created `config/bad-encoding.json` file.
I'll use Python to create a UTF-16 file with a proper BOM to accurately test the `check-encoding.sh` script.
I'll use `uv run python` to create the UTF-16 file, ensuring I'm using a correctly identified Python executable.
I'll rerun `check-encoding.sh` to confirm it now correctly identifies the UTF-16 encoded file.
I'll add `config/bad-encoding.json` to the git index so that `git ls-files` can see it, allowing `check-encoding.sh` to find and report the bad encoding.
I'll use the correct PowerShell syntax to add the file and run the check.
I'll verify if `config/bad-encoding.json` is listed by `git ls-files` to determine if it's being correctly included in the scan.
I'll debug `check-encoding.sh` with `bash -x` to trace its execution and understand why it's not reporting the bad encoding.
I've identified that the `uv run` command is failing because it's receiving two conflicting stdins. I'll fix this by writing the Python script to a temporary file and executing it from there.
I'll test the `check-encoding.sh` script again to verify that using a temporary file for the Python script resolved the issue.
I'll remove the `config/bad-encoding.json` test file and then run the check again to confirm the script returns a clean status.
I'll use the correct PowerShell syntax to remove the file, untrack it from git, and run the final check.
I'll perform a final verification of the changes in `scripts/operations/compliance/validate_work_queue_schema.sh` to ensure the integration of the portable Python resolver is correct.
I have implemented the plan WRK-309 to ensure portable Python invocation across different environments and optimize the encoding guard hook.

Key accomplishments:
1.  **Created `scripts/lib/python-resolver.sh`**: A portable utility that resolves the Python executable to either `python3` or `python`, depending on what's available in the environment.
2.  **Updated 7 core scripts**: Integrated the Python resolver into several scripts to ensure consistent cross-machine execution and eliminate "python3: command not found" errors on Windows.
    -   `scripts/cron/comprehensive-learning-nightly.sh`
    -   `scripts/operations/compliance/normalize_work_queue_metadata.sh`
    -   `scripts/operations/compliance/validate_work_queue_schema.sh`
    -   `scripts/test/lib/invoke-pytest.sh`
    -   `scripts/development/ai-workflow/auto-fix-loop.sh`
    -   `scripts/ai/assessment/auto-sync-usage.sh`
    -   `scripts/utilities/doc-to-context/doc2context.sh`
3.  **Refactored `.claude/hooks/check-encoding.sh`**: Optimized the script to use a batch mode approach. Instead of spawning a `uv run` process for every file, it now processes all files in a single Python invocation, significantly reducing execution time during the commit loop. Verified the refactoring with a test file, confirming it correctly identifies bad encodings while remaining efficient.
