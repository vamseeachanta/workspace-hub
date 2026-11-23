from __future__ import annotations

import ipaddress
import re
from pathlib import Path

import pytest

from tests.helpers.stale_reference_docs import scan_stale_reference_hits


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs/ops/remote-linux-access.md"
HANDOFF = ROOT / "docs/ops/ace-linux-2-handoff-runbook.md"
RELATED = [ROOT / "docs/README.md", ROOT / "docs/setup/README.md"]
RELATED += [ROOT / "docs/ops/machine-inventory.md", HANDOFF]
LEGACY = [ROOT / "config/tabby/REMOTE_ACCESS.md", ROOT / "config/tabby/TAILSCALE_SETUP.md"]
EXPECTED_CANONICAL_LINKS = {
    ROOT / "docs/README.md": "ops/remote-linux-access.md",
    ROOT / "docs/setup/README.md": "../ops/remote-linux-access.md",
    ROOT / "docs/ops/machine-inventory.md": "remote-linux-access.md",
    ROOT / "docs/ops/ace-linux-2-handoff-runbook.md": "remote-linux-access.md",
    ROOT / "config/tabby/REMOTE_ACCESS.md": "../../docs/ops/remote-linux-access.md",
    ROOT / "config/tabby/TAILSCALE_SETUP.md": "../../docs/ops/remote-linux-access.md",
}
ENDPOINT_DOCS = [RUNBOOK, *RELATED, *LEGACY]
SAFE_NETWORKS_BY_FILE = {RUNBOOK: {"100.64.0.0/10", "fd7a:115c:a1e0::/48"}}
TAILSCALE_RESERVED_ADDRESS_SOURCE = "tailscale.com/kb/1015/100.x-addresses"
NO_FORWARD_POLICY = "Never configure router port forwarding for SSH or port 22. " \
    "<!-- ssh-no-forward-policy -->"
LOCAL_TUNNEL_POLICY = "<!-- ssh-local-loopback-policy -->"
LOCAL_TUNNEL_POLICY_LINE = "- Opens an SSH tunnel from local port 5900 to " \
    f"ace-linux-2 localhost:5900. {LOCAL_TUNNEL_POLICY}"
EDGE_RE = re.compile(r"\b(?:router|wan|public|internet|external|inbound)\b", re.I)
TARGET_RE = re.compile(r"\bssh\b|\bport\s*:?[ ]*22\b|(?<!\d)22(?!\d)", re.I)
MARKDOWN_PREFIX_RE = re.compile(
    r"^\s*(?:>\s*)?(?:(?:[-*]\s+)(?:\[[ xX]\]\s+)?|\d+[.)]\s+)?")
DIRECT_DIRECTIVE_RE = re.compile(
    r"^(?:also\s+)?(?:open|map|forward|expose|publish|bind)\b",
    re.I,
)
EDGE_DIRECTIVE_RE = re.compile(
    r"^(?:also\s+)?(?:allow|permit|enable|accept|create|nat)\b",
    re.I,
)


def read_text_required(path: Path) -> str:
    assert path.is_file(), f"required documentation is missing: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def extract_ip_literals(line: str) -> set[str]:
    candidates = set(
        re.findall(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\w.])", line)
    )
    candidates.update(
        re.findall(
            r"(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}"
            r"(?:/\d{1,3})?(?![\w:])",
            line,
        )
    )
    valid: set[str] = set()
    for candidate in candidates:
        try:
            ipaddress.ip_network(candidate, strict=False)
        except ValueError:
            continue
        valid.add(candidate)
    return valid


