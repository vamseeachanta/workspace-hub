#!/usr/bin/env python3
"""
GTM Job Market Scanner — ACE Engineer
======================================
Scans multiple job boards and Google for engineering roles matching
ACE Engineer's capabilities. Produces structured JSON results and
a markdown dashboard.

Designed for weekly refresh — tracks history across runs, detects
NEW postings since last scan, flags trending companies (hiring more
over time), and maintains a cumulative index.

Usage:
    python scripts/gtm/job-market-scanner.py [--keywords KEY1,KEY2] [--limit N]
    python scripts/gtm/job-market-scanner.py --refresh   # weekly refresh mode

Output:
    docs/strategy/gtm/job-market-scan/raw-results/YYYY-MM-DD.json
    docs/strategy/gtm/job-market-scan/cumulative-index.json    (all-time seen jobs)
    docs/strategy/gtm/job-market-scan/new-this-week.md         (delta from last scan)
    docs/strategy/gtm/job-market-scan/dashboard.md
    docs/strategy/gtm/job-market-scan/priority-targets.md
    docs/strategy/gtm/job-market-scan/trend-report.md          (week-over-week trends)

Related: GitHub issues #1669, #1670, #1671
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "strategy" / "gtm" / "job-market-scan"
RAW_DIR = OUTPUT_DIR / "raw-results"
ARCHIVE_DIR = OUTPUT_DIR / "archive"
KEYWORD_DIR = OUTPUT_DIR / "keyword-results"
PROFILE_DIR = OUTPUT_DIR / "company-profiles"
RAW_RETENTION_WEEKS = 12
HISTORY_RETENTION_MONTHS = 6

# Search keywords ordered by specificity (most niche first = highest value)
KEYWORDS = [
    # Tier 1 — Elite niche (very few candidates globally)
    "OrcaFlex engineer",
    "OrcaWave analyst",
    "riser engineer offshore",
    "mooring engineer offshore",
    "hydrodynamic analyst offshore",
    # Tier 2 — Strong niche
    "cathodic protection engineer",
    "subsea engineer",
    "pipeline engineer offshore",
    "API 579 fitness for service",
    "integrity engineer offshore",
    "naval architect Houston",
    "floating wind engineer",
    # Tier 3 — Broader (still strong fit)
    "FEA analyst ANSYS",
    "finite element analyst",
    "structural engineer offshore",
    "corrosion engineer",
    "DNV engineer offshore",
    "Python engineer oil gas",
    # Tier 4 — Manufacturing / broader US
    "FEA analyst manufacturing",
    "ANSYS engineer manufacturing",
    "structural analyst aerospace",
    "cathodic protection manufacturing",
]

# Tier assignment for scoring
KEYWORD_TIERS = {}
for i, kw in enumerate(KEYWORDS):
    if i < 5:
        KEYWORD_TIERS[kw] = 1  # Elite
    elif i < 12:
        KEYWORD_TIERS[kw] = 2  # Strong
    elif i < 18:
        KEYWORD_TIERS[kw] = 3  # Broader
    else:
        KEYWORD_TIERS[kw] = 4  # Manufacturing

# Known target companies for priority scoring
PRIORITY_COMPANIES = {
    # Tier 1 — EPIC / Installation
    "subsea7", "technipfmc", "saipem", "mcdermott", "allseas", "heerema",
    "boskalis", "van oord", "deme",
    # Tier 2 — Operators
    "energy transfer", "crescent energy", "shell", "bp", "chevron",
    "exxonmobil", "talos energy", "murphy oil", "kosmos energy",
    "eog resources", "devon energy", "diamondback", "hess",
    # Tier 3 — Consultancies
    "2h offshore", "stress engineering", "zentech", "sofec", "intermoor",
    "wood group", "worley", "aker solutions", "genesis", "intecsea", "mcs kenny",
    # Tier 4 — FPSO
    "sbm offshore", "modec", "bw offshore", "yinson",
    # Tier 5 — Offshore Wind
    "orsted", "equinor", "vineyard wind", "principle power",
    # Tier 6 — LNG
    "cheniere", "venture global", "nextdecade", "sempra",
    # Tier 7 — Classification
    "dnv", "abs", "bureau veritas", "lloyd's register",
    # Manufacturing
    "trinity industries", "chart industries", "cameron", "flowserve",
    "dril-quip", "oceaneering", "forum energy", "ge vernova", "siemens energy",
    "bollinger shipyards", "huntington ingalls", "vt halter",
}

# Seniority keywords for scoring
SENIOR_KEYWORDS = {
    "senior", "lead", "principal", "staff", "director", "manager",
    "vp", "chief", "head of", "specialist", "expert", "sr.", "sr "
}

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Rate limiting and source policy
REQUEST_DELAY = 2.0  # default seconds between requests
SOURCE_RATE_LIMITS = {
    "google": 3.0,
    "google_direct": 3.0,
    "indeed": 4.0,
    "linkedin": 4.0,
    "rigzone": 4.0,
    "career_page": 3.0,
    "example-board": 2.0,
}
SOURCE_ALLOWLIST = set(SOURCE_RATE_LIMITS)
SOURCE_ALLOWED_DOMAINS = {
    "google": {"www.google.com", "google.com"},
    "google_direct": {"www.google.com", "google.com"},
    "indeed": {"www.indeed.com", "indeed.com"},
    "linkedin": {"www.linkedin.com", "linkedin.com"},
    "rigzone": {"www.rigzone.com", "rigzone.com"},
    "career_page": None,
    "example-board": {"boards.example.com"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_request(
    url: str,
    params: dict | None = None,
    timeout: int = 15,
    source: str | None = None,
    max_attempts: int = 2,
) -> requests.Response | None:
    """Make a rate-limited HTTP request with basic compliance handling."""
    parsed = urllib.parse.urlparse(url)
    source_name = (source or parsed.netloc or "").lower()
    if source_name and source_name not in SOURCE_ALLOWLIST:
        print(f"  [WARN] Skipping disallowed source: {source_name}")
        return None

    allowed_domains = SOURCE_ALLOWED_DOMAINS.get(source_name)
    if allowed_domains is not None and parsed.netloc.lower() not in allowed_domains:
        print(f"  [WARN] Skipping URL outside allowlist for {source_name}: {parsed.netloc}")
        return None

    delay = SOURCE_RATE_LIMITS.get(source_name, REQUEST_DELAY)
    time.sleep(delay)

    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            status_code = getattr(resp, "status_code", None)
            headers = getattr(resp, "headers", {}) or {}
            retry_after = headers.get("Retry-After")
            if status_code in {429, 503} and attempt < max_attempts:
                sleep_for = delay * (2 ** attempt)
                if retry_after:
                    try:
                        sleep_for = max(sleep_for, float(retry_after))
                    except ValueError:
                        pass
                print(f"  [WARN] {source_name or url} rate limited ({status_code}); retrying in {sleep_for}s")
                time.sleep(sleep_for)
                continue
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            print(f"  [WARN] Request failed: {e}")
            return None
        except requests.RequestException as e:
            print(f"  [WARN] Request failed: {e}")
            return None
    return None


def legacy_job_id(title: str, company: str, location: str) -> str:
    """Generate the legacy deduplication key used before #1708."""
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def job_id(
    title: str,
    company: str,
    location: str,
    source: str = "",
    url: str = "",
    posted_date: str = "",
) -> str:
    """Generate a unique ID for deduplication and repost tracking."""
    raw = "|".join([
        title.lower().strip(),
        company.lower().strip(),
        location.lower().strip(),
        source.lower().strip(),
        url.lower().strip(),
        posted_date.lower().strip(),
    ])
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def detect_seniority(title: str) -> str:
    """Detect seniority level from job title."""
    title_lower = title.lower()
    for kw in SENIOR_KEYWORDS:
        if kw in title_lower:
            return "senior"
    if any(w in title_lower for w in ["junior", "jr.", "jr ", "entry", "graduate", "intern"]):
        return "junior"
    return "mid"


