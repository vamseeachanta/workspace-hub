YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
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
Attempt 2 failed with status 429. Retrying with backoff... GaxiosError: [{
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
Attempt 3 failed with status 429. Retrying with backoff... GaxiosError: [{
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
# WRK-1061 Refined Plan: generate-review-input.sh

## Mission
Auto-generate a structured cross-review input file from the WRK item and its git diff, ensuring robust error handling, graceful fallbacks for missing context files, and stable diff truncation, so agents stop hand-writing review bundles and the review is always complete and formatted consistently.

## Step 1 — `scripts/review/generate-review-input.sh WRK-NNN [--phase N]`
Single bash script, strictly POSIX compliant where possible, no external deps beyond standard git + coreutils.

**Logic & Robustness Enhancements:**
1. **Parse args:** 
   - Validate `WRK-NNN` format using regex.
   - Accept optional `--phase N` (default: 1).
   - Support `-h|--help` for usage documentation.
2. **Find WRK item:**
   - Search paths explicitly within the workspace hub: `.claude/work-queue/pending/`, `.claude/work-queue/working/`.
   - Error gracefully with exit code 1 and a helpful message if not found.
3. **Extract frontmatter fields:**
   - Use a robust `awk` or `sed` routine to extract the block between the first `---` and second `---`.
   - Handle missing fields gracefully (default to "Unknown" or "Not specified" rather than failing).
   - Extract: title, mission text, ACs, complexity, route, subcategory, target_repos.
4. **Build git diff:**
   - Verify script is running inside a git repository before executing `git diff`.
   - If `target_repos` is non-empty, expand it safely (handling potential spaces or odd characters).
   - Use `git diff HEAD` to capture all staged and unstaged work in the workspace.
   - **Truncation Logic:** Capture the diff to a variable or temporary file. If the line count exceeds 300, pipe through `head -n 300` and append a clear warning: `\n\n> ⚠️ **[System] Diff truncated at 300 lines. Reviewer: note that the diff is incomplete.**`
5. **Read checkpoint summary:**
   - Check for the existence and readability of `assets/WRK-NNN/checkpoint.yaml`.
   - If missing, empty, or corrupt, inject fallback text: `_No valid checkpoint summary found._`
6. **Read test snapshot:**
   - Safely resolve the most recent test result: `ls -t scripts/testing/results/*.md 2>/dev/null | head -n 1`.
   - Check if the file exists and is not empty. If none found, inject fallback text: `_No test snapshot available._`
7. **Generate focus prompts:**
   - Implement a localized `case` statement based on `subcategory` and `complexity` to output 3–5 tailored prompts (e.g., if complexity is High, prompt for architectural review; if subcategory is security, prompt for input validation checks). Avoid external LLM calls for this step.
8. **Write output:**
   - Ensure the target directory exists: `mkdir -p scripts/review/results/`.
   - Write the finalized markdown to `scripts/review/results/wrk-NNN-phase-N-review-input.md`.

**Output sections:**
```markdown
# WRK-NNN Phase N Review Input

## WRK Context
- **Title:** [title]
- **Route / Subcategory:** [route] / [subcategory]
- **Complexity:** [complexity]

### Mission
[mission text]

### Acceptance Criteria
[ACs]

## Changed Files + Diff
```diff
[scoped diff, ≤300 lines]
```
[Truncation notice if applicable]

## Test Snapshot
[last test output or "not available"]

## Checkpoint Summary
[checkpoint summary or "not found"]

## Review Focus
[3–5 tailored prompts based on metadata]

## Verdict Request
Please review the above context and diff. Provide a clear **APPROVED** or **REJECTED** verdict along with any feedback.
```

## Step 2 — Tests: `tests/testing/test-generate-review-input.sh`
Expand test coverage from 6 to 10 cases to ensure resilience:

1. Basic invocation produces `wrk-NNN-phase-1-review-input.md`.
2. Output contains all required Markdown section headings.
3. `--phase 2` flag produces the correct updated filename.
4. Diff truncation notice is accurately appended for diffs >300 lines.
5. Missing WRK item exits non-zero with a clear error to standard error.
6. Empty `target_repos` falls back to a full workspace diff gracefully.
7. **[Added]** Missing `checkpoint.yaml` is handled gracefully without script failure.
8. **[Added]** Missing or empty test snapshot directory is handled gracefully.
9. **[Added]** Malformed Markdown frontmatter (missing keys) applies safe default values.
10. **[Added]** Target directory `scripts/review/results/` is dynamically created if it does not previously exist.

## Acceptance Criteria
- `generate-review-input.sh WRK-NNN` produces a valid input file.
- Output strictly includes: mission, ACs, diff (scoped), test snapshot, focus prompts.
- Diff truncation works correctly for large diffs (>300 lines) and clearly warns the reviewer.
- `--phase N` flag is respected in the output filename.
- Missing context files do not crash the script or corrupt the output Markdown.
- Integrates seamlessly with `cross-review.sh` without requiring modifications to the upstream script.
- Cross-review (Codex/Gemini) parsing of the output file succeeds without format confusion.

---

## Gemini Notes: Systems Reliability Review

1. **Failure Modes in Frontmatter Parsing:** 
   Relying on `awk` to parse YAML frontmatter is historically fragile, especially if fields like `mission` contain multiline text, colons, or embedded quotes. *Mitigation applied in refined plan:* Instructed the use of a more robust text block extraction between `---` markers, falling back to default values for missing keys rather than returning empty strings that could break downstream templates.
2. **Carry-Forward Logic (Context Files):** 
   The original draft assumed `checkpoint.yaml` and test snapshots would always exist. In reality, early-phase reviews or aborted test runs will lack these. *Mitigation applied:* Added explicit file existence and readability checks with graceful fallback text to prevent `cat` errors or blank sections in the output document.
3. **Diff Truncation Integrity:** 
   Arbitrarily truncating a unified diff at 300 lines can cut a git patch mid-hunk. If an LLM reviewer reads this without knowing it's truncated, it might flag a "syntax error" due to the missing lines. *Mitigation applied:* Enforced the injection of a highly visible Markdown blockquote (`> ⚠️ [System] Diff truncated...`) to explicitly warn the cross-review agent that context is incomplete.
4. **Test Coverage Gaps:** 
   The draft's 6 tests focused heavily on the happy path. *Mitigation applied:* Expanded to 10 test cases specifically targeting edge cases—missing directories, missing secondary files, and malformed metadata—ensuring the script fails safe.
5. **Runtime / Environmental Risks:**
   - **Missing Directories:** Redirection to `scripts/review/results/...` will fail if the directory was never created. Added `mkdir -p`.
   - **Git Context:** Running `git diff HEAD` outside of a git repository (e.g., in a weird CI runner state) will spew errors. The script must verify it is in a git tree.
   - **Filename Globbing Limit:** Sniffing the most recent test via `ls -t` can fail or produce errors if the directory is empty. Piped errors to `/dev/null` to keep standard output clean.
