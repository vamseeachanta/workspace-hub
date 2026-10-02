#!/usr/bin/env bash
# bundle-attest.sh — write a verifiable attestation sidecar next to each
# encrypted relocation bundle on /mnt/ace.
#
# WHY THIS AND NOT PERMISSIONS
# /mnt/ace is exported by Samba as [ace_drive] with `guest ok = yes`,
# `public = yes` AND `force user = vamsee` / `force group = vamsee`. Because
# every SMB guest is mapped to the owning user, unix permissions give NO
# protection whatsoever on this share — chmod would be theatre. age already
# authenticates content, so tampering surfaces as a decryption failure. The
# residual risk is silent TRUNCATION or DELETION, which these sidecars make
# detectable, and which the recorded entry counts make quantifiable.
#
# Also addresses the audit finding that source-to-bundle completeness was never
# provable: from now on each bundle carries its own entry count and a digest of
# its sorted member listing.
#
# Read-only with respect to the bundles themselves; writes only *.attest files.
set -uo pipefail
BULK=/mnt/ace/work-surface-bulk
KEY="$HOME/.config/age/keys.txt"
DRY_RUN="${DRY_RUN:-1}"

[ -s "$KEY" ] || { echo "FATAL: no age identity at $KEY"; exit 1; }

mapfile -t BUNDLES < <(find "$BULK" -name '*.tar.zst.age' | sort)
[ "${#BUNDLES[@]}" -gt 0 ] || { echo "no bundles found under $BULK"; exit 1; }
echo "found ${#BUNDLES[@]} bundles"

for b in "${BUNDLES[@]}"; do
  echo "=== $(basename "$b") ==="
  sz=$(stat -c %s "$b")
  echo "  bytes: $sz"
  if [ "$DRY_RUN" = 1 ]; then echo "  DRY-RUN: would write $b.attest"; continue; fi

  # Digest of the ciphertext — detects truncation or corruption at rest.
  cs=$(sha256sum "$b" | cut -d' ' -f1)

  # Decrypt-and-list in one pass. Never writes plaintext to disk; the listing is
  # streamed and reduced to a count plus a digest.
  listing=$(mktemp); trap 'rm -f "$listing"' RETURN
  if ! age -d -i "$KEY" "$b" | zstd -dc | tar -tf - > "$listing" 2>/dev/null; then
    echo "  FAILED to decrypt/list — NOT writing an attestation"; rm -f "$listing"; continue
  fi
  entries=$(wc -l < "$listing")
  ldigest=$(sort "$listing" | sha256sum | cut -d' ' -f1)
  rm -f "$listing"

  cat > "$b.attest" <<ATTEST
# attestation for $(basename "$b")
# written $(date -u '+%Y-%m-%dT%H:%M:%SZ') on $(hostname)
# Verify with:
#   sha256sum -c <(awk '/^ciphertext_sha256/{print \$2"  ${b}"}' "$b.attest")
#   age -d -i ~/.config/age/keys.txt "$b" | zstd -dc | tar -tf - | wc -l
ciphertext_sha256 $cs
ciphertext_bytes  $sz
tar_entries       $entries
tar_listing_sha256 $ldigest
age_recipient     $(age-keygen -y "$KEY")
ATTEST
  echo "  entries: $entries"
  echo "  wrote:   $(basename "$b").attest"
done

echo
echo "=== attestations on disk ==="
find "$BULK" -name '*.attest' -printf '%s  %p\n' | sort -k2
