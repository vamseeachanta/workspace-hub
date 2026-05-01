# Prospect-Demo SOP — 48hr Runbook

> Source of truth for the prospect-data → customized-demo pipeline.
> Plan: `docs/plans/2026-04-19-issue-2346-prospect-data-pipeline.md` (v3.1-APPROVED).
> Scaffold status: `docs/gtm/intake/IMPLEMENTATION-STATUS.md`.

This SOP is the operational runbook an engineer follows when a prospect
sends vessel / structure / project-condition data and asks for a
customized demo report. The SLA is **≤ 48 hours from intake receipt to
delivery on both channels**.

**No outbound outreach is performed by this SOP.** It starts only after
an inbound or already-authorized intake exists, and it never instructs an
agent to send unsolicited email, LinkedIn messages, or contractor contact.

**public-safe rule:** artifacts committed to git use **logical paths only**
(for example `docs/gtm/intake/...` or `private-log/fallback-applied.json`).
Do not commit workstation paths, prospect file-share paths, screenshots of
private directories, or proprietary data-source locations.

> Terminology: the word "demo" throughout refers to one of the five GTM
> parametric studies (`demo_01`..`demo_05`) already shipped under
> `digitalmodel/examples/demos/gtm/`. The intake YAML routes the prospect
> data to exactly one of them via `prospect.target_demo`.

---

## 0. Pre-flight (must be true before accepting intake)

- [ ] NDA is in place and a signed copy is filed (prospect YAML MUST
      declare `prospect.nda_in_place: true` — the schema validator rejects
      the field being absent).
- [ ] The canonical-vessel library at
      `docs/gtm/intake/canonical-vessels/` contains at least one vessel in
      each shape the prospect may request
      (`heavy-lift-csv.yaml` / `seven-borealis.yaml`,
      `pipelay-barge.yaml`, `plsv.yaml`).
- [ ] The aceengineer-website deploy gate (`robots.txt` `Disallow:
      /private/` + vercel `X-Robots-Tag: noindex, nofollow`) is known
      live on production. If in doubt, run the post-deploy verification
      at the bottom of this SOP before publishing any gated URL.

---

## 1. 48-hour decision tree

```
Hour 0-4    RECEIVE prospect data (email / LinkedIn / form)
             │
             ▼
            File raw intake at
             docs/gtm/intake/received/YYYY-MM-DD-<company>.yaml
             (directory is .gitignored — NDA isolation)
             │
             ▼
Hour 4-24   VALIDATE with prospect_adapter.load_and_validate()
             │
       ┌─────┴─────┐
       │           │
     PASS        FAIL
       │           │
       │           ▼  consult §2 refuse-vs-fix matrix
       │           │
       │           ├── F1 refuse      → email refusal + stop
       │           ├── F2 closest-can → substitute canonical vessel
       │           ├── F3 class-dflt  → substitute allowlist field
       │           ├── F4 clarify     → one clarification email, stop clock
       │           └── F5 reduced     → narrow sweep, flag on cover
       │
       ▼
Hour 6–24   MATERIALIZE + RUN demo via prospect_adapter.materialize_demo_inputs()
             + prospect_adapter.run_demo(). --from-cache MANDATORY in CI.
             │
       ┌─────┴─────┐
       │           │
    OK (HTML)    NaN / solver blowup
       │           │
       │           ▼  §2 row "Numerical failure"
       │           │
       ▼           ▼
Hour 24-40  RENDER branded report via branded_report.wrap_with_client_branding()
             Spot-check: all charts render, brand header/footer present,
             NDA watermark when nda_in_place=true, class-typical
             disclaimer on cover page when a canonical vessel was used.
             │
             ▼
Hour 40-48  INTERNAL REVIEW + DELIVER on BOTH channels (serial,
             email-first per §3):
             1. Email HTML + optional PDF to prospect.contact
             2. Publish to /private/<hash>/<slug>.html on aceengineer-website
                (unless output.publish_private_url == false)
             3. Append a row to docs/gtm/deliveries-log.md with
                prospect_id, demo, state, gated_url_hash, purge_after_utc,
                fallback_applied (F1-F5 or null).
```

---

## 2. Refuse-vs-Fix Fallback Matrix (F1–F5)

Pre-authorized — no ad-hoc escalation needed — but every fallback MUST be
logged to both:

- `docs/gtm/deliveries-log.md` (human-readable row, `fallback_applied` column)
- `digitalmodel/examples/demos/gtm/private-log/fallback-applied.json`
  (machine-readable sidecar, **gitignored, never shipped to prospect**)

### Matrix

