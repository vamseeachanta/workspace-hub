"""Pinned disposition contract for the scheduler-mutation guard (#3470).

Extracted from `scheduler_mutation_contract.py` in workspace-hub#3784. That
module sits under a hard 400-line cap enforced by
`tests/enforcement/test_scheduler_mutation_task3.py`, and was at exactly 400
when a new mutation surface needed registering — so any addition broke the cap.

Extraction rather than raising the cap is deliberate: the cap is an enforcement
guard, and relaxing a guard so a change can land under it is the failure mode
the guard exists to prevent. Splitting the constants out keeps the limit intact
and follows the pattern already used for `render_html`, which lives in
`scheduler_mutation_report`.

**These values are a governance surface, not configuration.** They are pinned in
code precisely so a mutation surface cannot be disposed of by editing YAML
alone: the checker compares each `disposition_groups` entry in
`config/scheduled-tasks/mutation-surfaces.yaml` against the tuple here and fails
on any divergence. Treat every edit below as governance requiring review.
"""
from __future__ import annotations

#: Recognised defect classes. A disposition group must name exactly one.
DEFECT_CLASSES = {
    "mixed-destructive-ownership-authority",
    "untransactional-whole-crontab-replacement",
    "untransactional-dual-backend-replacement",
    "windows-task-mutation-without-verified-transaction",
    "transitive-mutation-error-swallowing",
    # workspace-hub#3792. Distinct in kind from the classes above: those
    # describe surfaces that DO NOT implement a transaction. This one describes
    # a surface whose transaction cannot be ATTESTED. The reference shape is
    # proven by the python-*-v1 attestations, which analyse a Python crontab
    # implementation; there is no equivalent for a shell installer writing
    # systemd units, so such a surface is pinned to `missing_transaction`
    # however carefully it is written — indistinguishable in the registry from
    # one that does nothing. Retire this class when #3792 lands.
    "systemd-user-transaction-unattestable",
}

#: group_id -> (tracking issue number, defect class, exact member set).
DISPOSITION_CONTRACT = {
    "legacy-crontab-writers": (
        3476,
        "untransactional-whole-crontab-replacement",
        {
            "scripts/coordination/context/setup_cron.sh",
            "scripts/operations/maintenance/setup_maintenance_cron.sh",
            "scripts/setup/setup-engineering-update-cron.sh",
        },
    ),
    "kanban-dual-backend": (
        3477,
        "untransactional-dual-backend-replacement",
        {"scripts/install/setup-kanban-loader-timer.sh"},
    ),
    "windows-task-writers": (
        3478,
        "windows-task-mutation-without-verified-transaction",
        {
            "scripts/windows/setup-scheduler-tasks.ps1",
            "scripts/coordination/context/setup_scheduled_task.ps1",
            "scripts/solver/setup-scheduler.ps1",
        },
    ),
    "harness-update": (
        3479,
        "transitive-mutation-error-swallowing",
        {"scripts/cron/harness-update.sh"},
    ),
    # workspace-hub#3784 — the first new mutation surface since this contract
    # was pinned. Registering it required editing this dict as well as the YAML
    # registry; that double edit is the intended path, not a workaround.
    "tmux-session-persistence": (
        3792,
        "systemd-user-transaction-unattestable",
        {"scripts/install/setup-tmux-autosave-timer.sh"},
    ),
}