def is_priority_company(company: str) -> bool:
    """Check if company is in our priority list."""
    company_lower = company.lower()
    return any(pc in company_lower for pc in PRIORITY_COMPANIES)


def score_job(job: dict) -> int:
    """Score a job posting on alignment (higher = better consulting lead)."""
    score = 0

    # Keyword tier (niche keywords score higher)
    tier = job.get("keyword_tier", 4)
    score += (5 - tier) * 20  # Tier 1 = 80, Tier 4 = 20

    # Seniority (senior = they need experience NOW)
    seniority = job.get("seniority", "mid")
    if seniority == "senior":
        score += 30
    elif seniority == "mid":
        score += 15

    # Priority company
    if job.get("is_priority_company"):
        score += 25

    # Location (Houston = easiest, remote = also good)
    location = job.get("location", "").lower()
    if "houston" in location:
        score += 15
    elif "remote" in location:
        score += 10
    elif "texas" in location or "tx" in location:
        score += 10

    # Consulting/contract indicator
    title_lower = job.get("title", "").lower()
    if any(w in title_lower for w in ["contract", "consultant", "consulting", "freelance"]):
        score += 20

    return score


# ---------------------------------------------------------------------------
# Scrapers
# ---------------------------------------------------------------------------

def scrape_google_jobs(keyword: str, location: str = "United States") -> list[dict]:
    """
    Scrape Google search results for job postings.
    Uses Google search with site-specific queries.
    """
    jobs = []
    query = f'"{keyword}" job site:linkedin.com/jobs OR site:indeed.com OR site:rigzone.com'
    url = "https://www.google.com/search"
    params = {"q": query, "num": 20}

    resp = safe_request(url, params, source="google")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")
    for result in soup.select("div.g, div[data-sokoban-container]"):
        title_el = result.select_one("h3")
        link_el = result.select_one("a[href]")
        snippet_el = result.select_one("div.VwiC3b, span.aCOpRe")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        link = link_el.get("href", "")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        # Try to extract company from title/snippet
        company = ""
        # LinkedIn pattern: "Title - Company | LinkedIn"
        if "linkedin.com" in link:
            parts = title.split(" - ")
            if len(parts) >= 2:
                company = parts[-1].replace("| LinkedIn", "").strip()
                title = parts[0].strip()

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": link,
            "snippet": snippet[:300],
            "source": "google",
        })

    return jobs


def scrape_indeed(keyword: str, location: str = "United States") -> list[dict]:
    """Scrape Indeed job listings."""
    jobs = []
    encoded_kw = urllib.parse.quote_plus(keyword)
    url = f"https://www.indeed.com/jobs?q={encoded_kw}&l={urllib.parse.quote_plus(location)}&sort=date"

    resp = safe_request(url, source="indeed")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")

    # Indeed job cards
    for card in soup.select("div.job_seen_beacon, div.jobsearch-ResultsList div.result"):
        title_el = card.select_one("h2.jobTitle a, a.jcs-JobTitle")
        company_el = card.select_one("span[data-testid='company-name'], span.companyName")
        location_el = card.select_one("div[data-testid='text-location'], div.companyLocation")
        snippet_el = card.select_one("div.job-snippet, td.snip")

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        company = company_el.get_text(strip=True) if company_el else ""
        loc = location_el.get_text(strip=True) if location_el else location
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        href = title_el.get("href", "")
        if href and not href.startswith("http"):
            href = f"https://www.indeed.com{href}"

        jobs.append({
            "title": title,
            "company": company,
            "location": loc,
            "url": href,
            "snippet": snippet[:300],
            "source": "indeed",
        })

    return jobs


