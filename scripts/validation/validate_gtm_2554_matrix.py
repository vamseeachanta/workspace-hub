#!/usr/bin/env python3
"""Validate issue #2554 GTM vessel-contractor matrix artifacts.

The gate intentionally validates only repository-public artifacts. It parses the
Markdown scaffold as the source of truth, derives semantic target counts, checks
required row fields, compares generated counts to the scaffold/summary count
claims, and screens for public-contact leakage patterns.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
MIN_LIVE_TARGETS = 20
DISALLOWED_EVIDENCE_HOSTS = {"github.com", "linkedin.com", "wikipedia.org", "facebook.com", "x.com", "twitter.com"}
SCAFFOLD = ROOT / "docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md"
PLAN = ROOT / "docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md"
SUMMARY = ROOT / "docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md"
SCAN = ROOT / "docs/reports/gtm/legal-scans/2026-04-30-issue-2554-public-matrix-scan.md"
DENY = ROOT / ".legal-deny-list.yaml"

REQUIRED_FIELDS = [
    "company",
    "tier_seed",
    "tier_revised",
    "segment",
    "relevant_fleet",
    "demo_anchor",
    "pain_point_hypothesis",
    "corporate_root_evidence",
    "deep_link_evidence",
    "pain_point_evidence",
    "can_say_now",
    "cannot_claim_yet",
    "outreach_priority",
    "private_route",
]

CONTACT_REGEXES = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}(?!\d)"),
    "individual_linkedin": re.compile(r"https?://(?:www\.)?linkedin\.com/in/[^\s)]+"),
    "named_person_with_title": re.compile(
        r"\b(?:CEO|CTO|CFO|COO|VP|Vice President|Director|Manager|Lead|Engineer)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b|"
        r"\b[A-Z][a-z]+\s+[A-Z][a-z]+,\s*(?:CEO|CTO|CFO|COO|VP|Vice President|Director|Manager|Lead|Engineer)\b"
    ),
}


def parse_field(body: str, field: str) -> str:
    match = re.search(rf"^- \*\*{re.escape(field)}\.\*\*\s*(.*)$", body, re.M)
    return match.group(1).strip() if match else ""


def parse_rows(scaffold: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for match in re.finditer(r"^### Target (\d+) — (.+?)\n(.*?)(?=^### Target |^---\n\n## Summary Counts|\Z)", scaffold, re.M | re.S):
        target = int(match.group(1))
        title = match.group(2).strip()
        body = match.group(3)
        fields = {field: parse_field(body, field) for field in REQUIRED_FIELDS}
        priority_text = re.sub(r"[*`]", "", fields["outreach_priority"]).split("—", 1)[0].strip()
        priority = re.match(r"[A-Za-z]+", priority_text).group(0) if re.match(r"[A-Za-z]+", priority_text) else priority_text
        lower = f"{title}\n{body}".lower()
        exclusions: list[str] = []
        if "legacy" in title.lower() or "deprecated" in lower:
            exclusions.append("legacy/deprecated")
        if priority.lower().startswith("defer"):
            exclusions.append("defer")
        if "partner-shape" in lower or "not a vessel-fleet target" in lower or "non-counted for the vessel-contractor minimum" in lower:
            exclusions.append("explicit non-counted partner-shape")
        if "wind-only; excluded from live_countable until fowt worked example" in lower:
            exclusions.append("wind-only pending FOWT worked example")
        missing = [field for field, value in fields.items() if not value]
        if exclusions:
            missing = []
        rows.append(
            {
                "target": target,
                "title": title,
                "priority": priority,
                "status": ", ".join(exclusions) or "counted",
                "counted": not exclusions,
                "fields": fields,
                "missing_fields": missing,
            }
        )
    return rows


def deny_patterns() -> list[tuple[str, bool]]:
    patterns: list[tuple[str, bool]] = []
    if DENY.exists():
        for match in re.finditer(r'pattern: "(.*?)"\n\s+case_sensitive: (true|false)', DENY.read_text()):
            patterns.append((match.group(1), match.group(2) == "true"))
    return patterns


def scan_contacts(files: list[Path]) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    deny_hits: list[tuple[str, str]] = []
    contact_hits: list[tuple[str, str, str]] = []
    patterns = deny_patterns()
    for path in files:
        text = path.read_text()
        for pattern, case_sensitive in patterns:
            haystack = text if case_sensitive else text.lower()
            needle = pattern if case_sensitive else pattern.lower()
            if needle in haystack:
                deny_hits.append((str(path.relative_to(ROOT)), pattern))
        for name, regex in CONTACT_REGEXES.items():
            for match in regex.finditer(text):
                contact_hits.append((str(path.relative_to(ROOT)), name, match.group(0)[:100]))
    return deny_hits, contact_hits


def extract_int(pattern: str, text: str, label: str) -> tuple[int | None, str | None]:
    match = re.search(pattern, text, re.I | re.S)
    if not match:
        return None, f"missing count claim: {label}"
    return int(match.group(1)), None


def count_claims(scaffold: str, summary: str) -> tuple[dict[str, int | None], list[str]]:
    errors: list[str] = []
    claims: dict[str, int | None] = {}
    patterns = {
        "scaffold_live": (r"Live countable vessel/operator targets[^\n]*:\*\*\s*(\d+)", scaffold),
        "scaffold_high": (r"Targets in `outreach_priority: High`[^\n]*:\*\*\s*(\d+)", scaffold),
        "summary_live": (r"\*\*(\d+) live countable vessel/operator targets\*\*", summary),
        "summary_high": (r"High-priority rows?:[^\n]*?\*\*\s*(\d+)|\*\*(\d+) High-priority rows\*\*|\n-\s*(\d+)\s+High-priority targets", summary),
    }
    for key, (pattern, text) in patterns.items():
        match = re.search(pattern, text, re.I | re.S)
        if not match:
            claims[key] = None
            errors.append(f"missing count claim: {key}")
            continue
        value = next((g for g in match.groups() if g), None)
        claims[key] = int(value) if value else None
    return claims, errors



def extract_urls(text: str) -> list[str]:
    return re.findall(r"https://[^\s);]+", text)


def evidence_urls_are_allowed(text: str) -> bool:
    urls = extract_urls(text)
    if not urls:
        return False
    for url in urls:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        if any(host == disallowed or host.endswith("." + disallowed) for disallowed in DISALLOWED_EVIDENCE_HOSTS):
            return False
    return True


def high_deep_link_is_bounded(text: str) -> bool:
    lower = text.lower()
    if "pending" in lower:
        return False
    if "no-public-proof-found" in lower or "access-boundary" in lower or "official-site" in lower:
        return True
    return evidence_urls_are_allowed(text) and "official" in lower

def validate(rows: list[dict[str, object]], scaffold: str, summary: str, deny_hits: list[tuple[str, str]], contact_hits: list[tuple[str, str, str]]) -> list[str]:
    errors: list[str] = []
    live_count = sum(1 for row in rows if row["counted"])
    high_count = sum(1 for row in rows if row["priority"] == "High")
    claims, claim_errors = count_claims(scaffold, summary)
    errors.extend(claim_errors)
    for key, value in claims.items():
        expected = live_count if key.endswith("live") else high_count
        if value is not None and value != expected:
            errors.append(f"{key}={value} does not match derived {expected}")
    if live_count < MIN_LIVE_TARGETS:
        errors.append(f"live_countable={live_count} is below {MIN_LIVE_TARGETS}")
    if deny_hits:
        errors.append(f"deny_hits={len(deny_hits)}")
    if contact_hits:
        errors.append(f"contact_hits={len(contact_hits)}")
    for row in rows:
        missing = row["missing_fields"]
        if missing:
            errors.append(f"target {row['target']} missing required fields: {', '.join(missing)}")
        fields = row["fields"]
        if row["counted"] and not evidence_urls_are_allowed(str(fields["corporate_root_evidence"])):
            errors.append(f"target {row['target']} counted row lacks allowed public corporate_root_evidence URL")
        if row["counted"] and not str(fields["deep_link_evidence"]).strip():
            errors.append(f"target {row['target']} counted row lacks populated deep_link_evidence or explicit boundary")
        if row["priority"] == "High" and not high_deep_link_is_bounded(str(fields["deep_link_evidence"])):
            errors.append(f"target {row['target']} High row lacks official-domain deep_link_evidence or bounded no-public-proof/access note")
        if row["priority"] == "High" and not str(fields["private_route"]).lower().startswith("omitted-public-artifact"):
            errors.append(f"target {row['target']} High row must keep private_route omitted-public-artifact")
    return errors


def render_scan(rows: list[dict[str, object]], deny_hits: list[tuple[str, str]], contact_hits: list[tuple[str, str, str]], errors: list[str]) -> str:
    live_count = sum(1 for row in rows if row["counted"])
    high_count = sum(1 for row in rows if row["priority"] == "High")
    table = "\n".join(
        f"| {idx} | {row['target']} | {row['title']} | {row['priority']} | {row['status']} | {', '.join(row['missing_fields']) or 'none'} |"
        for idx, row in enumerate(rows, 1)
    )
    deny = "- none" if not deny_hits else "\n".join(f"- `{path}`: `{pattern}`" for path, pattern in deny_hits)
    contacts = "- none" if not contact_hits else "\n".join(f"- `{path}`: {kind} `{value}`" for path, kind, value in contact_hits)
    status = "PASS" if not errors else "FAIL"
    error_text = "- none" if not errors else "\n".join(f"- {error}" for error in errors)
    return f"""# Legal/privacy and semantic-count validation — issue #2554 public matrix

