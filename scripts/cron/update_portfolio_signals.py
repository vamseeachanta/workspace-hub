#!/usr/bin/env python3
"""update_portfolio_signals.py — WRK-1020 nightly portfolio signals updater.

L2: per-provider WRK activity counts from last-N-day archive files.
L3: gemini capability research (JSON structured output).
Output: .claude/state/portfolio-signals.yaml (atomic write).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parents[2]
DEFAULT_OUTPUT = REPO_ROOT / ".claude" / "state" / "portfolio-signals.yaml"
ARCHIVE_DIR = REPO_ROOT / ".claude" / "work-queue" / "archive"

KNOWN_ORCHESTRATORS = {"claude", "codex", "gemini"}
CATEGORY_MAP = {
    "harness": "harness",
    "engineering": "engineering",
    "data": "data",
}
OTHER_CATEGORIES = {"platform", "maintenance", "business", "personal", "uncategorised"}

OFFICIAL_DOMAINS = {
    "anthropic.com", "openai.com", "deepmind.google", "blog.google", "cloud.google.com"
}

PROMPT_ENG = (
    'List up to 5 AI capabilities announced in last 7 days relevant to '
    'engineering computation (subsea, structural, drilling, reservoir). '
    'Respond ONLY in JSON array:\n'
    '[{"date": "YYYY-MM-DD", "provider": "claude|codex|gemini", '
    '"capability": "brief name", "engineering_domains": ["domain1"], '
    '"impact": "low|medium|high", "source": "https://..."}]\n'
    'Output ONLY the JSON array, no prose.'
)

PROMPT_GEN = (
    'List up to 5 AI capabilities or model updates announced in last 7 days. '
    'Respond ONLY in JSON array:\n'
    '[{"date": "YYYY-MM-DD", "provider": "claude|codex|gemini", '
    '"capability": "brief name", "engineering_domains": [], '
    '"impact": "low|medium|high", "source": "https://..."}]\n'
    'Output ONLY the JSON array, no prose.'
)


# ── frontmatter ───────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter between --- delimiters. Raises ValueError on malformed YAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return {}
    try:
        return yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError:
        raise ValueError("malformed frontmatter")


# ── L2 collection ─────────────────────────────────────────────────────────────

def _empty_counts() -> dict:
    return {p: {"harness": 0, "engineering": 0, "data": 0, "other": 0}
            for p in ("claude", "codex", "gemini")}


def collect_l2_counts(archive_dir: Path, lookback_days: int) -> tuple[dict, dict]:
    cutoff = date.today() - timedelta(days=lookback_days)
    counts = _empty_counts()
    meta = {"files_scanned": 0, "files_with_orchestrator": 0,
            "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}

    for md_file in sorted(archive_dir.rglob("*.md")):
        meta["files_scanned"] += 1
        text = md_file.read_text(encoding="utf-8", errors="replace")
        try:
            fm = parse_frontmatter(text)
        except ValueError:
            meta["files_skipped_malformed"] += 1
            continue

        orchestrator = str(fm.get("orchestrator", "")).strip().lower()
        if not orchestrator or orchestrator not in KNOWN_ORCHESTRATORS:
            meta["files_skipped_no_orchestrator"] += 1
            continue

        completed_at_raw = str(fm.get("completed_at", "")).strip()
        try:
            completed_date = datetime.fromisoformat(
                completed_at_raw.replace("Z", "+00:00")
            ).date()
        except (ValueError, AttributeError):
            meta["files_skipped_malformed"] += 1
            continue

        if completed_date < cutoff:
            continue

        cat_raw = str(fm.get("category", "")).strip().lower()
        bucket = CATEGORY_MAP.get(cat_raw, "other")
        counts[orchestrator][bucket] += 1
        meta["files_with_orchestrator"] += 1

    return counts, meta


# ── L3 mode selection ─────────────────────────────────────────────────────────

def select_l3_mode(counts: dict) -> str:
    eng = sum(counts[p]["engineering"] for p in counts)
    har = sum(counts[p]["harness"] for p in counts)
    return "engineering" if eng >= har else "general"


# ── L3 source filtering / dedup / pruning ─────────────────────────────────────

def filter_official_sources(signals: list) -> list:
    def _domain_ok(url: str) -> bool:
        host = re.sub(r"^https?://", "", url.lower()).split("/")[0].split("?")[0]
        return any(host == d or host.endswith("." + d) for d in OFFICIAL_DOMAINS)
    return [s for s in signals if _domain_ok(str(s.get("source", "")))]


def _sig_hash(s: dict) -> str:
    key = f"{s.get('provider','')}/{s.get('capability','')}/{s.get('date','')}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def dedup_signals(existing: list, new_signals: list) -> list:
    seen = {_sig_hash(s) for s in existing}
    result = list(existing)
    for s in new_signals:
        h = _sig_hash(s)
        if h not in seen:
            result.append(s)
            seen.add(h)
    return result


def prune_signals(signals: list, days: int = 30) -> list:
    cutoff = date.today() - timedelta(days=days)
    out = []
    for s in signals:
        try:
            d = datetime.fromisoformat(
                str(s.get("date", "")).replace("Z", "+00:00")
            ).date()
            if d >= cutoff:
                out.append(s)
        except (ValueError, AttributeError):
            pass
    return out


def merge_signals(existing: list, new_signals: list,
                  max_new: int = 5, max_total: int = 20) -> list:
    # New signals prepended so they are not truncated when existing is full.
    capped_new = new_signals[:max_new]
    merged = dedup_signals(capped_new, existing)
    return merged[:max_total]


# ── L3 gemini query ───────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = re.sub(r"^```[a-z]*\n?", "", text.strip(), flags=re.MULTILINE)
    return re.sub(r"```$", "", text.strip(), flags=re.MULTILINE).strip()


def run_l3_query(mode: str, prior_signals: list, timeout: int = 60) -> tuple[list, dict]:
    meta = {"query_attempted": False, "query_mode": mode, "parse_success": False,
            "signals_added": 0, "signals_pruned": 0, "carry_forward": False,
            "source_verified": False}

    if not shutil.which("gemini"):
        meta["carry_forward"] = True
        return prior_signals, meta

    meta["query_attempted"] = True
    prompt = PROMPT_ENG if mode == "engineering" else PROMPT_GEN

    try:
        result = subprocess.run(
            ["gemini", "-p", prompt, "-y"],
            capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        meta["carry_forward"] = True
        return prior_signals, meta
    except Exception:
        meta["carry_forward"] = True
        return prior_signals, meta

    if result.returncode != 0:
        meta["carry_forward"] = True
        return prior_signals, meta

    try:
        raw = json.loads(_strip_fences(result.stdout))
        if not isinstance(raw, list):
            raise ValueError("not a list")
        meta["parse_success"] = True
    except (json.JSONDecodeError, ValueError):
        meta["carry_forward"] = True
        return prior_signals, meta

    valid = filter_official_sources(raw)
    if not valid:
        meta["carry_forward"] = True
        return prior_signals, meta

    meta["source_verified"] = True
    pruned_prior = prune_signals(prior_signals)
    meta["signals_pruned"] = len(prior_signals) - len(pruned_prior)
    merged = merge_signals(pruned_prior, valid)
    meta["signals_added"] = len(merged) - len(pruned_prior)
    return merged, meta


# ── output writer ─────────────────────────────────────────────────────────────

def write_output(output_path: Path, counts: dict, signals: list,
                 l3_meta: dict, l2_meta: dict, dry_run: bool,
                 lookback_days: int = 30) -> None:
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lookback_days": lookback_days,
        "provider_activity": counts,
        "l2_meta": l2_meta,
        "capability_signals": signals,
        "l3_meta": l3_meta or {},
    }
    text = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if dry_run:
        sys.stdout.write(text)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(".yaml.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.rename(output_path)


# ── arg validation ────────────────────────────────────────────────────────────

def validate_lookback(value: str) -> int:
    try:
        n = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"--lookback must be a positive integer, got: {value!r}")
    if n <= 0:
        raise ValueError(f"--lookback must be positive, got: {n}")
    return n


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Update portfolio-signals.yaml")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print to stdout, do not write file")
    parser.add_argument("--lookback", default="30", metavar="N",
                        help="Lookback window in days (default: 30)")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), metavar="PATH",
                        help="Output file path")
    args = parser.parse_args()

    lookback = validate_lookback(args.lookback)
    output_path = Path(args.output)

    counts, l2_meta = collect_l2_counts(ARCHIVE_DIR, lookback)

    prior_signals: list = []
    if output_path.exists():
        try:
            existing = yaml.safe_load(output_path.read_text(encoding="utf-8")) or {}
            prior_signals = existing.get("capability_signals", [])
        except Exception:
            pass

    mode = select_l3_mode(counts)
    signals, l3_meta = run_l3_query(mode, prior_signals=prior_signals, timeout=60)

    write_output(output_path, counts, signals, l3_meta, l2_meta,
                 dry_run=args.dry_run, lookback_days=lookback)

    if not args.dry_run:
        print(f"✔ portfolio-signals.yaml updated: {output_path}")


if __name__ == "__main__":
    main()
