---
name: contact-manager
description: Normalize, classify, and manage contact databases across 3 Gmail accounts. Clean CSV exports, deduplicate, tag categories, flag touchbase/unsubscribe candidates.
version: 1.0.0
author: vamsee
tags: [email, contacts, CRM, classification, data-cleanup]
related_skills: [gmail-multi-account, gmail-triage, gmail-outreach]
metadata:
  hermes:
    tags: [email, contacts, CRM, classification]
    related_skills: [gmail-multi-account]
---

# Contact Manager

Normalize and classify contact databases for multi-account Gmail management.

## Contact Sources

| Account | Source Path | Format | Entries |
|---|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_contacts.csv | Outlook CSV export | ~1,306 |
| personal | aceengineer-admin/admin/contacts/achantav_contacts.csv | Outlook CSV export | ~1,157 |
| skestates | sabithaandkrishnaestates/admin/contacts/ | Manual (from key_contacts.md) | ~20 |

## Normalization Steps

### Step 1: Parse and clean CSV

Known issues in the raw CSVs:
- Email addresses wrapped in angle brackets: `<email@domain.com>`
- Empty name fields with only email
- Duplicate entries (same person, multiple rows)
- Craigslist/spam entries mixed in
- Malformed CSV escaping (quotes inside fields)
- BOM encoding (use utf-8-sig)
- Outlook export has 64 columns with verbose names
- First Name field often contains the email in angle brackets

### Step 2: Create normalized schema

Output format (per account): `contacts_normalized.csv`

```csv
email,first_name,last_name,company,category,touchbase_cadence,notes
```

For SKEstates (expanded schema with department/phone):
```csv
email,first_name,last_name,title,company,department,category,touchbase_cadence,phone,notes
```

### Step 3: Category classification

Categories:
- `client` — current/past clients (EPCI operators, engineering firms)
- `colleague` — current/former colleagues, same-company contacts
- `vendor` — service providers, suppliers
- `recruiter` — staffing, job-related contacts
- `industry` — industry organizations, standards bodies
- `alumni` — university contacts (Rice, TAMU, UT McCombs)
- `personal` — friends, family (gmail/yahoo with known names)
- `financial` — banks, insurance, investment
- `government` — tax, legal, regulatory
- `newsletter` — subscriptions, marketing lists
- `spam` — junk, craigslist, unknown bulk
- `tenant` — tenant contacts (for real estate accounts)
- `vendor-functional` — shared functional inboxes (no touchbase)
- `tenant-functional` — shared tenant inboxes

#### Engineered domain mappings (from iteration on 2,400+ contacts)

**Ace client domains:**
```
ril.com, dorisgroup.com, mcdermott.com, shell.com, kbr.com,
technip.com, technipfmc.com, subsea7.com, nov.com, aker.com,
bp.com, awilcodrilling.com, eagle.org, vulcanoffshore.com,
boptechnologies.com, risersinc.com, sandsig.com,
engineeredcustomsolutions.com, mecorparada.com.ve
```

**Ace colleague domains:**
```
trendsetterengineering.com, spire-engineers.com,
2hoffshoreinc.com, 2hoffshore.com, prospricing.com
```

**Ace vendor domains:**
```
disys.com, winworldinfo.com, partneresi.com, ansys.com,
akselos.com, engys.com, dnvgl.com, tescocorp.com,
deccaconsulting.com, flooranddecor.com, pulse-monitoring.com,
quantumep.com, acematrix.com
```

**Ace recruiter domains:**
```
stepstoprogress.com, thejukesgroup.com, apexsystems.com,
indianeagle.com
```

**Ace industry domains:**
```
km.kongsberg.com, ceesol.com
```

**Personal alumni domains:**
```
rice.edu, mccombs.utexas.edu, neo.tamu.edu, tamu.edu, houstonisd.org
```

**Personal financial domains:**
```
aaa-texas.com, colehealth.com, harkandgroup.com, aol.com,
sbcglobal.net, constellation.com
```

**Spam domains (auto-remove):**
```
sale.craigslist.org, talkmatch.com
```

**Spam patterns (regex):**
```
unsubscribe, no.?reply, noreply, do.?not.?reply
mailer-daemon, postmaster@, bounce@
@unsubscribe2\., \.unsubscribe\., @sailthru\., @mcsv\., @rsys5\., @customer\.io
```

**Spam name fragments:**
```
craigslist, mailer-daemon, unsubscribe, academia.edu, 123greetings, machinemetrics
```

### Step 4: Intra-file deduplication

Rules:
- Same primary email → keep first occurrence
- Same name, different email → keep both, flag for review
- No name, only email → try to derive name from email prefix

### Step 5: Cross-file deduplication

132 overlaps found between ace and personal files. Decision rules (applied in order):

