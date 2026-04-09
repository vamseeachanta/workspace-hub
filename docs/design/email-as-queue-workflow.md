# Email-as-Queue Workflow Design

> **Issue:** [#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017)
> **Status:** Design specification
> **Date:** 2026-04-09
> **Supersedes:** Archive-everything approach in #1987, raw-email routing in gmail-archive-extract.py

---

## 1. Core Principle

**Email is a queue, not an archive.**

The previous system archived 36,100+ emails across 3 accounts into git repos by sender domain, storing full email bodies as markdown files. This created massive repo noise, inflated git history, and did not match how email should be managed.

The new model treats every email as a transient item in a processing queue. Data enters the queue, gets triaged, has its actionable information extracted into structured form, and then the raw email is deleted. Only the extracted data persists in repositories.

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
     | (delete)   |  | structured  |  | (hold for  |
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
            | RE-ACTIVATE     DELETE        |
            |  (back to       (email gone,  |
            |   INBOUND)       data stays)  |
            +----+---+----+--------+--------+
                     |
              all deletions
              logged locally
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
| Marketing/newsletters | DELETE immediately or after unsubscribe | -- |

VIP domains requiring immediate attention: `ril.com`, `dorisgroup.com`, `mcdermott.com`, `shell.com`, `kbr.com`, `bp.com`, `subsea7.com`, `technipfmc.com`

### 2.2 personal (achantav@gmail.com)

| Category | Handling | Extraction Target |
|---|---|---|
| Family (achanta* gmail addresses) | Keep while active, extract key dates/actions | achantas-data/data/family/ |
| Financial (banks, insurance, tax) | Extract amounts/dates/due-dates | achantas-data/data/finance/ |
| Tax documents (TurboTax, 1099s, K-1s) | Extract form type/amounts/year | achantas-data/data/tax/ |
| Alumni / career networking | Extract contact updates | achantas-data/data/networking/ |
| Social media notifications | DELETE immediately | -- |
| Marketing / promotions | DELETE after batch unsubscribe | -- |

### 2.3 skestates (skestatesinc@gmail.com)

| Category | Handling | Extraction Target |
|---|---|---|
| Tenant (Family Dollar, Dollar Tree) | Extract issue/resolution/dates | sabithaandkrishnaestates/data/tenant/ |
| Insurance (Marsh, Crown Insurance, Insureon) | Extract policy/claim/premium data | sabithaandkrishnaestates/data/insurance/ |
| HOA (FS Residential) | Extract dues/violations/dates | sabithaandkrishnaestates/data/hoa/ |
| Vendors (PHFM, CLH, GDS, Partner ESI) | Extract invoices/work orders | sabithaandkrishnaestates/data/vendor/ |
| Title company | Extract closing/filing data | sabithaandkrishnaestates/data/title/ |
| Tax / CPA | Extract filing status/deadlines | sabithaandkrishnaestates/data/tax/ |

VIP domains requiring immediate attention: `familydollar.com`, `dollartree.com`, `marsh.com`

---

## 3. Thread Lifecycle

### 3.1 States

| State | Gmail Label | Meaning | Auto-delete? |
|---|---|---|---|
| inbox | (none) | New, untriaged | No |
| extracted | `wh-email/extracted` | Data pulled, no pending action | No |
| awaiting-reply | `wh-email/awaiting-reply` | Operator replied, waiting for counterparty | Never |
| completed | `wh-email/completed` | Topic resolved, grace clock starts | After 7 days |
| noise | `wh-email/noise` | Spam/newsletter, no extraction needed | Immediately |

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
completed ------> [DELETED]          (grace period elapsed, no new replies)

noise ----------> [DELETED]          (immediate or batch delete)
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
- After grace period with no new reply: thread is deleted from Gmail
- Local state log retains the deletion record permanently (for audit trail)

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

`~/.hermes/email-state.yaml` is the authoritative state tracker. It records every state transition, extraction event, and deletion. This file survives Gmail label drift and provides the data needed for the learning loop.

```yaml
# ~/.hermes/email-state.yaml
threads:
  - thread_id: "18f3a2b..."
    account: ace
    subject: "Dollar General NNN | TX | 7.25% CAP"
    sender_domain: sandsig.com
    state: completed
    extracted_to: "assethold/data/cre-listings/"
    extracted_date: "2026-04-07"
    completed_date: "2026-04-08"
    eligible_for_deletion: "2026-04-15"
    last_activity: "2026-04-08"
    reply_count: 0
    reactivation_count: 0

  - thread_id: "18f3a2c..."
    account: skestates
    subject: "Family Dollar Store #30150 HVAC Issue"
    sender_domain: familydollar.com
    state: awaiting-reply
    extracted_to: "sabithaandkrishnaestates/data/tenant/"
    extracted_date: "2026-04-05"
    last_activity: "2026-04-07"
    reply_count: 3
    reactivation_count: 1

deletions:
  - thread_id: "18f3a1a..."
    account: personal
    deleted_date: "2026-04-08"
    reason: "noise — marketing newsletter"
    had_extraction: false

  - thread_id: "18f3a2b..."
    account: ace
    deleted_date: "2026-04-15"
    reason: "completed — grace period elapsed"
    had_extraction: true
    extracted_to: "assethold/data/cre-listings/"
```

### 5.2 State File Operations

| Operation | Trigger | State File Update |
|---|---|---|
| New thread scanned | Triage run | Add entry with state=inbox |
| Data extracted | Extraction pipeline | state -> extracted, set extracted_date and extracted_to |
| Operator replied | Send/draft detection | state -> awaiting-reply |
| Topic resolved | User marks complete | state -> completed, set completed_date and eligible_for_deletion |
| New reply arrives | Unread scan on labeled thread | state -> inbox, increment reactivation_count |
| Deleted | Deletion sweep | Move to deletions list, remove from threads list |

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
  # ---- NOISE (delete, no extraction) ----
  "collide.io":                     { action: DELETE }
  "promote.weebly.com":             { action: DELETE }

  # ---- REVIEW (hold for user decision) ----
  "substack.com":                   { action: REVIEW }

  # ---- EXTRACT (structured data extraction) ----
  "sandsig.com":
    action: EXTRACT
    template: cre-listing
    destination: assethold/data/cre-listings/
    account: ace

  "familydollar.com":
    action: EXTRACT
    template: tenant-communication
    destination: sabithaandkrishnaestates/data/tenant/
    account: skestates

  "marsh.com":
    action: EXTRACT
    template: insurance
    destination: sabithaandkrishnaestates/data/insurance/
    account: skestates

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
| Token management | `~/.gmail-{ace,personal,skestates}/credentials.json` | Auto-refresh via refresh_token grant |
| OAuth config | `~/.gmail-mcp/oauth-env.json` | Shared client_id / client_secret |
| Triage scheduling | Hermes cron | Daily at 7 AM CT (triage), 12 PM CT (digest) |
| Legal scanning | `scripts/legal/legal-sanity-scan.sh` | Runs before every git commit of extracted data |
| Contact enrichment | `scripts/email/contact-normalizer.py` outputs | CSV lookup during triage classification |
| State persistence | `~/.hermes/email-state.yaml` | Local YAML, not in git |

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
GET  /gmail/v1/users/me/messages?q=label:wh-email/completed+older_than:7d  -- find deletion candidates
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

        if rule.action == DELETE:
            if not dry_run: gmail_trash(message)
            log_deletion(state, message, reason="noise")
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

### 7.5 Deletion Sweep Pseudocode

```
function run_deletion_sweep(account, dry_run):
    token = refresh_oauth_token(account)
    state = load_state_file()

    for each thread in state.threads:
        if thread.account != account:
            continue

        if thread.state == "noise":
            if not dry_run: gmail_delete(thread.thread_id, token)
            move_to_deletions(state, thread, reason="noise")

        if thread.state == "completed":
            if days_since(thread.completed_date) >= 7:
                # Check for new replies before deleting
                has_new = check_for_new_messages(thread.thread_id, token)
                if has_new:
                    reactivate(state, thread)
                    continue
                if not dry_run: gmail_delete(thread.thread_id, token)
                move_to_deletions(state, thread, reason="grace period elapsed")

        if thread.state == "awaiting-reply":
            # NEVER auto-delete
            pass

    save_state_file(state)
```

---

## 8. Deletion Safety Rules

### 8.1 Safety Hierarchy

1. **Never auto-delete `awaiting-reply` threads.** These represent open conversations.
2. **Grace period is mandatory.** Completed threads wait 7 days before deletion.
3. **Check for new replies before deleting.** Even after grace period, verify no new messages arrived.
4. **Dry-run by default.** First production runs of any new domain/template should use `--dry-run`.
5. **Log every deletion.** The local state file records what was deleted, when, and why.
6. **Legal scan before commit.** Extracted data is scanned against the legal deny list before git commit.

### 8.2 Rollout Safety

| Phase | Delete behavior | Scope |
|---|---|---|
| Week 1 | Dry-run only, no actual deletions | All accounts |
| Week 2 | Delete noise only (known spam domains) | All accounts |
| Week 3 | Delete completed with grace period | 1 account (ace first) |
| Week 4+ | Full pipeline, all accounts | All accounts |

### 8.3 Recovery

If an email is deleted that should not have been:
- Gmail Trash retains messages for 30 days (API `DELETE` is permanent; use `trash` instead for safety)
- Local state file records the thread_id, which can be used to search Trash
- Extracted data in repos provides the structured content even after email deletion

**Decision: use `users/me/messages/{id}/trash` (recoverable) rather than `users/me/messages/{id}` DELETE (permanent) for all automated deletions during the first 90 days of operation.**

---

## 9. Learning Loop

### 9.1 How the System Gets Smarter

| Signal | What It Means | Action |
|---|---|---|
| Unknown domain in triage | No routing rule exists | Surface in digest; user adds rule or template |
| Extraction failure | Template could not parse required fields | Log failure with sample data; user refines template |
| User marks thread as noise | False negative in noise detection | Add domain to DELETE list in routing |
| User re-activates a completed thread | Grace period or completion was premature | Adjust completion heuristics |
| High reactivation_count on a domain | Threads from this domain are often re-opened | Increase grace period or change handling |
| User corrects extracted data | Template parsed incorrectly | Fix template regex/field definitions |

### 9.2 Exception Reporting in Digest

The daily digest (gmail-digest.py) should include a "Learning Backlog" section:

```
=== LEARNING BACKLOG ===
  Unknown domains (no routing rule):
    - newclient@unknowndomain.com (ace, 3 messages)
    - vendor@newcompany.io (skestates, 1 message)
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
| 4 | Run extraction pipeline in dry-run on all 3 accounts | None | Validates templates against real data |
| 5 | Enable extraction (write YAML to repos) with `wh-email/extracted` labels | Low | Data is additive, no deletions yet |
| 6 | Enable noise deletion (known spam domains only) | Low | Already identified in current routing |
| 7 | Enable completed+grace-period deletion on ace account | Medium | 7-day grace + trash (not permanent delete) |
| 8 | Extend deletion to personal and skestates | Medium | Same safeguards |
| 9 | Deprecate `gmail-archive-extract.py` | Low | New pipeline has parity |
| 10 | Retire deprecated skills (gmail-extract-and-clean, gmail-extract-archive, gmail-email-to-repo-extraction) | Low | Skills marked deprecated in docs/email/WORKFLOW.md |

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
| gmail-extract-and-clean | DEPRECATE | Replaced by gmail-extract-and-act |
| gmail-extract-archive | DEPRECATE | Replaced by gmail-extract-and-act |
| gmail-email-to-repo-extraction | DEPRECATE | Replaced by gmail-extract-and-act |
| gmail-data-extraction | KEEP (reference) | Code patterns only, not workflow |
| gmail-touchbase | MERGE into gmail-outreach | -- |
| gmail-unsubscribe | MERGE into gmail-outreach | -- |

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
- [x] Define thread state tracking approach (hybrid: Gmail labels + local YAML)
- [x] Define extraction format (structured YAML)
- [x] Define deletion policy and safety rules (grace period, trash not delete, dry-run first)
- [x] Define per-account routing and extraction targets
- [x] Define learning loop mechanics
- [x] Document migration plan

### Phase 2: Build Extract-and-Delete Pipeline (#2024)
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
- [ ] Implement `~/.hermes/email-state.yaml` read/write
- [ ] Implement Gmail label lifecycle (create, apply, remove)
- [ ] Implement grace period enforcement
- [ ] Implement re-activation detection
- [ ] Write tests: `tests/email/test_email_state_machine.py`

### Phase 5: Digest Integration
- [ ] Update `gmail-digest.py` to show queue state information
- [ ] Add learning backlog section to digest output
- [ ] Add exception reporting for unknown domains and extraction failures

### Phase 6: Skill Consolidation (#2019)
- [ ] Deprecate `gmail-extract-and-clean`, `gmail-extract-archive`, `gmail-email-to-repo-extraction`
- [ ] Merge `gmail-touchbase` + `gmail-unsubscribe` into `gmail-outreach`
- [ ] Update all remaining skills to reference queue model

### Phase 7: Learning Loop
- [ ] Track extraction patterns that work well
- [ ] Flag emails the system cannot classify
- [ ] User corrections feed back into routing rules and templates
- [ ] Periodic review of deleted-vs-kept decisions

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

2. **Immediate noise deletion confidence**: Should noise deletion be enabled from day one, or only after a dry-run confidence period? Decision: dry-run first week, noise deletion starting week 2 (Section 8.2).

3. **State file location**: `~/.hermes/email-state.yaml` is not in git. Should state be git-tracked? Decision: No. State is local and ephemeral. The extracted data in repos is the durable artifact.

4. **Attachment handling**: Large attachments (PDFs, spreadsheets) need their own extraction path. Should the extraction pipeline handle them inline or delegate to `gmail-attachment-to-document` skill? Decision: delegate to existing skill for complex parsing; inline only for simple metadata extraction.

5. **Multi-machine sync**: If triage runs on ace-linux-1 but email is also checked manually, how to handle state drift? Decision: Gmail labels are the source of truth for state visibility; local YAML catches up on next scan.
