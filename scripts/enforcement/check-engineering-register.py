#!/usr/bin/env python3
"""Level-2 check: engineering register compliance.

Enforces the register recorded in `config/agents/SHARED_SOUL.md` and detailed in
`llm-wiki` engineering/concepts/engineering-report-house-style, which was derived
by reading our own issued reports rather than by prescription.

Checks are deliberately narrow. Every rule here is one the corpus settles and a
regular expression can decide; register rules that need judgement are listed in
the guide and are not checked. A linter that guesses trains people to ignore it.

    check-engineering-register.py PATH [PATH ...]
    check-engineering-register.py --self-test

Exit 0 when clean, 1 on any violation, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Regions that are not prose: fenced code, inline code, link targets, frontmatter,
# and the guide's own quoted exemplars.
_FENCE = re.compile(r"^```", re.M)
_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_INLINE = re.compile(r"`[^`\n]*`")
_LINK = re.compile(r"\]\([^)]*\)")
_QUOTE = re.compile(r"^\s*>.*$", re.M)
# A list item consisting solely of a quoted phrase is a citation -- a style guide
# must be able to list the constructions it bans without tripping its own linter.
_QUOTED_ITEM = re.compile(r"^\s*[-*]\s*[\"\u201c\u2018'].{0,120}?[\"\u201d\u2019'\u2026]\s*$", re.M)
# Explicit suppression, for a line that must contain an example.
_SUPPRESSED = re.compile(r"^.*<!--\s*register-lint:\s*ignore\s*-->.*$", re.M)
# Bare URLs and paths are identifiers. "noblecorp.com/our-fleet" is not
# first-person plural, and markdown-link exemption alone does not cover a URL
# written in running text.
_URL = re.compile(r"(?:https?://|www\.)\S+|\b[\w.-]+\.(?:com|org|net|gov|io|ai)/\S*", re.I)
# A short inline quotation is citation, not the author's prose -- a page may quote
# the directive that founded it without adopting its register.
_INLINE_QUOTE = re.compile(r"[\u201c\"][^\u201d\"\n]{0,200}[\u201d\"]")


def prose_only(text: str) -> str:
    """Blank non-prose regions, preserving offsets so line numbers stay true."""
    def blank(m: re.Match) -> str:
        return re.sub(r"\S", " ", m.group(0))

    out = _FRONTMATTER.sub(blank, text)
    fences = [m.start() for m in _FENCE.finditer(out)]
    for a, b in zip(fences[0::2], fences[1::2]):
        end = out.find("\n", b)
        end = len(out) if end == -1 else end
        out = out[:a] + re.sub(r"\S", " ", out[a:end]) + out[end:]
    for pat in (_INLINE, _LINK, _URL, _INLINE_QUOTE, _QUOTE, _QUOTED_ITEM, _SUPPRESSED):
        out = pat.sub(blank, out)
    return out


@dataclass(frozen=True)
class Rule:
    code: str
    pattern: re.Pattern[str]
    message: str


# Constructions the issued corpus never uses. Each is a phrase, not a word, so
# ordinary technical prose does not trip them.
BANNED = [
    (r"\bI think\b|\bin my opinion\b|\bI believe\b", "first-person opinion"),
    # Negated forms are excluded here and handled by HEDGE below. "Not obviously
    # correct" asserts the OPPOSITE of an intensifier: it admits something is
    # unproven, which is what the register asks for. Flagging the admission while
    # passing the bare assertion "X is correct" inverts the rule.
    (r"(?<!not )(?<!n't )(?<!nor )\bobviously\b"
     r"|(?<!not )\bclearly,"
     r"|(?<!not )\bdefinitely\b", "unsupported intensifier"),
    (r"\bworld[- ]class\b|\bbest[- ]in[- ]class\b|\bvalue[- ]add\b"
     r"|\bactionable insights?\b|\bholistic approach\b|\btransformative\b"
     r"|\bgame changer\b|\bstrategic roadmap\b", "marketing register"),
    (r"\bthe (?:analysis|data|results?) proves?\b", "overclaim; use indicates or supports"),
    (r"\bthe results speak for themselves\b", "assertion without result"),
    (r"\bit is exciting\b|\bwe are excited\b", "enthusiasm in place of a result"),
]

RULES: list[Rule] = [
    Rule(f"R1.{i}", re.compile(p, re.I), f"excluded construction: {why}")
    for i, (p, why) in enumerate(BANNED, 1)
]

# shall/must used for advice rather than for a requirement.
ADVICE_MODAL = re.compile(
    r"\bit (?:is|shall be) recommended that .{0,120}?\b(?:shall|must)\b"
    r"|\bwe (?:shall|must) (?:consider|look|review|explore)\b", re.I)

# "acceptable"/"conservative"/"safe" with no criterion nearby.
# The criterion may be named ("against the allowable"), cited ("per Reference [2]"),
# or simply explained in the clause that follows. The first version of this rule
# recognised only the first two forms and flagged two pages that had in fact given
# their reason -- "contained by the second" and "analogous to a screen-out". A
# justification is a justification whatever vocabulary carries it.
_CRITERION = (r"against|per\b|criteri|limit|threshold|allowable|basis|code|standard"
              r"|because|since|as it|Reference|Table|Section|by design|in that")
UNSUPPORTED = re.compile(
    r"\b(?:is|are|remains?|were)\s+(acceptable|conservative|safe)\b"
    r"(?!\s*(?:[-\u2013\u2014:;,]|\band\b|\bwhich\b|\bbut\b))"      # an explanation follows
    rf"(?![^.]{{0,160}}(?:{_CRITERION}))",
    re.I)

# A hedge is honest but weak when it names no criterion. This is a separate
# finding from an unsupported intensifier because the remedy differs: supply the
# criterion, do not delete the word. Raised by ws-8c against llm-wiki-risersintl,
# where three of four "obviously" hits were the negated form.
# The justification may follow anywhere in the sentence, not immediately after the
# hedge: "does not obviously fit behind it: the long-lead items exceed the window"
# explains itself four words later. Scan the remainder of the sentence for a named
# criterion or an explanatory mark.
HEDGE = re.compile(
    r"\b(?:not|n't|nor)\s+(?:obviously|clearly|evidently|necessarily)\b"
    rf"(?![^.]{{0,200}}(?:{_CRITERION}|[:\u2013\u2014]))",
    re.I)

# Caption placed above its table rather than below it.
CAPTION_ABOVE = re.compile(r"^\s*(?:Table|Figure)\s+\d+[.\-]\d+\s*[-–:].*\n\s*\|", re.M)


# First-person plural. The rule applies to every document, including internal
# working records: "the survey records", not "we recorded". The single exemption
# is the proposal genre, where the corpus itself uses first-person plural --
# "2H are considered to be particularly well qualified". That exemption is
# corpus-evidenced, not a convenience.
FIRST_PERSON = re.compile(r"\b(?:we|our|us)\b(?!\s*[\u2019']s\b)", re.I)
PROPOSAL_MARKERS = ("proposal", "-prp-", "-pro-", "qualification", "capability-statement")


def is_proposal(path: Path, head: str) -> bool:
    posix = path.as_posix().lower()
    if any(m in posix for m in PROPOSAL_MARKERS):
        return True
    return bool(re.search(r"^(?:type|document_type|genre)\s*:\s*(?:proposal|qualification)",
                          head, re.M | re.I))


# Verbatim transcriptions of third-party material are not our prose. Linting a
# standard's own wording for register produced 1,489 findings on first run, none
# of them actionable, which is exactly how a linter teaches people to ignore it.
TRANSCRIBED_DIRS = ("/standards/", "/papers/", "/sources/", "/datasets/papers/",
                    "/corpus/", "/extracted/", "/raw/", "/_archive/", "/vendor/")
TRANSCRIBED_NAMES = ("full-text", "-ocr.", "verbatim", "transcript")


def is_transcribed(path: Path) -> bool:
    posix = path.as_posix()
    if any(d in posix for d in TRANSCRIBED_DIRS):
        return True
    if any(n in path.name.lower() for n in TRANSCRIBED_NAMES):
        return True
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:600]
    except OSError:
        return False
    return bool(re.search(r"^(?:extraction|provenance|verbatim)\s*:\s*(?:true|verbatim)",
                          head, re.M | re.I))


def check(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = prose_only(raw)
    out: list[str] = []

    def report(pos: int, code: str, msg: str, hit: str) -> None:
        out.append(f"{path}:{raw.count(chr(10), 0, pos) + 1}: [{code}] {msg} — {hit!r}")

    for rule in RULES:
        for m in rule.pattern.finditer(text):
            report(m.start(), rule.code, rule.message, m.group(0))
    for m in ADVICE_MODAL.finditer(text):
        report(m.start(), "R2", "shall/must used for advice; use should or is recommended",
               m.group(0)[:60])
    for m in UNSUPPORTED.finditer(text):
        report(m.start(), "R3", f"{m.group(1)!r} without its governing criterion",
               m.group(0)[:60])
    for m in HEDGE.finditer(text):
        report(m.start(), "R5", "hedge without a criterion; supply the criterion rather "
               "than remove the hedge", m.group(0)[:60])
    if not is_proposal(path, raw[:600]):
        for m in FIRST_PERSON.finditer(text):
            # "US" is the country, not first-person plural. Matching it case-
            # insensitively turned "US Outer Continental Shelf" into a register
            # violation and inflated the backlog several-fold on first run.
            if m.group(0) == "US":
                continue
            report(m.start(), "R6", "first-person plural outside a proposal; the subject "
                   "is the analysis, record or practice", m.group(0))
    for m in CAPTION_ABOVE.finditer(text):
        report(m.start(), "R4", "caption placed above its table; captions sit below",
               m.group(0).split("\n")[0][:60])
    return out


SELF_TEST = {
    "clean": ("The analysis is performed in accordance with Reference [2]. The maximum "
              "allowable working pressure is 2,850 psi, which exceeds the design pressure "
              "of 2,220 psi. Remaining life is not established; the corrosion rate is to be "
              "obtained from a further campaign.\n", 0),
    "opinion": ("I think the joint is fine.\n", 1),
    "intensifier": ("The result is obviously acceptable against the criterion in Table 4.1.\n", 1),
    "marketing": ("This provides actionable insights for the client.\n", 1),
    "overclaim": ("The analysis proves the string is fit for service.\n", 1),
    "advice_modal": ("It is recommended that the operator must reface the connection.\n", 1),
    "unsupported": ("The assessed wall thickness is conservative.\n", 1),
    "criterion_named": ("The result is acceptable against the allowable in Table 4.1.\n", 0),
    "criterion_explained": ("The approach is conservative: any single failure is "
                            "contained by the second barrier.\n", 0),
    "criterion_clause": ("The value is conservative and analogous to a screen-out.\n", 0),
    "caption_above": ("Table 4.1 – Wall thickness\n| a | b |\n|---|---|\n", 1),
    # Negated intensifier is a hedge, not an intensifier (ws-8c, llm-wiki-risersintl).
    "negated_with_criterion": ("X80 is not obviously correct because the mill "
                                "certificate is absent.\n", 0),
    "negated_explained": ("Manufacture does not obviously fit behind it: the long-lead "
                           "items exceed the window.\n", 0),
    "negated_bare": ("The grade is not obviously correct.\n", 1),
    "bare_intensifier_still_caught": ("This entire file, obviously.\n", 1),
    "quoted_exemplar_exempt": ("> I think the joint is fine.\n", 0),
    "code_exempt": ("```\nI think this is fine\n```\n", 0),
    "quoted_list_item_exempt": ('- "It is exciting to note..."\n', 0),
    "suppression_comment": ("I think so. <!-- register-lint: ignore -->\n", 0),
    "first_person_plural": ("We design the riser to the stated basis.\n", 1),
    "impersonal_ok": ("The riser is designed to the stated basis.\n", 0),
    "us_country_not_pronoun": ("Wells on the US Outer Continental Shelf are recorded.\n", 0),
    "url_not_pronoun": ("Canonical source: noblecorp.com/our-fleet for fleet status.\n", 0),
    "inline_quote_exempt": ('Founded under the directive "we need all rig specs".\n', 0),
}


def self_test() -> int:
    import tempfile
    failures = 0
    for name, (body, expected) in SELF_TEST.items():
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(body)
            p = Path(fh.name)
        found = len(check(p))
        ok = (found > 0) == (expected > 0)
        print(f"  {'PASS' if ok else 'FAIL'}  {name:24} expected {'≥1' if expected else '0'}, found {found}")
        failures += 0 if ok else 1
        p.unlink()
    print(f"\n{'self-test passed' if not failures else f'self-test FAILED ({failures})'}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--include-sources", action="store_true",
                    help="also check verbatim third-party extracts (off by default)")
    a = ap.parse_args(argv[1:])
    if a.self_test:
        return self_test()
    if not a.paths:
        ap.print_usage()
        return 2

    files = []
    for p in a.paths:
        files.extend(sorted(p.rglob("*.md")) if p.is_dir() else [p])
    if not a.include_sources:
        files = [f for f in files if not is_transcribed(f)]
    violations = [v for f in files for v in check(f)]
    for v in violations:
        print(v)
    print(f"\n{len(files)} file(s) checked, {len(violations)} violation(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
