#!/usr/bin/env python
"""Contact normalizer for aceengineer and personal Gmail contacts.

Reads raw Outlook CSV exports, cleans, deduplicates, classifies, and outputs normalized CSVs.
Run with: uv run scripts/email/contact-normalizer.py

This script is the canonical version — it generated the _normalized.csv files
in aceengineer-admin/admin/contacts/. Re-run after updating domain mappings.
"""

import csv
import re
from pathlib import Path
from collections import Counter

# ============================================================
# CONFIG
# ============================================================
ACE_CLIENT_DOMAINS = {
    "ril.com", "dorisgroup.com", "mcdermott.com", "shell.com",
    "kbr.com", "technip.com", "technipfmc.com", "subsea7.com",
    "nov.com", "aker.com", "bp.com", "awilcodrilling.com",
    "eagle.org", "vulcanoffshore.com", "boptechnologies.com",
    "risersinc.com", "sandsig.com", "engineeredcustomsolutions.com",
    "mecorparada.com.ve", "applied.com",
}
ACE_COLLEAGUE_DOMAINS = {
    "trendsetterengineering.com", "spire-engineers.com",
    "2hoffshoreinc.com", "2hoffshore.com",
    "prospricing.com",
}
ACE_VENDOR_DOMAINS = {
    "disys.com", "winworldinfo.com", "partneresi.com", "ansys.com",
    "akselos.com", "engys.com", "dnvgl.com", "tescocorp.com",
    "deccaconsulting.com", "flooranddecor.com",
    "pulse-monitoring.com", "quantumep.com", "acematrix.com",
}
ACE_RECRUITER_DOMAINS = {
    "stepstoprogress.com", "thejukesgroup.com", "apexsystems.com",
    "indianeagle.com",
}
ACE_INDUSTRY_DOMAINS = {"km.kongsberg.com", "ceesol.com"}
PERSONAL_ALUMNI_DOMAINS = {"rice.edu", "mccombs.utexas.edu", "neo.tamu.edu", "tamu.edu", "houstonisd.org"}
PERSONAL_FINANCIAL_DOMAINS = {"aaa-texas.com", "colehealth.com", "harkandgroup.com", "aol.com", "sbcglobal.net", "constellation.com"}
PERSONAL_GMAIL_NAMES_ACHANTA = {"achanta"}

SPAM_DOMAINS = {"sale.craigslist.org", "talkmatch.com"}
UNSUB_PATTERNS = [
    r"unsubscribe", r"no.?reply", r"noreply", r"do.?not.?reply",
    r"mailer-daemon", r"postmaster@", r"bounce@",
    r"@unsubscribe2\.", r"\.unsubscribe\.",
    r"@sailthru\.", r"@mcsv\.", r"@rsys5\.", r"@customer\.io",
]
SPAM_NAME_PARTS = [
    "craigslist", "mailer-daemon", "unsubscribe", "academia.edu",
    "123greetings", "machinemetrics",
]

DOMAIN_COMPANY = {
    "ril.com": "Reliance Industries", "dorisgroup.com": "DORIS",
    "mcdermott.com": "McDermott", "shell.com": "Shell",
    "kbr.com": "KBR", "bp.com": "BP",
    "technip.com": "TechnipFMC", "technipfmc.com": "TechnipFMC",
    "subsea7.com": "Subsea7", "nov.com": "NOV",
    "aker.com": "Aker Solutions", "awilcodrilling.com": "Awilco Drilling",
    "eagle.org": "American Bureau of Shipping",
    "vulcanoffshore.com": "Vulcan Offshore",
    "boptechnologies.com": "BOP Technologies",
    "risersinc.com": "Risers", "sandsig.com": "Sands International",
    "engineeredcustomsolutions.com": "Engineered Custom Solutions",
    "km.kongsberg.com": "Kongsberg Maritime",
    "ansys.com": "ANSYS", "dnvgl.com": "DNV GL", "engys.com": "ENGYS",
    "tescocorp.com": "TESCO Corporation",
    "partneresi.com": "Partner Engineering", "akselos.com": "Akselos",
    "2hoffshoreinc.com": "2H Offshore", "2hoffshore.com": "2H Offshore",
    "prospricing.com": "Pros Pricing",
    "deccaconsulting.com": "Decca Consulting",
    "apexsystems.com": "Apex Systems", "disys.com": "DISYS",
    "trendsetterengineering.com": "Trendsetter Engineering",
    "spire-engineers.com": "Spire Engineers",
    "winworldinfo.com": "WinWorld",
    "stepstoprogress.com": "Steps to Progress",
    "thejukesgroup.com": "The Jukes Group",
    "aceengineer.com": "ACE Engineer",
    "rice.edu": "Rice University", "mccombs.utexas.edu": "UT McCombs",
    "neo.tamu.edu": "Texas A&M", "houstonisd.org": "Houston ISD",
    "pulse-monitoring.com": "Pulse Monitoring", "quantumep.com": "Quantum EP",
    "acematrix.com": "AceMatrix", "aaa-texas.com": "AAA Texas",
    "colehealth.com": "Cole Health", "harkandgroup.com": "Harkand Group",
    "flooranddecor.com": "Floor & Decor",
    "mecorparada.com.ve": "MECOR Parada C.A.",
    "indianeagle.com": "Indian Eagle",
}

TOUCHBASE_CADENCE = {
    "client": "quarterly", "colleague": "quarterly", "prospect": "monthly",
    "recruiter": "none", "newsletter": "none", "spam": "none",
    "industry": "biannual", "internal": "none", "personal": "biannual",
    "alumni": "biannual", "government": "none", "vendor": "none",
    "financial": "none", "unknown": "none",
}


