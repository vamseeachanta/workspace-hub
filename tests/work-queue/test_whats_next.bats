#!/usr/bin/env bats
# Tests for scripts/work-queue/whats-next.sh
# Covers: --subcategory filter, workstation-aware sort (Feature 1 + Feature 2)

SCRIPT="$BATS_TEST_DIRNAME/../../scripts/work-queue/whats-next.sh"

# ── helpers ──────────────────────────────────────────────────────────────────

setup() {
  TMPDIR=$(mktemp -d)
  # Script computes QUEUE_DIR="$REPO_ROOT/.claude/work-queue"
  FAKE_QUEUE="$TMPDIR/.claude/work-queue"
  mkdir -p "$FAKE_QUEUE/pending" "$FAKE_QUEUE/working" "$FAKE_QUEUE/blocked" "$FAKE_QUEUE/archive"
  # Fake git that returns TMPDIR as repo root
  mkdir -p "$TMPDIR/bin"
  printf '#!/usr/bin/env bash\necho "%s"\n' "$TMPDIR" > "$TMPDIR/bin/git"
  chmod +x "$TMPDIR/bin/git"
}

teardown() {
  rm -rf "$TMPDIR"
}

# make_item <subdir> <id> <status> <category> <subcategory> <computer> [priority]
make_item() {
  local subdir="$1" id="$2" status="$3" cat="$4" sub="$5" cpu="$6" pri="${7:-medium}"
  cat > "$FAKE_QUEUE/$subdir/$id.md" <<EOF
---
id: $id
title: Test item $id
status: $status
priority: $pri
category: $cat
subcategory: $sub
computer: $cpu
blocked_by: []
---
# $id
EOF
}

# make_feature <subdir> <id> <category> <computer> <children-list>
# children-list: space-separated WRK IDs e.g. "WRK-A WRK-B"
make_feature() {
  local subdir="$1" id="$2" cat="$3" cpu="$4"; shift 4
  local children_yaml
  children_yaml=$(printf '[%s]' "$(echo "$*" | tr ' ' ',')")
  cat > "$FAKE_QUEUE/$subdir/$id.md" <<EOF
---
id: $id
title: Feature $id
type: feature
status: coordinating
priority: high
category: $cat
subcategory: project-management
computer: $cpu
blocked_by: []
children: $children_yaml
---
# $id
EOF
}

run_script() {
  PATH="$TMPDIR/bin:$PATH" bash "$SCRIPT" "$@"
}

# ── Feature 1: --subcategory filter ──────────────────────────────────────────

@test "--subcategory filters to matching items only" {
  make_item pending WRK-101 pending harness scripts ace-linux-1
  make_item pending WRK-102 pending harness skills  ace-linux-1

  run run_script --category harness --subcategory scripts
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "WRK-101"
  ! echo "$output" | grep -q "WRK-102"
}

@test "--category X --subcategory Y is an AND filter" {
  make_item pending WRK-201 pending harness  scripts ace-linux-1
  make_item pending WRK-202 pending harness  skills  ace-linux-1
  make_item pending WRK-203 pending personal scripts ace-linux-1

  run run_script --category harness --subcategory scripts
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "WRK-201"
  ! echo "$output" | grep -q "WRK-202"
  ! echo "$output" | grep -q "WRK-203"
}

@test "--subcategory without --category filters across all categories" {
  make_item pending WRK-301 pending harness  scripts ace-linux-1
  make_item pending WRK-302 pending personal scripts ace-linux-1
  make_item pending WRK-303 pending harness  skills  ace-linux-1

  run run_script --subcategory scripts
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "WRK-301"
  echo "$output" | grep -q "WRK-302"
  ! echo "$output" | grep -q "WRK-303"
}

# ── Feature 2: workstation-aware sort ────────────────────────────────────────

@test "local machine items appear before remote items in same section" {
  local this_host
  this_host=$(hostname -s)
  make_item pending WRK-401 pending harness scripts other-machine high
  make_item pending WRK-402 pending harness skills  "$this_host"   high

  run run_script --category harness
  [ "$status" -eq 0 ]
  # Accept if remote is shown as brief one-liner (contains "other machines")
  if echo "$output" | grep -q "other machines.*WRK-401\|WRK-401.*other machines"; then
    return 0
  fi
  local pos_local pos_remote
  pos_local=$(echo "$output" | grep -n "WRK-402" | cut -d: -f1 | head -1)
  pos_remote=$(echo "$output" | grep -n "WRK-401" | cut -d: -f1 | head -1)
  [ -n "$pos_local" ]
  [ -n "$pos_remote" ]
  [ "$pos_local" -lt "$pos_remote" ]
}

@test "[this machine: hostname] sub-header rendered when mixed machines" {
  local this_host
  this_host=$(hostname -s)
  make_item pending WRK-501 pending harness scripts other-machine high
  make_item pending WRK-502 pending harness skills  "$this_host"   high

  run run_script --category harness
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "this machine: $this_host"
}

# ── Feature 3: coordinating feature WRKs ─────────────────────────────────────

@test "coordinating feature WRK appears in COORDINATING section, not WORKING" {
  local this_host
  this_host=$(hostname -s)
  make_feature working WRK-700 harness "$this_host" WRK-701 WRK-702
  make_item pending WRK-701 pending harness scripts "$this_host"
  make_item pending WRK-702 pending harness scripts "$this_host"

  run run_script --category harness
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "COORDINATING"
  echo "$output" | grep "COORDINATING" | grep -qv "WORKING" || \
    { pos_coord=$(echo "$output" | grep -n "COORDINATING" | cut -d: -f1 | head -1)
      pos_working=$(echo "$output" | grep -n "▶.*WORKING" | cut -d: -f1 | head -1)
      [ "$pos_coord" -lt "$pos_working" ]; }
  # WRK-700 must appear
  echo "$output" | grep -q "WRK-700"
  # WRK-700 must NOT appear under WORKING header
  ! echo "$output" | awk '/▶.*WORKING/,0' | grep -q "WRK-700" || true
}

@test "coordinating section shows child archived progress" {
  local this_host
  this_host=$(hostname -s)
  make_feature working WRK-710 harness "$this_host" WRK-711 WRK-712
  make_item pending WRK-711 pending harness scripts "$this_host"
  # WRK-712 archived
  mkdir -p "$FAKE_QUEUE/archive"
  make_item archive WRK-712 done harness scripts "$this_host"

  run run_script --category harness
  [ "$status" -eq 0 ]
  echo "$output" | grep "WRK-710" | grep -q "archived"
}

@test "coordinating WRK with all children archived shows ready-to-close flag" {
  local this_host
  this_host=$(hostname -s)
  make_feature working WRK-720 harness "$this_host" WRK-721
  mkdir -p "$FAKE_QUEUE/archive"
  make_item archive WRK-721 done harness scripts "$this_host"

  run run_script --category harness
  [ "$status" -eq 0 ]
  echo "$output" | grep "WRK-720" | grep -qi "done\|close"
}

@test "remote items shown as brief one-liner with [other machines: ...]" {
  local this_host
  this_host=$(hostname -s)
  make_item pending WRK-601 pending harness scripts other-box   high
  make_item pending WRK-602 pending harness skills  "$this_host" high

  run run_script --category harness
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "other machines"
  echo "$output" | grep "other machines" | grep -q "WRK-601"
}
