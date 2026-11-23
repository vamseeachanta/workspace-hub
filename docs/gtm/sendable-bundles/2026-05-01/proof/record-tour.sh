#!/usr/bin/env bash
# Record the 2026-05-01 GTM bundle tour via google-chrome --headless.
# Captures one full-page screenshot per URL, then ffmpeg-encodes to MP4 + GIF.
# Output lands in this directory; intentionally tracked so the proof artifact
# is reproducible.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMES_DIR="${SCRIPT_DIR}/frames"
OUT_GIF="${SCRIPT_DIR}/2026-05-01-gtm-bundle-tour.gif"
OUT_MP4="${SCRIPT_DIR}/2026-05-01-gtm-bundle-tour.mp4"
WIN_W=1600
WIN_H=900
HOLD_S=3        # human-readable speed: 3 sec per page
WORK_TMP="$(mktemp -d)"
trap 'rm -rf "${WORK_TMP}"' EXIT

mkdir -p "${FRAMES_DIR}"
rm -f "${FRAMES_DIR}"/*.png

URLS=(
  "https://www.aceengineer.com/outreach/"
  "https://www.aceengineer.com/outreach/vessel-contractor-brochure.html"
  "https://www.aceengineer.com/outreach/fowt-mooring-screening.html"
  "https://www.aceengineer.com/demos/freespan.html"
  "https://www.aceengineer.com/demos/wall-thickness.html"
  "https://www.aceengineer.com/demos/mudmat.html"
  "https://www.aceengineer.com/demos/pipelay.html"
  "https://www.aceengineer.com/demos/jumper-installation.html"
  "https://www.aceengineer.com/demos/mooring.html"
)

i=0
# Chrome stderr goes to a log file (not /dev/null) so failures are debuggable.
CHROME_LOG="${WORK_TMP}/chrome.log"

for url in "${URLS[@]}"; do
  out=$(printf "%s/frame_%02d.png" "${FRAMES_DIR}" "${i}")
  echo "[${i}] ${url}"
  google-chrome \
    --headless=new \
    --disable-gpu \
    --hide-scrollbars \
    --no-sandbox \
    --window-size="${WIN_W},${WIN_H}" \
    --virtual-time-budget=8000 \
    --screenshot="${out}" \
    "${url}" 2>>"${CHROME_LOG}"
  # Per-URL validation: refuse to silently encode a tour with missing pages.
  if [ ! -s "${out}" ]; then
    echo "ERROR: chrome produced empty/missing screenshot for ${url}" >&2
    echo "       see ${CHROME_LOG} for diagnostic output" >&2
    exit 1
  fi
  i=$((i + 1))
done

# Post-loop assertion: frame count must equal URL count exactly.
expected_frames=${#URLS[@]}
actual_frames=$(ls "${FRAMES_DIR}"/*.png 2>/dev/null | wc -l)
if [ "${actual_frames}" -ne "${expected_frames}" ]; then
  echo "ERROR: expected ${expected_frames} frames, got ${actual_frames}" >&2
  echo "       see ${CHROME_LOG} for diagnostic output" >&2
  exit 1
fi

echo
echo "Captured ${actual_frames} frames (expected ${expected_frames}, all non-empty)."

# Build a concat list (each frame held HOLD_S seconds)
CONCAT="${WORK_TMP}/concat.txt"
: > "${CONCAT}"
for f in "${FRAMES_DIR}"/*.png; do
  printf "file '%s'\nduration %d\n" "${f}" "${HOLD_S}" >> "${CONCAT}"
done
# Repeat the last frame so ffmpeg honors its duration
last=$(ls "${FRAMES_DIR}"/*.png | tail -1)
printf "file '%s'\n" "${last}" >> "${CONCAT}"

echo
echo "Encoding MP4 (H.264, screen-content tuning)..."
ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i "${CONCAT}" \
  -vf "scale=1280:-2:flags=lanczos,fps=15" \
  -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p \
  -tune stillimage -movflags +faststart \
  "${OUT_MP4}"

echo "Encoding GIF (palette + dithering for screen content)..."
PALETTE="${WORK_TMP}/palette.png"
ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i "${CONCAT}" \
  -vf "scale=900:-1:flags=lanczos,fps=10,palettegen=stats_mode=diff" \
  "${PALETTE}"

ffmpeg -y -hide_banner -loglevel error \
  -f concat -safe 0 -i "${CONCAT}" -i "${PALETTE}" \
  -filter_complex "scale=900:-1:flags=lanczos,fps=10[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" \
  "${OUT_GIF}"

echo
echo "Done."
ls -la "${OUT_MP4}" "${OUT_GIF}"
