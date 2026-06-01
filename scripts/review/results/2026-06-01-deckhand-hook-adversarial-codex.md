## VERDICT

CHANGES-REQUESTED.

The classifier is not safe as a destructive-intent gate. It is built around `shlex` plus a small destructive table, but shell execution has expansion, separators, aliases, wrapper commands, and CLI subcommand surfaces that are not modeled. Many destructive `git`/`gh` actions currently become plain `write`, `read`, or no detected action.

## Confirmed bypasses (ranked, input -> wrong class -> correct -> fix)

### BLOCKER

- `git push $F origin main` -> `write` -> `unparseable_suspicious` / destructive if `$F=--force` -> fail closed on any `$...` token in a gitish command.
- `git push ${F} origin main` -> `write` -> `unparseable_suspicious` / destructive if `${F}=--force` -> same: fail closed on shell parameter expansion.
- `git p${X}ush --force` -> `write` -> `unparseable_suspicious` / `force_push` if `${X}=u` -> reject `$` anywhere in tool/subcommand/flag tokens.
- `$GIT push --force` -> `[]` / no git action -> `unparseable_suspicious` -> fail closed on command-position `$...` when command contains destructive-looking git args, or deny all command-position expansion.
- `${GIT} push --force` -> `[]` -> `unparseable_suspicious` -> same.
- `${G:-git} push --force` -> `[]` -> `unparseable_suspicious` -> same.
- `g${X}it push --force` -> `[]` -> `unparseable_suspicious` -> same.
- `git push origin :old` -> `write` -> `branch_delete` -> classify push refspecs with empty source before `:` as delete.
- `git push origin :refs/heads/old` -> `write` -> `branch_delete` -> same, including full refs.
- `git push origin +main:main` -> `write` -> `force_push` -> treat leading `+` refspec as force push.
- `git push --atomic origin :old +main:main` -> `write` -> `branch_delete` and `force_push` -> scan all push refspecs, not just flags.
- `git push --mirror origin` -> `write` -> destructive mirror push -> classify `--mirror` as destructive.
- `git push --prune origin main` -> `write` -> destructive remote prune -> classify `--prune` as destructive.
- `git push --\nforce` -> `write` -> `force_push` -> fail closed on backslash-newline or normalize shell line continuations before parsing.
- `git pu\nsh --force` via line continuation -> `write` -> `force_push` -> same.
- `git status\ngit push --force` -> `read` -> second action `force_push` -> split on newline or fail closed on newline in gitish commands.
- `git status & git push --force` -> `read` -> second action `force_push` -> split on `&` or fail closed on background operators.
- `git status \\\n& git push --force` -> `read` -> second action `force_push` -> fail closed on line continuation plus separators.
- `git-push --force origin main` -> `[]` -> `force_push` / suspicious external git command -> detect `git-*` dashed external helpers or fail closed on `git-` command names.
- `g push --force` when shell alias/function `g=git` exists -> `[]` -> `unparseable_suspicious` -> deny alias/function indirection; require canonical executable command position only.
- `git -c alias.nuke='push --force' nuke origin main` -> `write` -> `force_push` -> fail closed on `-c alias.*=` or resolve alias expansion.
- `git -c alias.wipe='branch -D main' wipe` -> `write` -> `branch_delete` -> same.

### BLOCKER - `gh api` and GitHub destructive surfaces

- `gh api repos/o/r/git/refs/heads/main -X DELETE` -> `write` -> destructive API delete -> fail closed on `gh api` unless method and endpoint are explicitly allowlisted read-only.
- `gh api --method DELETE /repos/o/r/releases/assets/1` -> `write` -> destructive API delete -> same.
- `gh api -X PATCH /repos/o/r --field archived=true` -> `write` -> repo mutation/archive -> fail closed on non-GET `gh api`.
- `hub api repos/o/r -X DELETE` -> `write` -> destructive API delete -> apply same `api` rule to `hub`.
- `gh alias set wipe 'api -X DELETE /repos/o/r'` -> `write` -> destructive alias creation / future bypass -> classify all `gh alias set/delete/import` as destructive or disallow aliases.
- `gh release delete-asset v1.0.0 asset.zip` -> `write` -> `release_delete` / asset delete -> add `("release", "delete-asset")`.
- `gh repo archive owner/repo` -> `write` -> repo archive destructive -> add `("repo", "archive")`.
- `gh repo edit owner/repo --visibility public` -> `write` -> repo visibility/security mutation -> classify `repo edit` with sensitive flags as destructive.
- `gh repo rename newname` -> `write` -> repo rename destructive -> add `("repo", "rename")`.
- `gh repo transfer owner/repo someone` -> `write` -> repo transfer destructive -> add `("repo", "transfer")`.
- `gh repo deploy-key delete 1` -> `write` -> key delete -> add nested delete detection.
- `gh secret delete TOKEN` -> `write` -> secret delete -> add `("secret", "delete")`.
- `gh ssh-key delete abc` -> `write` -> key delete -> add `("ssh-key", "delete")`.
- `gh pr close 1` -> `write` -> PR close destructive/out-of-policy -> add `("pr", "close")`.
- `gh issue close 1` -> `write` -> issue close destructive/out-of-policy -> add `("issue", "close")`.
- `gh cache delete 1` -> `write` -> cache delete -> add `("cache", "delete")`.
- `gh ruleset delete 1` -> `write` -> ruleset delete -> add `("ruleset", "delete")`.
- `gh run delete 1` -> `write` -> run delete -> add `("run", "delete")`.
- `gh workflow disable ci.yml` -> `write` -> CI disable -> add `("workflow", "disable")`.
- `gh variable delete NAME` -> `write` -> variable delete -> add `("variable", "delete")`.
- `gh label delete bug` -> `write` -> label delete -> add `("label", "delete")`.
- `gh auth refresh -h github.com -s delete_repo` -> `write` -> credential scope escalation -> classify `auth refresh` with write/destructive scopes as destructive or disallow `gh auth`.
- `gh auth logout` -> `write` -> auth state destructive -> classify `gh auth` mutations as destructive.
- `hub delete owner/repo` -> `write` -> repo delete -> add hub-specific destructive commands or disallow `hub` except read allowlist.

