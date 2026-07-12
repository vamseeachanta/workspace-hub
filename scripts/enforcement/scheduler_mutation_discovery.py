"""Conservative scheduler-indirection and operation-shape derivation."""
from __future__ import annotations

import re


def derive_kanban_operations(records: dict[bytes, bytes]) -> set[str]:
    body = records.get(b"scripts/install/setup-kanban-loader-timer.sh", b"")
    code = b"\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith(b"#")
    )
    checks = {
        "install:systemd-unit-write": rb"do_install\(\)[\s\S]+service_body \| write_unit",  # scheduler-mutation-forensic
        "install:systemd-enable": rb"do_install\(\)[\s\S]+run_systemctl enable --now",  # scheduler-mutation-forensic
        "install:crontab-replace": rb"do_install\(\)[\s\S]+run_crontab -",  # scheduler-mutation-forensic
        "uninstall:systemd-unit-remove": rb"do_uninstall\(\)[\s\S]+remove_unit \"\$SERVICE_PATH\"",  # scheduler-mutation-forensic
        "uninstall:systemd-disable": rb"do_uninstall\(\)[\s\S]+run_systemctl disable --now",  # scheduler-mutation-forensic
        "uninstall:crontab-replace": rb"do_uninstall\(\)[\s\S]+run_crontab -",  # scheduler-mutation-forensic
    }
    return {name for name, pattern in checks.items() if re.search(pattern, code)}


def has_primitive_alias_call(code: bytes) -> bool:
    cron_name = rb"cron" + rb"tab"
    task_name = rb"Scheduled" + rb"Task"
    shell = re.findall(
        rb"(?m)^\s*([A-Za-z_]\w*)\s*=\s*['\"]?(" + cron_name + rb")['\"]?\s*$",
        code,
    )
    powershell = re.findall(
        rb"(?mi)^\s*\$([A-Za-z_]\w*)\s*=\s*['\"]"
        rb"((?:Register|Unregister)-" + task_name + rb")['\"]\s*$",
        code,
    )
    for variable, _primitive in shell:
        call = rb"(?m)(?:^|[|;]\s*)\"?\$\{?" + variable + rb"\}?\"?\s+-(?:\s|$)"
        if re.search(call, code):
            return True
    for variable, _primitive in powershell:
        reference = rb"\$" + variable + rb"\b"
        direct = rb"(?mi)^\s*&\s*" + reference
        expression = rb"(?mi)^\s*Invoke-Expression\b[^\n]*" + reference
        if re.search(direct, code) or re.search(expression, code):
            return True
    return False


def derive_windows_task_operations(records: dict[bytes, bytes]) -> set[str]:
    body = records.get(b"scripts/windows/setup-scheduler-tasks.ps1", b"")
    code = b"\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith(b"#")
    )
    task_name = rb"Scheduled" + rb"Task"
    checks = {
        "remove:unregister-fixed-task": (
            rb"if \(\$RemoveMode\) \{[\s\S]+Unregister-" + task_name + rb"[\s\S]+return"
        ),
        "replace:unregister-register-fixed-task": (
            rb"if \(\$existing\) \{[\s\S]+Unregister-" + task_name
            + rb"[\s\S]+Register-" + task_name
        ),
    }
    return {name for name, pattern in checks.items() if re.search(pattern, code)}
