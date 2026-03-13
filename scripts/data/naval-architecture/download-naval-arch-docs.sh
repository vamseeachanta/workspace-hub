#!/usr/bin/env bash
# ABOUTME: Download open-access naval architecture documents to /mnt/ace/docs/_standards/SNAME/
# ABOUTME: Sources: direct PDFs (SNAME, Tupper, Biran), Internet Archive, maritime.org ship plans
# Usage: bash scripts/data/naval-architecture/download-naval-arch-docs.sh [--dry-run]

set -euo pipefail

DEST="/mnt/ace/docs/_standards/SNAME"
LOG_DIR="$(git rev-parse --show-toplevel)/.claude/work-queue/assets/WRK-1151"
LOG_FILE="${LOG_DIR}/download.log"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

mkdir -p "${DEST}/textbooks"
mkdir -p "${DEST}/ship-plans"
mkdir -p "${DEST}/hydrostatics-stability"
mkdir -p "${LOG_DIR}"

# shellcheck source=scripts/lib/download-helpers.sh
source "$(git rev-parse --show-toplevel)/scripts/lib/download-helpers.sh"

log "=== Naval Architecture Download — WRK-1151 ==="
log "Destination: ${DEST}"
log "Dry run: ${DRY_RUN}"

# ─────────────────────────────────────────────
# TEXTBOOKS — direct PDF links
# ─────────────────────────────────────────────
log "--- Textbooks ---"

download \
  "https://navalifpe.wordpress.com/wp-content/uploads/2011/09/principles-of-naval-architecture-vol-1-sname.pdf" \
  "${DEST}/textbooks" \
  "Principles-of-Naval-Architecture-Vol1-SNAME.pdf"

download \
  "https://navalifpe.files.wordpress.com/2011/09/principles-of-naval-architecture-vol-2-sname.pdf" \
  "${DEST}/textbooks" \
  "Principles-of-Naval-Architecture-Vol2-SNAME.pdf"

download \
  "https://ftp.idu.ac.id/wp-content/uploads/ebook/tdg/ADNVANCED%20MILITARY%20PLATFORM%20DESIGN/Principles%20of%20Naval%20Architecture%20(Second%20Revision),%20Volume%20I.pdf" \
  "${DEST}/textbooks" \
  "Principles-of-Naval-Architecture-SecondRevision-Vol1.pdf"

download \
  "https://home.hvl.no/ansatte/gste/ftp/MarinLab_files/Litteratur/IntroductionToNavalArchitecture_Tupper1996.pdf" \
  "${DEST}/textbooks" \
  "Introduction-to-Naval-Architecture-Tupper-1996.pdf"

# Internet Archive — direct download URLs
download \
  "https://archive.org/download/Comstock1942NavalArchitecture/Comstock%201942%20Naval%20architecture_text.pdf" \
  "${DEST}/textbooks" \
  "Introduction-to-Naval-Architecture-Comstock-1942.pdf"

# Note: introductiontona0000gill, navalarchitectur0000baxt are access-restricted borrow-only — skipped.

download \
  "https://archive.org/download/principles-of-naval-architecture-vol-ii-resistance-propulsion-and-vibration/Principles_Of_Naval_Architecture_Vol_II_-_Resistance%2C_Propulsion_and_Vibration.pdf" \
  "${DEST}/textbooks" \
  "Principles-of-Naval-Architecture-Vol2-Resistance-Propulsion-Vibration.pdf"

# ─────────────────────────────────────────────
# ADDITIONAL RESOURCES (WRK-1151 Step 2 web search)
# ─────────────────────────────────────────────
log "--- Additional Resources (web search) ---"

# USNA EN400 — Principles of Ship Performance (full course textbook)
download \
  "https://www.usna.edu/NAOE/_files/documents/Courses/EN400/EN400_Course_Notes,_Summer_2020.pdf" \
  "${DEST}/textbooks" \
  "USNA-EN400-Principles-Ship-Performance-2020.pdf" || true

# DTIC — Engineering for Ship Production
download \
  "https://apps.dtic.mil/sti/pdfs/ADA452843.pdf" \
  "${DEST}/textbooks" \
  "DTIC-Engineering-for-Ship-Production.pdf" || true