| Fallback | Code | Applies to | Prospect authorization | Report-cover disclosure |
|---|---|---|---|---|
| **F1 — refuse** | `refuse` | Default for any unclear or ambiguous failure | None | N/A — no report rendered |
| **F2 — closest canonical vessel** | `closest-canonical` | Missing `vessel` block (demos 3/4/5) OR vessel fails numeric-sanity gate | **Pre-authorized** (intake email said "use your closest vessel") | "Vessel spec supplied by ACE canonical library: `<class name>`. Class-typical values; not vessel-specific." + source citations |
| **F3 — canonical-class default** | `canonical-default-field` | One missing scalar inside an otherwise-complete block (e.g. `crane_main.swl_max_radius_m` missing but rest of vessel present). Allowlist only. | Implicit for allowlist fields; explicit otherwise | Line-item list of every substituted field with its canonical-class value |
| **F4 — one clarification email** | `clarify` | Single well-defined missing field or ambiguous enum value | None (this IS the refuse) | N/A — no report rendered until reply |
| **F5 — reduced scope with caveats** | `reduced-scope` | Parametric-sweep failure sidesteppable by narrowing sweep (e.g. depth > vessel rating → cap sweep at vessel rating) | **Pre-authorized** (intake email said "deliver reduced-scope if needed") OR explicit email confirmation within Hour 0-4 | "Scope reduced: `<what was cut>`. Full-envelope analysis requires `<what>`." red-banner caveat |

### Applicability by failure mode

| Failure mode                                                  | F1     | F2          | F3                | F4      | F5                 |
|---------------------------------------------------------------|--------|-------------|-------------------|---------|--------------------|
| Schema missing top-level block (e.g. `structure`)             | DEFAULT | —           | —                 | ALLOWED | —                  |
| Schema missing required field                                 | —      | —           | ALLOWED (allowlist only) | DEFAULT | —          |
| Schema `additionalProperties` (typo)                          | —      | —           | —                 | DEFAULT | —                  |
| Schema type mismatch (string-where-number)                    | —      | —           | —                 | DEFAULT | —                  |
| Cross-field: wrong vessel shape for demo                      | DEFAULT | —          | —                 | ALLOWED | —                  |
| Cross-field: depth > vessel rating                            | ALLOWED | —          | —                 | ALLOWED | DEFAULT (if pre-auth) |
| Cross-field: entire vessel block missing (demos 3/4/5)        | —      | DEFAULT (if pre-auth) | —     | ALLOWED (otherwise) | —        |
| Numerical failure (NaN / solver blowup)                       | DEFAULT | ALLOWED (if pre-auth AND root-cause is vessel) | — | ALLOWED | ALLOWED (if parametric edge) |
| Canonical-ref file not found                                  | DEFAULT | —           | —                 | —       | —                  |
| Demo 1 / 2 intake with stray `vessel:` block                  | —      | —           | —                 | DEFAULT | —                  |

### F3 allowlist

Implementation constant `FIELDS_ALLOWED_FOR_CLASS_DEFAULT` in
`prospect_adapter.py` enumerates the safe-to-substitute scalar fields.
Any field NOT in the allowlist requires explicit prospect authorization;
the adapter raises `ProspectIntakeError` on a non-allowlist substitution
attempt.

### Sidecar schema (`private-log/fallback-applied.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["prospect_id", "timestamp_utc", "fallback_code", "failure_mode"],
  "properties": {
    "prospect_id":       { "type": "string" },
    "timestamp_utc":     { "type": "string", "format": "date-time" },
    "fallback_code":     { "type": "string", "enum": ["F1", "F2", "F3", "F4", "F5"] },
    "failure_mode":      { "type": "string" },
    "field_substituted": { "type": ["string", "null"] },
    "canonical_source":  { "type": ["string", "null"] },
    "pre_authorization": { "type": "string", "enum": ["explicit", "implicit_allowlist", "none"] },
    "engineer":          { "type": "string" }
  }
}
```

The sidecar path appears in `.gitignore` and is hard-excluded by the
`deliver()` packager from both the email-attachment bundle and the
gated-URL publish set.

---

## 3. Dual-Delivery State Machine

Implementation lives in `prospect_adapter.deliver()`.

```
           ┌────────────────────────┐
           │   email_send(prospect) │
           │   retry 3× (30s, 2m,   │
           │   10m) on transient    │
           │   SMTP failure         │
           └──────────┬─────────────┘
                      │
          success?    ▼     failure (after retries)
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
  publish_private_url==true?    state=FAILED_EMAIL
         │                       URL NOT published
    ┌────┴────┐                  engineer alerted via SOP Hour 44-48 checkpoint
    │         │                  END
    │         │
    YES       NO
    │         └─> state=DELIVERED (email-only by prospect choice)
    │             END
    ▼
   publish_gated_url(prospect)
   retry 3× on transient publish failure
         │
         ▼
       success?
   ┌───────┴────────────┐
   │                    │
   YES                  NO (after retries)
   │                    │
   ▼                    ▼
 state=DELIVERED      state=DELIVERED_EMAIL_ONLY
 END                  (email is authoritative;
                       no compensating action)
                      END