def scrape_rigzone(keyword: str) -> list[dict]:
    """Scrape Rigzone job listings (oil & gas specific)."""
    jobs = []
    encoded_kw = urllib.parse.quote_plus(keyword)
    url = f"https://www.rigzone.com/oil/jobs/search/?keyword={encoded_kw}&sort=date"

    resp = safe_request(url, source="rigzone")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")

    for row in soup.select("tr.job_listing, div.job-listing, div.search-result"):
        title_el = row.select_one("a.title, a.job-title, td.title a")
        company_el = row.select_one("span.company, td.company, a.company")
        location_el = row.select_one("span.location, td.location")

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        company = company_el.get_text(strip=True) if company_el else ""
        loc = location_el.get_text(strip=True) if location_el else ""
        href = title_el.get("href", "")
        if href and not href.startswith("http"):
            href = f"https://www.rigzone.com{href}"

        jobs.append({
            "title": title,
            "company": company,
            "location": loc,
            "url": href,
            "snippet": "",
            "source": "rigzone",
        })

    return jobs


def scrape_linkedin_search(keyword: str, location: str = "United States") -> list[dict]:
    """Scrape LinkedIn job search (public, no login required)."""
    jobs = []
    params = {
        "keywords": keyword,
        "location": location,
        "sortBy": "DD",  # sort by date
        "f_TPR": "r604800",  # past week
    }
    url = "https://www.linkedin.com/jobs/search/"

    resp = safe_request(url, params, source="linkedin")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")

    for card in soup.select("div.base-card, li.result-card"):
        title_el = card.select_one("h3.base-search-card__title, h3.result-card__title")
        company_el = card.select_one("h4.base-search-card__subtitle, h4.result-card__subtitle")
        location_el = card.select_one("span.job-search-card__location, span.result-card__location")
        link_el = card.select_one("a.base-card__full-link, a.result-card__full-link")

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        company = company_el.get_text(strip=True) if company_el else ""
        loc = location_el.get_text(strip=True) if location_el else location
        href = link_el.get("href", "") if link_el else ""

        jobs.append({
            "title": title,
            "company": company,
            "location": loc,
            "url": href,
            "snippet": "",
            "source": "linkedin",
        })

    return jobs


def scrape_google_direct(keyword: str) -> list[dict]:
    """
    Use Google search to find job postings more broadly.
    This catches company career pages, niche boards, etc.
    """
    jobs = []
    query = f'"{keyword}" hiring OR "open position" OR "apply now" OR "job posting" engineer 2025 OR 2026'
    url = "https://www.google.com/search"
    params = {"q": query, "num": 15}

    resp = safe_request(url, params, source="google_direct")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")

    for result in soup.select("div.g"):
        title_el = result.select_one("h3")
        link_el = result.select_one("a[href]")
        snippet_el = result.select_one("div.VwiC3b, span.aCOpRe")

        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        link = link_el.get("href", "")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        # Skip non-job results
        title_lower = title.lower()
        if not any(w in title_lower or w in snippet.lower() for w in
                   ["job", "career", "hiring", "position", "apply", "engineer", "analyst"]):
            continue

        jobs.append({
            "title": title,
            "company": "",
            "location": "USA",
            "url": link,
            "snippet": snippet[:300],
            "source": "google_direct",
        })

    return jobs


# ---------------------------------------------------------------------------
# Company Career Page Scanner
# ---------------------------------------------------------------------------

COMPANY_CAREER_URLS = {
    "Energy Transfer": "https://www.energytransfer.com/careers",
    "Crescent Energy": "https://crescentenergyco.com/careers/",
    "Subsea7": "https://www.subsea7.com/en/careers.html",
    "TechnipFMC": "https://careers.technipfmc.com/",
    "Oceaneering": "https://careers.oceaneering.com/",
    "Dril-Quip": "https://www.dril-quip.com/careers",
    "Cheniere Energy": "https://www.cheniere.com/careers",
    "SBM Offshore": "https://www.sbmoffshore.com/careers",
    "Heerema": "https://heerema.com/careers",
    "McDermott": "https://careers.mcdermott.com/",
    "Wood": "https://www.woodplc.com/careers",
    "Worley": "https://www.worley.com/en/careers",
    "ABS": "https://ww2.eagle.org/en/careers.html",
    "DNV": "https://www.dnv.com/careers/",
    "Bureau Veritas": "https://group.bureauveritas.com/careers",
    "Aker Solutions": "https://www.akersolutions.com/careers/",
    "Saipem": "https://www.saipem.com/en/work-us",
    "Allseas": "https://allseas.com/careers/",
    "DOF Subsea": "https://www.dofsubsea.com/careers",
    "Chart Industries": "https://www.chartindustries.com/careers",
    "GE Vernova": "https://www.gevernova.com/careers",
    "Siemens Energy": "https://www.siemens-energy.com/global/en/company/careers.html",
    "Bollinger Shipyards": "https://bollingershipyards.com/careers/",
    "VT Halter Marine": "https://www.vthalter.com/careers/",
    "Huntington Ingalls": "https://www.huntingtoningalls.com/careers/",
    "Orsted": "https://orsted.com/en/careers",
    "Equinor": "https://www.equinor.com/careers",
    "Vineyard Wind": "https://www.vineyardwind.com/careers",
    "Talos Energy": "https://www.talosenergy.com/careers",
    "Shell": "https://www.shell.com/careers",
}


