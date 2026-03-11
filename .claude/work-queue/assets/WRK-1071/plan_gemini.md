YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
Error executing tool read_file: File path '/mnt/local-analysis/workspace-hub/worldenergydata/pyproject.toml' is ignored by configured ignore patterns.
Attempt 1 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3.1-pro-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3.1-pro-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3.1-pro-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/node_modules/gaxios/build/cjs/src/gaxios.js:155:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:463:20)
    at async CodeAssistServer.requestStreamingPost (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:256:21)
    at async CodeAssistServer.generateContentStream (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:48:27)
    at async file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:256:26
    at async file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/telemetry/trace.js:81:20
    at async retryWithBackoff (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:130:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40) {
  config: {
    url: URL {
      href: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      origin: 'https://cloudcode-pa.googleapis.com',
      protocol: 'https:',
      username: '',
      password: '',
      host: 'cloudcode-pa.googleapis.com',
      hostname: 'cloudcode-pa.googleapis.com',
      port: '',
      pathname: '/v1internal:streamGenerateContent',
      search: '?alt=sse',
      searchParams: URLSearchParams { 'alt' => 'sse' },
      hash: ''
    },
    method: 'POST',
    params: { alt: 'sse' },
    headers: Headers {
      authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'content-type': 'application/json',
      'User-Agent': 'GeminiCLI/0.32.1/gemini-3.1-pro-preview (linux; x64) google-api-nodejs-client/10.6.1',
      'x-goog-api-client': 'gl-node/22.22.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    retry: false,
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor],
    duplex: 'half'
  },
  response: Response {
    size: 0,
    data: undefined,
    config: {
      url: URL {},
      method: 'POST',
      params: [Object],
      headers: Headers {
        authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
        'content-type': 'application/json',
        'User-Agent': 'GeminiCLI/0.32.1/gemini-3.1-pro-preview (linux; x64) google-api-nodejs-client/10.6.1',
        'x-goog-api-client': 'gl-node/22.22.0'
      },
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      retry: false,
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor],
      duplex: 'half'
    },
    [Symbol(Body internals)]: {
      body: [PassThrough],
      stream: [PassThrough],
      boundary: null,
      disturbed: false,
      error: null
    },
    [Symbol(Response internals)]: {
      type: 'default',
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      status: 429,
      statusText: 'Too Many Requests',
      headers: [Object],
      counter: 0,
      highWaterMark: 16384
    }
  },
  code: 429,
  status: 429,
  error: undefined,
  [Symbol(gaxios-gaxios-error)]: '7.1.3',
  [cause]: {
    message: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3.1-pro-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3.1-pro-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3.1-pro-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    code: 429,
    status: 'Too Many Requests'
  }
}
Error executing tool grep_search: Path does not exist: /mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection
Attempt 1 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3.1-pro-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3.1-pro-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3.1-pro-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/node_modules/gaxios/build/cjs/src/gaxios.js:155:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:463:20)
    at async CodeAssistServer.requestStreamingPost (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:256:21)
    at async CodeAssistServer.generateContentStream (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:48:27)
    at async file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:256:26
    at async file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/telemetry/trace.js:81:20
    at async retryWithBackoff (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:130:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:445:32)
    at async GeminiChat.streamWithRetries (file:///home/vamsee/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:265:40) {
  config: {
    url: URL {
      href: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      origin: 'https://cloudcode-pa.googleapis.com',
      protocol: 'https:',
      username: '',
      password: '',
      host: 'cloudcode-pa.googleapis.com',
      hostname: 'cloudcode-pa.googleapis.com',
      port: '',
      pathname: '/v1internal:streamGenerateContent',
      search: '?alt=sse',
      searchParams: URLSearchParams { 'alt' => 'sse' },
      hash: ''
    },
    method: 'POST',
    params: { alt: 'sse' },
    headers: Headers {
      authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'content-type': 'application/json',
      'User-Agent': 'GeminiCLI/0.32.1/gemini-3.1-pro-preview (linux; x64) google-api-nodejs-client/10.6.1',
      'x-goog-api-client': 'gl-node/22.22.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    retry: false,
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor],
    duplex: 'half'
  },
  response: Response {
    size: 0,
    data: undefined,
    config: {
      url: URL {},
      method: 'POST',
      params: [Object],
      headers: Headers {
        authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
        'content-type': 'application/json',
        'User-Agent': 'GeminiCLI/0.32.1/gemini-3.1-pro-preview (linux; x64) google-api-nodejs-client/10.6.1',
        'x-goog-api-client': 'gl-node/22.22.0'
      },
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      retry: false,
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor],
      duplex: 'half'
    },
    [Symbol(Body internals)]: {
      body: [PassThrough],
      stream: [PassThrough],
      boundary: null,
      disturbed: false,
      error: null
    },
    [Symbol(Response internals)]: {
      type: 'default',
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      status: 429,
      statusText: 'Too Many Requests',
      headers: [Object],
      counter: 0,
      highWaterMark: 16384
    }
  },
  code: 429,
  status: 429,
  error: undefined,
  [Symbol(gaxios-gaxios-error)]: '7.1.3',
  [cause]: {
    message: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3.1-pro-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3.1-pro-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3.1-pro-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    code: 429,
    status: 'Too Many Requests'
  }
}
Here is the refined plan based on an investigation of the workspace configuration, codebase structure, and CLI/cron behaviors.

