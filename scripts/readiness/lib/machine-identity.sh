# machine-identity.sh — shared machine-label resolution helpers (#3571).
#
# Some boxes run under an OS hostname that must NEVER appear in this public repo
# (legal-client-pii-gate precedent: PR #3279 was closed for exactly that). Those
# boxes declare their fleet identity in an OFF-REPO, gitignored identity file,
# provisioned once per box from the private client machine registry:
#
#   ~/.config/workspace-hub/machine-identity.yaml   (override: WORKSPACE_HUB_MACHINE_IDENTITY)
#   machine: "<logical-label>"          # required — one of KNOWN_MACHINE_LABELS
#   public_host: "<label>"              # optional — serialized as evidence host:; defaults to machine
#   expected_hostname: "<os-hostname>"  # optional — fail-loud guard against a file copied to the wrong box
#
# Resolution precedence everywhere: explicit flag/env > hardcoded hostname map >
# identity file > fail. The file can therefore never override a correctly-mapped
# host — it only exists for hostnames the public map cannot (must not) know.
#
# Sourced by collect-equality.sh and reconcile-ecosystem.sh. The PowerShell mirror
# (scripts/windows/equality-report.ps1) duplicates the label set as
# $KnownMachineLabels; tests/readiness/test_collect_equality.py asserts the two
# stay identical.

KNOWN_MACHINE_LABELS="dev-primary dev-secondary macbook-portable ace-win-1 ace-win-2"

is_known_machine_label() {
  case " $KNOWN_MACHINE_LABELS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

machine_identity_file() {
  printf '%s' "${WORKSPACE_HUB_MACHINE_IDENTITY:-${HOME}/.config/workspace-hub/machine-identity.yaml}"
}

# identity_get <key> <file> — value of a top-level `key: value` line (quotes stripped).
identity_get() {
  awk -v k="$1" -F': *' '$1==k {v=$2; sub(/\r$/,"",v); gsub(/^"|"$/,"",v); print v; exit}' "$2" 2>/dev/null
}

# resolve_identity_file <os-hostname>
#   stdout "<machine> <public_host>" and rc 0 on success
#   rc 2 when no identity file exists (caller falls through)
#   rc 1 + stderr diagnostic on a malformed/foreign file (caller must fail loud —
#   NEVER fall through, or a bad file would silently mint the wrong column).
#   Diagnostics intentionally omit hostname VALUES: stderr can end up in tracked logs.
resolve_identity_file() {
  local host="$1" f m ph eh
  f="$(machine_identity_file)"
  [ -f "$f" ] || return 2
  m="$(identity_get machine "$f")"
  if [ -z "$m" ]; then
    echo "machine-identity: $f lacks the required 'machine:' key" >&2
    return 1
  fi
  if ! is_known_machine_label "$m"; then
    echo "machine-identity: label in $f is not one of: $KNOWN_MACHINE_LABELS" >&2
    return 1
  fi
  eh="$(identity_get expected_hostname "$f")"
  if [ -n "$eh" ] && [ "$(printf '%s' "$eh" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$host" | tr '[:upper:]' '[:lower:]')" ]; then
    echo "machine-identity: expected_hostname in $f does not match this box — refusing a copied identity file" >&2
    return 1
  fi
  ph="$(identity_get public_host "$f")"
  printf '%s %s\n' "$m" "${ph:-$m}"
}
