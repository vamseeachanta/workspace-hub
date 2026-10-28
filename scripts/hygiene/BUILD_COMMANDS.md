# Artifact rebuild commands

A repository can declare published reports, pages, figures and data files in
`artifacts.registry.json`. The verifier checks coverage and dependencies without
running commands by default. Explicit `--run` compares outputs in disposable
copies of tracked files. This tooling implements the convention requested in
issue #4222; it does not enroll repositories or change publication workflows.

## Revision history

| Revision | Date | What changed and why |
| --- | --- | --- |
| 1 | 2026-10-22 | Define registry, verification and suggestion interfaces so artifact rebuild commands can be checked. |
| 2 | 2026-10-28 | Add synthetic matrix producer integration coverage to check independent projections, repeatability and per-artifact rebuild failures. |

## Registry

The root document is an array. Each object contains:

| Field | Required value |
| --- | --- |
| `path` | Unique output file, relative to the repository root. |
| `kind` | One of `report`, `page`, `figure`, `data`; these are classification conventions. |
| `build.cwd` | Working directory relative to the root; `.` means the root. |
| `build.argv` | Nonempty array of nonempty strings; the executable is followed by its arguments. |
| `inputs` | Array of input paths relative to the root, including build scripts where appropriate. Directories are permitted. |
| `budget_seconds` | Optional finite positive number overriding the default rebuild timeout. |

Unknown fields and duplicate JSON keys are errors. Declaration paths use
canonical POSIX spelling: no absolute paths, drive prefixes, backslashes, parent
traversal, control characters, `.git` components or symlinks. Only `cwd` may be
`.`. A build string or an `argv` shell string is refused; argument arrays are
passed without a shell. Shell interpreters in arrays still execute trusted code.

## Configuration

`--patterns patterns.json` reads a small JSON object. Omitted fields keep their
defaults; an explicit `patterns` list replaces the defaults, including an empty
list. Revision 1 defines these maintainer policy defaults, rather than physical
acceptance criteria:

```json
{
  "patterns": [
    "docs/reports/**/*.html",
    "docs/reports/**/*.pdf",
    "**/figures/**/*.svg",
    "**/assets/**/*.svg"
  ],
  "default_timeout_seconds": 120,
  "normalise": []
}
```

The timeout applies separately to each command. An artifact's `budget_seconds`
takes precedence. These numbers are configurable operational policy. Glob `**`
matches zero or more directories; `*` matches within one path component. Matching
is case sensitive. Registry entries are checked even outside the selected globs.

With `--run --normalise`, configured rules remove complete matching UTF-8 lines
from both reference and rebuilt output. Without `--normalise`, all comparisons
are byte comparisons. For example:

```json
{
  "normalise": [
    {"pattern": "docs/reports/**/*.html", "regex": "^built-at: .*$"}
  ]
}
```

Expressions must start with `^` and end with `$`; matching uses `fullmatch` on
each line without its line terminator. Other bytes, including remaining line
terminators, are unchanged. Rules apply only to their matching output paths.
Invalid expressions and non-UTF-8 outputs selected for normalisation are errors.
The maintainer is responsible for ensuring rules remove only irrelevant
timestamp lines; broad rules can conceal changes. No heuristic tolerance applies.

## Worked example

Run this block from any directory after setting `CHECKER` to the wrapper's
location. `EXAMPLE_ROOT` can name an existing temporary directory; otherwise
`mktemp` supplies it. Only disposable example files are written. The expected
bytes are calculated directly: the builder and reference each contain
`example` followed by a newline. Adding `extra.html` introduces exactly one
unregistered output. Git staging below affects only the temporary repository.

<!-- example:start -->
```sh
: "${CHECKER:?set CHECKER to the wrapper location}"
: "${EXAMPLE_ROOT:=$(mktemp -d)}"
mkdir -p "$EXAMPLE_ROOT/repository"
cd "$EXAMPLE_ROOT/repository"
git init -q
mkdir -p docs/reports
cat > build.py <<'PY'
from pathlib import Path
Path('docs/reports/example.html').write_bytes(b'example\n')
PY
cat > artifacts.registry.json <<'JSON'
[
  {
    "path": "docs/reports/example.html",
    "kind": "report",
    "build": {"cwd": ".", "argv": ["python3", "build.py"]},
    "inputs": ["build.py"]
  }
]
JSON
python3 build.py
git add --all
sh "$CHECKER" --repo .
python3 -I "${CHECKER%.sh}.py" --repo . --run
printf 'extra\n' > docs/reports/extra.html
if sh "$CHECKER" --repo .; then
    echo 'Expected an unregistered output' >&2
    exit 1
else
    result=$?
    test "$result" -eq 1
    printf 'failure status: %s\n' "$result"
fi
```

Expected standard output:

<!-- output:start -->
```text
OK
OK
UNREGISTERED: "docs/reports/extra.html"
failure status: 1
```

The executable documentation test runs this exact block:

```sh
uv run --no-project --with pytest python -m pytest tests/hygiene/ -q -p no:cacheprovider
```

## Findings and exit codes

Revision 1 defines exit `0` for success (`OK`), `1` for findings, and `2` for
configuration, repository-access or usage errors. Findings print the code and
JSON-escaped relative path. Diagnostic messages never echo command arguments,
child output or raw filesystem exceptions.