```

### Key sequencing rules

- **Email first, URL second.** This is the required email-first sequence.
  URL publish is gated on email-success so the prospect never sees a URL
  without the accompanying email context; if email fails, no private URL
  is published (`no private URL is published` is the gate invariant).
- **Retry budget:** 3 attempts per channel with exponential backoff
  `[30s, 2min, 10min]`, tolerance ±10%.
- **No email recall.** `state=DELIVERED_EMAIL_ONLY` is terminal — we do
  NOT auto-send a follow-up "URL now available" email on late-success.
  SOP allows a manual engineer-sent note if the prospect requests it.
- **Unpublish is manual.** `unpublish_url(hash)` deletes the gated file
  and writes `state=UNPUBLISHED` with a reason. Triggered only by SOP
  action (NDA violation discovered, wrong prospect, etc.). Email is not
  withdrawn.

### Delivery-log row schema

Every row in `docs/gtm/deliveries-log.md` has the columns defined in
that file's table header. `state` is an enum:

- `DELIVERED` — email OK, URL OK (or URL-opt-out with email OK)
- `DELIVERED_EMAIL_ONLY` — email OK, URL publish failed after retries
- `FAILED_EMAIL` — email failed after retries (terminal; URL never
  attempted)
- `UNPUBLISHED` — URL was published then deleted via SOP action

### TDD coverage

`digitalmodel/examples/demos/gtm/tests/test_prospect_pipeline_e2e.py`
includes the following state-machine tests (all mocked, <2s each):

- `test_delivery_email_first_then_url`
- `test_delivery_email_fail_aborts_url`
- `test_delivery_url_fail_records_email_only_state`
- `test_delivery_retry_backoff_bounds`
- `test_delivery_unpublish_records_state`

---

## 4. Gated-URL mechanics

- **Path scheme:** `/private/<sha256(prospect_id + salt + date)>/<slug>.html`.
- **Default gating:** unique-hash (security-by-obscurity + NDA). Stronger
  alternatives (Vercel basic-auth, signed URLs) are intake-opt-in via
  `output.gating: basic-auth | signed`.
- **Robots exclusion:** `aceengineer-website/robots.txt` has
  `Disallow: /private/`. `vercel.json` sets
  `X-Robots-Tag: noindex, nofollow` on `/private/(.*)`.
- **Purge contract:** every publish MUST set `output.purge_after_utc`
  in intake and record that same timestamp in `docs/gtm/deliveries-log.md`.
  Purge-enforcement cron is a filed follow-up (not this plan's scope).

### Cross-repo deploy note

`aceengineer-website/` is a **separate nested git repo**. Shipping the
`robots.txt` + `vercel.json` edits requires:

1. Push workspace-hub commits (this SOP + adapter + schema + tests).
2. **Separately** push the `aceengineer-website` commits to that repo's
   remote.
3. Wait for Vercel auto-rebuild to complete.
4. Run the post-deploy verification block at the bottom of this SOP.

A `git revert` in workspace-hub does NOT unpublish the
`robots.txt` / `vercel.json` changes; rollback requires a separate
revert in `aceengineer-website`.

---

## 5. Canonical-vessel usage rules

The three canonical vessel YAMLs at
`docs/gtm/intake/canonical-vessels/` each carry a top-of-file disclaimer
and ≥2 pinned citations. When the adapter materializes a canonical
vessel (via `vessel.source: canonical_ref`), the branded report MUST:

1. Place the class-typical disclaimer prominently on the cover page.
2. Include the citations (URLs, DOIs, ISBNs) in the report appendix.
3. Use language such as "`<class>` class-typical — not representing any
   specific commercial asset."

If the canonical YAML's `sources[].accessed_utc` is older than 12
months at intake time, surface a WARN in the adapter log so the
engineer can refresh the citation before delivery (URL rot mitigation).

---

## 6. Post-deploy verification (cross-repo)

After any `aceengineer-website` push that touches `robots.txt` or
`vercel.json`, run:

```bash
curl -sS https://aceengineer.com/robots.txt | grep -F 'Disallow: /private/'
curl -sSI https://aceengineer.com/private/test/index.html | grep -F 'X-Robots-Tag: noindex, nofollow'
```

Both commands MUST exit 0 before the first gated URL is published.

---

## 7. Explicit non-promises

- This SOP does NOT commit ACE to any specific turnaround better than
  48 hours; `delivery_deadline_utc` in the intake is informational for
  prioritization, not a contractual SLA.
- This SOP does NOT cover paid engineering work post-demo; once the
  prospect engages, the delivery model switches to the project-contract
  path documented elsewhere.
- This SOP does NOT permit silent data changes. Every substitution or
  scope reduction is logged in both the human-facing deliveries-log and
  the machine-readable sidecar.
