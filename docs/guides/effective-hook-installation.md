# Effective Git hook installation

The setup installer now registers the tracked pre-push checker under Git's
standard event filename at Git's effective hook path. Installation, protocol
forwarding and dry-run preservation are tested in disposable repositories.
This does not establish activation in other checkouts or native providers.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Resolve effective hook paths and distinguish Git dispatch from native provider configuration. |

## Inventory and scope

The existing entrypoints were inspected before changing installation. No new
installer is introduced. The implemented slices are event registration,
enforcement-path repair, and consumer-boundary regression tests/documentation.

| Entrypoint or caller | Observed responsibility | Disposition |
| --- | --- | --- |
| `scripts/setup/install-all-hooks.sh` | Copied helper filenames into a fixed metadata directory, including `pre-push.sh` without the Git event name. | Installs only the supported `pre-push` event wrapper at the path resolved by Git. |
| `scripts/setup/new-machine-setup.sh` | Calls the setup installer. | Retains that call; activation remains an explicit operation. |
| `scripts/skills/install-skill-validator-hook.sh` | Delegates to the setup installer. | Retains that call; no validator coverage is inferred from the caller's name. |
| `scripts/enforcement/install-hooks.sh` | Inserts enforcement into existing hooks. | Uses the effective path; recognizes the setup wrapper without injecting duplicate gates. Legacy extension-point insertion remains supported. |
| `scripts/operations/setup-hooks.sh` | Changes `core.hooksPath` and creates encoding wrappers. | Separate legacy installer; not invoked or changed here. Running it can change which wrappers Git finds. |
| `scripts/agents/install-pre-commit-hook-cross-repo.sh` | Vendors a conflict-marker checker into sibling repositories. | Separate consumer, not invoked; its common-directory resolution does not establish custom-path coverage. |
| `scripts/agents/install-wiki-frontmatter-hook-cross-repo.sh` | Vendors a frontmatter checker and wires sibling hooks. | Separate consumer, not invoked; custom-path repair remains follow-up. |
| `scripts/development/ai-review/install-codex-hooks.sh`, `install-gemini-hooks.sh` | Install review automation into Git hooks. | Separate consumers; not invoked or claimed covered. |
| `scripts/operations/compliance/install_compliance_hooks.sh` | Installs compliance hooks. | Separate consumer; not invoked or claimed covered. |
| `scripts/propagate-hooks.sh` | Redirects to ecosystem propagation. | Not invoked; propagation is not installation evidence. |
| `scripts/setup/verify-setup.sh` | Checks fixed hook paths and probes installed tools. | Not invoked; its fixed-path checks are not evidence for this repair. |

The setup installer leaves helper scripts in the working tree and creates a
wrapper that resolves the invoking working tree at runtime. Shared hook metadata
therefore does not pin the source to whichever worktree installed it first.
The source must exist in every working tree that uses this shared hook path.
An already installed, identical wrapper is unchanged. A disabled identical
wrapper can be made executable by an explicit install. Unknown regular files,
symlinks and directories at `pre-push` are preserved and installation fails with
a composition diagnostic. There is no automatic backup, overwrite or chaining
of foreign hooks. Composition requires inspection and maintainer review.

## Installation and observation

Run from the target working tree, including from a nested directory:

```bash
bash scripts/setup/install-all-hooks.sh --dry-run
bash scripts/setup/install-all-hooks.sh --check
```

Dry-run reports the proposed change without creating directories or changing
contents or permissions. Check succeeds only when the source exists and the
effective `pre-push` entry is the expected executable wrapper. Check failure is
an observation, not permission to replace another hook.

After authority and review requirements are satisfied, an explicit installation
uses `bash scripts/setup/install-all-hooks.sh`. No `core.hooksPath` setting is
changed. An absolute or relative configured path is respected. Git's own path
resolution handles shared linked-worktree metadata. Run the enforcement installer
separately when the enforcement environment needs provisioning. Its dry-run
preserves legacy dead tails and hook modes; normal installation retains the
existing extension-point repair behavior.

## Consumer protocols

The protocol basis is the public [Git githooks manual](https://git-scm.com/docs/githooks),
DESCRIPTION and pre-push sections, and the public
[Claude Code hooks reference](https://code.claude.com/docs/en/hooks), matcher,
JSON input and decision output sections, accessed 2026-10-22.
These are software contracts; no engineering coefficients, numerical acceptance
limits or equations apply.

| Consumer | Event and selection | Input | Rejection |
| --- | --- | --- | --- |
| Git | Executable file named `pre-push` at the effective hook path. | Remote name/location arguments and ref lines on stdin. | A nonzero exit status aborts the push. |
| Native tool hook | `PreToolUse`, selected by tool name such as `Bash`. | JSON with event, tool name and tool input fields. | The provider's documented blocking status or decision JSON. Git exit conventions alone do not implement provider decisions. |

The wrapper uses `exec bash` and passes its arguments unchanged. It does not
parse, consume or translate stdin. The tracked checker buffers ref lines and
replays them to the state-size guard. A native JSON payload cannot identify an
arbitrary Git push destination or its selected refspecs by inference from the
current branch. The removed state-size native registrations remain absent in
both repository manifests; the retained native review registration uses `Bash`.
The corrected manifest tests establish only these declarations. They do not
establish provider loading, event dispatch or blocking response behavior.

## Worked example

The behavioral test `test_installs_event_at_effective_path_and_git_dispatches`
uses a disposable repository and a checker stub. Its inputs are a custom hook
path containing spaces, two remote arguments (`origin`, `destination with spaces`),
and this opaque ref-line text:

```text
refs/heads/topic a refs/heads/topic b
(delete) 0 refs/heads/old c
```

The stub records arguments and stdin without resolving object IDs. The short
OID tokens deliberately test transport only; they are not valid real push IDs.
The method installs the wrapper, runs installation again, then invokes it through
`git hook run --to-stdin <input-file> pre-push -- origin 'destination with spaces'`.
The stub returns a nonzero status.

Independent answer: the recorded argument file contains `origin` and
`destination with spaces` on separate lines; the input file is byte-identical to
the text above, including its final newline; Git reports failure. A second
installation changes no hook bytes or permissions. The expected result follows
by direct identity of input and output, not by calling production code to
compute an expected value. A separate test replaces the stub with the tracked
checker and requires the effective enforcement environment to be sourced.

## Coverage and limits

Observed repository: the current `workspace-hub` checkout. Execution coverage:
disposable default, relative-path, absolute-path, linked-worktree and
linked-worktree-relative-path repositories; nested-directory installation;
foreign-hook preservation; idempotence; dry-run contents and permissions;
Git dispatch arguments, stdin and failure; tracked enforcement environment
loading; setup followed by enforcement; static native manifest declarations.
No other repository installation was visited or changed.

Live native provider execution, installed provider configuration, other
checkouts and other platforms are **NOT_EVALUATED**. No assistant runtime was
started. No claim is made that every event or every guard is installed by this
pre-push repair. Second-provider review remains pending before merging.

Follow-up work includes explicit composition for foreign hooks, activation
checks for authorized targets, the legacy encoding installer, setup diagnostics,
and sibling/review/compliance installers. Each consumer requires its own
effective-path and protocol evidence before an installation claim is made.