---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: draft
version: "1.1"
---

## Mission

Establish performance baselines for compute-heavy engineering calculations so
regressions are caught before they reach production reports.

## Phase 1 — pytest-benchmark integration (TDD first)

**Tests first** (`scripts/testing/test_run_benchmarks.py`, 5 tests):
- `test_run_benchmarks_all_repos_exit_zero` — script returns 0 on clean run
- `test_run_benchmarks_single_repo` — `--repo assetutilities` runs only that suite
- `test_save_baseline_writes_json` — `--save-baseline` writes `config/testing/benchmark-baseline.json`
- `test_regression_detection_flags_slowdown` — injected 25% slowdown → exit 1
- `test_no_regression_passes` — baseline-equal result → exit 0

**assetutilities**:
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test` in `pyproject.toml`
- Create `assetutilities/tests/benchmarks/__init__.py`
- Create `assetutilities/tests/benchmarks/test_scr_fatigue_benchmarks.py`
  - `bench_keulegan_carpenter_number(benchmark)` — synthetic (D, U, T) inputs
  - `bench_soil_interaction_fatigue_factor(benchmark)` — synthetic soil profile

*Note: assetutilities CP calcs live in digitalmodel. assetutilities targets riser/fatigue calcs (`scr_fatigue.py`) — `keulegan_carpenter_number`, `soil_interaction_fatigue_factor`.*

**digitalmodel** (pytest-benchmark already installed; `tests/benchmarks/` exists):
- Create `digitalmodel/tests/benchmarks/test_cp_benchmarks.py`
  - `bench_cp_router_abs_gn_ships(benchmark)` — `ABS_gn_ships_2018` cfg dict
  - `bench_cp_router_dnv_rp_f103(benchmark)` — `DNV_RP_F103_2010` cfg dict
  - `bench_cp_router_all_routes(benchmark)` — parametrize over all 4 methods
- Create `digitalmodel/tests/benchmarks/test_wall_thickness_benchmarks.py`
  - `bench_wall_thickness_dnv(benchmark)` — synthetic DNV-ST-F101 input

*Import path: `from digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection import CathodicProtection`*

**worldenergydata** (pytest-benchmark in optional-dev; `tests/performance/` has conftest):
- Create `worldenergydata/tests/benchmarks/__init__.py`
- Create `worldenergydata/tests/benchmarks/test_eia_benchmarks.py`
  - Reuse `tests/performance/conftest.py` BenchmarkFixture setup
  - `bench_state_production_loader(benchmark)` — 1000 synthetic EIA records
  - `bench_basin_production_loader(benchmark)` — 500 synthetic basin records

## Phase 2 — run-benchmarks.sh + baseline tooling

**`scripts/testing/run-benchmarks.sh`** (modelled on `run-all-tests.sh` from WRK-1054):
```bash
REPOS = [
  {name: assetutilities, dir: assetutilities, pythonpath: src, benchmark_dir: tests/benchmarks},
  {name: digitalmodel, dir: digitalmodel, pythonpath: src, benchmark_dir: tests/benchmarks},
  {name: worldenergydata, dir: worldenergydata, pythonpath: "src:../assetutilities/src", benchmark_dir: tests/benchmarks},
]
```
- The script must `cd` into each repository directory before execution to guarantee `uv` resolves the correct local environment and lockfile.
- Per-repo execution: `uv run --with pytest-benchmark python -m pytest <benchmark_dir> --benchmark-only --benchmark-json=../scripts/testing/benchmark-results/<name>-tmp.json -q`
- Collect results → Aggregate into `scripts/testing/benchmark-results/benchmark-YYYY-MM-DD.json`
- `--repo <name>` — single-repo run
- `--save-baseline` — writes `config/testing/benchmark-baseline.json` from latest run
- `--no-compare` — skips comparison (bootstrap / first run)
- Default compare mode: reads baseline, flags any mean >20% slower as REGRESSION (exit 1)

**`scripts/testing/parse_benchmark_output.py`**:
- Reads aggregated pytest-benchmark JSONs; compares means against baseline
- Prints regression table; exits 1 if any regression found

`.gitignore`: add `scripts/testing/benchmark-results/` (runtime artifacts)

## Phase 3 — cron + integration

- Add weekly cron entry to `scripts/cron/crontab-template.sh`:
  `0 4 * * 0 PATH=$PATH:~/.local/bin <REPO_ROOT>/scripts/testing/run-benchmarks.sh >> logs/quality/benchmark-cron.log 2>&1` *(Note: Explicit PATH definition ensures cron can locate `uv`)*
- Bootstrap baseline: `./scripts/testing/run-benchmarks.sh --save-baseline --no-compare`
- `config/testing/benchmark-baseline.json` committed from initial run

## Test Strategy

| Layer | What | When |
|-------|------|------|
| TDD harness | 5 tests in `test_run_benchmarks.py` | Before implementation |
| Unit (benchmark) | Each `bench_*` function runs without error | Each commit |
| Integration | `run-benchmarks.sh` exits 0 | Before merge |
| Regression gate | >20% slowdown = exit 1 | Weekly cron + pre-merge |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| worldenergydata pytest-benchmark only in optional-dev deps | High | Medium | Use `uv run --with pytest-benchmark` or `--group dev` to force activation. |
| Benchmark variance causing false positives | Medium | Low | Use `--benchmark-min-rounds=5`; flag only >20% (not >5%) |
| Cron missing `uv` executable in restricted `$PATH` | High | High | Explicitly define `PATH=$PATH:~/.local/bin` (or equivalent absolute path) in the cron template |
| Multi-repo aggregation limitations | Low | Low | Use custom `parse_benchmark_output.py` script instead of pytest's native `--benchmark-compare` to handle comparing multiple separate repository json outputs against a unified baseline |

## Out of Scope

- Benchmark results dashboard (WRK-1057 repo-health integration — follow-on)
- assethold / ogmanufacturing benchmarks (no heavy calc modules identified)
- Historical regression tracking beyond baseline comparison

---

### Review Notes

1. **CP Calculation Configurations**: The original draft defined `bench_cp_router_abs_gn_ships` but instructed it to use a `DNV_RP_F103_2010` configuration dict. I corrected this in Phase 1 to ensure the function names and their respective input configuration dictionaries match properly (`ABS_gn_ships_2018` for the ABS function, and added a specific DNV function). 
2. **`uv run` Environment Isolation**: If `run-benchmarks.sh` invokes `uv run` from the workspace root for all repositories, `uv` might use the root's environment or fail to resolve local imports. The refined plan explicitly instructs the bash script to `cd` into each `dir` before execution to bind exactly to that repository's configurations and lockfile.
3. **Cron PATH limitations**: A classic failure point for CI/CD scheduled tasks. Cron jobs execute with a highly restricted `PATH` (typically just `/usr/bin:/bin`). Since `uv` is likely installed in the user's `~/.local/bin` or a system-managed location, the refined plan explicitly injects a `PATH` update into the crontab execution line.
4. **`pytest-benchmark` Dependency in `worldenergydata`**: `pytest-benchmark` currently lives in `[project.optional-dependencies] dev` and the `dev` dependency group in `worldenergydata/pyproject.toml`. Standard `uv run` will bypass it unless explicitly requested. I modified the command in Phase 2 to use `--with pytest-benchmark` ensuring it installs into the ephemeral runner if not natively present in the synced environment.
5. **assetutilities Test Path Risks**: The original draft noted a risk that `assetutilities` tests are in `src/assetutilities/tests/`. However, inspection of `assetutilities/pyproject.toml` reveals `testpaths = ["tests"]` is already explicitly configured to support the repo root. Thus, placing the benchmarks directly in `<repo_root>/tests/benchmarks/` is structurally correct and will be picked up properly by `pytest`.