Status: **{status}**
Date: 2026-04-30
Generator: `uv run python scripts/validation/validate_gtm_2554_matrix.py --write-artifact`
Scope:
- `docs/plans/2026-04-29-issue-2554-vessel-contractor-outreach-matrix.md`
- `docs/reports/gtm/2026-04-29-vessel-contractor-outreach-matrix-scaffold.md`
- `docs/plans/overnight-prompts/2026-04-29-weekly-gtm-targets/results/issue-2554-summary.md`

## Why this exists

The r1 post-fill review found that `scripts/legal/legal-sanity-scan.sh --diff-only` can false-pass once the matrix files are already committed. This artifact is generated from the scaffold and targeted committed files so #2554 promotion does not depend on an empty diff or hand-counted rows.

## Results

- Legal deny-list fixed-string hits: {len(deny_hits)}
- Contact-pattern hits (email, phone-like, individual LinkedIn URL, simple named-person-with-title pattern): {len(contact_hits)}
- Semantic live/countable vessel/operator target count: {live_count}
- High-priority row count: {high_count}

## Validation errors

{error_text}

## Legal deny-list hits

{deny}

## Contact-pattern hits

{contacts}

## Semantic target inventory (visual rows are contiguous; original target heading preserved)

| Row | Target heading | Title | Priority | Count status | Missing required fields |
|---:|---:|---|---|---|---|
{table}

## Promotion note

This scan does not authorize outreach or send. It supports the #2554 plan-review promotion gate by parsing the scaffold, deriving live/countable and High-priority counts, checking required row fields, rejecting disallowed evidence URL hosts, comparing count claims across artifacts, and screening direct contact leakage patterns. Manual public/private boundary review remains required for semantic named-person leakage that no regex can prove exhaustively.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-artifact", action="store_true")
    args = parser.parse_args()
    scaffold = SCAFFOLD.read_text()
    summary = SUMMARY.read_text()
    rows = parse_rows(scaffold)
    deny_hits, contact_hits = scan_contacts([PLAN, SCAFFOLD, SUMMARY])
    errors = validate(rows, scaffold, summary, deny_hits, contact_hits)
    output = render_scan(rows, deny_hits, contact_hits, errors)
    if args.write_artifact:
        SCAN.write_text(output)
    live_count = sum(1 for row in rows if row["counted"])
    high_count = sum(1 for row in rows if row["priority"] == "High")
    print(f"status={'PASS' if not errors else 'FAIL'} live_countable={live_count} high={high_count} deny_hits={len(deny_hits)} contact_hits={len(contact_hits)} errors={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