| Finding | Meaning |
| --- | --- |
| `UNREGISTERED` | A file matches a selected pattern but has no registry entry. Untracked matching files are included. |
| `MISSING_OUTPUT` | A declared output is not a file. |
| `MISSING_COMMAND` | The working directory is absent, or the executable is neither a file relative to `build.cwd`, an executable name on `PATH`, nor `python`/`python3`. This is a presence check, not an executability guarantee. |
| `MISSING_INPUT` | A declared input is absent. |
| `BUILD_FAILED` | A rebuild could not start or returned a nonzero status. |
| `NOT_REPRODUCED` | The rebuilt output is absent or its bytes differ after any enabled rules. |
| `TIMEOUT` | A rebuild exceeded its configured budget. |

Rebuilds start only when static checks pass. Each artifact gets a fresh plain
copy of regular files enumerated by `git ls-files --cached -z`, without Git
metadata, untracked files or ignored caches. Its copied output is removed before
execution, so a no-op cannot pass. File modes are copied. Declared inputs are
existence checks, not a complete dependency graph or dependency hashes.

The reference bytes and copied inputs come from the current tracked working
tree. This supports checking pending changes before a commit. To check published
bytes, invoke the verifier on a clean checkout of that revision. This tool does
not authenticate commits or fetch history. The repository root must be supplied
for Git operations. Deleted tracked files, symlinks and submodules prevent a
tracked export rather than silently changing the build basis.

## Integration coverage

`tests/hygiene/test_build_commands_matrix_integration.py` exercises an exact copy
of `scripts/reporting/readiness_matrix_view.py` through its CLI in disposable Git
repositories. Explicit synthetic JSON inputs define roles `alpha` and `beta`:
alpha requires `checks/build` and `checks/test` and supplies a `pass` observation
covering both; beta requires `checks/review` and supplies no observation. Both
have nonempty task and authentication expectations and empty CLI requirements.
The JSON reference and parsed HTML cells are compared against literal expected
rows, including beta's `unverified` status and empty evidence references, before
the verifier runs.

Separate argv declarations rebuild the JSON and HTML outputs twice with `--run`,
checking byte preservation of source files, inputs, references and Git metadata,
including the index. Changing alpha's observation rejects both stale references;
replacing either command with a successful no-output fixture rejects only that
artifact while the other command remains a positive control. Child diagnostics
are excluded from verifier output. The examples follow issue #4222 and use the
existing registry schema and strict byte comparisons without normalisation.

This coverage establishes producer/verifier integration only. Repository-wide
artifact enrollment, live evidence authenticity, readiness and publication
remain outside the demonstrated scope; the existing publication limits apply.

## Suggestions

```sh
python -I scripts/hygiene/check_build_commands.py --repo . --suggest
```

`--suggest` also works before a registry exists. It lists unregistered outputs,
then prints `CANDIDATE` JSON records containing their path and proposed `build`
object. It searches tracked UTF-8 text scripts for the output basename. Python,
shell, JavaScript, Ruby and Perl suffixes suggest `python3`, `sh`, `node`, `ruby`
and `perl`, respectively; executable scripts with shebangs suggest direct
execution. A shell suffix does not establish compatibility with POSIX `sh`.
Multiple candidates remain alternatives; absence of a candidate prints only the
unregistered finding. No command runs and no registry is written. These are
basename hints requiring maintainer review, not proven recipes. Standard output
can contain candidate relative filenames but never matched source lines.

## Hook usage

```sh
sh scripts/hygiene/check_build_commands.sh --repo . --patterns patterns.json
```

The POSIX wrapper locates its sibling verifier, selects Python from `PATH`, and
uses isolated mode (`-I`). It is suitable for a pre-push hook, runs static checks
only and refuses execution/suggestion flags. Hook installation and default
repository enrollment are intentionally left to the maintainer.

## Limits and portability

Python 3.11 or newer and Git are required for rebuilds/suggestions. The wrapper
and worked example require POSIX `sh`. Direct script execution requires its
platform's executable permissions; tests use POSIX mode `0755`. The validator's
control-character exclusion follows ASCII codes below `32` and DEL (column 7,
row 15, or `127`), per [RFC 20 (1969), section 2](https://www.rfc-editor.org/rfc/rfc20.txt).
No engineering coefficients or acceptance limits are used.

Commands must be trusted. A temporary copy is not a security sandbox: arbitrary
code can access the surrounding filesystem or network. The verifier itself
does not write into the checked repository or its Git metadata. Rebuilds receive
only `PATH` and platform system-directory variables, plus disposable user,
temporary and cache directories. Credentials, Python search-path overrides and
Git bindings are not forwarded. A Git discovery ceiling prevents ancestor
checkout discovery, and temporary roots inside the checked repository are refused.
No dependency installation is performed. Tools
depending on Git metadata, undeclared environment variables, unavailable external
programs or credentials can therefore fail and need a self-contained recipe.
Command standard output/error are discarded to avoid publishing credentials.
POSIX timeouts kill the command process group; other platforms kill the direct
child only. Detached descendants are outside this tool's supervision.

Byte equality is strict, including PDF metadata and SVG identifiers. Semantic
equality, hermetic toolchains, build caching, publication and automatic command
discovery are outside this convention. Normalisation is an explicit maintainer
policy, not proof that omitted content is immaterial.

## Sources

- Issue #4222 defines the artifact registry and required finding categories.
- `scripts/reporting/generate-calc-report.py` provides the existing
  required-field validation and inherited-Git-binding isolation patterns.
- `scripts/readiness/publish-equality.sh` documents why generated artifacts need
  rebuild and publication evidence; this verifier does not change that script.
- This document, revision 1, defines the configurable patterns, timeout, kind
  vocabulary and exit-code policy used by this tooling.