# DTIC — Small Craft Design Guide (1977)
download \
  "https://apps.dtic.mil/sti/tr/pdf/ADA047494.pdf" \
  "${DEST}/textbooks" \
  "DTIC-Small-Craft-Design-Guide-1977.pdf" || true

# Attwood — Text-book of Theoretical Naval Architecture (1899, public domain)
download \
  "https://www.dieselduck.info/historical/06%20books/1899%20Therory%20of%20Naval%20Architecture.pdf" \
  "${DEST}/textbooks" \
  "Theoretical-Naval-Architecture-Attwood-1899.pdf" || true

# University of Michigan — Basic Naval Architecture Vol I
download \
  "https://deepblue.lib.umich.edu/bitstream/2027.42/809/2/78490.0001.001.pdf" \
  "${DEST}/textbooks" \
  "UMich-Basic-Naval-Architecture-Vol1.pdf" || true

# University of Michigan — Basic Naval Architecture Vol II
download \
  "https://deepblue.lib.umich.edu/bitstream/2027.42/810/2/78491.0001.001.pdf" \
  "${DEST}/textbooks" \
  "UMich-Basic-Naval-Architecture-Vol2.pdf" || true

# DNV-RP-C205 Environmental Conditions and Environmental Loads (2007)
download \
  "https://rules.dnv.com/docs/pdf/dnvpm/codes/docs/2007-10/RP-C205.pdf" \
  "${DEST}/hydrostatics-stability" \
  "DNV-RP-C205-Environmental-Conditions-Loads-2007.pdf" || true

# DNV-RP-H103 Modelling and Analysis of Marine Operations (2010)
download \
  "https://rules.dnv.com/docs/pdf/dnvpm/codes/docs/2010-04/RP-H103.pdf" \
  "${DEST}/hydrostatics-stability" \
  "DNV-RP-H103-Marine-Operations-2010.pdf" || true

# Ship Structural Analysis and Design (Hughes & Paik)
download \
  "https://rexresearch1.com/BoatShipBuildingLibrary/ShipStructuralAnalysisDesign.pdf" \
  "${DEST}/textbooks" \
  "Ship-Structural-Analysis-Design-Hughes-Paik.pdf" || true

# ─────────────────────────────────────────────
# HYDROSTATICS, STABILITY & RESISTANCE
# ─────────────────────────────────────────────
log "--- Hydrostatics / Stability / Resistance ---"

download \
  "https://home.hvl.no/ansatte/gste/ftp/mas124_intro_marinteknikk/Litteratur/Kompendier_Books/Ship_hydrostatics_and_stability_Biran.pdf" \
  "${DEST}/hydrostatics-stability" \
  "Ship-Hydrostatics-and-Stability-Biran.pdf"

download \
  "https://rexresearch1.com/BoatShipBuildingLibrary/ShipHydrostaticsStability.pdf" \
  "${DEST}/hydrostatics-stability" \
  "Ship-Hydrostatics-and-Stability-2ndEd.pdf"

download \
  "https://rexresearch1.com/BoatShipBuildingLibrary/PrinciplesNavalArchitShipResistanceFlow.pdf" \
  "${DEST}/hydrostatics-stability" \
  "Principles-Naval-Architecture-Ship-Resistance-Flow.pdf"

# ─────────────────────────────────────────────
# ABS — classification rules (freely downloadable from eagle.org)
# ─────────────────────────────────────────────
log "--- ABS ---"

download \
  "https://ww2.eagle.org/content/dam/eagle/rules-and-resources/RuleManager2/intro-to-abs-rules-and-guides.pdf" \
  "${DEST}/textbooks" \
  "ABS-Intro-to-Rules-and-Guides.pdf"

# ABS Marine Vessel Rules — hull structure (Part 4) — WAF may block wget
download \
  "https://ww2.eagle.org/content/dam/eagle/rules-and-guides/current/other/1-rules-for-building-and-classing-marine-vessels-2024/1-mvr-part-4-jan24.pdf" \
  "${DEST}/textbooks" \
  "ABS-MVR-Part4-Vessel-Systems-Machinery-2024.pdf" || log "NOTE: ABS WAF blocks wget — download manually via browser"

