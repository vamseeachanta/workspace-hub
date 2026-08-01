# Licensed-solver dispatch — agent rule (#3721, deckhand#579)

**When to apply:** dispatching OrcaFlex, OrcaWave, AQWA, or any ANSYS work to a Windows fleet host from a control surface; or planning routing/capacity for those solvers.

**Why:** two full sessions were spent re-deriving the facts below, and both reached a *wrong* conclusion first. Every claim here was measured on a live host on 2026-07-31 and is stated with the evidence, so the next session tests a hypothesis rather than rebuilding one.

---

## 1. Never dispatch a licensed solver over direct SSH — use the Scheduled-Task path

Measured, same probe file, same host, minutes apart, seat confirmed free:

| path | OrcaFlex result |
|---|---|
| `ssh <host> '<solver command>'` | `DLLError Error code: 25` → `FlexNet Error 21` |
| `dispatch-run.ps1 -Action submit` | **`LICENCE_OK dll=11.6c`, exit 0** (reproduced twice) |

An **SSH public-key logon token cannot complete a FlexNet checkout.** A Windows Scheduled Task does **not** inherit that token — Task Scheduler establishes its own batch logon when the task fires, and that one works.

```bash
ssh <host> "powershell -NoProfile -ExecutionPolicy Bypass \
  -File '<repo>/scripts/windows/dispatch-run.ps1' \
  -Action submit -Shell bash -JobId <id> -Command '<solver command>'"
```

`-RunAsUser` / `/ru` / `/rp` are **NOT** required. That was a wrong hypothesis (workspace-hub#3738): it assumed the task inherits the caller's token. It does not. Do not add a credential path for this reason.

Ruled out by measurement, so do not re-investigate: env vars, `ORCINA_LICENSE_FILE`, the HKCU hive, and TCP reach to every licence port are byte-identical between the working and failing sessions; exporting the licence variable does not help; **session 0 is not the cause** — the deckhand licensed-run agent runs in session 0 as the same user and completes OrcaFlex at rc 0.

**AQWA is unaffected** and succeeds on both paths. Only the Orcina products care about the token.

## 2. Enumerate ALL FlexNet ports — there are four

`FlexNet.ini` reads `SERVER <host> ANY`. **`ANY` means the port is not pinned**, which is the signal that more than one server is in play. Querying one port and generalising to "the server" produced a confident, wrong "no OrcaFlex entitlement exists" claim on deckhand#579.

| port | serves |
|---|---|
| `1055` | ANSYS / AQWA — `aqwa_solve` ×2, `aqwa_pre` ×2, `ansys` ×2, `anshpc` ×4 |
| `27002` | **Orcina** — daemon UP, feature `Flex` v11.6, expiry **2027-03-15** |
| `27000`, `27001` | 0 features |

```
lmutil lmstat -c <port>@<licence-server> -a          # per port, all of them
lmutil lmstat -c 27002@<licence-server> -f Flex      # who holds the Orcina seat
```

## 3. Capacity: one `Flex` seat licenses a SESSION, not a job

**There is exactly one floating Orcina seat, fleet-wide** — not one per host. But a seat licenses a *session*, and a single dispatched job can fan out internally across the host's cores.

So model it as **one concurrent dispatch slot that parallelises inside itself** — never as "one model at a time". Treating it as the latter idles the entire box to respect a limit that does not apply at that level.

- Two concurrent *dispatches* fail on checkout, wherever they land.
- Parallel model runs **within** one dispatched job are fine and expected.
- Encode as a **capacity limit of 1 slot**, not a boolean capability (relevant to #3730's licence-and-capacity routing).

**An interactive session holding the seat blocks all dispatch.** Closing the solver releases it; logging off is not required — a logged-in session with no solver running holds nothing.

## 4. OrcaWave shares the same seat — the constraint is resources, not licence

Measured: `OrcFxAPI.Diffraction()` constructs successfully through the dispatch path, and the Orcina server publishes **only** the `Flex` feature. **There is no separate OrcaWave entitlement.**

Consequences:

- OrcaWave and OrcaFlex **compete for the same single seat**. One running blocks the other.
- Any "OrcaWave needs dedicated resources" requirement is therefore a **scheduling constraint layered on top of the licence**, not something the licence server can express or enforce. It must be encoded in routing.

Host envelope for sizing (measured 2026-07-31): **64 logical cores** (2 physical sockets), **256 GB RAM** (~206 GB free), **1.35 TB free on D:**.

Diffraction output is large — a comparable AQWA diffraction set on the same host produced a 538 MB `.PAC`, 327 MB `.PAG` and 127 MB `.POT`. **Route solver scratch to a temp dir, not into `results/`** — the licensed-run lane's `result_return` collector will otherwise ship a validator's own JSON back as if it were a result and strand `.sim`/`.LIS` files in the returned tree.

**Not yet measured, and worth measuring before heavy OrcaWave scheduling:** actual core/RAM draw of a representative OrcaWave panel run, and whether it scales with cores or saturates. Until that exists, do not assume a concurrency number for OrcaWave beyond the licence limit of one.

## Do NOT apply when

- The work is pure Python/CPU with no licensed solver — plain SSH is fine and simpler.
- The target is a Linux host — none of this applies; the token issue is Windows-specific.

## Related

[`model-routing.md`](model-routing.md), [`merge-authorization.md`](merge-authorization.md). Issues: workspace-hub#3721, #3729 (dispatch wrapper), #3730 (licence+capacity routing), #3734 (idle AQWA capacity), #3738 (the wrong-premise PR), deckhand#579 (Windows role migration). Memory: `project_fleet_reachability_and_solver_access_2026_07_31`.