def is_affirmative_ssh_forwarding(line: str) -> bool:
    line = MARKDOWN_PREFIX_RE.sub("", line)
    heading = re.search(r"^\s*#{1,6}\s+.*\bforward\w*\b", line, re.I)
    gateway = re.search(r"\bgatewayports\b\s+(?:yes|clientspecified)\b", line, re.I)
    mapping = re.search(r"\b(?:wan|router|public|external)\b.*(?:->|→).*", line, re.I)
    text_mapping = re.search(
        r"^(?:wan|router)\b.*\bport\s+\d{2,5}\b.*\bto\b.*"
        r"\b(?:linux\s+)?host\b.*\bport\s*22\b",
        line,
        re.I,
    )
    inverted_policy = re.search(
        r"^\s*(?:[-*]\s+)?(?:do not block|never prohibit)\b.*"
        r"(?:forward|expos)\w*.*\bssh\b",
        line,
        re.I,
    )
    if gateway or inverted_policy:
        return True
    if text_mapping or (TARGET_RE.search(line) and (heading or mapping)):
        return True
    for segment in re.split(r"[.;]|\s+[—–]\s+", line):
        segment = MARKDOWN_PREFIX_RE.sub("", segment)
        direct = DIRECT_DIRECTIVE_RE.search(segment)
        edge_direct = EDGE_DIRECTIVE_RE.search(segment) and EDGE_RE.search(segment)
        if TARGET_RE.search(segment) and (direct or edge_direct):
            return True
    return False


def is_local_tunnel_policy_line(path: Path, line: str) -> bool:
    return path == HANDOFF and line == LOCAL_TUNNEL_POLICY_LINE


def is_router_mapping_start(line: str) -> bool:
    stripped = MARKDOWN_PREFIX_RE.sub("", line)
    if not EDGE_RE.search(stripped):
        return False
    return bool(
        re.search(r"^(?:map|forward|nat)\b", stripped, re.I)
        or re.search(r"^open\b.*\b(?:port|route|rule|service|access)\b", stripped, re.I)
        or re.search(r"^create\b.*\b(?:rule|mapping|route|forward)\w*\b", stripped, re.I)
    )


def has_affirmative_ssh_forwarding(lines: list[str]) -> bool:
    if any(is_affirmative_ssh_forwarding(line) for line in lines):
        return True
    for start, line in enumerate(lines):
        if not is_router_mapping_start(line):
            continue
        blanks = 0
        for candidate in lines[start + 1 : start + 8]:
            if not candidate.strip():
                blanks += 1
            if blanks > 1:
                break
            if TARGET_RE.search(candidate):
                return True
    return False


def test_canonical_runbook_has_required_sections() -> None:
    text = read_text_required(RUNBOOK)
    required_sections = (
        "Authority", "Architecture", "Security controls", "Setup sequence",
        "Verification matrix", "Rollback and recovery", "Troubleshooting", "Drift ledger",
    )
    for section in required_sections:
        assert re.search(rf"^## {re.escape(section)}$", text, re.MULTILINE), section


def test_runbook_separates_transport_and_authentication() -> None:
    text = read_text_required(RUNBOOK).lower()
    assert "tailscale transport" in text
    assert "conventional openssh keys" in text
    assert "tailscale ssh is optional" in text


def test_docs_allow_only_cited_tailscale_networks_and_prohibit_public_ssh() -> None:
    violations: list[str] = []

    for path in ENDPOINT_DOCS:
        text = read_text_required(path)
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            for literal in extract_ip_literals(line):
                allowed = literal in SAFE_NETWORKS_BY_FILE.get(path, set())
                cited = TAILSCALE_RESERVED_ADDRESS_SOURCE in line
                if not (allowed and cited):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{line_no}: prohibited address {literal}"
                    )
        forwarding_lines = []
        for line in lines:
            if path in [RUNBOOK, *LEGACY] and line == NO_FORWARD_POLICY:
                continue
            if is_local_tunnel_policy_line(path, line):
                continue
            forwarding_lines.append(line)
        if has_affirmative_ssh_forwarding(forwarding_lines):
            violations.append(
                f"{path.relative_to(ROOT)}: affirmative SSH forwarding guidance"
            )

    assert read_text_required(RUNBOOK).splitlines().count(NO_FORWARD_POLICY) == 1
    assert not violations, "\n".join(violations)


