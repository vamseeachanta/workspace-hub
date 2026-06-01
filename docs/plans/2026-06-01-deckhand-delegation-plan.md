# Deckhand work — delegation & lane plan (2026-06-01)

> Host: ace-linux-2 (all live Deckhand work). Gate: plan → adversarial review → **owner applies `status:plan-approved`** → TDD implement. Owner gate is load-bearing; agents never self-approve.

## Lanes

| Lane | Owner | Work |
|---|---|---|
| Synthesis | claude (main) | Decisions, glossary (`CONTEXT.md`), governance records, flowcharts, HTML dashboard, YAML config authoring, git, board/issue orchestration |
| Recon | codex | Repo-membership recon, git/gh choke-point recon (done) |
| Adversarial review | codex | Plan/POC review (done: CHANGES-REQUESTED), board+task+delegation review (this pass) |
| Build (post-approval) | codex preferred | TDD tests, `pre_tool_call` hook + PATH `git`/`gh` shim, canary wiring |

Constraint: only the `default` Hermes kanban profile exists on ace-linux-2 — no on-disk `claude`/`codex` profiles, so kanban auto-dispatch can't spawn named lanes yet. Lanes are represented by who runs the work + board comment authorship until profiles are provisioned.

## Kanban board → issue → status

Board `repo-workspace-hub-deckhand` (12 ready tasks).

| Task | Issue | GH status |
|---|---|---|
| t_d36d4625 | #2931 named scopes & repo policy | **plan-review** (this work) |
| t_28ed2d54 | #2902 delivery group + clearance | needs-plan (cross-ref posted) |
| t_d9be8df2 | #2903 reply guardrails | needs-plan (cross-ref) |
| t_c7a0a03b | #2901 platform parity recon | needs-plan (recon fed) |
| t_3d352af0 | #2741 destructive-action canary | needs-plan (cross-ref) |
| t_95dfc823 | #2900 board-level fanout | needs-plan (alignment posted) |
| t_84cbb375 | #2904 send_message fanout | needs-plan |
| t_0910b4d7 | #2905 operator docs | needs-plan |
| t_a6d843ec | #2906 product naming | needs-plan |
| t_df8756ca / t_7cfe94f6 / t_7731a586 | #2563/#1881/#1885 Telegram setup | operational |

## Claude task list (this session)

1. POC flowcharts — done
2. Codex adversarial review — done
3. Update GH issues — done (plan-review on #2931)
4. Update kanban board — done
5. Externalize config → generalized YAML — in progress
6. HTML review dashboard — in progress
7. Codex review of board+task+delegation — this pass
8. Commit artifacts — pending

## Open gate items (owner)
- Apply `status:plan-approved` on #2931 to authorize live cutover.
- External tester platform IDs for `acma`/`doris` operator allowlists (ecosystem off for them).
- Include archived `acma-projects`? planned `llm-wiki-doris`? channel→repo bindings?