### MAJOR - unlisted destructive `git` commands

- `git update-ref -d refs/heads/main` -> `write` -> ref delete -> add `update-ref -d/--delete` as destructive.
- `git branch -m main old` -> `write` -> branch rename -> classify branch rename/move/copy separately and deny if out-of-policy.
- `git branch --move main old` -> `write` -> branch rename -> same.
- `git branch --copy main old` -> `write` -> branch copy/ref mutation -> same.
- `git stash clear` -> `write` -> stash destructive -> add `stash clear`.
- `git stash drop` -> `write` -> stash destructive -> add `stash drop`.
- `git reflog delete HEAD@{0}` -> `write` -> reflog destructive -> add `reflog delete/expire`.
- `git filter-branch --force ...` -> `write` -> history rewrite -> add `filter-branch` as destructive.
- `git rebase -i HEAD~3` -> `write` -> history rewrite -> add `rebase` as destructive unless explicitly allowlisted.
- `git gc --prune=now` -> `write` -> object pruning/destructive recovery loss -> add `gc --prune*` as destructive.
- `git maintenance run --task=gc` -> `write` -> object pruning path -> classify maintenance gc/prune tasks as destructive.
- `git worktree remove --force ../wt` -> `write` -> worktree deletion -> add `worktree remove/prune`.
- `git remote remove origin` -> `write` -> remote config deletion -> add `remote remove/rm`.
- `git submodule deinit -f vendor/x` -> `write` -> submodule removal/deinit -> add `submodule deinit`.
- `git checkout -- .` -> `write` -> working tree discard -> add checkout path restore/discard detection.
- `git restore .` -> `write` -> working tree discard -> add restore path detection.
- `git switch other` -> `write` -> branch switch can discard/redirect work context -> classify `switch` as controlled/destructive unless read-only dry-run.
- `git rm -r .` -> `write` -> mass deletion -> add `rm` as destructive or require diff-risk elevation before allow.
- `git mv a b` -> `write` -> path mutation -> keep as write but require explicit file-scope/diff gate.
- `git notes remove HEAD` -> `write` -> metadata delete -> add `notes remove/prune`.
- `git replace -d abc` -> `write` -> ref replacement delete -> add `replace -d`.
- `git merge --abort` -> `write` -> working tree/index rollback -> classify abort/reset-like operations as destructive.
- `git rebase --abort` -> `write` -> working tree/index rollback -> same.

### MAJOR - parser and detection evasion

- `git.exe push --force` -> `[]` -> suspicious git executable -> detect Windows executable suffixes if cross-platform commands are possible.
- `gh-api -X DELETE /repos/o/r` -> `[]` -> suspicious gh wrapper -> detect `gh-*` helper/wrapper names or deny.
- `Git push --force` -> `[]` -> suspicious if case-insensitive shell/filesystem can resolve it -> normalize tool names where platform may be case-insensitive, otherwise document unsupported.
- Existing shell function `git() { ...; }; git push --force` can redefine semantics while still classifying by argv -> `force_push` only if literal args expose it; hidden body evades source command review -> fail closed on function definitions or shell reserved syntax in gitish input.
- Existing shell alias `git='git push --force --'` with `git origin main` -> likely `write` -> actual `force_push` -> do not trust shell aliases; run hook in alias-free noninteractive shell or fail closed on alias-bearing contexts.
- PATH shadowing `./git push --force` -> currently `force_push`, but executable may be arbitrary local wrapper -> require resolved executable path to trusted `git`/`gh`, or treat non-system paths as suspicious.
- `_looks_gitish` misses `$GIT`, `${GIT}`, `g${X}it`, `git-push`, `git.exe`, `gh-api` -> no fail-closed gate triggers -> replace regex-only gitish detection with token/AST plus conservative expansion detection.
- Parse failures only fail closed when `_looks_gitish` matches -> hidden expanded command can parse-fail or bypass without denial -> if shell metacharacters/expansions exist with destructive-looking args, fail closed even without literal `git`.

