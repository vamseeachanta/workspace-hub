"""Pure markdown renderer for the daily digest."""
from __future__ import annotations
from scripts.ecosystem_sync.models import Signal


def render_digest(
    signals_by_repo: dict[str, list[Signal]],
    skipped: dict[str, str],
    date: str,
    duration_s: int,
    repos_total: int,
    issues_filed: int,
    suppressed_signals: list[Signal],
) -> str:
    parts: list[str] = [f"# Ecosystem Sync — {date}\n\n"]

    total_signals = sum(len(v) for v in signals_by_repo.values()) + len(suppressed_signals)
    repos_ok = repos_total - len(skipped)

    if total_signals == 0 and not skipped:
        parts.append("_No signals detected. Nothing to propose today._\n")
    else:
        parts.append("## Signals\n")
        if not signals_by_repo:
            parts.append("_No signals from any repo._\n")
        for repo in sorted(signals_by_repo):
            parts.append(f"\n### {repo}\n\n")
            for sig in signals_by_repo[repo]:
                parts.append(f"- **{sig.kind}**: {sig.title}\n")
                parts.append(f"  - dedupe: `{sig.dedupe_key}`\n")

    if skipped:
        parts.append("\n## Skipped repos\n\n")
        for repo in sorted(skipped):
            parts.append(f"- ⚠ `{repo}`: {skipped[repo]}\n")

    if suppressed_signals:
        parts.append(f"\n## Suppressed signals ({len(suppressed_signals)})\n")
        parts.append("_20-issue cap reached; these were NOT filed as issues:_\n\n")
        for sig in suppressed_signals:
            parts.append(f"- **{sig.kind}** `{sig.repo}`: {sig.title}\n")

    parts.append(
        f"\n---\n\n"
        f"Run footer: Duration: {duration_s}s · Repos OK: {repos_ok}/{repos_total} · "
        f"Signals: {total_signals} · Issues filed: {issues_filed} · "
        f"Next run: tomorrow 06:00 CT\n"
    )
    return "".join(parts)
