# Email-as-Queue Workflow Design

> **Issue:** [#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017)
> **Status:** Design specification
> **Date:** 2026-04-09
> **Supersedes:** Archive-everything approach in #1987, raw-email routing in gmail-archive-extract.py

---

## 2026 Scope Update

Issue [#2026](https://github.com/vamseeachanta/workspace-hub/issues/2026) implements the local queue-state layer for only two active accounts: `ace` (`vamsee.achanta@aceengineer.com`) and `personal` (`achantav@gmail.com`). No other account is active in this implementation pass.

The #2026 state layer can report whether known in-scope mail has pending work and whether a supplied inbox snapshot contains unknown in-scope threads. It does not archive or delete Gmail messages; destructive Gmail cleanup remains follow-on issue [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423). Durable information extracted from mail belongs in the appropriate repo ecosystem target, not in repo-tracked raw email. Any older deletion examples below are historical context only when they conflict with this boundary.

---

## 1. Core Principle

**Email is a queue, not an archive.**

The previous system archived 36,100+ emails across 3 accounts into git repos by sender domain, storing full email bodies as markdown files. This created massive repo noise, inflated git history, and did not match how email should be managed.

The new model treats every email as a transient item in a processing queue. Data enters the queue, gets triaged, has its actionable information extracted into structured form, and the durable record moves into the appropriate repository. Gmail archive/delete automation is outside #2026.

```
                    +------------------+
                    |    INBOUND       |
                    |  (Gmail inbox)   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |     TRIAGE       |
                    | classify, route  |
                    +---+----+----+----+
                        |    |    |
              +---------+    |    +----------+
              |              |               |
     +--------v---+  +------v------+  +-----v------+
     |   NOISE    |  |   EXTRACT   |  |   REVIEW   |
     | (label)    |  | structured  |  | (hold for  |
     +------+-----+  |   data      |  |  decision) |
            |        +------+------+  +-----+------+
            |               |               |
            |        +------v------+        |
            |        |     ACT     |        |
            |        | commit data |        |
            |        | to repos    |        |
            |        +------+------+        |
            |               |               |
            |        +------v------+        |
            |        | TRACK STATE |        |
            |        | label thread|        |
            |        +---+----+----+        |
            |            |    |             |
            |     +------+    +------+      |
            |     |               |         |
            | +---v--------+ +---v-------+  |
            | | AWAITING   | | COMPLETED |  |
            | | REPLY      | | (grace    |  |
            | | (keep)     | |  period)  |  |
            | +---+--------+ +---+-------+  |
            |     |               |         |
            |     | new reply     | 7 days  |
            |     | arrives       | elapsed |
            |     v               v         |
            | RE-ACTIVATE     PURGE LOCAL   |
            |  (back to       (email gone,  |
            |   INBOUND)       data stays)  |
            +----+---+----+--------+--------+
                     |
              Gmail delete/archive
              remains #2423
```

---

## 2. Per-Account Rules

### 2.1 ace (vamsee.achanta@aceengineer.com)

| Category | Handling | Extraction Target |
|---|---|---|
| Active clients (RIL, DORIS, McDermott, Shell, etc.) | Extract project data, track threads | aceengineer-admin/data/client-{name}/ |
| Recruiters (DISYS, Steps to Progress, etc.) | Extract role/rate/contact | aceengineer-admin/data/recruiting/ |
| CRE listings (Sands IG, Marcus Millichap, LoopNet) | Extract property/cap-rate/tenant data | assethold/data/cre-listings/ |
| Software vendors (ANSYS, DNV, ENGYS) | Extract license/support data only if actionable | aceengineer-admin/data/vendor/ |
| Industry colleagues | Keep for networking touchbase, extract contact if new | aceengineer-admin/data/colleague/ |
| Marketing/newsletters | Label/no pending extraction; Gmail delete belongs to #2423 | -- |

VIP domains requiring immediate attention: `ril.com`, `dorisgroup.com`, `mcdermott.com`, `shell.com`, `kbr.com`, `bp.com`, `subsea7.com`, `technipfmc.com`

### 2.2 personal (achantav@gmail.com)

| Category | Handling | Extraction Target |
|---|---|---|
| Family (achanta* gmail addresses) | Keep while active, extract key dates/actions | achantas-data/data/family/ |
| Financial (banks, insurance, tax) | Extract amounts/dates/due-dates | achantas-data/data/finance/ |
| Tax documents (TurboTax, 1099s, K-1s) | Extract form type/amounts/year | achantas-data/data/tax/ |
| Alumni / career networking | Extract contact updates | achantas-data/data/networking/ |
| Social media notifications | Label/no pending extraction; Gmail delete belongs to #2423 | -- |
| Marketing / promotions | Label/no pending extraction; Gmail delete belongs to #2423 | -- |

### 2.3 Disabled Accounts

Additional accounts require a future issue and explicit approval before they are added to queue-state processing, label creation, or cleanup reporting.

---

## 3. Thread Lifecycle

### 3.1 States

| State | Gmail Label | Meaning | #2026 cleanup behavior |
|---|---|---|---|
| inbox | (none) | New, untriaged | Pending work |
| extracted | `wh-email/extracted` | Data pulled, no pending action | Local state only |
| awaiting-reply | `wh-email/awaiting-reply` | Operator replied, waiting for counterparty | Not pending by itself |
| completed | `wh-email/completed` | Topic resolved, grace clock starts | Local `purged` marker after 7 days and clean precheck |
| noise | `wh-email/noise` | Spam/newsletter, no extraction needed | Local label/state only; Gmail deletion belongs to #2423 |

### 3.2 Transition Rules

```
inbox -----------> extracted          (data successfully extracted and committed)
inbox -----------> noise              (classified as spam/newsletter/promotion)
inbox -----------> review             (system cannot classify; held for user)

extracted -------> awaiting-reply     (operator sends a response in the thread)
extracted -------> completed          (no reply needed; topic is resolved)

awaiting-reply --> inbox              (new inbound reply arrives -- RE-ACTIVATE)
awaiting-reply --> completed          (topic resolved without further reply)

completed ------> inbox              (new inbound reply during grace period -- RE-ACTIVATE)
completed ------> purged             (local grace marker only in #2026)

noise ----------> wh-email/noise     (label only in #2026)
```

### 3.3 Re-activation

When a thread marked `completed` or `awaiting-reply` receives a new inbound message:

1. Gmail automatically surfaces the thread in inbox (unread notification)
2. The system detects the `wh-email/*` label on the thread plus the new unread message
3. The existing label is removed and the thread returns to `inbox` state
4. The local state log is updated with `reactivated_date` and `reactivation_count`
5. Triage runs again on the thread

### 3.4 Grace Period

- Duration: 7 calendar days from `completed_date`
- During grace period: thread stays in Gmail with `wh-email/completed` label
- If new reply arrives: grace timer resets, thread returns to inbox
- After grace period with no new reply: #2026 can mark local state as `purged` only after a clean reactivation precheck.
- Gmail archive/delete remains follow-on #2423.

---

## 4. Data Extraction Targets

### 4.1 What Gets Extracted (structured data only)

| Email Type | Extracted Fields | Destination Repo/Path | Format |
|---|---|---|---|
| CRE listing | property_name, tenant, address, state, price, cap_rate, building_sf, lease_years, vpd, broker | assethold/data/cre-listings/ | YAML |
| Client RFP/SOW | sender, company, project, scope_summary, timeline, budget, contacts | aceengineer-admin/data/prospects/ | YAML |
| Invoice/payment | invoice_number, vendor, amount, due_date, status, payment_method | per-account finance path | YAML |
| Tenant communication | store_number, issue_type, date_reported, resolution, vendor, cost_estimate | sabithaandkrishnaestates/data/tenant/ | YAML |
| Tax document | form_type, entity, tax_year, amounts, due_date, filing_status | achantas-data/data/tax/ | YAML |
| Recruiter outreach | company, role, rate, location, contact_name, contact_email | aceengineer-admin/data/recruiting/ | YAML |
| Insurance | policy_number, carrier, premium, coverage_type, renewal_date, claim_number | sabithaandkrishnaestates/data/insurance/ | YAML |
| New contact | name, email, company, category, source_thread | contact-manager pipeline | CSV row |

### 4.2 Extraction Format

All extracted data uses YAML as the canonical format:

```yaml
# Example: CRE listing extraction
extraction:
  type: cre-listing
  source:
    account: ace
    thread_id: "18f3a2b..."
    sender: listings@sandsig.com
    date: "2026-04-08"
  data:
    property_name: "Dollar General NNN"
    tenant: "Dollar General"
    address: "1234 Main St"
    state: "TX"
    price: 1250000
    cap_rate: 7.25
    building_sf: 9100
    lease_years: 15
    vpd: null
    broker: "Sands Investment Group"
  extracted_date: "2026-04-09T14:30:00"
```

Why YAML:
- Machine-readable for downstream analysis and dashboards
- Human-scannable during review
- Git-diffable for change tracking
- Consistent with existing workspace-hub data conventions

### 4.3 What Gets Deleted Without Extraction

No extraction or repo write needed for:

- Marketing emails and newsletters (after unsubscribe where appropriate)
- Social media notifications (LinkedIn, GitHub, Vercel, etc.)
- Promotional/coupon emails
- Expired event invitations
- Duplicate cross-account forwards (ace <-> personal)
- Known spam domains (per `email-routing.yaml` DELETE rules)
- Automated system notifications with no actionable content

---

## 5. State Tracking System

### 5.1 Dual-Layer Tracking

**Layer 1: Gmail Labels (operational visibility)**

Gmail labels in the `wh-email/` namespace provide real-time visibility inside the Gmail UI and allow Gmail search queries for state-based filtering (e.g., `label:wh-email/completed older_than:7d`).

Labels are created lazily via the Gmail API when first needed. Label operations use `users/me/threads/{id}/modify` to apply labels at the thread level.

**Layer 2: Local State File (authoritative audit trail)**

`~/.hermes/email-state/queue-state.jsonl` is the authoritative state tracker by default. It records every state transition and extraction event. This private runtime directory survives Gmail label drift and provides the data needed for the learning loop.

```yaml
# ~/.hermes/email-state/queue-state.jsonl
{"account_id":"ace","thread_id":"18f3a2b","from_state":"inbound","to_state":"extracted","ts_utc":"2026-06-14T00:00:00Z","cycle_id":"initial","dedup_event_id":"msg:18f3a2b-1"}
```

### 5.2 State File Operations

| Operation | Trigger | State File Update |
|---|---|---|
| New thread scanned | Triage run | Add entry with state=inbox |
| Data extracted | Extraction pipeline | state -> extracted, set extracted_date and extracted_to |
| Operator replied | Send/draft detection | state -> awaiting-reply |
| Topic resolved | User marks complete | state -> completed, set completed_at |
| New reply arrives | Unread scan on labeled thread | state -> inbox, increment reactivation_count |
| Grace elapsed | Clean reactivation precheck | state -> purged locally; Gmail untouched in #2026 |

---

## 6. Routing Configuration Evolution

### 6.1 Current State (archive-first)

`scripts/email/email-routing.yaml` currently maps sender domains to raw archive paths:

```yaml
"familydollar.com": "sabithaandkrishnaestates/docs/email/tenant"
"sandsig.com":      "assethold/data/sandsig-cre-listings/email"
```

### 6.2 Target State (queue-first)

The routing file evolves to specify extraction templates and structured data destinations:

```yaml
rules:
  # ---- NOISE (label, no extraction) ----
  "collide.io":                     { action: NOISE }
  "promote.weebly.com":             { action: NOISE }

  # ---- REVIEW (hold for user decision) ----
  "substack.com":                   { action: REVIEW }

  # ---- EXTRACT (structured data extraction) ----
  "sandsig.com":
    action: EXTRACT
    template: cre-listing
    destination: assethold/data/cre-listings/
    account: ace

  # ---- DEFAULT ----
  "default":
    action: REVIEW
    destination: achantas-data/data/unclassified/
```

### 6.3 Migration Path for Routing

1. Keep current `email-routing.yaml` working during transition (backward compatibility)
2. Add a `routing-v2.yaml` with the new schema alongside the old file
3. New extraction pipeline reads `routing-v2.yaml`; old script continues with current file
4. After parity is confirmed, rename v2 to primary and deprecate old file

---

## 7. Technical Implementation

### 7.1 Tools and APIs

| Component | Tool | Notes |
|---|---|---|
| Email reading | Gmail REST API (urllib, no pip deps) | Direct OAuth2 with refresh tokens |
| Email CLI fallback | himalaya v1.2.0 | For IMAP operations where API is overkill |
| Token management | Existing per-account Gmail helper credentials for `ace` and `personal` | Auto-refresh via refresh_token grant |
| OAuth config | `~/.gmail-mcp/oauth-env.json` | Shared client_id / client_secret |
| Triage scheduling | Hermes cron | Daily at 7 AM CT (triage), 12 PM CT (digest) |
| Legal scanning | `scripts/legal/legal-sanity-scan.sh` | Runs before every git commit of extracted data |
| Contact enrichment | `scripts/email/contact-normalizer.py` outputs | CSV lookup during triage classification |
| State persistence | `~/.hermes/email-state/queue-state.jsonl` | Local JSONL, not in git |

### 7.2 Scripts (new and modified)

| Script | Purpose | Status |
|---|---|---|
| `scripts/email/gmail-extract-and-act.py` | Queue-first extraction pipeline | NEW (replaces gmail-archive-extract.py) |
| `scripts/email/templates/*.yaml` | Per-domain/type extraction field definitions | NEW |
| `scripts/email/gmail-digest.py` | Daily digest, updated to be state-aware | MODIFY |
| `scripts/email/email-routing.yaml` | Current routing file | KEEP (backward compat) |
| `scripts/email/routing-v2.yaml` | New queue-aware routing schema | NEW |
| `scripts/email/gmail-archive-extract.py` | Archive-first extraction | DEPRECATE after parity |

### 7.3 Gmail Label Management

Labels are managed via the Gmail API:

```
POST /gmail/v1/users/me/labels       -- create wh-email/* labels (lazy, first use)
POST /gmail/v1/users/me/threads/{id}/modify  -- add/remove labels on threads
GET  /gmail/v1/users/me/messages?q=label:wh-email/completed+older_than:7d  -- optional read-only precheck input
```

The `wh-email/` prefix namespaces all automation labels to avoid collisions with user labels.

### 7.4 Extraction Pipeline Pseudocode

```
function run_extraction(account, query, dry_run):
    token = refresh_oauth_token(account)
    routing = load_routing_v2()
    state = load_state_file()

    messages = gmail_search(token, query)

    for each message in messages:
        domain = extract_sender_domain(message)
        rule = routing.lookup(domain)

        if rule.action == NOISE:
            if not dry_run: label_thread(message.thread_id, "noise", token)
            update_state(state, message, new_state="noise")
            continue

        if rule.action == REVIEW:
            log_review_needed(state, message)
            continue

        if rule.action == EXTRACT:
            template = load_template(rule.template)
            fields = template.parse(message.subject, message.body, message.attachments)

            if not fields.validates():
                log_extraction_failure(state, message, reason="insufficient fields")
                continue

            yaml_output = format_yaml(fields)
            legal_ok = legal_scan(yaml_output)

            if not legal_ok:
                log_legal_block(state, message)
                continue

            if not dry_run:
                write_yaml(rule.destination, yaml_output)
                git_commit(rule.destination_repo, f"extract: {domain} data")
                label_thread(message.thread_id, "extracted", token)

            update_state(state, message, new_state="extracted")

    save_state_file(state)
    return stats
```

### 7.5 Local Grace Sweep Pseudocode

```
function run_local_grace_sweep(account, dry_run, reactivation_precheck):
    state = load_state_file()
    require_clean(reactivation_precheck)

    for each thread in state.threads:
        if thread.account != account:
            continue

        if thread.state == "completed":
            if days_since(thread.completed_date) >= 7:
                if not dry_run: mark_local_state(thread, "purged")

        if thread.state == "awaiting-reply":
            # Not pending work by itself; new replies are detected by snapshot comparison.
            pass

    save_state_file(state)
```

---

## 8. Gmail Mutation Boundary

### 8.1 #2026 Safety Hierarchy

1. **No Gmail archive/delete in #2026.** This issue writes local state and optional labels only.
2. **Grace period is mandatory.** Completed threads wait 7 days before a local `purged` marker.
3. **Clean reactivation precheck required before local purge apply.** Dry-run can list candidates, but apply must prove no unknown or newer in-scope Gmail thread.
4. **Dry-run by default.** Scheduled automation runs with `--dry-run`.
5. **Legal scan before commit.** Extracted data is scanned against the legal deny list before git commit.

### 8.2 Follow-On Gmail Cleanup

| Phase | Behavior | Scope |
|---|---|---|
| #2026 | Local state + labels + dry-run local grace sweep | `ace`, `personal` |
| #2423 | Gmail archive/delete automation design and implementation | Requires separate approval |

### 8.3 Recovery

If local state is marked incorrectly, append a corrective state transition and learning-log entry. If Gmail content is ever moved by a future #2423 workflow, that workflow must carry its own recovery contract.

---

## 9. Learning Loop

### 9.1 How the System Gets Smarter

| Signal | What It Means | Action |
|---|---|---|
| Unknown domain in triage | No routing rule exists | Surface in digest; user adds rule or template |
| Extraction failure | Template could not parse required fields | Log failure with sample data; user refines template |
| User marks thread as noise | False negative in noise detection | Add domain to noise routing and label taxonomy |
| User re-activates a completed thread | Grace period or completion was premature | Adjust completion heuristics |
| High reactivation_count on a domain | Threads from this domain are often re-opened | Increase grace period or change handling |
| User corrects extracted data | Template parsed incorrectly | Fix template regex/field definitions |

### 9.2 Exception Reporting in Digest

The daily digest (gmail-digest.py) should include a "Learning Backlog" section:

```
=== LEARNING BACKLOG ===
  Unknown domains (no routing rule):
    - newclient@unknowndomain.com (ace, 3 messages)
    - vendor@newcompany.io (disabled account, 1 message)
  Extraction failures:
    - sandsig.com: 2 messages failed CRE template (missing cap_rate)
  Reactivated threads (consider longer grace):
    - Thread "Family Dollar HVAC" reactivated 3 times
```

### 9.3 Template Improvement Cycle

1. New domain appears in triage -> routed to REVIEW by default
2. User reviews messages, decides which template fits (or creates new one)
3. Template added to `scripts/email/templates/{name}.yaml`
4. Routing rule added to `routing-v2.yaml` mapping domain -> template
5. Next triage run auto-extracts using the new template
6. Extraction results reviewed; template refined if fields were mis-parsed

---

## 10. Migration Plan

### 10.1 From Archive-Everything to Queue Model

| Step | Action | Risk | Mitigation |
|---|---|---|---|
| 1 | Create `routing-v2.yaml` alongside existing routing file | None | Old file still works |
| 2 | Build `gmail-extract-and-act.py` with dry-run mode | None | No side effects in dry-run |
| 3 | Create first 5 extraction templates (CRE, client, tenant, tax, invoice) | Low | Templates are additive |
| 4 | Run extraction pipeline in dry-run on the two approved accounts | None | Validates templates against real data |
| 5 | Enable extraction (write YAML to repos) with `wh-email/extracted` labels | Low | Data is additive, no deletions yet |
| 6 | Enable queue-state reporting and local grace-sweep dry-run | Low | No Gmail archive/delete |
| 7 | Plan Gmail archive/delete separately in #2423 | Medium | Separate approval and recovery contract |
| 9 | Deprecate `gmail-archive-extract.py` | Low | New pipeline has parity |
| 10 | Retire deprecated active skills (gmail-extract-and-clean, gmail-extract-archive, gmail-email-to-repo-extraction, gmail-touchbase, gmail-unsubscribe) | Low | Active folders removed; archived twins retained under `.claude/skills/email/_archived/` |

### 10.2 Existing Data

Raw email archives already committed to repos are not deleted retroactively. They remain in git history. Going forward, no new raw email bodies are written to repos. Only structured YAML extractions are committed.

### 10.3 Skill Consolidation (per #2019)

| Current Skill | Disposition | Replacement |
|---|---|---|
| gmail-extract-and-act | KEEP | Primary extraction skill |
| gmail-triage | KEEP | Updated to reference queue model |
| gmail-multi-account | KEEP | Foundation infrastructure |
| gmail-outreach | KEEP | Merges touchbase + unsubscribe |
| gmail-attachment-to-document | KEEP | Attachment parsing utility |
| contact-manager | KEEP | Contact normalization |
| himalaya | KEEP | CLI reference |
| gmail-headless-oauth | KEEP | Infra utility |
| gmail-extract-and-clean | RETIRED from active skills | Replaced by gmail-extract-and-act; archived twin retained |
| gmail-extract-archive | RETIRED from active skills | Replaced by gmail-extract-and-act; archived twin retained |
| gmail-email-to-repo-extraction | RETIRED from active skills | Replaced by gmail-extract-and-act; archived twin retained |
| gmail-data-extraction | KEEP (reference) | Code patterns only, not workflow |
| gmail-touchbase | RETIRED from active skills | Replaced by gmail-outreach; archived twin retained |
| gmail-unsubscribe | RETIRED from active skills | Replaced by gmail-outreach; archived twin retained |

---

## 11. Related Issues

| Issue | Relationship | Impact |
|---|---|---|
| #2017 | This issue (design specification) | Defines the workflow |
| #1963 | Parent cluster (multi-account management) | Owns the operating envelope |
| #2024 | Extraction pipeline rewrite | First implementation issue |
| #2025 | Per-domain extraction templates | Template registry |
| #2026 | State tracking system | Gmail labels + local state |
| #1987 | Legacy cleanup pipeline | SUPERSEDED -- do not follow archive-first approach |
| #2019 | Skill consolidation | Retire deprecated skills |
| #1986 | Communication style profiles | Still needed for drafting replies |
| #1991 | Sands IG flooding | Extraction target: structured CRE data |
| #1968 | Personal triage | Must follow queue model |
| #1969 | SKEstates triage | Must follow queue model |
| #1971 | ACE triage | Must follow queue model |

---

## 12. Implementation Phases

### Phase 1: Workflow Design (this document -- #2017)
- [x] Define thread state tracking approach (hybrid: Gmail labels + local JSONL)
- [x] Define extraction format (structured YAML)
- [x] Route Gmail deletion/archive policy to #2423; define local grace-state safety rules
- [x] Define per-account routing and extraction targets
- [x] Define learning loop mechanics
- [x] Document migration plan

### Phase 2: Build Extract-and-Act Pipeline (#2024)
- [ ] Create `scripts/email/gmail-extract-and-act.py`
- [ ] Create `scripts/email/routing-v2.yaml`
- [ ] Implement template-driven extraction engine
- [ ] Implement thread state transitions and label management
- [ ] Add dry-run support for all destructive operations
- [ ] Write tests: `tests/email/test_gmail_extract_and_act.py`

### Phase 3: Template Registry (#2025)
- [ ] Create `scripts/email/templates/cre-listing.yaml`
- [ ] Create `scripts/email/templates/client-email.yaml`
- [ ] Create `scripts/email/templates/tenant-communication.yaml`
- [ ] Create `scripts/email/templates/tax-financial.yaml`
- [ ] Create `scripts/email/templates/invoice-payment.yaml`
- [ ] Write tests: `tests/email/test_email_templates.py`

### Phase 4: State Tracking (#2026)
- [ ] Implement `~/.hermes/email-state/queue-state.jsonl` read/write
- [ ] Implement Gmail label taxonomy and optional label creation
- [ ] Implement local grace period state enforcement
- [ ] Implement re-activation detection
- [ ] Write tests: `tests/email/test_email_state_machine.py`

### Phase 5: Digest Integration
- [ ] Update `gmail-digest.py` to show queue state information
- [ ] Add learning backlog section to digest output
- [ ] Add exception reporting for unknown domains and extraction failures

### Phase 6: Skill Consolidation (#2019)
- [x] Retire active `gmail-extract-and-clean`, `gmail-extract-archive`, `gmail-email-to-repo-extraction` folders; preserve archived twins
- [x] Retire active `gmail-touchbase` + `gmail-unsubscribe` folders after replacement by `gmail-outreach`
- [x] Update active email workflow docs and wiki frontmatter to reference queue-model skills

### Phase 7: Learning Loop
- [ ] Track extraction patterns that work well
- [ ] Flag emails the system cannot classify
- [ ] User corrections feed back into routing rules and templates
- [ ] Periodic review of noise-vs-kept decisions

---

## 13. Agent Assignment

| Agent | Responsibility |
|---|---|
| Claude Code | Workflow design (this doc), skill consolidation, pipeline code |
| Hermes | Cron execution, daily triage runs, digest delivery |
| Codex | Extraction template patterns, test coverage, regex refinement |
| Gemini | Research email workflow best practices, template design research |

---

## 14. Open Questions

1. **Routing schema migration**: Should `routing-v2.yaml` use a completely new schema or extend the current flat format? Decision: new schema (Section 6.2) for clarity; old file kept for backward compatibility.

2. **Noise deletion confidence**: Should Gmail deletion be enabled from day one, or only after a dry-run confidence period? Decision: no Gmail deletion in #2026; archive/delete automation requires #2423 approval.

3. **State file location**: `~/.hermes/email-state/queue-state.jsonl` is not in git. Should state be git-tracked? Decision: No. State is local and ephemeral. The extracted data in repos is the durable artifact.

4. **Attachment handling**: Large attachments (PDFs, spreadsheets) need their own extraction path. Should the extraction pipeline handle them inline or delegate to `gmail-attachment-to-document` skill? Decision: delegate to existing skill for complex parsing; inline only for simple metadata extraction.

5. **Multi-machine sync**: If triage runs on ace-linux-1 but email is also checked manually, how to handle state drift? Decision: Gmail labels are the source of truth for state visibility; local YAML catches up on next scan.