def scan_career_page(company: str, url: str, search_terms: list[str] | None = None) -> list[dict]:
    """Scan a company career page for relevant job postings."""
    jobs = []
    if search_terms is None:
        search_terms = [
            "engineer", "analyst", "orcaflex", "structural", "fea",
            "subsea", "pipeline", "mooring", "riser", "naval",
            "corrosion", "cathodic", "integrity", "python", "hydrodynamic"
        ]

    resp = safe_request(url, source="career_page")
    if not resp:
        return jobs

    soup = BeautifulSoup(resp.text, "lxml")
    page_text = soup.get_text().lower()

    # Check if any search terms appear on the page
    found_terms = [t for t in search_terms if t.lower() in page_text]

    if found_terms:
        # Look for job listing links
        for link in soup.select("a[href]"):
            text = link.get_text(strip=True)
            href = link.get("href", "")
            text_lower = text.lower()

            if any(t.lower() in text_lower for t in search_terms) and len(text) > 10:
                if not href.startswith("http"):
                    base = urllib.parse.urljoin(url, href)
                    href = base

                jobs.append({
                    "title": text[:200],
                    "company": company,
                    "location": "",
                    "url": href,
                    "snippet": f"Found terms: {', '.join(found_terms[:5])}",
                    "source": "career_page",
                })

    return jobs


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_scan(keywords: list[str] | None = None, limit: int | None = None,
             skip_career_pages: bool = False) -> dict:
    """Run the full job market scan."""
    if keywords is None:
        keywords = KEYWORDS
    if limit:
        keywords = keywords[:limit]

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    all_jobs = []
    seen_ids = set()
    stats = {
        "timestamp": timestamp,
        "keywords_searched": len(keywords),
        "sources_used": [],
        "jobs_by_source": Counter(),
        "jobs_by_keyword": Counter(),
        "jobs_by_company": Counter(),
        "jobs_by_tier": Counter(),
    }

    print(f"\n{'='*60}")
    print(f"  GTM Job Market Scanner — ACE Engineer")
    print(f"  {timestamp}")
    print(f"  Keywords: {len(keywords)} | Sources: Google, Indeed, LinkedIn, Rigzone")
    print(f"{'='*60}\n")

    # Phase 1: Keyword-based scraping across job boards
    for i, keyword in enumerate(keywords):
        tier = KEYWORD_TIERS.get(keyword, 4)
        print(f"[{i+1}/{len(keywords)}] Scanning: \"{keyword}\" (Tier {tier})")

        keyword_jobs = []

        # Google Jobs search
        print(f"  → Google search...")
        gj = scrape_google_jobs(keyword)
        keyword_jobs.extend(gj)
        print(f"    Found {len(gj)} results")

        # Indeed
        print(f"  → Indeed...")
        ij = scrape_indeed(keyword)
        keyword_jobs.extend(ij)
        print(f"    Found {len(ij)} results")

        # LinkedIn
        print(f"  → LinkedIn...")
        lj = scrape_linkedin_search(keyword)
        keyword_jobs.extend(lj)
        print(f"    Found {len(lj)} results")

        # Rigzone (only for oil & gas keywords)
        if tier <= 3:
            print(f"  → Rigzone...")
            rj = scrape_rigzone(keyword)
            keyword_jobs.extend(rj)
            print(f"    Found {len(rj)} results")

        # Google direct (broader search)
        print(f"  → Google direct...")
        gd = scrape_google_direct(keyword)
        keyword_jobs.extend(gd)
        print(f"    Found {len(gd)} results")

        # Enrich and deduplicate
        for job in keyword_jobs:
            job["search_keyword"] = keyword
            job["keyword_tier"] = tier
            job["seniority"] = detect_seniority(job["title"])
            job["is_priority_company"] = is_priority_company(job.get("company", ""))
            job["alignment_score"] = score_job(job)

            jid = job_id(
                job["title"],
                job.get("company", ""),
                job.get("location", ""),
                source=job.get("source", ""),
                url=job.get("url", ""),
                posted_date=job.get("posted_date", ""),
            )
            if jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(job)
                stats["jobs_by_source"][job["source"]] += 1
                stats["jobs_by_keyword"][keyword] += 1
                stats["jobs_by_tier"][f"tier_{tier}"] += 1
                if job.get("company"):
                    stats["jobs_by_company"][job["company"]] += 1

        print(f"  ✓ {len(keyword_jobs)} found, {len(all_jobs)} unique total\n")

    # Phase 2: Company career page scanning
    if not skip_career_pages:
        print(f"\n{'='*60}")
        print(f"  Phase 2: Scanning {len(COMPANY_CAREER_URLS)} company career pages")
        print(f"{'='*60}\n")

        for company, url in COMPANY_CAREER_URLS.items():
            print(f"  → {company}: {url}")
            cj = scan_career_page(company, url)
            for job in cj:
                job["search_keyword"] = "career_page_scan"
                job["keyword_tier"] = 2
                job["seniority"] = detect_seniority(job["title"])
                job["is_priority_company"] = True
                job["alignment_score"] = score_job(job)

                jid = job_id(
                    job["title"],
                    job.get("company", ""),
                    job.get("location", ""),
                    source=job.get("source", ""),
                    url=job.get("url", ""),
                    posted_date=job.get("posted_date", ""),
                )
                if jid not in seen_ids:
                    seen_ids.add(jid)
                    all_jobs.append(job)
                    stats["jobs_by_source"]["career_page"] += 1
                    stats["jobs_by_company"][company] += 1

            print(f"    Found {len(cj)} relevant listings")

    # Sort by alignment score (highest first)
    all_jobs.sort(key=lambda j: j.get("alignment_score", 0), reverse=True)

    # Build result
    result = {
        "meta": {
            "timestamp": timestamp,
            "total_jobs": len(all_jobs),
            "total_unique_companies": len(stats["jobs_by_company"]),
            "keywords_searched": stats["keywords_searched"],
            "sources": dict(stats["jobs_by_source"]),
            "by_tier": dict(stats["jobs_by_tier"]),
        },
        "jobs": all_jobs,
        "company_rankings": dict(stats["jobs_by_company"].most_common(50)),
    }

    # Save raw results
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{date_str}.json"
    with open(raw_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\n✓ Raw results saved: {raw_path}")

    # Generate dashboard
    generate_dashboard(result, date_str)

    # Generate priority targets
    generate_priority_targets(result, date_str)

    return result


# ---------------------------------------------------------------------------
# Report Generators
# ---------------------------------------------------------------------------

def generate_dashboard(result: dict, date_str: str):
    """Generate the markdown dashboard from scan results."""
    meta = result["meta"]
    jobs = result["jobs"]

    lines = [
        "# GTM Job Market Scan — Dashboard",
        "",
        f"> Auto-generated: {date_str}",
        f"> Related: GitHub issues #1669, #1670, #1671",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total job postings found | **{meta['total_jobs']}** |",
        f"| Unique companies | **{meta['total_unique_companies']}** |",
        f"| Keywords searched | {meta['keywords_searched']} |",
        f"| Sources queried | {', '.join(meta['sources'].keys())} |",
        "",
        "## Results by Source",
        "",
        "| Source | Count |",
        "|--------|-------|",
    ]

    for source, count in sorted(meta["sources"].items(), key=lambda x: -x[1]):
        lines.append(f"| {source} | {count} |")

    lines.extend([
        "",
        "## Results by Keyword Tier",
        "",
        "| Tier | Description | Count |",
        "|------|-------------|-------|",
    ])

    tier_labels = {
        "tier_1": "Elite niche (OrcaFlex, riser, mooring, hydro)",
        "tier_2": "Strong niche (cathodic, subsea, pipeline, API 579)",
        "tier_3": "Broader fit (FEA, structural, corrosion, DNV)",
        "tier_4": "Manufacturing / wide net (ANSYS, aerospace)",
    }
    for tier_key in ["tier_1", "tier_2", "tier_3", "tier_4"]:
        count = meta["by_tier"].get(tier_key, 0)
        label = tier_labels.get(tier_key, tier_key)
        lines.append(f"| {tier_key.replace('_', ' ').title()} | {label} | {count} |")

    # Top companies
    lines.extend([
        "",
        "## Top Companies by Posting Volume",
        "",
        "| Rank | Company | Postings | Priority Target? |",
        "|------|---------|----------|------------------|",
    ])

    for rank, (company, count) in enumerate(result["company_rankings"].items(), 1):
        if rank > 30:
            break
        is_priority = "✅ YES" if is_priority_company(company) else ""
        lines.append(f"| {rank} | {company} | {count} | {is_priority} |")

    # Top 20 highest-scoring jobs
    lines.extend([
        "",
        "## Top 20 Highest-Scoring Job Postings",
        "",
        "| Score | Title | Company | Location | Source | Keyword |",
        "|-------|-------|---------|----------|--------|---------|",
    ])

    for job in jobs[:20]:
        score = job.get("alignment_score", 0)
        title = job.get("title", "")[:60]
        company = job.get("company", "")[:30]
        location = job.get("location", "")[:20]
        source = job.get("source", "")
        keyword = job.get("search_keyword", "")[:30]
        lines.append(f"| {score} | {title} | {company} | {location} | {source} | {keyword} |")

    # Seniority breakdown
    seniority_counts = Counter(j.get("seniority", "unknown") for j in jobs)
    lines.extend([
        "",
        "## Seniority Breakdown",
        "",
        "| Level | Count | Consulting Fit |",
        "|-------|-------|----------------|",
        f"| Senior | {seniority_counts.get('senior', 0)} | ★★★★★ Best — they need experience NOW |",
        f"| Mid | {seniority_counts.get('mid', 0)} | ★★★☆☆ Good — can pitch senior-level delivery |",
        f"| Junior | {seniority_counts.get('junior', 0)} | ★☆☆☆☆ Low — they want cheap labor |",
        "",
        "---",
        "",
        "*Run `uv run --no-project python scripts/gtm/job-market-scanner.py` to refresh.*",
    ])

    dashboard_path = OUTPUT_DIR / "dashboard.md"
    dashboard_path.write_text("\n".join(lines))
    print(f"✓ Dashboard saved: {dashboard_path}")


def generate_priority_targets(result: dict, date_str: str):
    """Generate the priority targets markdown from scan results."""
    jobs = result["jobs"]

    # Group by company and calculate aggregate scores
    company_data = defaultdict(lambda: {"jobs": [], "total_score": 0, "max_score": 0})
    for job in jobs:
        company = job.get("company", "").strip()
        if not company:
            continue
        company_data[company]["jobs"].append(job)
        company_data[company]["total_score"] += job.get("alignment_score", 0)
        company_data[company]["max_score"] = max(
            company_data[company]["max_score"],
            job.get("alignment_score", 0)
        )

    # Sort by total score
    ranked = sorted(
        company_data.items(),
        key=lambda x: (x[1]["total_score"], x[1]["max_score"]),
        reverse=True
    )

    lines = [
        "# GTM Priority Targets — Ranked Company List",
        "",
        f"> Auto-generated: {date_str}",
        f"> Based on job market scan of {result['meta']['total_jobs']} postings",
        "",
        "## Scoring Method",
        "",
        "Companies ranked by aggregate alignment score across all matching job postings.",
        "Score factors: keyword niche level, seniority, priority company flag, location, contract indicator.",
        "",
        "## Hot Targets (3+ matching roles = very busy = prime consulting lead)",
        "",
        "| Rank | Company | Open Roles | Aggregate Score | Top Score | Top Keywords | Action |",
        "|------|---------|------------|-----------------|-----------|-------------|--------|",
    ]

    hot_count = 0
    for rank, (company, data) in enumerate(ranked, 1):
        if len(data["jobs"]) < 3:
            continue
        hot_count += 1
        keywords = list(set(j["search_keyword"] for j in data["jobs"]))[:3]
        kw_str = ", ".join(keywords)
        lines.append(
            f"| {hot_count} | **{company}** | {len(data['jobs'])} | "
            f"{data['total_score']} | {data['max_score']} | {kw_str} | 📧 Email pitch |"
        )

    if hot_count == 0:
        lines.append("| — | No companies with 3+ matching roles found yet | — | — | — | — | — |")

    lines.extend([
        "",
        "## All Ranked Companies",
        "",
        "| Rank | Company | Roles | Score | Priority? | Keywords |",
        "|------|---------|-------|-------|-----------|----------|",
    ])

    for rank, (company, data) in enumerate(ranked[:50], 1):
        keywords = list(set(j["search_keyword"] for j in data["jobs"]))[:3]
        kw_str = ", ".join(keywords)
        priority = "✅" if is_priority_company(company) else ""
        lines.append(
            f"| {rank} | {company} | {len(data['jobs'])} | "
            f"{data['total_score']} | {priority} | {kw_str} |"
        )

    lines.extend([
        "",
        "## Next Steps",
        "",
        "1. Review hot targets — validate company fit and current project activity",
        "2. Research decision-maker contacts (VP Engineering, Chief Engineer, Director of Projects)",
        "3. Draft personalized emails referencing their specific open roles",
        "4. Execute outreach (see #1669 for templates, #1670 for energy company specifics)",
        "",
        "---",
        "",
        "*Auto-generated by `scripts/gtm/job-market-scanner.py`*",
    ])

    targets_path = OUTPUT_DIR / "priority-targets.md"
    targets_path.write_text("\n".join(lines))
    print(f"✓ Priority targets saved: {targets_path}")


# ---------------------------------------------------------------------------
# History Tracking & Cumulative Index
# ---------------------------------------------------------------------------

CUMULATIVE_PATH = OUTPUT_DIR / "cumulative-index.json"


def enforce_retention_policy(date_str: str) -> dict:
    """Archive raw GTM scan outputs and prune cumulative history beyond retention windows."""
    current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    raw_cutoff = current_date - timedelta(weeks=RAW_RETENTION_WEEKS)
    history_cutoff = current_date - timedelta(days=HISTORY_RETENTION_MONTHS * 30)

    archived_raw_results = 0
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for raw_file in RAW_DIR.glob("*.json"):
        try:
            file_date = datetime.strptime(raw_file.stem, "%Y-%m-%d").date()
        except ValueError:
            continue
        if file_date < raw_cutoff:
            archived_path = ARCHIVE_DIR / raw_file.name
            raw_file.replace(archived_path)
            archived_raw_results += 1

    cumulative = load_cumulative_index()
    cumulative["scan_history"] = [
        entry for entry in cumulative.get("scan_history", [])
        if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= history_cutoff
    ]
    for company, entries in list(cumulative.get("company_history", {}).items()):
        filtered_entries = [
            entry for entry in entries
            if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= history_cutoff
        ]
        if filtered_entries:
            cumulative["company_history"][company] = filtered_entries
        else:
            del cumulative["company_history"][company]

    CUMULATIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CUMULATIVE_PATH, "w") as f:
        json.dump(cumulative, f, indent=2, default=str)

    return {
        "archived_raw_results": archived_raw_results,
        "retained_scan_history": len(cumulative.get("scan_history", [])),
    }


