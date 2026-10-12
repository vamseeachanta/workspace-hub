# Interactive review/rating app submit pattern

Use when building local browser apps for human review, scoring, calibration, triage, QA queues, or annotation.

## Lesson

Do not make the user complete a manual export/download/upload loop as the primary workflow. For local review apps, provide a one-click **Submit** path by default, with JSON/CSV export only as fallback.

## Recommended shape

1. Build the self-contained HTML app with:
   - localStorage autosave.
   - visible progress state.
   - JSON/CSV export fallback.
   - JSON import/resume if useful.
   - a prominent `Submit` button.
2. Add a tiny localhost receiver next to the HTML artifact, for example:
   - Python `http.server` on `127.0.0.1:<port>`.
   - `POST /submit` accepts JSON payload.
   - `GET /health` returns `{ok: true, out_dir: ...}`.
   - writes timestamped submissions plus `latest.json` under `submissions/`.
   - sets permissive CORS headers for `file://` HTML posting to localhost.
3. In the browser app, implement submit fallback:
   - Try `fetch('http://127.0.0.1:<port>/submit', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})`.
   - On failure, copy JSON to clipboard and show exact receiver start command.
4. Verify before handing off:
   - Static JS syntax check by extracting `<script>` and running `node --check` if Node is available.
   - Browser load renders expected card/control counts.
   - A test score/note/checkbox updates app state.
   - Submit receiver `/health` works.
   - Test POST saves `submissions/latest.json`.
   - Reset any test ratings before user handoff.

## Pitfalls

- Embedded JS strings generated from Python often break if newline escaping is wrong. Prefer `\\n` inside generated JavaScript string literals and run `node --check`.
- Self-contained `file://` apps cannot write files directly. Use a localhost receiver for real submit, not a fake button that only downloads.
- Keep export/copy paths as fallback, but do not make them the primary UX for repeated human calibration work.
- If the receiver is not running, the app should fail soft with instructions and clipboard/export fallback.

## Minimal receiver contract

```text
GET  /health -> {"ok": true, "out_dir": "..."}
POST /submit JSON -> {"ok": true, "saved": "...timestamped.json", "latest": "...latest.json", "count": N}
```
