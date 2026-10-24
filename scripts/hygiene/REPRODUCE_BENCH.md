# Artifact reproduction benchmark

Measure trusted, registered rebuild commands using Python 3.11 and the standard
library. The checked repository is read only: reports, history and temporary
copies must be outside it. This tool does not install dependencies.

## Configuration

The config is a JSON object. Unknown fields are rejected.

| Field | Type | Meaning |
| --- | --- | --- |
| `target_seconds` | positive finite number | Default 60 seconds: the maintainer's stated target in issue #4223. |
| `repeats` | positive integer | Configurable implementation default 3; provenance is unverified. |
| `timeout_seconds` | positive finite number | Required subprocess wall-time limit; no inferred default. |
| `clean_checkout` | boolean | Default true; a new committed tracked-file copy for every repeat. False reuses an isolated copy within each artifact. |
| `history` | string | Optional JSONL output path, resolved relative to the config directory. Created if absent. |
| `history_window` | positive integer | Required with `--compare history`; number of prior matching successful runs to consider. |
| `regression_ratio` | positive finite number | Configurable implementation default 1.5; provenance is unverified. Growth strictly above baseline times this ratio is a regression. |

The positivity constraints define valid measurements and counts, rather than
performance acceptance limits. Explicit small targets and timeouts are useful
for synthetic tests. Performance settings belong to each repository's maintainers.

The committed `artifacts.registry.json` is a JSON list with the format from
registry issue #4222 and the benchmark task:

```json
[
  {
    "path": "alpha.txt",
    "kind": "text",
    "build": {"cwd": ".", "argv": ["python3", "alpha.py"]},
    "inputs": ["alpha.py"],
    "budget_seconds": 60
  }
]
```

`budget_seconds` is optional and overrides the target. Artifact paths and inputs
must name committed regular files; working directories must be relative. Paths
with traversal, backslashes, drive prefixes or Git metadata components are
rejected. `argv` is a literal argument list; no shell is inserted. Commands and
all dependency access must already be trusted. Inputs enumerate files, not
directories. The registry and snapshot use HEAD, so uncommitted edits are excluded.

## Method and verdicts

`git rev-parse HEAD` pins one revision. `git ls-tree -rz` selects its paths
and executable modes; `git cat-file` supplies its bytes. Staged additions,
deletions and edits do not affect the snapshot. Each copy excludes Git metadata, ignored
files and untracked caches. The committed output is removed before every build,
including warm repeats: a command that does nothing cannot pass. Preparation,
copying, output hashing and report writing are excluded from the measurement.
`time.perf_counter` brackets only the subprocess call, including its startup,
wait and timeout cleanup. Build output is discarded rather than published.

Every observation records elapsed seconds, exit status (null if unavailable),
output SHA-256 (null if absent), status and phase. The first observation is called
cold and the remainder warm by order. System caches are not flushed. With clean
copies, warm means later observations with potentially warmer system caches;
with reuse enabled, intermediates may also survive within that artifact's copy.
Environment and user cache directories remain separate for every observation.

| Verdict | Condition |
| --- | --- |
| `PASS` | Every output matches the committed bytes and median time is within budget. |
| `SLOW` | Every output matches, but median time exceeds the stated budget. |
| `NOT_REPRODUCED` | A successful command leaves no output or different bytes. |
| `FAILED` | A command fails to start or exits unsuccessfully. |
| `TIMEOUT` | A subprocess exceeds the configured timeout. |

All repeats run. Aggregate precedence is TIMEOUT, FAILED, NOT_REPRODUCED, then the
median-based speed verdict. The total row sums artifact medians and identifies
the longest single observed artifact. It does not claim end-to-end elapsed time.

History comparison reads prior records before appending the current record. It
uses the median of the last N matching, successfully reproduced records for each
artifact, then compares the current median strictly against that baseline times
the configured ratio. A first run has no baseline and no regression. A zero
baseline permits no positive growth. Matching requires the same artifact bytes,
command and declared input object digests. Failed records are excluded. History
is appended even when a build fails. Serialize callers sharing a history file;
concurrent append locking is outside this tool's scope.