# ─────────────────────────────────────────────
# IMO — freely available convention extracts
# ─────────────────────────────────────────────
log "--- IMO ---"

# UK MCA guidance on intact stability
download \
  "https://assets.publishing.service.gov.uk/media/6441189f22ef3b000f66f5dc/MSIS43_Intact_Stability_R05.23.pdf" \
  "${DEST}/hydrostatics-stability" \
  "UK-MCA-MSIS43-Intact-Stability-Guidance.pdf"

# IMO guidelines on intact stability 2014 (maritime mutual copy — may 403)
download \
  "https://maritime-mutual.com/wp-content/uploads/2020/06/Vol_3_2014_Guidelines_on_Intact_Stabili.pdf" \
  "${DEST}/hydrostatics-stability" \
  "IMO-Guidelines-Intact-Stability-2014.pdf" || log "NOTE: IMO guidelines download failed — try manually"

# SOLAS 2020 consolidated edition (Icelandic maritime authority copy)
download \
  "https://www.samgongustofa.is/media/english/SOLAS-2020-Consolidated-Edition.pdf" \
  "${DEST}/textbooks" \
  "SOLAS-2020-Consolidated-Edition.pdf" || log "NOTE: SOLAS download failed — try manually"

# ─────────────────────────────────────────────
# MARITIME.ORG SHIP PLANS (~100 PDFs)
# ─────────────────────────────────────────────
log "--- Maritime.org Ship Plans ---"

BASE="https://maritime.org/doc/plans"
PLANS=(
  ac3.pdf acr13.pdf acv6.pdf aks20.pdf am55.pdf ao106.pdf ap71.pdf ap110.pdf
  ap130.pdf apa170.pdf apd89.pdf apl24.pdf ar17.pdf arc3.pdf arg2.pdf
  ars5.pdf ars38.pdf bb34.pdf bb35.pdf bb42.pdf bb45.pdf bb48.pdf bb49.pdf
  bb62.pdf bb63.pdf bb64.pdf c6.pdf ca34.pdf cc2.pdf cg11.pdf cl89.pdf
  cv2.pdf cv3.pdf cv4.pdf cv5.pdf cv7.pdf cv12.pdf cv41.pdf cv60.pdf
  cv60color.pdf cve53-d79.pdf cve90.pdf cvl26.pdf cvs36.pdf dd1.pdf
  dd376.pdf dd445.pdf dd502.pdf dd616.pdf dd618.pdf dd692.pdf dd765.pdf
  de701.pdf dms5.pdf lsd21.pdf lsm354.pdf lst983.pdf mso438.pdf pc483.pdf
  pce874.pdf pg50.pdf pe60.pdf ss1.pdf s26-ss131.pdf ss167.pdf ss170.pdf
  ss190.pdf ss298.pdf ss339.pdf ss343.pdf ss350.pdf ss376.pdf ss381.pdf
  ss394.pdf ss481.pdf ssr481.pdf ss563.pdf ssg577.pdf sst2.pdf ytb142.pdf
  yf732.pdf yog86.pdf ysd76.pdf castle.pdf cgs119.pdf j311.pdf j337.pdf
  k124.pdf mcb143.pdf river.pdf tribal.pdf ec2-s-c1.pdf hmb1.pdf
  savannah.pdf ptboat.pdf r338.pdf marine-raven.pdf alligator.pdf x5.pdf
  wagl212.pdf wagl330.pdf wagl686.pdf wal605.pdf wlb307.pdf wli65303.pdf
  wlm688.pdf wlr311.pdf wmec628.pdf wpb82301.pdf wpc627.pdf
)

for plan in "${PLANS[@]}"; do
  download "${BASE}/${plan}" "${DEST}/ship-plans" "${plan}"
done

log "=== Download complete ==="
log "Files in ${DEST}:"
total=$(find "${DEST}" -name "*.pdf" | wc -l)
log "  Total PDFs: ${total}"