def is_spam(email, first_name=""):
    domain = email.split("@")[-1].lower() if "@" in email else ""
    if domain in SPAM_DOMAINS:
        return True
    for pat in UNSUB_PATTERNS:
        if re.search(pat, email.lower()):
            return True
    for sn in SPAM_NAME_PARTS:
        if sn in (first_name or "").lower():
            return True
    return False


def is_family_gmail(email):
    prefix = email.split("@")[0] if "@" in email else ""
    for name in PERSONAL_GMAIL_NAMES_ACHANTA:
        if name in prefix:
            return True
    return False


def infer_category_ace(domain):
    if domain in ACE_CLIENT_DOMAINS: return "client"
    if domain in ACE_COLLEAGUE_DOMAINS: return "colleague"
    if domain in ACE_VENDOR_DOMAINS: return "vendor"
    if domain in ACE_RECRUITER_DOMAINS: return "recruiter"
    if domain in ACE_INDUSTRY_DOMAINS: return "industry"
    if domain.endswith((".gov", ".mil")): return "government"
    if domain.endswith(".edu"): return "alumni"
    return "unknown"


def infer_category_personal(domain, email):
    if domain in ACE_COLLEAGUE_DOMAINS: return "colleague"
    if domain in ACE_CLIENT_DOMAINS: return "client"
    if domain in ACE_VENDOR_DOMAINS: return "vendor"
    if domain in ACE_RECRUITER_DOMAINS: return "recruiter"
    if domain in PERSONAL_ALUMNI_DOMAINS: return "alumni"
    if domain in PERSONAL_FINANCIAL_DOMAINS: return "financial"
    if is_family_gmail(email): return "personal"
    if domain.endswith((".gov", ".mil")): return "government"
    if domain.endswith(".edu"): return "alumni"
    return "unknown"


def touchbase_cadence(category):
    return TOUCHBASE_CADENCE.get(category, "none")


def infer_company(domain):
    if "@" in domain:
        domain = domain.split("@")[-1]
    return DOMAIN_COMPANY.get(domain, domain)


def process_account(account, input_path, output_path):
    with open(input_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    counts = Counter()
    seen = set()
    normalized = []

    for row in rows:
        first_raw = (row.get("First Name") or "").strip()
        last_raw = (row.get("Last Name") or "").strip()
        company_raw = (row.get("Company") or "").strip()
        job_title = (row.get("Job Title") or "").strip()
        notes = (row.get("Notes") or "").strip()

        emails = []
        for col in ["E-mail Address", "E-mail 2 Address", "E-mail 3 Address"]:
            e = (row.get(col) or "").strip()
            if e:
                e = re.sub(r"[<>]", "", e).strip().lower()
                if re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", e):
                    emails.append(e)

        if not emails:
            counts["empty_email"] += 1
            continue

        primary = emails[0]
        if is_spam(primary, first_raw):
            counts["spam"] += 1
            continue
        if primary in seen:
            counts["dup_primary"] += 1
            continue
        seen.add(primary)

        first = re.sub(r"<[^>]+>", "", first_raw).strip()
        last = re.sub(r"<[^>]+>", "", last_raw).strip()
        if "@" in first: first = ""
        if "@" in last: last = ""

        if not first and not last:
            prefix = primary.split("@")[0]
            prefix = re.sub(r"[._]+", " ", prefix)
            if all(c.isalpha() or c == " " for c in prefix) and len(prefix) > 2:
                first = prefix.title()

        domain = primary.split("@")[-1]
        if account == "ace":
            category = infer_category_ace(domain)
        else:
            category = infer_category_personal(domain, primary)

        company = company_raw or infer_company(domain)
        cadence = touchbase_cadence(category)

        extra = []
        if emails[1:]:
            extra.append("Alt: " + "; ".join(emails[1:]))
        if job_title:
            extra.append("Title: " + job_title)
        if notes:
            extra.append(notes)
        if not company_raw:
            extra.append("Company inferred from domain")

        normalized.append({
            "email": primary,
            "first_name": first or "?",
            "last_name": last or "?",
            "company": company,
            "category": category,
            "touchbase_cadence": cadence,
            "notes": " | ".join(extra),
        })
        counts[category] += 1

    normalized.sort(key=lambda r: (r["category"], r.get("company", ""), r.get("last_name", "")))

    fieldnames = ["email", "first_name", "last_name", "company",
                   "category", "touchbase_cadence", "notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(normalized)

    print(f"  {account}: {len(seen)} unique emails, "
          f"{counts['spam']} spam, {counts['dup_primary']} dupes, "
          f"{counts['empty_email']} empty")
    print(f"  Categories: {dict(counts.most_common())}")

    return normalized


if __name__ == "__main__":
    # Determine base path
    script_dir = Path(__file__).resolve().parent.parent
    base = script_dir.parent

    for config in [
        ("ace", base / "aceengineer-admin/admin/contacts/aceengineer_contacts.csv",
         base / "aceengineer-admin/admin/contacts/aceengineer_normalized.csv"),
        ("personal", base / "aceengineer-admin/admin/contacts/achantav_contacts.csv",
         base / "aceengineer-admin/admin/contacts/achantav_normalized.csv"),
    ]:
        acc, inp, out = config
        print(f"\nProcessing {acc}...")
        process_account(acc, inp, out)

    # Cross-file dedup
    ace_set = set()
    per_set = set()
    for f in [base / "aceengineer-admin/admin/contacts/aceengineer_normalized.csv",
              base / "aceengineer-admin/admin/contacts/achantav_normalized.csv"]:
        with open(f) as fh:
            emails = {r["email"] for r in csv.DictReader(fh)}
        if "aceengineer" in str(f):
            ace_set = emails
        else:
            per_set = emails

    overlap = ace_set & per_set
    print(f"\nCross-file overlap: {len(overlap)} emails")