### MAJOR - Python source scan bypasses

- `from subprocess import Popen; Popen(('git','push','--force'))` -> `False` -> should gate -> scan Python AST for imported subprocess callables and tuple/list argv literals.
- `import os as o; o.system('git push --force')` -> `False` -> should gate -> AST-track aliases for `os.system`, `os.popen`.
- `from os import system; system('git push --force')` -> `False` -> should gate -> AST-track direct imports.
- `from os import popen; popen('git push --force')` -> `False` -> should gate -> same.
- `runner = __import__('subprocess').Popen; runner(('git','push','--force'))` -> may be missed unless literal list regex fires -> should gate -> fail closed on dynamic imports plus gitish string literals.
- `getattr(__import__('subprocess'), 'run')(['git','push','--force'])` -> currently caught only by `['git'` regex; string-built argv can bypass -> AST should detect dynamic subprocess usage or fail closed.
- `cmd = 'git ' + 'push --force'; subprocess.run(cmd, shell=True)` -> only caught because `subprocess.` appears, but command classification still needs fail-closed shell parsing -> route all shell=True subprocess strings through hardened classifier.
- `cmd = ['g'+'it','push','--force']; subprocess.run(cmd)` -> current source scanner catches `subprocess.` but argv-level classifier would not see literal `git` if only command hook sees source -> use AST constant folding or deny string-built git/gh argv.

### MINOR / Not currently bypassing but still hardening candidates

- `( git push --force )` -> `unparseable_suspicious` -> correct denial -> keep and test.
- `{ git push --force; }` -> `unparseable_suspicious` -> correct denial -> keep and test.
- `command git push --force` -> `unparseable_suspicious` -> correct denial, but noisy false positive -> either strip `command` as a safe prefix or keep fail-closed.
- `\git push --force` -> `force_push` -> correct denial -> keep and test.
- `git\ push --force` -> `unparseable_suspicious` -> correct denial -> keep and test.
- Quoted flags `git push "--force"` / `git push '--force'` -> `force_push` -> correct denial -> keep and test.
- Pipes with literal gitish input fail closed -> correct for `|`, but process substitution and redirections should be explicitly covered, not incidental.

## Recommended hardening (minimal, fail-closed)

1. Add a pre-parse fail-closed guard for gitish command strings containing unsupported shell features: `$`, newline, `&`, `(`, `)`, `{`, `}`, `<`, `>`, backslash-newline, function definitions, alias definitions, and command-position variables.

2. Split or fail closed on all shell command separators, not just `;`, `&&`, `||`: newline and single `&` are currently exploitable.

3. Treat `gh api` / `hub api` as denied by default unless method is `GET` and endpoint is on a narrow read allowlist. Any `DELETE`, `PATCH`, `PUT`, `POST`, `--field`, or `--raw-field` should be destructive/write-gated at minimum.

4. Expand the destructive table:
   `git push` refspec deletes, `+` refspecs, `--mirror`, `--prune`; `update-ref -d`; branch move/copy/delete; `stash clear/drop`; `reflog delete/expire`; `filter-branch`; `rebase`; `gc --prune`; `maintenance gc`; `worktree remove/prune`; `remote remove`; `submodule deinit`; `checkout/restore` path discard; `rm`; `notes remove`; `replace -d`; abort/reset-like operations.

5. Expand `gh` destructive table:
   `api`, `alias`, `auth`, `repo archive/edit/rename/transfer/deploy-key delete`, `release delete-asset`, `secret delete`, `ssh-key delete`, `pr close`, `issue close`, `cache delete`, `ruleset delete`, `run delete`, `workflow disable`, `variable delete`, `label delete`.

6. Replace `_looks_gitish` as the fail-closed dependency. It misses expanded commands and helper names. Add conservative detection for command-position expansion, `git-*`, `gh-*`, `hub-*`, Windows suffixes, and destructive git/gh argument patterns even when the literal tool token is absent.

7. Disallow or explicitly trust-resolve executable paths. `os.path.basename(argv[0]) == "git"` lets `./git` or a PATH-shadowed wrapper inherit trust.

8. Replace `scan_python_source` regexes with an AST scanner that tracks imports/aliases for `subprocess`, `os.system`, `os.popen`, direct imports, dynamic imports, `shell=True`, and string/list/tuple construction containing git/gh/hub. Regex is not adequate as a security gate.