1. `aceengineer.com` → ace only (internal domain)
2. `achanta` in email prefix → personal only (family)
3. Company domain (not gmail/yahoo/hotmail) → ace only (professional)
4. Personal email with company tag in source → ace only
5. Personal email with company in ace record → ace only
6. Both unknown, personal email → personal only
7. Ace has real classification → ace wins

Result: 122 moved from personal to ace, 10 kept in personal.
Zero remaining overlaps.

Report template: `reports/email/contact-dedup-report.md`

## Scripts

### Contact normalizer (run with uv)
```bash
uv run scripts/email/contact-normalizer.py
```

Input: raw Outlook CSV exports from both accounts.
Output: `aceengineer_normalized.csv` (1,281 contacts) + `achantav_normalized.csv` (994 contacts).

### SKEstates contact builder
Built from two markdown files:
- `key_contacts.md` (3 PCA vendor contacts)
- `fd_corporate_contact_maintenance.md` (22 Family Dollar/Dollar Tree staff)

Output: `sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv` (25 contacts).
# Count unknown domains to discover missing mappings
unknown_domains = Counter(r["email"].split("@")[-1] for r in contacts if r["category"] == "unknown")
for domain, count in unknown_domains.most_common(20):
    print(f"  {domain:40s} {count}")
```

Then expand the domain classification sets (ACE_CLIENT_DOMAINS, ACE_VENDOR_DOMAINS, etc.)
in the normalizer script and re-run. Second pass typically reaches 80%+ classification.

### Step 4: Cross-file deduplication

When contacts appear in multiple account files (email addresses imported into
multiple Outlook exports), resolve overlaps using these rules:

| Signal | Canonical Home | Rationale |
|---|---|---|
| aceengineer.com domain | ace | Internal domain |
| achantav* in email prefix | personal | Family email |
| Company domain (non-gmail/yahoo) | ace | Professional contact |
| Personal email with company in record | ace | Cross-referenced professional |
| Both unknown, personal email | personal | No business value |
| Ace has classification | ace | Already categorized |

After dedup: annotate the canonical file with cross-ref note, remove from duplicate file.

### Step 5: Write output files

## Scripts

### Contact normalizer (run with uv)
```bash
uv run scripts/email/contact-normalizer.py
```
The normalizer processes ALL accounts in one run. It reads both raw CSVs and outputs normalized files alongside them. No CLI args needed — paths are hardcoded for the workspace-hub convention.

### Re-running after adding domain mappings
Edit the domain sets in `scripts/email/contact-normalizer.py` (ACE_CLIENT_DOMAINS, ACE_VENDOR_DOMAINS, etc.) then re-run. The script is idempotent.

## File Locations (post-normalization)

| Account | Normalized CSV | Classified CSV |
|---|---|---|
| ace | aceengineer-admin/admin/contacts/aceengineer_normalized.csv | aceengineer-admin/admin/contacts/aceengineer_classified.csv |
| personal | aceengineer-admin/admin/contacts/achantav_normalized.csv | aceengineer-admin/admin/contacts/achantav_classified.csv |
| skestates | sabithaandkrishnaestates/admin/contacts/skestates_contacts.csv | (small enough to classify manually) |

## Pitfalls

1. Outlook CSV export has 64 columns with verbose names ("E-mail Address", "E-mail 2 Address", etc.)
2. Email addresses often wrapped in angle brackets: `<email@domain.com>`
3. Some entries have email stored in "First Name" field when name is unknown
4. Windows BOM (utf-8-sig) — always open with `encoding="utf-8-sig"`
5. Empty first/last name rows are common (~30-36% of contacts) — use email prefix for name inference
6. Cross-file email overlap is guaranteed (~132 of ~2,400) — always dedup after normalizing
7. External repos (aceengineer-admin, sabithaandkrishnaestates) must be committed from within their own git dirs
8. Legal scan: contact CSVs may contain client names — run `.legal-deny-list.yaml` scan before committing
9. Don't delete raw Outlook exports — keep originals, create `_normalized.csv` alongside
10. Domain inference from email prefix is heuristic-only — tag uncertain results for manual review
3. Don't delete raw CSVs — keep originals, create normalized copies alongside
4. Legal: contact data is PII — never commit to public repos, .gitignore if needed
5. The personal CSV has craigslist/talkmatch spam entries — auto-classify as spam
6. Company field often empty — try to infer from email domain
7. External repos (aceengineer-admin, sabithaandkrishnaestates) are separate git repos — `cd` into them to commit, don't use `git add` from workspace-hub root
8. First-pass domain classification yields ~20% — ALWAYS run the unknown-domain-frequency analysis and expand mappings before claiming done
9. The contact-normalizer.py script lives in workspace-hub root (`scripts/email/`) but reads/writes in repo subdirectories — it finds the root by walking up from its own path
