#!/usr/bin/env bash
# ABOUTME: Build MYSTRAN (MIT, Nastran-compatible linear FEA solver) from source
# on Ubuntu/Debian into ~/.local/bin and smoke-test it with a CBAR cantilever.
#
# Usage (no root needed once prerequisites are present):
#   bash scripts/setup/mystran-build-linux.sh [--prefix DIR] [--ref TAG] [--skip-smoke]
#   ssh ace-linux-2 'bash -s' < scripts/setup/mystran-build-linux.sh
#
# Prerequisites (apt): gfortran cmake ninja-build libopenblas-dev git
#   -> run `sudo bash scripts/setup/engineering-suite-install.sh --fea` or
#      `sudo apt install -y gfortran cmake ninja-build libopenblas-dev git`
#
# Related: docs/research/mystran-eval.md, digitalmodel/src/digitalmodel/solvers/mystran
set -euo pipefail

PREFIX="${HOME}/.local"
REF="19.0.0"
SKIP_SMOKE=0
SRC_DIR="${TMPDIR:-/tmp}/mystran-src"
REPO="https://github.com/MYSTRANsolver/MYSTRAN.git"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix) PREFIX="$2"; shift 2 ;;
        --ref) REF="$2"; shift 2 ;;
        --skip-smoke) SKIP_SMOKE=1; shift ;;
        -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { printf '[mystran-build] %s\n' "$*"; }

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------
missing=()
for t in gfortran cmake ninja git; do
    command -v "$t" >/dev/null 2>&1 || missing+=("$t")
done
if [[ ${#missing[@]} -gt 0 ]]; then
    log "missing tools: ${missing[*]}"
    log "install with: sudo apt install -y gfortran cmake ninja-build libopenblas-dev git"
    exit 1
fi
# ldconfig lives in /sbin, which non-login ssh shells often omit from PATH
LDCONFIG="$(command -v ldconfig || echo /sbin/ldconfig)"
if ! "$LDCONFIG" -p 2>/dev/null | grep -q openblas && ! ls /usr/lib/*/libopenblas.so* >/dev/null 2>&1; then
    log "WARN: libopenblas not found; build may fall back to reference BLAS"
fi

# ---------------------------------------------------------------------------
# Fetch + build
# ---------------------------------------------------------------------------
if [[ -d "$SRC_DIR/.git" ]]; then
    log "reusing $SRC_DIR"
    git -C "$SRC_DIR" fetch --tags -q
else
    log "cloning $REPO ($REF) -> $SRC_DIR"
    git clone -q --depth 1 --branch "$REF" "$REPO" "$SRC_DIR"
fi
git -C "$SRC_DIR" checkout -q "$REF"

log "configuring (Ninja; no CMAKE_BUILD_TYPE — Release adds -DNDEBUG, which clobbers MYSTRAN's NDEBUG parameter)"
cmake -S "$SRC_DIR" -B "$SRC_DIR/build" -G Ninja >/dev/null
log "building with $(nproc) cores"
cmake --build "$SRC_DIR/build" --parallel "$(nproc)" | tail -3

BIN="$(find "$SRC_DIR" -type f -name mystran -perm -u+x | head -1)"
if [[ -z "$BIN" ]]; then
    log "ERROR: mystran binary not found after build"
    exit 1
fi
mkdir -p "$PREFIX/bin"
install -m 755 "$BIN" "$PREFIX/bin/mystran"
log "installed $PREFIX/bin/mystran"
case ":$PATH:" in
    *":$PREFIX/bin:"*) ;;
    *) log "NOTE: add $PREFIX/bin to PATH (e.g. in ~/.bashrc)" ;;
esac

# ---------------------------------------------------------------------------
# Smoke test: CBAR cantilever, tip deflection PL^3/3EI = 1.904762E-04 m
# ---------------------------------------------------------------------------
[[ $SKIP_SMOKE -eq 1 ]] && exit 0
WORK="$(mktemp -d)"
cat > "$WORK/cantilever.bdf" <<'EOF'
ID CANTILEVER,SMOKE
SOL 101
CEND
TITLE = CBAR CANTILEVER SMOKE TEST
SPC = 1
LOAD = 1
DISP = ALL
SPCFORCE = ALL
BEGIN BULK
GRID,1,,0.0,0.0,0.0
GRID,2,,0.25,0.0,0.0
GRID,3,,0.5,0.0,0.0
GRID,4,,0.75,0.0,0.0
GRID,5,,1.0,0.0,0.0
CBAR,1,1,1,2,0.0,0.0,1.0
CBAR,2,1,2,3,0.0,0.0,1.0
CBAR,3,1,3,4,0.0,0.0,1.0
CBAR,4,1,4,5,0.0,0.0,1.0
PBAR,1,1,0.01,8.3333333E-06,8.3333333E-06,1.4E-05
MAT1,1,2.1E+11,,0.3
SPC1,1,123456,1
FORCE,1,5,,1000.0,0.0,1.0,0.0
ENDDATA
EOF
(cd "$WORK" && "$PREFIX/bin/mystran" cantilever.bdf >/dev/null 2>&1) || true
F06="$(ls "$WORK"/cantilever.[Ff]06 2>/dev/null | head -1)"
if [[ -z "$F06" ]]; then
    log "SMOKE FAIL: no F06 produced (see $WORK)"
    exit 1
fi
TIP="$(awk '/D I S P L A C E M E N T S/{f=1} f && $1==5 && $2==0 {print $4; exit}' "$F06")"
log "smoke: tip T2 = ${TIP:-?} (expect 1.904762E-04)"
if [[ "$TIP" == 1.90476*E-04 ]]; then
    log "SMOKE PASS"
    rm -rf "$WORK"
else
    log "SMOKE FAIL: unexpected tip deflection (outputs in $WORK)"
    exit 1
fi