@pytest.mark.parametrize(
    "prohibited_line",
    (
        "## SSH port forwarding", "> ## SSH port forwarding",
        "Forward port 22 to the Linux host.", "WAN:2222 -> ace-linux-2:22",
        "Map SSH to the Linux host.", "Open port 22 for remote access.",
        "Open SSH for remote access.",
        (
            "100.64.0.0/10 https://tailscale.com/kb/1015/100.x-addresses — "
            "Open public port 22 for SSH."
        ),
        "Expose SSH through internet port 2222.",
        "Publish SSH through public port 2222.",
        "Bind SSH to public port 2222.",
        "Allow inbound SSH on external port 2222.",
        "Enable GatewayPorts yes for SSH.",
        "GatewayPorts yes", "GatewayPorts clientspecified",
        "Expose SSH on the WAN.",
        "Expose SSH.", "Publish SSH.",
        "Bind SSH to all interfaces.", "Permit inbound SSH.",
        "Enable SSH on the WAN.",
        "Accept inbound SSH connections.",
        "Create a public router rule for SSH.",
        "NAT public port 2222 to SSH.",
        "Do not block forwarding SSH.",
        "> Do not block forwarding SSH.",
        "- [ ] Do not block forwarding SSH.",
        "WAN port 2222 to Linux host port 22.",
        "Router port 2222 to host port 22.",
        "> Forward port 22 to the Linux host.",
        "- [ ] Open SSH for remote access.",
    ),
)
def test_public_ssh_forwarding_mutations_are_rejected(prohibited_line: str) -> None:
    assert is_affirmative_ssh_forwarding(prohibited_line), prohibited_line


@pytest.mark.parametrize(
    "safe_line",
    (
        "Do not forward port 22.", "SSH forwarding is prohibited.",
        "Inbound SSH is not allowed.", "Never configure WAN port 2222 to Linux host port 22.",
        "SSH must remain bound to the private tailnet, never the public interface.",
        "Do not map router port 2222 to host port 22.",
    ),
)
def test_negative_ssh_policy_is_not_affirmative_guidance(safe_line: str) -> None:
    assert not is_affirmative_ssh_forwarding(safe_line), safe_line


@pytest.mark.parametrize(
    "prohibited_block",
    (
        ["Forward external port 2222 to the Linux host.", "Target: home.example.test:22"],
        ["Forward the router service to the Linux host.", "Destination port: 22 (SSH)"],
        ["Forward this router service:", "- Protocol: TCP", "- Port: 22 (SSH)"],
        ["Open a public route to the Linux host:", "- Description: travel", "- Service: SSH"],
        ["Map the router to the Linux host:", "", "Port 22"],
        ["Map the router to Linux.", "", "Protocol TCP.", "Port 22 SSH."],
        ["Map the router to Linux.", "", "Protocol TCP.", "Source any.",
            "Description travel.", "Enabled yes.", "Port 22 SSH.",
        ],
        ["Use this recipe to connect", "Forward port 22 to the Linux host."],
        ["Connection steps", "Open SSH for remote access."],
        ["Forward a local client port.", "Also map public port 22 to SSH."],
        ["Forward a local port over SSH.", "Make that listener public."],
        ["Forward a local port over SSH.", "Open that listener to the internet."],
        ["Forward a local client port.", "Expose SSH through internet port 2222."],
        ["Forward a local client port.", "Publish SSH through internet port 2222."],
    ),
)
def test_multiline_public_ssh_forwarding_mutations_are_rejected(
    prohibited_block: list[str],
) -> None:
    assert has_affirmative_ssh_forwarding(prohibited_block), prohibited_block


def test_split_mapping_scan_is_physically_bounded_and_respects_negative_policy() -> None:
    assert not has_affirmative_ssh_forwarding(
        ["Open the router admin page.", "", "", "", "First note.", "SSH stays private."]
    )
    assert not has_affirmative_ssh_forwarding(
        ["Never open the router for inbound traffic.", "Use SSH through Tailscale."]
    )


def test_local_loopback_tunnel_exception_is_exact_and_path_restricted() -> None:
    handoff_lines = read_text_required(HANDOFF).splitlines()
    policy_lines = [line for line in handoff_lines if LOCAL_TUNNEL_POLICY in line]
    assert policy_lines == [LOCAL_TUNNEL_POLICY_LINE]
    assert all(
        LOCAL_TUNNEL_POLICY not in read_text_required(path)
        for path in ENDPOINT_DOCS
        if path != HANDOFF
    )

    bypass = f"Forward SSH to a remote host; local client port loopback. {LOCAL_TUNNEL_POLICY}"
    assert not is_local_tunnel_policy_line(HANDOFF, bypass)


