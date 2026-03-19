#!/usr/bin/env python3
"""categorize-uncategorized.py — Assign category/subcategory to archived WRKs
that currently lack them.

Rules are applied in priority order: first match wins.
After running, re-run synthesize_archive.py --all to regenerate the report.

Usage:
    uv run --no-project python scripts/knowledge/categorize_uncategorized.py [--dry-run]
"""
import argparse
import re
import subprocess
from pathlib import Path


def _repo_root():
    try:
        return Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL, text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


# ── Category rules: (regex_pattern, category, subcategory) ──────────────
# Applied against lowercased title. First match wins.
RULES = [
    # ── Personal / household ──
    (r"(sink faucet|stove repair|garage clean|reorganize storage|piping rock|"
     r"upload videos|smart watch|krishna adhd|family dollar|1099)", "personal", "household"),
    (r"personal habit", "personal", "development"),

    # ── Engineering: hydrodynamics / diffraction / hull ──
    (r"(diffraction|aqwa|orcawave|bemrosetta|hull\b|rao\b|mesh (format|convergence)|"
     r"panel (shapes|meshes)|gyrad|barge hull|spar hull|ship hull|"
     r"hull (library|size|analysis|form)|spec\.yml.*diffraction|"
     r"reverse parser|canonical spec\.yml)", "engineering", "hydrodynamics"),

    # ── Engineering: OrcaFlex / mooring ──
    (r"(orcaflex|mooring benchmark)", "engineering", "orcaflex"),

    # ── Engineering: pipeline / wall thickness / S-lay ──
    (r"(pipeline (wall|integrity|installation)|wall thickness|"
     r"s-lay|api rp (1111|2rd)|api std 2rd|dnv.st.f101|"
     r"three-way design code|submarine pipeline)", "engineering", "pipeline"),

    # ── Engineering: cathodic protection ──
    (r"(cathodic.protection|cp (standards|worked|capability|client)|"
     r"dnv.rp.(b401|f103)|abs.*cp|abs.*guidance)", "engineering", "cathodic-protection"),

    # ── Engineering: fatigue ──
    (r"(fatigue (analysis|assessment)|s-n curve)", "engineering", "fatigue"),

    # ── Engineering: drilling / well ──
    (r"(drilling|dynacard|well (bore|planning)|mpd system|slim.hole|"
     r"drillbotics|decline curve)", "engineering", "drilling"),

    # ── Engineering: decommissioning ──
    (r"decommission", "engineering", "decommissioning"),

    # ── Engineering: safety / HSE / risk ──
    (r"(hse risk|enigma|marine safety|safety (case|analysis|scoring)|"
     r"cross.database.*safety|incident.*correlation)", "engineering", "safety"),

    # ── Engineering: units / TrackedQuantity ──
    (r"(trackedquantity|dimension analysis|lineagegraph|unit (tracking|conversion|provenance)|"
     r"common\.units|m-t envelope|symmetric m-t)", "engineering", "units"),

    # ── Engineering: metocean ──
    (r"(metocean|met-om)", "engineering", "metocean"),

    # ── Engineering: LNG ──
    (r"lng terminal", "engineering", "lng"),

    # ── Data: BSEE ──
    (r"(bsee\b|lower tertiary|buckskin field|keathley canyon|"
     r"bsee (field|data|excel|incident|platform))", "data", "bsee"),

    # ── Data: production (non-BSEE) ──
    (r"(ncs production|ukcs production|brazil anp|eia us production|"
     r"canada offshore|emerging basin|cross.regional production|"
     r"production data (module|query))", "data", "production"),

    # ── Data: safety (OSHA/NTSB/PHMSA) ──
    (r"(osha\b|ntsb\b|phmsa\b|epa tri\b|severe injury|fatality data)", "data", "safety"),

    # ── Data: fleet / vessel / rig ──
    (r"(rig fleet|vessel (fleet|marine)|contractor (contact|bd)|"
     r"offshore.*survey|drilling rig.*dataset|riser component)", "data", "fleet"),

    # ── Data: general ingestion / index ──
    (r"(data (collection|index|pipeline|source)|refresh pipeline|"
     r"document.index|saipem.*index|acma.projects.*index|"
     r"content index|discoverability|module.*index|"
     r"navigation layer|legacy root)", "data", "ingestion"),

    # ── Business / finance ──
    (r"(stock analysis|position strategy|portfolio)", "business", "finance"),

    # ── Career / outreach / vision ──
    (r"(anthropic outreach|vision document|orient all work|"
     r"accomplishment|aceengineer.*vision|future.boost)", "career", "strategy"),

    # ── Website ──
    (r"(aceengineer.website|website.*data card)", "website", "aceengineer"),

    # ── Platform / ops / machine setup ──
    (r"(ace.linux|acma.ansys|install.*suite|gemini cli|"
     r"node 18|portable python|cross.machine|workstation|"
     r"filesystem naming|naming cleanup)", "platform", "ops"),

    # ── CAD / FEA ──
    (r"(cad.development|fea pipeline|gmsh)", "engineering", "cad-fea"),

    # ── CI / workflows ──
    (r"(ci workflow|github action|test coverage improvement)", "ci", "testing"),

    # ── Harness: skills ──
    (r"(skill.*(curation|research|register|callable|improvement|index|"
     r"capability|manifest|assessment)|skills\.sh|"
     r"agent.callable.*skill)", "harness", "skills"),

    # ── Harness: work-queue ──
    (r"(work.queue|work.item|wqe|close.*wrk|"
     r"linear stage|gate enforcement|gatepass|"
     r"active wrk|stage.*schematic|workflow.*gate)", "harness", "work-queue"),

    # ── Harness: session / context ──
    (r"(session.*(analysis|lifecycle|bootstrap|logging|start)|"
     r"context budget|stop hook|comprehensive.learning)", "harness", "session"),

    # ── Harness: AI orchestration ──
    (r"(multi.agent|provider.neutral|ensemble planning|"
     r"model.tier routing|agent (team|usage|performance|delegation)|"
     r"orchestrat|claude.*codex.*gemini|"
     r"ai.agent.*track|quota display|credits display)", "harness", "ai-orchestration"),

    # ── Harness: general ──
    (r"(ecosystem (truth|health)|submodule|"
     r"spec migration|refactor large file|"
     r"move modules|consolidate modules|merge.*structure|"
     r"audit.*module|interoperability|"
     r"legal.sanity|deny list|pre.commit)", "harness", "maintenance"),

    # ── Standards acquisition ──
    (r"(abs.*download|abs.*acquisition|standards.*folder|"
     r"raw.*docs|o&g.standards)", "engineering", "standards"),

    # ── Design code versioning ──
    (r"design code version", "engineering", "standards"),

    # ── Data: HSE audit / gap analysis ──
    (r"(hse.*data|hse.*coverage|hse.*gap|mishap.*activity)", "data", "safety"),

    # ── Data: vessel / construction vessel ──
    (r"(construction.*vessel|vessel data)", "data", "fleet"),

    # ── Data: general (worldenergydata cleanup, residence, git history) ──
    (r"(data residence|worldenergydata.*cleanup|worldenergydata.*root|"
     r"7\.1gb|large data.*git)", "data", "maintenance"),

    # ── Engineering: drilling (ROP, production test, nodal) ──
    (r"(rop prediction|bourgoyne|nodal analysis|production test.*quality)", "engineering", "drilling"),

    # ── Engineering: general rename / restructure within repos ──
    (r"(digitalmodel.*rename|digitalmodel.*naming)", "engineering", "maintenance"),

    # ── Harness: improve skill / /improve ──
    (r"(/improve|improve.*skill.*health|usage.based.*skill|"
     r"graph.aware.*skill|skill relationship|skill discovery|"
     r"subagent learning|plugins vs skills|repo.structure skill|"
     r"agent_os|ai.engineering.*interface)", "harness", "skills"),

    # ── Harness: work-queue process ──
    (r"(future.work.*brainstorm|archiv.*completed)", "harness", "work-queue"),

    # ── Harness: session / hooks / snapshot ──
    (r"(start hook|pre.clear.*snapshot|save.snapshot|save skill|"
     r"ecosystem.health.check|agent capacity)", "harness", "session"),

    # ── Harness: uv / python enforcement ──
    (r"(uv enforcement|python3.*fallback)", "harness", "maintenance"),

    # ── Platform: network / mount / SSHFS ──
    (r"(network.mount|sshfs|daily.*readiness)", "platform", "ops"),

    # ── Platform: licensed software ──
    (r"licensed software", "platform", "ops"),

    # ── Maintenance: test fixes / cleanup / repo structure ──
    (r"(pre.existing test|test failure.*assetutilities|"
     r"test coverage across|test suite optimization|"
     r"windows.path.*artifact|root cleanup|"
     r"empty dir|orphaned src|assethold.*cleanup|"
     r"assetutilities.*cleanup)", "maintenance", "repo-cleanup"),

    # ── Maintenance: Claude Code / cc-insights ──
    (r"(claude code version|cc.insights)", "maintenance", "tooling"),

    # ── Harness: workflow / planning ──
    (r"(workspace.hub workflow|plan.*reassess)", "harness", "work-queue"),

    # ── Data: general pipeline output ──
    (r"multi.format export", "data", "ingestion"),

    # ── Data: MAIB/IMO/EMSA/TSB importers ──
    (r"(maib|imo|emsa|tsb).*importer", "data", "safety"),

    # ── Session artifact ──
    (r"^session \d{8}", "harness", "session"),

    # ── Catch-all for remaining engineering-ish titles ──
    (r"(spec converter|benchmark|parametric)", "engineering", "general"),
]


