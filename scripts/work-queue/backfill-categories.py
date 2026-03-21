#!/usr/bin/env python3
"""Backfill category + subcategory into WRK files missing them.

Usage:
    uv run --no-project python scripts/work-queue/backfill-categories.py [--dry-run] [--limit N]
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = REPO_ROOT / ".claude" / "work-queue"

# Ordered list of (pattern, category, subcategory) — first match wins.
# Patterns are case-insensitive regexes matched against the title.
RULES = [
    # --- Harness / cross-review (match BEFORE structural to avoid false positives) ---
    (r"cross.review|submit.to.*claude|submit.to.*codex|submit.to.*gemini|review.*bundle|review.*artifact|review.*transport|review.*mode.*policy|review.*artifact|compact.*review|full.*bundle.*review", "harness", "cross-review"),
    (r"orchestrat|gate.*enforc|gate.*evidence|claim.*gate|close.*gate|plan.*gate|resource.intelli|orchestrator.*gate|orchestrator.*flow|orchestrator.*timeline", "harness", "workflow-gates"),
    (r"Claude.*CLI|Codex.*CLI|Gemini.*CLI|agent.*coord|agent.*cost|agent.*alloc|agent.*perf|AI.*agent|multi.agent|provider.*cost|Superintelligent.*Agent", "ai-orchestration", "ai-tools"),
    (r"session.*manage|session.*start|session.*log|session.*preflight|session.*health|session.*auto.refresh|session.*wrapper", "harness", "session"),
    (r"skill.*curat|skill.*gap|skill.*improv|skill.*enhanc|skill.*design|skill.*architect|skill.*driven|skill.*name|file.structure.*skill|file.taxonomy", "harness", "skills"),
    (r"WRK.*queue|work.queue|wrk.*lifecycle|wrk.*triage|wrk.*scope|wrk.*explosion|queue.*sync|queue.*priority|WRK.*explos|Gap.to.WRK", "work-queue-infrastructure", "work-queue"),
    (r"stage.transition|workflow.*parity|workflow.*doc|workflow.*enforce|workflow.*standard|gatepass", "harness", "workflow"),
    (r"hook(?!.*fish)|pre.commit|stop.hook|uv\b.*hook|uv\b.*cache|repo.local.*uv", "harness", "hooks"),
    (r"statusline|terminal.*UX|cross.terminal", "harness", "ops"),
    (r"check.all\.sh|split.*responsib", "harness", "scripts"),
    (r"harness.*file|CLAUDE\.md|AGENTS\.md|CODEX\.md|agent.*harness|context.*reduc|recurring.*correction.*pattern|not.responding.to.improve", "harness", "ai-config"),
    (r"test.*health|test.*coverage|TDD.*promot|test.*fix|sandbox.*gate|automate.*gate", "harness", "testing"),
    (r"commit.*harden|git.*hygien|chore.*commit|repository_sync", "harness", "git"),
    (r"back.link|missing.*link", "harness", "skills-maintenance"),

    # --- Engineering: specific disciplines first ---
    (r"cathodic.protect|CP\b.*market|CP\b.*brochure", "engineering", "cathodic-protection"),
    (r"drill(?:ing)?(?!.*blog)|completion.*interven|MPD\b|coiled.tubing|drill.*riser|casing.*tubing|triaxial.*stress|von.Mises.*API", "engineering", "drilling"),
    (r"GIS|geospatial|QGIS|Google.Earth|(?<!analy)spatial", "engineering", "gis"),
    (r"hull|naval.architect|waterline|section.*profile|ship.plan|offset.table", "engineering", "naval-architecture"),
    (r"VIV|free.span|DNV.RP.F105|pipeline.*viv", "engineering", "structural-dynamics"),
    (r"pipeline.*geom|pipeline.*design|pipeline.*lookup|pressure.*containment|flexibles.*module", "engineering", "pipeline"),
    (r"FFS|fitness.for.service|wall.thickness|API.579|corrosion.*allow", "engineering", "asset-integrity"),
    (r"(?<!infra)structur(?!e.*skill)|FEA\b|CalculiX|ANSYS|APDL|finite.element|mesh.*decim|mesh.*util|CLT.*strength|[Cc]omposite.*panel|laminate", "engineering", "structural"),
    (r"hydro|wave|current.*profile|metocean|sea.state|weather.window|operability.*Hs", "engineering", "hydrodynamics"),
    (r"moor|anchor|foundation|geotech|soil", "engineering", "mooring"),
    (r"offshore.*resilien|offshore.*platform|field.develop", "engineering", "offshore"),
    (r"vessel.*fleet|heavy.vessel|construction.vessel", "engineering", "fleet"),
    (r"marine|seakeep", "engineering", "marine"),
    (r"subsea|riser(?!.*drill)|jumper|umbilical", "engineering", "subsea-risers"),
    (r"reservoir|production.*surveil|production.*forecast|Arps.*decline|decline.*curve", "engineering", "reservoir-engineering"),
    (r"decommission", "engineering", "decommissioning"),
    (r"LNG|liquef", "engineering", "lng"),
    (r"orcaflex|OrcaFlex|enrichment.*pipeline.*orcaflex", "engineering", "orcaflex"),
    (r"safety|HSE|risk.index", "engineering", "safety"),
    (r"artificial.lift|dynacard", "engineering", "artificial-lift"),
    (r"installation|lay.*vessel|pipelay", "engineering", "installation"),
    (r"fatigue|S.N.*curve", "engineering", "fatigue"),
    (r"wind.*turb|wind.*energy", "engineering", "wind"),
    (r"unit.*valid|unit.*conver|EnvironmentSpec", "engineering", "units"),
    (r"calc.example|calc_example", "engineering", "calculation-examples"),
    (r"FreeCAD|FCStd|Gmsh|Blender.*mesh|CAD", "engineering", "cad-fea"),
    (r"capability.map|Standards.to.Module|doc.*module.*linkage", "engineering", "standards"),

    # --- Data ---
    (r"BSEE|bureau.*safety", "data", "bsee"),
    (r"EIA\b|energy.*data.*blog|energy.*market", "data", "data-extraction"),
    (r"NUPRC|EITI|Nigeria.*data|West.Africa.*data", "data", "data-extraction"),
    (r"vessel.*data|fleet.*data", "data", "fleet"),
    (r"data.*residen|data.*tier|data.*complian", "data", "data-pipeline"),
    (r"data.*extract|data.*ingest|data.*load|data.*pipeline|data.*source", "data", "data-extraction"),
    (r"data.*quality|data.*fix|data.*clean", "data", "data-quality"),

    # --- Document Intelligence ---
    (r"document.*extract|document.*index|doc.*index|PDF|excel.*skill|phase.A.*index|phase.E", "document-intelligence", "document-index"),
    (r"standards.*raw|standards.*transfer|standards.*triage", "document-intelligence", "standards"),
    (r"knowledge.*graph|knowledge.*map|knowledge.*base|[Oo]nline.*[Rr]esources.*[Rr]esearch", "document-intelligence", "knowledge-management"),
    (r"curve.*digitiz|parametric.*extract", "document-intelligence", "data-extraction"),
    (r"query.doc|search.*index", "document-intelligence", "search-indexing"),

    # --- Platform / DevOps ---
    (r"machine.*setup|workstation|dev.secondary|dev.primary|Windows|Git.Bash|cross.machine|environment.*parity|smartmontools|SMART.*health|install.*program", "platform", "workstations"),
    (r"CI(?!.*skill)|pre.hook|automation.*refresh", "ci", "automation"),
    (r"pypi|release.*manag|setup\.py.*supersed|pyproject", "platform", "release-management"),
    (r"dependency|dep.*graph|dep.*pin", "platform", "dependency-graph"),
    (r"static.analysis|type.stub|code.*quality", "platform", "code-quality"),
    (r"[Uu]nified.*CLI|single.*ace.*command", "platform", "tooling"),
    (r"Codex.*relocation|/mnt/ace/", "platform", "workstations"),

    # --- Business / Career ---
    (r"website|aceengineer.*web|positioning|narrative|social.proof|NPV.*calc.*website|public.*sample.*data.*page", "business", "website"),
    (r"marketing|brochure|roadshow|lead.gen", "business", "marketing"),
    (r"blog|SEO|content.*strat", "business", "gtm"),
    (r"CV\b|resume|career|labor.market", "career", "cv-strategy"),
    (r"strategy.*repo|business.*operation|long.term.*plan", "business", "strategy"),
    (r"Anthropic.*course|agent.*skill.*course", "career", "training"),
    (r"Polymathic|The.Well.*integrat", "career", "research"),

    # --- Personal ---
    (r"family.*tree|Achantas|Krishna|ADHD|calendar", "personal", "household"),
    (r"Jabra|dongle|USB", "personal", "household"),
    (r"appliance|home.*analyt|Heriberto|powder.room|garage.*fence|faucet", "personal", "household"),
    (r"invest|portfolio|assethold.*test|covered.call|option.chain|sector.*exposure|P/E.*P/B|EV/EBITDA|fundamentals.*scor|yfinance", "personal-finance", "financial-analysis"),
    (r"tax|IRS|1099", "personal-finance", "tax-preparation"),
    (r"hobbies|hobby", "personal", "hobbies"),

    # --- Repo-specific ---
    (r"digitalmodel.*src|digitalmodel.*fix|digitalmodel.*clean|digitalmodel.*migrat", "engineering-module", "digitalmodel"),
    (r"worldenergydata.*src|worldenergydata.*fix|worldenergydata.*clean", "engineering-module", "worldenergydata"),
    (r"assetutilities.*test|assetutilities.*cover|remove.*agent_os.*assetutil|consolidate.*validator.*assetutil", "engineering-module", "assetutilities"),
    (r"OGManufacturing|ogmanufacturing", "engineering-module", "ogmanufacturing"),
    (r"repo.*struct|src.*violation|src.*structure|stale.*content|standard.*src.*layout", "maintenance", "repo-cleanup"),
    (r"benchmark.*plot|activity.*taxon|report.*gen|split.*module", "maintenance", "refactoring"),
    (r"2H.*legacy|discoverability|navigation.layer", "maintenance", "docs"),

    # --- Catch-all by conventional commit prefix ---
    (r"feat\(digitalmodel\)|digitalmodel", "engineering", "general"),
    (r"feat\(worldenergydata\)|worldenergydata", "data", "general"),
    (r"feat\(scripts\)", "harness", "scripts"),
    (r"chore\(wrk\)|chore\(work", "work-queue-infrastructure", "work-queue"),
    (r"chore\(review\)|review\(workflow\)|validate\(review\)|investigate\(review\)|docs\(review\)", "harness", "cross-review"),
    (r"chore\(docs?\)|audit.*triage.*Python.*script", "maintenance", "docs"),
    (r"fix\(agents?\)|fix\(devtools\)", "harness", "ai-config"),
    (r"fix\(assethold\)|assethold.*tz|assethold.*datetime|assethold.*stock", "personal-finance", "financial-analysis"),
    (r"governance|standardization|arch\(", "harness", "workflow"),
    (r"feat\(work.queue\)|feat\(workflow\)", "work-queue-infrastructure", "work-queue"),
    (r"analysis\(workspace\)", "harness", "work-queue"),
    (r"docs\(skills?\)", "harness", "skills"),
    (r"improve\(workflow\)", "harness", "workflow"),
    (r"test\(workflow\)|test\(review\)", "harness", "testing"),
    (r"doc\(review\)", "harness", "cross-review"),
    (r"chore\(digitalmodel\)", "engineering-module", "digitalmodel"),
    (r"chore\(doc.index\)", "document-intelligence", "document-index"),
    (r"feat\(document.index\)", "document-intelligence", "document-index"),
    (r"data\(vessel|data\(world", "data", "data-extraction"),
    (r"feat\(orcaflex\)", "engineering", "orcaflex"),
    (r"feat\(skills\)", "harness", "skills"),
    (r"doris.*calc|doris.*workflow", "engineering", "general"),
    (r"aceengineer.admin|aceengineer.*strategy", "business", "strategy"),
    (r"feat\(assetutilities/calculations\)", "engineering-calculations", "standards"),
    (r"session.*signal|session.*emitter|/clear.*plan.mode", "harness", "session"),
]

# Compiled patterns
COMPILED_RULES = [(re.compile(pat, re.IGNORECASE), cat, sub) for pat, cat, sub in RULES]


def classify(title: str) -> tuple[str, str] | None:
    """Return (category, subcategory) or None if no match."""
    if not title:
        return None
    for pattern, cat, sub in COMPILED_RULES:
        if pattern.search(title):
            return cat, sub
    return None


def read_frontmatter(path: Path) -> tuple[dict, str, str]:
    """Return (frontmatter_dict, frontmatter_text, body_text)."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)", text, re.DOTALL)
    if not m:
        return {}, "", text
    fm_text = m.group(1)
    body = m.group(2)
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip("\"'")
    return fm, fm_text, body