## Worked example

Run this from the tool's repository. All generated files will be under a new
temporary directory; no example output is written into this checkout:

```sh
export REPRODUCE_BENCH="$(git rev-parse --show-toplevel)/scripts/hygiene/reproduce_bench.py"
# Save the following Python block externally, then run: python3 example.py
```

The two artifacts below independently contain `expected` followed by a newline.
Three repeats per artifact imply six builds. The demonstration timeout of five
seconds and history window of two records are explicit example inputs, not
recommended limits. Git's import protocol creates a synthetic local revision
without requiring configured identity or changing the tool's repository.

```python
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(tempfile.mkdtemp(prefix="reproduce-example-"))
repo = root / "repo"
repo.mkdir()
output = root / "output"
output.mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
subprocess.run(["git", "init", "-q", str(repo)], check=True, env=env)
registry = []
for name in ("alpha", "beta"):
    (repo / f"{name}.py").write_text(
        f"from pathlib import Path; Path('{name}.txt').write_bytes(b'expected\\n')\n",
        encoding="utf-8", newline="\n"
    )
    (repo / f"{name}.txt").write_text("expected\n", encoding="utf-8", newline="\n")
    registry.append({"path": f"{name}.txt", "kind": "text",
                     "build": {"cwd": ".", "argv": [sys.executable, f"{name}.py"]},
                     "inputs": [f"{name}.py"]})
(repo / "artifacts.registry.json").write_text(json.dumps(registry), encoding="utf-8", newline="\n")
stream = b"commit refs/heads/example\ncommitter Example <example> 0 +0000\ndata 7\nexample\n"
for file in sorted(repo.iterdir()):
    if file.is_file():
        content = file.read_bytes()
        stream += f"M 100644 inline {json.dumps(file.name)}\ndata {len(content)}\n".encode()
        stream += content + b"\n"
subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet"],
               input=stream + b"\ndone\n", check=True, env=env)
subprocess.run(["git", "-C", str(repo), "symbolic-ref", "HEAD", "refs/heads/example"],
               check=True, env=env)
subprocess.run(["git", "-C", str(repo), "read-tree", "HEAD"], check=True, env=env)
settings = {"timeout_seconds": 5, "history": "bench-history.jsonl", "history_window": 2}
(output / "bench.json").write_text(json.dumps(settings), encoding="utf-8", newline="\n")
subprocess.run([sys.executable, "-I", os.environ["REPRODUCE_BENCH"],
               "--repo", str(repo), "--config", str(output / "bench.json"),
               "--out", str(output / "report.json"), "--compare", "history"], check=True)
report = json.loads((output / "report.json").read_text(encoding="utf-8"))
assert [a["verdict"] for a in report["artifacts"]] == ["PASS", "PASS"]
print("PASS: two artifacts; JSON, HTML and history written")
```

Report excerpt (volatile timestamps, descriptors, digests and measured durations
omitted; these fixed fields follow directly from the example inputs):

```json
{"schema_version": 1, "method": {"target_seconds": 60, "repeats": 3,
 "timeout_seconds": 5, "clean_checkout": true}}
```

The test `test_worked_example` executes this exact block and validates both
reports, the history record, the six observations and the unchanged source tree.

## Report schema

`validate_report` is the standard-library validator for the closed version-1
JSON contract. Objects require exactly their defined fields; unsupported schema
versions, malformed digests, non-finite or negative times and inconsistent repeat
summaries are rejected. The contract is intentionally versioned locally, with no
external schema downloads.

- Root: `schema_version`, `recorded_at` (UTC ISO timestamp), `revision` (Git HEAD),
  `machine`, `method`, `comparison`, `artifacts` and `totals`.
- Machine: `source`, `system`, `release`, `machine`, `python_version`, `cpu_count`.
  Strings come from `platform`; processor count comes from `os.cpu_count` and may
  be null. `hostname` is omitted by default.
