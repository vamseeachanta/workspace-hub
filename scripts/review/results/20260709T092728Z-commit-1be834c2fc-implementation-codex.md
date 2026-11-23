### Verdict: MAJOR

### Summary
REQUEST_CHANGES. The implementation is functionally well covered and the dedicated suite passes, but the new test harness leaks every temporary directory it creates because its cleanup bookkeeping is lost through command substitution. That is enough to block as-is for a bootstrap/tooling change that will be run repeatedly.

### Issues Found
- [P2] Important: scripts/agents/tests/test_voice_dictation_detection.sh:49 `make_tmp` appends to `tmpdirs`, but every caller uses `tmp="$(make_tmp)"`. Command substitution runs the function in a subshell, so the parent `tmpdirs` array remains empty and the `cleanup` trap never removes the temp directories. I confirmed this by running `bash scripts/agents/tests/test_voice_dictation_detection.sh`; it passed but left `/tmp/tmp.*` stub dirs behind.
- [P3] Minor: scripts/agents/tests/test_voice_dictation_detection.sh:1 The new test file is 456 lines, above this repo's 400-line file guardrail. Split by concern if that guardrail is enforced for this tree.

### Suggestions
- Change temp allocation so cleanup state is updated in the parent shell, for example `make_tmp tmp` using `printf -v "$var" '%s' "$d"`, or avoid command substitution and push paths into a cleanup file/list that the trap can read.
- Add a regression check that runs the test and asserts its owned temp directories are removed, or refactor the test helper to create all temp state under one parent directory with a single trap.
- Consider splitting the test into detection, installer, launcher, and static-contract scripts to stay under the file-size convention.

### Questions for Author
- None.