def classify(title: str) -> tuple[str, str]:
    """Return (category, subcategory) for a WRK title."""
    t = title.lower()
    for pattern, cat, subcat in RULES:
        if re.search(pattern, t):
            return cat, subcat
    return "uncategorized", "other"


def scan_all_archives(root: Path):
    """Find all WRK-*.md in archive directories."""
    dirs = [
        root / ".claude" / "work-queue" / "archive",
        root / ".claude" / "work-queue" / "archived",
    ]
    files = []
    for d in dirs:
        if not d.is_dir():
            continue
        files.extend(d.glob("WRK-*.md"))
        files.extend(d.glob("*/WRK-*.md"))
    return sorted(set(files))


def read_frontmatter(path: Path) -> tuple[str, dict, str]:
    """Return (frontmatter_text, parsed_fields, body)."""
    text = path.read_text(errors="replace")
    m = re.match(r'^(---\n)(.*?)\n(---)', text, re.DOTALL)
    if not m:
        return "", {}, text
    fm_text = m.group(2)
    body = text[m.end():]
    fields = {}
    for line in fm_text.split("\n"):
        km = re.match(r'^(\w[\w_]*):\s*(.*)$', line)
        if km:
            fields[km.group(1)] = km.group(2).strip().strip('"').strip("'")
    return fm_text, fields, body


