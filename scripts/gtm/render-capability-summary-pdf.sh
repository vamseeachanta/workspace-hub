#!/usr/bin/env bash
# Render capability-summary HTML -> 1-page PDF. Reproducible, fail-fast.
# Per plan: docs/plans/2026-04-19-issue-2344-capability-summary-pdf.md
# Must be run from workspace-hub repo root.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

HTML_SRC="docs/gtm/website-pages/capability-summary.html"
PDF_INTERNAL="docs/gtm/capability-summary.pdf"
PDF_PUBLIC="aceengineer-website/assets/capability-summary-v1.pdf"
SIDECAR="aceengineer-website/assets/capability-summary.pdf.meta"
PDF_PUBLIC_SHA="${PDF_PUBLIC}.sha256"
APPROVED_CHROME_MAJOR="147"

# --- 0. Precondition checks --------------------------------------------------
command -v google-chrome >/dev/null || { echo "FAIL: google-chrome not installed"; exit 1; }
command -v pdfinfo       >/dev/null || { echo "FAIL: pdfinfo (poppler-utils) not installed"; exit 1; }
command -v pdffonts      >/dev/null || { echo "FAIL: pdffonts (poppler-utils) not installed"; exit 1; }
command -v pdftotext     >/dev/null || { echo "FAIL: pdftotext (poppler-utils) not installed"; exit 1; }
command -v sha256sum     >/dev/null || { echo "FAIL: sha256sum not installed"; exit 1; }
test -f "$HTML_SRC"                 || { echo "FAIL: missing $HTML_SRC"; exit 1; }

# --- 1. Chrome version pin ---------------------------------------------------
CHROME_VERSION="$(google-chrome --version | awk '{print $NF}')"
CHROME_MAJOR="${CHROME_VERSION%%.*}"
if [ "$CHROME_MAJOR" != "$APPROVED_CHROME_MAJOR" ]; then
  echo "FAIL: Chrome major $CHROME_MAJOR != approved $APPROVED_CHROME_MAJOR"
  echo "Update APPROVED_CHROME_MAJOR in this script after re-verifying 1-page layout with the new Chrome."
  exit 1
fi
echo "Chrome version: $CHROME_VERSION (approved)"

# --- 2. Render ---------------------------------------------------------------
# Pinned flags:
#   --no-sandbox           required for container/CI; harmless on this host.
#   --disable-gpu          prevents GPU-init error spam in headless.
#   --no-pdf-header-footer suppresses Chrome's default page/URL/timestamp headers.
#   --print-background     CRITICAL: without this the navy/orange gradient prints white.
#   --virtual-time-budget  advances virtual clock up to 5s so @font-face load completes.
google-chrome \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --print-to-pdf="$PDF_INTERNAL" \
  --no-pdf-header-footer \
  --print-background \
  --virtual-time-budget=5000 \
  "file://$REPO_ROOT/$HTML_SRC"

# --- 3. Post-render assertions (fail-fast gates) -----------------------------
# 3a. Exactly 1 page
PAGES="$(pdfinfo "$PDF_INTERNAL" | awk '/^Pages:/{print $2}')"
if [ "$PAGES" != "1" ]; then
  echo "FAIL: rendered PDF is $PAGES pages; must be exactly 1. NOT staging. NOT copying to public asset path."
  echo "Investigate CSS overflow in $HTML_SRC (@media print / .body padding / .service margin) before retry."
  exit 1
fi

# 3b. Letter page size (612 x 792 pts)
if ! pdfinfo "$PDF_INTERNAL" | grep -qE "Page size:[[:space:]]+612 x 792 pts"; then
  echo "FAIL: page size is not Letter (612 x 792 pts)"
  pdfinfo "$PDF_INTERNAL" | grep "Page size"
  exit 1
fi

# 3c. Inter font embedded (font-portability gate)
if ! pdffonts "$PDF_INTERNAL" | awk 'NR>2 {print $1}' | grep -qi Inter; then
  echo "FAIL: Inter font not embedded in PDF (pdffonts)."
  echo "Check that aceengineer-website/assets/fonts/inter/*.woff2 files exist AND capability-summary.html <link> points at the vendored path."
  pdffonts "$PDF_INTERNAL"
  exit 1
fi

# 3d. Credentials line present with U+2014 em-dash
if ! pdftotext "$PDF_INTERNAL" - | grep -qE 'Licensed P\.E\. — Houston'; then
  echo "FAIL: credentials line 'Licensed P.E. — Houston, TX' (em-dash U+2014) not found in extracted text."
  exit 1
fi

# 3e. Proof-point survives render
if ! pdftotext "$PDF_INTERNAL" - | grep -q '1,292'; then
  echo "FAIL: '1,292' proof-point not found in extracted text"
  exit 1
fi

# --- 4. Copy to public asset path (versioned filename) ---------------------
cp "$PDF_INTERNAL" "$PDF_PUBLIC"

# --- 5. Write output PDF sha256 sidecar ------------------------------------
(cd "$(dirname "$PDF_PUBLIC")" && sha256sum "$(basename "$PDF_PUBLIC")" > "$(basename "$PDF_PUBLIC_SHA")")

# --- 6. Write sidecar metadata ---------------------------------------------
SHA="$(sha256sum "$PDF_INTERNAL" | awk '{print $1}')"
PUB_SHA="$(sha256sum "$PDF_PUBLIC" | awk '{print $1}')"
GIT_SHA="$(git rev-parse HEAD)"
SOURCE_HTML_SHA="$(sha256sum "$HTML_SRC" | awk '{print $1}')"
RENDERED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$SIDECAR" <<EOF
# capability-summary.pdf sidecar metadata
# Written by scripts/gtm/render-capability-summary-pdf.sh
renderer: google-chrome
renderer_version: $CHROME_VERSION
html_source: $HTML_SRC
source_html_sha256: $SOURCE_HTML_SHA
git_sha: $GIT_SHA
rendered_at_utc: $RENDERED_AT
pages: $PAGES
sha256_internal: $SHA
output_pdf_sha256: $PUB_SHA
internal_path: $PDF_INTERNAL
public_path: $PDF_PUBLIC
public_url: https://www.aceengineer.com/assets/capability-summary-v1.pdf
EOF

echo "OK: rendered $PDF_INTERNAL ($PAGES page, Inter embedded, sha256=$SHA)"
echo "OK: copied to $PDF_PUBLIC"
echo "OK: sha256 sidecar written to $PDF_PUBLIC_SHA"
echo "OK: metadata sidecar written to $SIDECAR"
echo "Next: git add the new/updated files, review diff, commit (DO NOT push)."