def load_cumulative_index() -> dict:
    """Load the cumulative index of all previously seen jobs."""
    if CUMULATIVE_PATH.exists():
        with open(CUMULATIVE_PATH) as f:
            return json.load(f)
    return {"jobs": {}, "scan_history": [], "company_history": {}}


def update_cumulative_index(result: dict, date_str: str) -> dict:
    """
    Merge new scan results into the cumulative index.
    Returns dict with 'new_jobs' (not seen before) and 'returning_jobs'.
    """
    cumulative = load_cumulative_index()
    new_jobs = []
    returning_jobs = []

    for job in result["jobs"]:
        jid = job_id(
            job["title"],
            job.get("company", ""),
            job.get("location", ""),
            source=job.get("source", ""),
            url=job.get("url", ""),
            posted_date=job.get("posted_date", ""),
        )
        legacy_jid = legacy_job_id(job["title"], job.get("company", ""), job.get("location", ""))
        existing_jid = jid if jid in cumulative["jobs"] else legacy_jid if legacy_jid in cumulative["jobs"] else None

        if existing_jid:
            # Seen before — update last_seen and migrate legacy key if needed
            record = cumulative["jobs"].pop(existing_jid)
            record["title"] = job["title"]
            record["company"] = job.get("company", "")
            record["location"] = job.get("location", "")
            record["source"] = job.get("source", "")
            record["url"] = job.get("url", "")
            record["posted_date"] = job.get("posted_date", "")
            record["search_keyword"] = job.get("search_keyword", "")
            record["alignment_score"] = job.get("alignment_score", 0)
            record["last_seen"] = date_str
            record["seen_count"] = record.get("seen_count", 1) + 1
            cumulative["jobs"][jid] = record
            returning_jobs.append(job)
        else:
            # New job!
            cumulative["jobs"][jid] = {
                "title": job["title"],
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "source": job.get("source", ""),
                "url": job.get("url", ""),
                "posted_date": job.get("posted_date", ""),
                "search_keyword": job.get("search_keyword", ""),
                "alignment_score": job.get("alignment_score", 0),
                "first_seen": date_str,
                "last_seen": date_str,
                "seen_count": 1,
            }
            new_jobs.append(job)

    # Update company history (track posting counts over time)
    company_counts = Counter(j.get("company", "") for j in result["jobs"] if j.get("company"))
    for company, count in company_counts.items():
        if company not in cumulative["company_history"]:
            cumulative["company_history"][company] = []
        cumulative["company_history"][company].append({
            "date": date_str,
            "count": count,
        })

    # Record scan metadata
    cumulative["scan_history"].append({
        "date": date_str,
        "total_jobs": result["meta"]["total_jobs"],
        "new_jobs": len(new_jobs),
        "returning_jobs": len(returning_jobs),
        "unique_companies": result["meta"]["total_unique_companies"],
    })

    # Save
    CUMULATIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CUMULATIVE_PATH, "w") as f:
        json.dump(cumulative, f, indent=2, default=str)
    print(f"✓ Cumulative index saved: {CUMULATIVE_PATH}")
    print(f"  All-time jobs tracked: {len(cumulative['jobs'])}")
    print(f"  New this scan: {len(new_jobs)}")
    print(f"  Returning: {len(returning_jobs)}")

    return {
        "new_jobs": new_jobs,
        "returning_jobs": returning_jobs,
        "cumulative": cumulative,
    }