def update_frontmatter(path: Path, category: str, subcategory: str,
                       dry_run: bool = False) -> bool:
    """Add category/subcategory to frontmatter. Returns True if changed."""
    text = path.read_text(errors="replace")
    m = re.match(r'^(---\n)(.*?)(\n---)', text, re.DOTALL)
    if not m:
        return False

    fm = m.group(2)
    # Remove existing category/subcategory lines
    fm_lines = [l for l in fm.split("\n")
                if not re.match(r'^(category|subcategory):\s', l)]

    # Insert after id/title/status (whichever comes last)
    insert_idx = 0
    for i, line in enumerate(fm_lines):
        if re.match(r'^(id|title|status|priority|complexity):', line):
            insert_idx = i + 1

    fm_lines.insert(insert_idx, f"category: {category}")
    fm_lines.insert(insert_idx + 1, f"subcategory: {subcategory}")

    new_text = m.group(1) + "\n".join(fm_lines) + m.group(3) + text[m.end():]

    if not dry_run:
        path.write_text(new_text)
    return True


def main():
    ap = argparse.ArgumentParser(description="Categorize uncategorized archived WRKs")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print changes without writing")
    args = ap.parse_args()

    root = _repo_root()
    files = scan_all_archives(root)

    stats = {"updated": 0, "already_categorized": 0, "still_uncategorized": 0,
             "errors": 0}
    by_category = {}

    for f in files:
        fm_text, fields, body = read_frontmatter(f)
        existing_cat = fields.get("category", "")

        # Skip already-categorized items
        if existing_cat and existing_cat not in ("uncategorized", ""):
            stats["already_categorized"] += 1
            continue

        title = fields.get("title", "")
        if not title:
            stats["errors"] += 1
            continue

        cat, subcat = classify(title)
        if cat == "uncategorized":
            stats["still_uncategorized"] += 1
            wid = fields.get("id", f.stem)
            print(f"  UNMATCHED: {wid} | {title}")
            continue

        wid = fields.get("id", f.stem)
        ok = update_frontmatter(f, cat, subcat, dry_run=args.dry_run)
        if ok:
            stats["updated"] += 1
            by_category.setdefault(cat, {}).setdefault(subcat, []).append(wid)
            prefix = "[DRY] " if args.dry_run else ""
            print(f"  {prefix}{wid}: {cat}/{subcat}")
        else:
            stats["errors"] += 1

    print(f"\n{'=' * 60}")
    print(f"Results:")
    print(f"  Updated:            {stats['updated']}")
    print(f"  Already categorized:{stats['already_categorized']}")
    print(f"  Still uncategorized:{stats['still_uncategorized']}")
    print(f"  Errors:             {stats['errors']}")
    print(f"\nCategory breakdown:")
    for cat in sorted(by_category):
        total = sum(len(v) for v in by_category[cat].values())
        subs = ", ".join(f"{sc}({len(ids)})"
                         for sc, ids in sorted(by_category[cat].items()))
        print(f"  {cat} ({total}): {subs}")

    if args.dry_run:
        print("\n[DRY RUN — no files modified. Remove --dry-run to apply.]")


if __name__ == "__main__":
    main()
