#!/usr/bin/env python3
"""Plan cadence report archival without changing the filesystem. Refs issues/2336.

Usage: cadence_retention.py --report-root REPORTS --config CONFIG.json

Configuration is an object containing only a ``reports`` array. Each registration
has exactly ``pattern``, ``cadence`` and ``keep`` fields, for example::

    {"reports": [{"pattern": "memory-health-{period}.md",
                  "cadence": "weekly", "keep": 12}]}

The policy in issues/2336 keeps 12 weekly, 12 monthly and 4 quarterly reports.
Counts are explicitly supplied, independently per registration; no live policy
or default report root is installed here. Patterns are literal POSIX relative
paths with one ``{period}`` in the basename, using letters, digits, dot, dash and
underscore elsewhere. Globs, dot segments and registrations under archive are
rejected. Missing registered subdirectories contain no reports.

Period spellings follow lib/cadence-common.sh:cadence_period(): YYYY-Www,
YYYY-MM and YYYY-Qq. Weekly uses calendar year (%Y) plus ISO week (%V), so it
permits W53 even when that calendar year is not an ISO year with that week.
Retention orders the encoded year and period number; it cannot recover dates
or resolve weekly year-boundary ambiguity in the existing naming convention.

Output is a JSON array of root-relative source/destination records, sorted by
source. Destinations are archive/<encoded-year>/<basename>. All matching files,
including retained ones, are validated before any output. Files with other names
and existing archives are not scanned. Planning reads directory metadata only;
it never reads report contents, creates directories, moves or deletes files.
This is a filesystem snapshot, not authorization or a safe concurrent executor.
"""

from __future__ import annotations

import argparse
import json
import re
import stat
from pathlib import Path


# Structural ranges and widths follow cadence_period(), strftime %Y/%V/%m,
# and its Gregorian quarter calculation; these are not retention policy counts.
PERIODS = {
    "weekly": (re.compile(r"([0-9]{4})-W([0-9]{2})"), 53),
    "monthly": (re.compile(r"([0-9]{4})-([0-9]{2})"), 12),
    "quarterly": (re.compile(r"([0-9]{4})-Q([1-4])"), 4),
}
LITERAL = re.compile(r"[A-Za-z0-9._-]*")


class RetentionError(ValueError):
    """An input cannot produce an unambiguous, confined plan."""


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RetentionError("duplicate configuration key")
        result[key] = value
    return result


def _nonfinite(_value):
    raise RetentionError("non-finite configuration number")


def _registrations(config):
    if not isinstance(config, dict) or set(config) != {"reports"}:
        raise RetentionError("configuration must contain only reports")
    if not isinstance(config["reports"], list):
        raise RetentionError("reports must be an array")
    registrations = []
    for entry in config["reports"]:
        if not isinstance(entry, dict) or set(entry) != {"pattern", "cadence", "keep"}:
            raise RetentionError("registration requires pattern, cadence and keep")
        cadence, keep, pattern = entry["cadence"], entry["keep"], entry["pattern"]
        if not isinstance(cadence, str) or cadence not in PERIODS:
            raise RetentionError("unknown cadence")
        # bool is an int subclass, but is not a declarative count.
        if type(keep) is not int or keep < 0:
            raise RetentionError("keep must be a nonnegative integer")
        if not isinstance(pattern, str) or pattern.count("{period}") != 1:
            raise RetentionError("pattern requires one period placeholder")
        parts = pattern.split("/")
        if any(part in ("", ".", "..") for part in parts) or parts[0] == "archive":
            raise RetentionError("unsafe pattern path")
        if any(not LITERAL.fullmatch(part) for part in parts[:-1]):
            raise RetentionError("unsafe pattern directory")
        if "{period}" not in parts[-1]:
            raise RetentionError("pattern period must be in the basename")
        prefix, suffix = parts[-1].split("{period}")
        if not LITERAL.fullmatch(prefix + suffix):
            raise RetentionError("unsafe pattern basename")
        registrations.append((parts[:-1], prefix, suffix, cadence, keep))
    return registrations


def _directory(root, parts):
    """Return a directory, or None if absent; never traverse a symlink."""
    directory = root
    for part in parts:
        directory = directory / part
        try:
            mode = directory.lstat().st_mode
        except FileNotFoundError:
            return None
        if not stat.S_ISDIR(mode):
            raise RetentionError("directory is symlinked or not a directory")
    return directory


def _period_key(period, cadence):
    expression, upper = PERIODS[cadence]
    match = expression.fullmatch(period)
    if match is None:
        raise RetentionError("malformed report period")
    year, number = map(int, match.groups())
    if year < 1 or not 1 <= number <= upper:
        raise RetentionError("report period out of range")
    return year, number


def build_plan(report_root: Path, config: dict) -> list[dict[str, str]]:
    """Validate registrations and return a deterministic read-only archive plan."""
    registrations = _registrations(config)
    if not stat.S_ISDIR(report_root.lstat().st_mode):
        raise RetentionError("report root is symlinked or not a directory")
    root = report_root.resolve(strict=True)
    records = []
    sources = set()
    destinations = set()
    for parts, prefix, suffix, cadence, keep in registrations:
        directory = _directory(root, parts)
        if directory is None:
            continue
        candidates = []
        for path in directory.iterdir():
            name = path.name
            if not name.startswith(prefix) or not name.endswith(suffix):
                continue
            # Empty suffixes are allowed; avoid the empty slice produced by -0.
            end = len(name) - len(suffix) if suffix else len(name)
            period = name[len(prefix):end]
            key = _period_key(period, cadence)
            if not stat.S_ISREG(path.lstat().st_mode):
                raise RetentionError("candidate is symlinked or not a regular file")
            source = path.relative_to(root).as_posix()
            if source in sources:
                raise RetentionError("duplicate candidate registration")
            sources.add(source)
            candidates.append((key, source, name, period))
        candidates.sort(reverse=True)
        for _key, source, name, period in candidates[keep:]:
            year = period.split("-")[0]
            destination = Path("archive") / year / name
            relative = destination.as_posix()
            if relative in destinations:
                raise RetentionError("duplicate archive destination")
            destinations.add(relative)
            parent = _directory(root, destination.parts[:-1])
            if parent is not None:
                try:
                    (root / destination).lstat()
                except FileNotFoundError:
                    pass
                else:
                    raise RetentionError("archive destination already exists")
            records.append({"source": source, "destination": relative})
    return sorted(records, key=lambda record: record["source"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config = json.loads(
            args.config.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_keys, parse_constant=_nonfinite,
        )
        plan = build_plan(args.report_root, config)
    except RetentionError as error:
        parser.exit(2, f"retention: {error}\n")
    except (OSError, UnicodeError, ValueError):
        # Do not echo raw filenames, configuration text or system paths.
        parser.exit(2, "retention: unable to read inputs or invalid JSON\n")
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
