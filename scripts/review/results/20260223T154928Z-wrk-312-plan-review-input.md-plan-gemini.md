I will begin by investigating the current repository structure to locate any existing git hooks or setup scripts, specifically looking for `scripts/hooks` or `scripts/setup` directories.

I will use the `list_directory` tool to inspect the contents of the `scripts` directory to identify any existing hook or setup subdirectories.

I will read the `scripts/propagate-hooks.sh` file to understand its current role and whether it already handles hook distribution across the repository.

I will read `scripts/propagate-ecosystem.sh` to determine how it manages hook propagation and if it can be integrated with or replaced by the proposed `WRK-312` solution.

I will list the files in the `.git/hooks/` directory to see if any Git hooks are already present and active.

I will use the `list_directory` tool to inspect the `.git/hooks` directory and avoid any path-related issues with shell commands.

I will list all files in the `.git/hooks` directory, including those typically ignored, to confirm if any active Git hooks (non-sample files) exist.

I will read the contents of the `post-commit` and `pre-commit` hooks in the `.git/hooks` directory to understand their current functionality and how they might be affected by the proposed changes.

I will use the `run_shell_command` with `cat` to read the contents of the `.git/hooks/pre-commit` file, bypassing the ignore patterns that prevented me from reading it with `read_file`.

I will check if the `scripts/skills/install-skill-validator-hook.sh` file exists, as its presence will influence how I implement the delegation to the new `install-all-hooks.sh` script.

I will read the `scripts/skills/install-skill-validator-hook.sh` file to understand its current implementation and determine the best way to refactor it to delegate hook installation.

I will read the `.gitattributes` file to see if there are existing rules for enforcing LF line endings on script files, which is important for the cross-platform functionality of Git hooks.

### Verdict: APPROVE

### Summary
The proposed plan for WRK-312 is well-reasoned and addresses the critical need for consistent git hook environments across different machines. By tracking canonical hooks and using a `post-merge` trigger, it ensures that developers automatically receive hook updates without manual intervention.

### Issues Found
- [P2] **Important: Rebase Support.** `post-merge` does not fire during a `git pull --rebase` or after a standard `git rebase`. To ensure hooks are synced for developers using rebase workflows, a `post-rewrite` hook should be included that also triggers the installer.
- [P3] **Minor: Explicit LF enforcement.** While `.gitattributes` covers `scripts/*`, git hooks in `scripts/hooks/` often lack extensions (e.g., `pre-commit`, `post-merge`). Ensuring these are explicitly forced to LF in `.gitattributes` will prevent shebang failures on Windows (MINGW/Cygwin).

### Suggestions
- **Add `post-rewrite`:** Include `scripts/hooks/post-rewrite` to complement `post-merge`, covering the `git rebase` / `pull --rebase` scenarios.
- **Update `.gitattributes`:** Add `scripts/hooks/* text eol=lf` to ensure extensionless hook files are handled correctly.
- **Verbose installer:** Consider adding a check in `install-all-hooks.sh` to see if the hooks actually changed before copying, though `cp` is fast enough that idempotency is likely sufficient.
- **Handle `post-checkout`:** If hooks ever become branch-specific or need to be refreshed on branch switches, `post-checkout` could be added as well.

### Questions for Author
- Do we want to support `git pull --rebase` via `post-rewrite` in this iteration?
- Should the `install-all-hooks.sh` script also handle the removal of stale hooks that are no longer in `scripts/hooks/`?
- For the initial bootstrap, should we add a notice to `scripts/setup-claude-env.sh` or a similar entry point to encourage developers to run `install-all-hooks.sh` once?
