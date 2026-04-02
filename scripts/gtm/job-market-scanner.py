#!/usr/bin/env python3
"""
GTM Job Market Scanner — ACE Engineer
======================================
Scans multiple job boards and Google for engineering roles matching
ACE Engineer's capabilities. Produces structured JSON results and
a markdown dashboard.

Usage:
    python scripts/gtm/job-market-scanner.py [--keywords KEY1,KEY2] [--limit N]

Output:
    docs/strategy/gtm/job-market-scan/raw-results/YYYY-MM-DD.json
    docs/strategy/gtm/job-market-scan/dashboard.md
    docs/strategy/gtm/job-market-scan/priority-targets.md

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
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "strategy" / "gtm" / "job-market-scan"
RAW_DIR = OUTPUT_DIR / "raw-results"
KEYWORD_DIR = OUTPUT_DIR / "keyword-results"
PROFILE_DIR = OUTPUT_DIR / "company-profiles"

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

# Rate limiting
REQUEST_DELAY = 2.0  # seconds between requests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_request(url: str, params: dict | None = None, timeout: int = 15) -> requests.Response | None:
    """Make a rate-limited HTTP request with error handling."""
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        print(f"  [WARN] Request failed: {e}")
        return None


def job_id(title: str, company: str, location: str) -> str:
    """Generate a unique ID for deduplication."""
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
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

    resp = safe_request(url, params)
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

    resp = safe_request(url)
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

    resp = safe_request(url)
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

    resp = safe_request(url, params)
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

    resp = safe_request(url, params)
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

    resp = safe_request(url)
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

            jid = job_id(job["title"], job.get("company", ""), job.get("location", ""))
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

                jid = job_id(job["title"], job.get("company", ""), job.get("location", ""))
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

    args = parser.parse_args()

    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]

    if args.output_dir:
        global OUTPUT_DIR, RAW_DIR, KEYWORD_DIR, PROFILE_DIR
        OUTPUT_DIR = Path(args.output_dir)
        RAW_DIR = OUTPUT_DIR / "raw-results"
        KEYWORD_DIR = OUTPUT_DIR / "keyword-results"
        PROFILE_DIR = OUTPUT_DIR / "company-profiles"

    result = run_scan(
        keywords=keywords,
        limit=args.limit,
        skip_career_pages=args.skip_career_pages,
    )

    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE")
    print(f"  Total jobs found: {result['meta']['total_jobs']}")
    print(f"  Unique companies: {result['meta']['total_unique_companies']}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