def generate_new_this_week(new_jobs: list[dict], date_str: str):
    """Generate markdown report of NEW postings since last scan."""
    lines = [
        "# New Job Postings This Week",
        "",
        f"> Scan date: {date_str}",
        f"> New postings not seen in any previous scan",
        "",
        f"## Summary: {len(new_jobs)} new postings found",
        "",
    ]

    if not new_jobs:
        lines.append("No new postings this week. All results were seen in previous scans.")
    else:
        # Group by tier
        by_tier = defaultdict(list)
        for job in new_jobs:
            tier = job.get("keyword_tier", 4)
            by_tier[tier].append(job)

        tier_labels = {
            1: "Tier 1 — Elite Niche (OrcaFlex, riser, mooring)",
            2: "Tier 2 — Strong Niche (cathodic, subsea, pipeline)",
            3: "Tier 3 — Broader Fit (FEA, structural, corrosion)",
            4: "Tier 4 — Manufacturing / Wide Net",
        }

        for tier in sorted(by_tier.keys()):
            jobs = sorted(by_tier[tier], key=lambda j: j.get("alignment_score", 0), reverse=True)
            lines.extend([
                f"### {tier_labels.get(tier, f'Tier {tier}')} ({len(jobs)} new)",
                "",
                "| Score | Title | Company | Location | Source | Keyword |",
                "|-------|-------|---------|----------|--------|---------|",
            ])
            for job in jobs[:20]:  # Cap at 20 per tier
                score = job.get("alignment_score", 0)
                title = job.get("title", "")[:60]
                company = job.get("company", "")[:30]
                location = job.get("location", "")[:20]
                source = job.get("source", "")
                keyword = job.get("search_keyword", "")[:30]
                lines.append(f"| {score} | {title} | {company} | {location} | {source} | {keyword} |")
            lines.append("")

        # New companies this week
        new_companies = set(j.get("company", "") for j in new_jobs if j.get("company"))
        if new_companies:
            lines.extend([
                "## New Companies This Week",
                "",
                f"**{len(new_companies)} companies** appeared for the first time:",
                "",
            ])
            for c in sorted(new_companies):
                count = sum(1 for j in new_jobs if j.get("company") == c)
                priority = " ✅ PRIORITY" if is_priority_company(c) else ""
                lines.append(f"- **{c}** ({count} roles){priority}")
            lines.append("")

    lines.extend([
        "---",
        "",
        "*Auto-generated by `scripts/gtm/job-market-scanner.py`*",
    ])

    path = OUTPUT_DIR / "new-this-week.md"
    path.write_text("\n".join(lines))
    print(f"✓ New-this-week report saved: {path}")


