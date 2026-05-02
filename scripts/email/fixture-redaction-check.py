#!/usr/bin/env python3
"""Reject real PII in committed email fixtures."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "test.invalid",
    "user.test",
}
KNOWN_DOMAINS = {
    "aceengineer.com",
    "achantav@gmail.com",
    "skestatesinc@gmail.com",
}

EMAIL_RE = re.compile(r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")
STREET_RE = re.compile(
    r"\b\d{2,6}\s+[A-Za-z0-9.'-]+(?:\s+[A-Za-z0-9.'-]+){0,4}\s+"
    r"(?:st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|boulevard|ct|court)\b",
    re.IGNORECASE,
)


def violations_for_text(text: str) -> list[str]:
    violations: list[str] = []

    for match in EMAIL_RE.finditer(text):
        email = match.group(0).lower()
        domain = match.group(1).lower()
        if domain in PLACEHOLDER_DOMAINS or any(
            domain.endswith(f".{placeholder}") for placeholder in PLACEHOLDER_DOMAINS
        ):
            continue
        if domain in KNOWN_DOMAINS or email in KNOWN_DOMAINS:
            violations.append("real email/domain")
        else:
            violations.append("real email/domain")

    if PHONE_RE.search(text):
        violations.append("phone number")
    if STREET_RE.search(text):
        violations.append("street address")

    return sorted(set(violations))


def main(argv: list[str]) -> int:
    failed = False
    for raw_path in argv[1:]:
        path = Path(raw_path)
        text = path.read_text(encoding="utf-8")
        violations = violations_for_text(text)
        if violations:
            failed = True
            print(f"{path}: fixture contains {', '.join(violations)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