def add_fields(path: Path, category: str, subcategory: str, dry_run: bool) -> bool:
    """Add category and subcategory to frontmatter. Returns True if modified."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return False

    fm_text = m.group(1)
    new_lines = []
    has_cat = False
    has_sub = False

    for line in fm_text.split("\n"):
        if line.startswith("category:"):
            has_cat = True
        if line.startswith("subcategory:"):
            has_sub = True
        new_lines.append(line)

    if not has_cat:
        new_lines.append(f"category: {category}")
    if not has_sub:
        new_lines.append(f"subcategory: {subcategory}")

    if has_cat and has_sub:
        return False

    new_fm = "\n".join(new_lines)
    new_text = text[:m.start(1)] + new_fm + text[m.end(1):]

    if not dry_run:
        path.write_text(new_text)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    dirs = ["pending", "working", "done", "blocked", "archived"]
    updated = 0
    skipped_no_match = 0
    skipped_no_title = 0
    skipped_has_both = 0
    total = 0
    no_match_titles = []

    for d in dirs:
        dirpath = QUEUE_DIR / d
        if not dirpath.is_dir():
            continue
        for f in sorted(dirpath.glob("WRK-*.md")):
            fm, fm_text, body = read_frontmatter(f)
            if fm.get("category") and fm.get("subcategory"):
                skipped_has_both += 1
                continue

            total += 1
            if args.limit and total > args.limit:
                break

            title = fm.get("title", "")
            if not title:
                skipped_no_title += 1
                continue

            result = classify(title)
            if not result:
                skipped_no_match += 1
                no_match_titles.append(f"{f.name}: {title}")
                continue

            cat, sub = result
            existing_cat = fm.get("category", "")
            existing_sub = fm.get("subcategory", "")
            final_cat = existing_cat or cat
            final_sub = existing_sub or sub

            if add_fields(f, final_cat, final_sub, args.dry_run):
                prefix = "DRY-RUN " if args.dry_run else ""
                print(f"  {prefix}{f.name}: +category={final_cat} +subcategory={final_sub}")
                updated += 1

    print(f"\nBackfill complete:")
    print(f"  {updated} updated")
    print(f"  {skipped_has_both} already had both fields")
    print(f"  {skipped_no_title} no title in frontmatter")
    print(f"  {skipped_no_match} no classification match")
    print(f"  {total} total processed")

    if no_match_titles:
        print(f"\nUnmatched titles ({len(no_match_titles)}):")
        for t in no_match_titles:
            print(f"  {t}")


if __name__ == "__main__":
    main()
