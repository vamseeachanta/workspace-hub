"""Ecosystem-sync orchestrator. Loads config, iterates repos, writes digest + issues."""
from __future__ import annotations
import argparse
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from scripts.ecosystem_sync.config import SyncConfig, load_config
from scripts.ecosystem_sync.state import (
    RepoState, load_state, save_state, has_substantive_change,
)
from scripts.ecosystem_sync.signals import (
    detect_release_tag, detect_new_case_study,
    detect_readme_capability_diff, detect_showcase_labeled_closed_issues,
    _hash_section, _extract_section,
)
from scripts.ecosystem_sync.digest import render_digest
from scripts.ecosystem_sync.issues import open_issue_if_new
from scripts.ecosystem_sync.models import Signal


LOG = logging.getLogger("ecosystem-sync")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "scripts" / "ecosystem-sync" / "config.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip issue filing and state writes; print digest to stdout.")
    parser.add_argument("--doctor", action="store_true",
                        help="Validate config, repos, gh auth, state writability.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)

    if args.doctor:
        return _doctor(cfg)
    return _sync(cfg, dry_run=args.dry_run)


def _doctor(cfg: SyncConfig) -> int:
    ok = True
    for r in cfg.repos:
        p = Path(r.path)
        if not p.exists():
            LOG.error("repo missing: %s at %s", r.name, p); ok = False; continue
        if not (p / ".git").exists():
            LOG.error("not a git repo: %s", p); ok = False
    try:
        subprocess.run(["gh", "auth", "status"], check=True,
                       capture_output=True, text=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        LOG.error("gh auth check failed: %s", e); ok = False
    state_path = Path(cfg.state_file)
    if not state_path.parent.exists():
        LOG.error("state dir missing: %s", state_path.parent); ok = False
    digest_path = Path(cfg.digest_dir)
    if not digest_path.exists():
        LOG.error("digest dir missing: %s", digest_path); ok = False
    LOG.info("doctor: %s", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _sync(cfg: SyncConfig, dry_run: bool) -> int:
    t0 = time.time()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    since = today  # gh accepts YYYY-MM-DD
    state_path = Path(cfg.state_file)
    try:
        before = load_state(state_path)
    except Exception as e:
        LOG.error("state file unparseable: %s", e)
        return 2

    after: dict[str, RepoState] = {k: v for k, v in before.items()}
    signals_by_repo: dict[str, list[Signal]] = {}
    skipped: dict[str, str] = {}

    for r in cfg.repos:
        try:
            subprocess.run(["git", "-C", r.path, "fetch", "origin",
                            "--tags", "--prune"],
                           check=True, capture_output=True, text=True, timeout=30)
            st = before.get(r.name, RepoState(last_sync_utc=today, last_commit_sha=""))
            sigs: list[Signal] = []
            sigs += detect_release_tag(r.name, Path(r.path), st)
            sigs += detect_new_case_study(r.name, Path(r.path), st)
            sigs += detect_readme_capability_diff(r.name, Path(r.path), st, r.readme_sections)
            sigs += detect_showcase_labeled_closed_issues(r.name, st, since)
            if sigs:
                signals_by_repo[r.name] = sigs
            after[r.name] = _updated_state(r, st, Path(r.path), today)
        except Exception as e:
            LOG.exception("repo failed: %s", r.name)
            skipped[r.name] = str(e)

    all_signals: list[Signal] = [s for sigs in signals_by_repo.values() for s in sigs]
    to_file = all_signals[: cfg.max_issues_per_run]
    suppressed = all_signals[cfg.max_issues_per_run :]

    issues_filed = 0
    if not dry_run:
        for s in to_file:
            r = open_issue_if_new(s, cfg.issue_repo)
            if r.status == "created":
                issues_filed += 1
            LOG.info("issue: %s kind=%s status=%s", s.repo, s.kind, r.status)

    digest_md = render_digest(
        signals_by_repo=signals_by_repo, skipped=skipped, date=today,
        duration_s=int(time.time() - t0), repos_total=len(cfg.repos),
        issues_filed=issues_filed, suppressed_signals=suppressed,
    )

    if dry_run:
        print(digest_md)
        return 0

    digest_path = Path(cfg.digest_dir) / f"{today}.md"
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(digest_md)

    if has_substantive_change(before, after):
        save_state(state_path, after)
    return 0


def _updated_state(
    r, old: RepoState, repo_path: Path, today: str,
) -> RepoState:
    """Compute new RepoState after a successful scan."""
    # New tags observed
    try:
        tags_out = subprocess.run(
            ["git", "-C", str(repo_path), "tag", "-l"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout
        all_tags = [t.strip() for t in tags_out.splitlines() if t.strip()]
    except Exception:
        all_tags = old.last_seen_tags
    # New commit sha
    try:
        sha = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
    except Exception:
        sha = old.last_commit_sha
    # New readme hashes
    readme_path = repo_path / "README.md"
    hashes: dict[str, str] = dict(old.last_readme_hash)
    if readme_path.exists():
        try:
            md = readme_path.read_text()
            for heading in r.readme_sections:
                body = _extract_section(md, heading)
                if body:
                    hashes[heading] = _hash_section(body)
        except Exception:
            pass
    return RepoState(
        last_sync_utc=today + "T00:00:00Z",
        last_commit_sha=sha,
        last_seen_tags=all_tags,
        last_readme_hash=hashes,
        last_case_studies=old.last_case_studies,
        last_closed_showcase_issues=old.last_closed_showcase_issues,
    )


if __name__ == "__main__":
    sys.exit(main())