- Method: `target_seconds`, `repeats`, `timeout_seconds`, `clean_checkout`.
- Comparison: `enabled`, `history_window` (null when disabled), `regression_ratio`.
- Artifact: `path`, `kind`, `expected_sha256`, `fingerprint`, `budget_seconds`,
  `verdict`, `runs`, `timing`, `regression`, `baseline_median_seconds`.
- Run: `phase`, `seconds`, `exit_status`, `sha256`, `status`.
- Timing: `min_seconds`, `median_seconds`, `max_seconds`.
- Totals: `sum_medians_seconds`, `longest_single_artifact` (null for an empty
  registry, otherwise `{path, seconds}`).

The adjacent single-file HTML report uses inline styles, no scripts and no
external resources. It shows paths, verdict badges, time/budget bars, method,
limits and standard-library descriptors. Names are HTML-escaped. JSON retains
measurement precision; HTML rounds displayed timing values.

## Invocation and scheduling

From an external output directory, a scheduler can use repository and tool paths
supplied through its environment:

```sh
python3 -I "$BENCHMARK_TOOL" --repo "$REPOSITORY" --config bench.json --out report.json --compare history
```

Omit `--compare history` for collection without regression evaluation. With a
configured history path, every completed report is appended regardless. Output
JSON and HTML paths must differ from the history path. `--anonymise-host` is on
by default; only explicit `--no-anonymise-host` adds `platform.node()` to a report.
Schedulers publishing results should retain the default.

Exit codes are part of this local command contract: 0 means all artifacts PASS
without regressions; 1 means any SLOW, regression, non-reproduction, failure or
timeout; 2 means invalid configuration, invalid history or execution setup error.
A valid empty registry reports an empty table and zero aggregate time.

## Limits

Wall time on one machine is not comparable across machines. Standard-library
descriptors do not establish equivalence of machine load, thermal conditions or
dependencies. History should be collected in a controlled environment. This tool
neither flushes system caches nor installs, pins or downloads build dependencies.
It rejects tracked symlinks and submodules rather than following them into other
trees. Git LFS materialization is outside scope; committed pointer bytes are what
Git supplies. Full tracked copies can be expensive; that expense is excluded.

Commands execute with the caller's permissions and must be trusted. The tool
isolates their cwd, temporary files, user directory and caches, and removes
inherited Git bindings and other environment values. This is not an operating
system sandbox; an arbitrary command can still access absolute paths or the
network. Timeouts kill the process group on POSIX; other systems kill the direct
child. No command text, environment values, stdout or stderr is included in reports.

## Sources and numerical basis

- Issue #4223, benchmark requirement: committed rebuild, timing, JSON/HTML and
  the maintainer's 60-second target.
- Issue #4222 describes the registry requirement. The provenance of the
  implementation defaults of three repeats and regression ratio 1.5 is unverified;
  neither is established by the linked issues. Both remain configurable and
  require a linked maintainer statement before attribution as approved criteria.
- `scripts/benchmarks/perf-bench.sh`, `run_bench`: existing subprocess wall-time
  and append-only history convention; this implementation substitutes a monotonic
  standard-library timer and omits machine names.
- [Python 3.11 time, perf_counter](https://docs.python.org/3.11/library/time.html#time.perf_counter):
  elapsed high-resolution clock including sleep. Public documentation retrieved successfully.
- [Python 3.11 statistics, median](https://docs.python.org/3.11/library/statistics.html#statistics.median):
  middle value; arithmetic mean of the middle two for even sample counts. Public
  documentation retrieved successfully.

Test-only constants are defined by independent hand calculations in test
docstrings. For example, sorted [1, 2, 3] has median 2; [4, 6, 8] has median 6;
the sum is 8. Prior median 2 times ratio 1.5 gives a threshold of 3. Display
percentages use the definition of percent: 100 times median divided by budget.
SHA-256 digests use 64 hexadecimal digits because 256 bits divided by four bits
per hexadecimal digit is 64. Chunk sizes and file modes implement copying and
Git's regular/executable-file representation; they are not acceptance limits.