def test_runbook_declares_authority_hierarchy() -> None:
    text = read_text_required(RUNBOOK)
    authority = text.split("## Authority", 1)[1].split("\n## ", 1)[0]
    assert "../../config/workstations/registry.yaml" in authority
    assert "../../scripts/operations/connection/" in authority
    assert "machine-local secret storage" in authority.lower()
    assert authority.find("registry.yaml") < authority.find("remote-linux-access.md")
    assert authority.find("remote-linux-access.md") < authority.find("connection/")


def test_legacy_tabby_docs_defer_to_canonical_authority() -> None:
    for path in LEGACY:
        text = read_text_required(path)
        assert "Legacy client note" in text
        assert "canonical authority" in text.lower()
        assert EXPECTED_CANONICAL_LINKS[path] in text


def test_drift_ledger_has_required_rows_and_owners() -> None:
    text = read_text_required(RUNBOOK).lower()
    ledger = text.split("## drift ledger", 1)[1]
    required_rows = {
        "endpoint and alias exposure": "#3549",
        "ace-linux-2 capability and vnc divergence": "#3550",
        "ace-linux-1 historical address and installed-state claims": "#3551",
    }
    for drift, owner in required_rows.items():
        matching_line = next((line for line in ledger.splitlines() if drift in line), "")
        assert owner in matching_line, f"missing owner {owner} for {drift}"
        assert "unverified" in matching_line


@pytest.mark.parametrize("source,target", EXPECTED_CANONICAL_LINKS.items())
def test_expected_canonical_links_resolve(source: Path, target: str) -> None:
    text = read_text_required(source)
    assert f"]({target})" in text
    assert (source.parent / target).resolve() == RUNBOOK.resolve()


def test_security_controls_and_hardening_order() -> None:
    text = read_text_required(RUNBOOK).lower()
    for control in (
        "multi-factor authentication",
        "device approval",
        "least-privilege grants",
        "magicdns",
        "tailscale server device key expiry",
        "tailscale client device key expiry",
        "conventional openssh keys",
        "tailscale ssh is optional",
    ):
        assert control in text, control

    ordered_markers = (
        "preserve recovery access", "prove key authentication",
        "apply the hardening drop-in", "sudo sshd -t", "reload, do not restart",
        "prove a second session", "close recovery access",
    )
    offsets = [text.find(marker) for marker in ordered_markers]
    assert all(offset >= 0 for offset in offsets), dict(zip(ordered_markers, offsets))
    assert offsets == sorted(offsets)


def test_host_identity_effective_config_and_prior_state_are_proven() -> None:
    text = read_text_required(RUNBOOK).lower()
    normalized_text = " ".join(text.split())
    for safeguard in (
        "verify the ssh host key fingerprint",
        "out-of-band",
        "changed host key",
        "capture the prior drop-in state",
        "sudo sshd -t",
        "sudo sshd -t -c",
        "passwordauthentication no",
        "kbdinteractiveauthentication no",
        "permitrootlogin no",
        "restore the prior file or remove the newly created file",
    ):
        assert safeguard in normalized_text, safeguard
    assert "host=<client-resolved-hostname>" in text
    assert "host=<registry-hostname>" not in text
    assert "every authorized client context" in text


def test_verification_and_rollback_contract() -> None:
    text = read_text_required(RUNBOOK).lower()
    for evidence in (
        "batch-mode key login",
        "password authentication rejected",
        "keyboard-interactive authentication rejected",
        "root login rejected",
        "external network",
        "post-reboot",
        "router no-forward evidence",
        "rollback path",
    ):
        assert evidence in text, evidence


def test_primary_security_sources_are_cited() -> None:
    text = read_text_required(RUNBOOK).lower()
    for knowledge_base_path in (
        "1031/install-linux", "1099/device-approval", "1324/grants", "1081/magicdns",
        "1028/key-expiry", "1257/connection-types", "1193/tailscale-ssh",
    ):
        official_source = f"https://tailscale.com/kb/{knowledge_base_path}"
        assert official_source in text, official_source
    assert "man.openbsd.org/sshd_config" in text


def test_changed_durable_docs_have_no_stale_references() -> None:
    durable_docs = [RUNBOOK, *RELATED]
    hits: list[str] = []
    for path in durable_docs:
        read_text_required(path)
        hits.extend(scan_stale_reference_hits(str(path.relative_to(ROOT))))
    assert not hits, "\n".join(hits)