def generate_trend_report(cumulative: dict, date_str: str):
    """Generate week-over-week trend report showing company hiring momentum."""
    scan_history = cumulative.get("scan_history", [])
    company_history = cumulative.get("company_history", {})

    lines = [
        "# GTM Trend Report — Week-over-Week Hiring Momentum",
        "",
        f"> Generated: {date_str}",
        f"> Total scans to date: {len(scan_history)}",
        "",
    ]

    # Scan history table
    if len(scan_history) > 1:
        lines.extend([
            "## Scan History",
            "",
            "| Date | Total Jobs | New | Returning | Companies |",
            "|------|-----------|-----|-----------|-----------|",
        ])
        for scan in scan_history[-10:]:  # Last 10 scans
            lines.append(
                f"| {scan['date']} | {scan['total_jobs']} | "
                f"{scan['new_jobs']} | {scan['returning_jobs']} | "
                f"{scan['unique_companies']} |"
            )
        lines.append("")

    # Trending companies (hiring more over time)
    if company_history:
        trending_up = []
        trending_stable = []

        for company, history in company_history.items():
            if len(history) < 2:
                continue
            latest = history[-1]["count"]
            previous = history[-2]["count"]
            delta = latest - previous
            if delta > 0:
                trending_up.append((company, latest, previous, delta))
            elif delta == 0 and latest >= 3:
                trending_stable.append((company, latest))

        if trending_up:
            trending_up.sort(key=lambda x: x[3], reverse=True)
            lines.extend([
                "## 📈 Trending UP — Companies Hiring MORE This Week",
                "",
                "These companies have MORE open roles than last scan — they are getting busier.",
                "**These are your highest-priority outreach targets.**",
                "",
                "| Company | This Week | Last Week | Change | Priority? |",
                "|---------|-----------|-----------|--------|-----------|",
            ])
            for company, latest, previous, delta in trending_up[:20]:
                priority = "✅" if is_priority_company(company) else ""
                lines.append(f"| **{company}** | {latest} | {previous} | +{delta} | {priority} |")
            lines.append("")

        if trending_stable:
            trending_stable.sort(key=lambda x: x[1], reverse=True)
            lines.extend([
                "## ➡️ Consistently Busy — Stable High Hiring",
                "",
                "| Company | Roles (stable) | Priority? |",
                "|---------|---------------|-----------|",
            ])
            for company, count in trending_stable[:15]:
                priority = "✅" if is_priority_company(company) else ""
                lines.append(f"| {company} | {count} | {priority} |")
            lines.append("")

    # Long-running openings (seen in multiple scans = hard to fill = consulting gold)
    all_jobs = cumulative.get("jobs", {})
    persistent = [(jid, data) for jid, data in all_jobs.items()
                  if data.get("seen_count", 1) >= 2]
    if persistent:
        persistent.sort(key=lambda x: x[1].get("seen_count", 1), reverse=True)
        lines.extend([
            "## 🔥 Persistent Openings — Hard to Fill = Consulting Gold",
            "",
            "These jobs have appeared in multiple scans. The company CANNOT fill them.",
            "They are the most likely to accept a consulting alternative.",
            "",
            "| Weeks Seen | Title | Company | Score | First Seen |",
            "|------------|-------|---------|-------|------------|",
        ])
        for jid, data in persistent[:25]:
            lines.append(
                f"| {data.get('seen_count', 1)} | {data['title'][:50]} | "
                f"{data['company'][:25]} | {data.get('alignment_score', 0)} | "
                f"{data.get('first_seen', '?')} |"
            )
        lines.append("")

    # All-time stats
    total_unique = len(all_jobs)
    total_companies = len(set(d.get("company", "") for d in all_jobs.values() if d.get("company")))
    lines.extend([
        "## Cumulative Statistics",
        "",
        f"- **{total_unique}** unique job postings tracked all-time",
        f"- **{total_companies}** unique companies seen",
        f"- **{len(scan_history)}** scans completed",
        "",
        "---",
        "",
        "*Auto-generated by `scripts/gtm/job-market-scanner.py`*",
    ])

    path = OUTPUT_DIR / "trend-report.md"
    path.write_text("\n".join(lines))
    print(f"✓ Trend report saved: {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GTM Job Market Scanner — ACE Engineer")
    parser.add_argument("--keywords", type=str, default=None,
                       help="Comma-separated keywords to search (default: all)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of keywords to scan")
    parser.add_argument("--skip-career-pages", action="store_true",
                       help="Skip company career page scanning")
    parser.add_argument("--output-dir", type=str, default=None,
                       help="Override output directory")
    parser.add_argument("--refresh", action="store_true",
                       help="Weekly refresh mode — runs full scan with history tracking")

    args = parser.parse_args()

    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]

    if args.output_dir:
        global OUTPUT_DIR, RAW_DIR, KEYWORD_DIR, PROFILE_DIR, CUMULATIVE_PATH
        OUTPUT_DIR = Path(args.output_dir)
        RAW_DIR = OUTPUT_DIR / "raw-results"
        KEYWORD_DIR = OUTPUT_DIR / "keyword-results"
        PROFILE_DIR = OUTPUT_DIR / "company-profiles"
        CUMULATIVE_PATH = OUTPUT_DIR / "cumulative-index.json"

    result = run_scan(
        keywords=keywords,
        limit=args.limit,
        skip_career_pages=args.skip_career_pages,
    )

    # Always update cumulative index and generate delta reports
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = update_cumulative_index(result, date_str)
    retention = enforce_retention_policy(date_str)
    generate_new_this_week(history["new_jobs"], date_str)
    generate_trend_report(history["cumulative"], date_str)

    print(f"  Raw archives moved: {retention['archived_raw_results']}")

    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE")
    print(f"  Total jobs found:  {result['meta']['total_jobs']}")
    print(f"  Unique companies:  {result['meta']['total_unique_companies']}")
    print(f"  NEW this scan:     {len(history['new_jobs'])}")
    print(f"  Returning:         {len(history['returning_jobs'])}")
    print(f"  All-time tracked:  {len(history['cumulative']['jobs'])}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
