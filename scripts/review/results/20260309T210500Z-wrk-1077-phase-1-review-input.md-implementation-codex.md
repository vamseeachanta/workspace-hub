### Verdict: APPROVE

### Summary
The runbook is close, but it does not fully prove all acceptance criteria yet. The main gap is alias availability: the plan appends the snippet to `~/.bash_profile`, but never reloads the shell or explicitly checks that `ws`, `wrk`, and `wh-verify` are usable. There is also a manifest lookup risk in `dev-env-check.sh` because it derives the manifest filename directly from `hostname` without normalization, so a case mismatch on Windows could cause a false "No manifest found" result.

### Issues Found
- Alias AC is not fully covered. The acceptance criterion requires `ws`, `wrk`, and `wh-verify` to be available in Git Bash, but the plan only appends the source line and then runs verification. `verify-setup.sh` checks whether the snippet is referenced in `~/.bash_profile`, not whether the aliases are active in the current shell, and it separately warns if `CLAUDE_SCREENSHOT_DIR` is unset until the shell is reloaded. See `/D:/workspace-hub/.claude/work-queue/pending/WRK-1077.md:43`, `/D:/workspace-hub/.claude/work-queue/pending/WRK-1077.md:51`, `/D:/workspace-hub/scripts/setup/verify-setup.sh:104`, `/D:/workspace-hub/scripts/setup/verify-setup.sh:195`, `/D:/workspace-hub/config/shell/bashrc-snippets.sh:57`.
- Manifest detection is case-sensitive in `dev-env-check.sh`. It uses `MANIFEST_FILE="$MANIFESTS_DIR/${CURRENT_HOSTNAME}.yml"` with `CURRENT_HOSTNAME="$(hostname)"`, while the manifest on disk is lowercase `acma-ansys05.yml`. If Windows returns `ACMA-ANSYS05`, step 7 can fail even though the manifest exists. See `/D:/workspace-hub/scripts/operations/system/dev-env-check.sh:20`, `/D:/workspace-hub/scripts/operations/system/dev-env-check.sh:21`, `/D:/workspace-hub/specs/modules/hardware-inventory/manifests/acma-ansys05.yml:1`.
- The runbook relies on remaining in the repo root after step 1, but steps 2, 6, and 7 use relative paths without restating `cd /c/workspace-hub`. For a manual runbook, that is easy to mis-execute if operators paste commands one at a time. See `/D:/workspace-hub/.claude/work-queue/pending/WRK-1077.md:49` and `/D:/workspace-hub/.claude/work-queue/pending/WRK-1077.md:50`.
- There is a Windows path-format risk in the manifest itself. `workspace_root` is `C:\workspace-hub`, but `dev-env-check.sh` concatenates it as a bash path (`$WORKSPACE_ROOT/$repo`). In Git Bash that may produce false repo misses unless MSYS path handling happens to tolerate it. This is not an explicit AC blocker for "finds and reads manifest", but it is a readiness risk if step 7 is interpreted as broader validation. See `/D:/workspace-hub/specs/modules/hardware-inventory/manifests/acma-ansys05.yml:4` and `/D:/workspace-hub/scripts/operations/system/dev-env-check.sh:179`.
- Workflow note: the WRK file still has `plan_approved: false`, so this is not yet ready for execution under the workspace gate rules until explicit approval names `WRK-1077`. See `/D:/workspace-hub/.claude/work-queue/pending/WRK-1077.md:18`.

### Suggestions
- Add an explicit shell reload and proof step after updating `~/.bash_profile`, for example: `source ~/.bash_profile` followed by `type ws wrk wh-verify`. That closes the alias AC directly.
- Strengthen step 7 wording to say whether success means only "manifest file was found/read" or also "repo/domain checks look sane". Right now the script can print repo/tool misses while still satisfying the narrow AC.
- Make every runbook command self-contained with `cd /c/workspace-hub && ...` or use absolute paths throughout. That removes operator ambiguity.
- Before approving execution, confirm the actual output of `hostname` on `acma-ansys05`. If it is not lowercase `acma-ansys05`, the manifest lookup logic needs a workaround or the runbook needs to account for it.

### Questions for Author
- On `acma-ansys05`, does `hostname` return exactly `acma-ansys05`, including case?
- For the step-7 acceptance, do you only need `dev-env-check.sh` to locate/read the manifest, or do you also expect its repo and domain-tool checks to be clean on this workstation?
- Do you want the runbook to require immediate alias usability in the same shell session, or is "available after reopening Git Bash" acceptable?
