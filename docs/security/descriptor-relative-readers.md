# Descriptor-relative regular-file readers

Descriptor-relative lookup and no-follow flags do not by themselves prevent a
reader from waiting on a FIFO before validating its type. The hub readers audited
here use nonblocking opens and reject non-regular descriptors before reading.
This is a bounded source audit and Linux regression result, not a certification
of every filesystem consumer or device driver. Refs #3439.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Record the source inventory, prevent FIFO waits in hub readers, and document regression coverage. |
| Update | 2026-10-25 | Describe clone preflight isolation and extend real-Git regression controls for replacement, includes and branch tracking. |

## Method and source

[POSIX.1-2024, open() DESCRIPTION](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html)
defines the relevant flags:

- `O_NOFOLLOW` rejects a symbolic link in the final pathname component.
- `O_DIRECTORY` rejects a non-directory during directory traversal.
- `O_NONBLOCK` allows a read-only FIFO open to return without a writer. It also
  prevents readiness waits on devices that support nonblocking opens.
- `O_CREAT | O_EXCL` rejects an existing entry atomically, including a FIFO.

For an existing input, retain the trusted parent descriptor, open the leaf with
`O_RDONLY | O_NOFOLLOW | O_NONBLOCK`, inspect `fstat()`, reject a non-regular
mode, and only then read or pass the descriptor to a parser. Close the descriptor
on rejection. Keep the existing permissions, identity, hard-link, digest and
post-read checks. A preceding pathname `stat()` alone leaves a replacement race.
`O_RDWR` config readers require the same type validation before Git or writes.

Where a caller supplies a size budget, require
`S_ISREG(mode) and size <= limit` before reading, and read at most `limit + 1`
bytes to detect growth. The extra byte is a direct boundary construction, not
an empirical coefficient. Existing hub budgets remain unchanged. New call sites
must choose a budget from their input contract; this audit establishes no new
universal byte limit.

## Empirical coverage

The tier-1 set comes from `config/tier1-python-repos.txt`. The audit searched the
available checkout's `src`, `scripts` and, where present, `packages` trees for
`O_NOFOLLOW`, `dir_fd=` (including whitespace), and `openat(` in Python, shell,
C and Rust source. Tests and documentation were distinguished from runtime
readers after inspection. Git-ignored files, other languages, plain `open()`
consumers and unavailable historical revisions are outside this search.

| Repository | Observed revision | Result |
| --- | --- | --- |
| Hub | `410bd3eb36c08be61b947713b08bd21afaf0119b` | Existing-file reader groups below are hardened; directory and exclusive-creation sites remain unchanged. |
| assetutilities | `8c8e83ef0f35400c050a45c9981b997e44b427dd` | No matching source in the inspected trees. |
| digitalmodel | `e92bcfe4d4e8df898ca79cc968ba682f1248636e` | Four runtime files contain five existing-file opens requiring nonblocking protection; one additional workflow file only describes the pattern. |
| worldenergydata | `84e702f566fa26ccd00345dc9c9c4c46fa433199` | No matching source in the inspected trees, including packages. |
| assethold | `0e734cc7f406bd8b72a9a68672d027277437eaf9` | No matching source in the inspected trees. |

No-match observations do not prove the absence of unsafe readers. The linked
provider-routing issue supplied the defect context; the observed checkout is
the source basis for this inventory. No solver was started or imported.

### Hub disposition

| Source group | Existing-file read surfaces | Disposition |
| --- | --- | --- |
| `scripts/client_llm_wiki/bootstrap_attestation.py` | Rendered members and shared stable digest | Nonblocking leaf open; type and existing size budget checked before digest reads. |
| `bootstrap_manifest.py` in the same package | Config, final manifest and publication links | Nonblocking leaf flags; shared digest rejects special files before read. |
| `bootstrap_bound_manifest.py` | Final and backing manifest | Nonblocking leaf flags; existing descriptor validation retained. |
| `bootstrap_layout.py` | Bound clone config | Nonblocking open; existing regular-file validation retained. |
| `bootstrap_contract.py`, `bootstrap_clone_setup.py`, `bootstrap_git.py` | Reopened clone config and Git parser input | Nonblocking opens and shared type validation before invoking Git. |
| `bootstrap_finalizer.py` | Packed refs | Nonblocking open and regular-file validation before reading. |
| `scripts/legal/manage_rule_authority.py` | Authority documents | Nonblocking open; existing type and size validation retained. |
| `scripts/legal/genesis_broker.py` | Retained input | Nonblocking open; existing ownership, mode, link and size checks retained. |
| `scripts/legal/rule_authority/private_io.py` | Private input, transaction members and cleanup marker | Nonblocking opens, type rejection and descriptor closure on rejection. |
| `scripts/cron/cron_runtime.py` | Runtime JSON, both pathname and descriptor-relative forms | Nonblocking opens; non-regular files return the existing invalid-state structure. |

Directory traversal in these modules and `bootstrap_renderer.py` and
`bootstrap_snapshot.py` uses `O_DIRECTORY`. Exclusive writers in
`bootstrap_renderer.py`, `bootstrap_manifest.py`, `rule_authority/envelope.py`
and `private_io.py` cannot open an existing FIFO. The genesis launcher match is
a flag declaration and commentary, not another leaf reader. The read-guard audit
append, runtime log append and runtime lock sites are writers or locks and remain
outside this reader fix; their special-file handling needs separate review.

### Cross-repository follow-up

The following digitalmodel paths were inspected without modifying or importing
them. Each opens an existing leaf with no-follow protection but without
`O_NONBLOCK`:

- `src/digitalmodel/contract_validation/riser_parent_contract.py::_read_regular`
- `src/digitalmodel/solvers/openfoam/artifact_index.py::_hash_open_file`
- `src/digitalmodel/solvers/openfoam/gmsh_bridge.py::_file_digest`
- `src/digitalmodel/solvers/openfoam/gmsh_bridge.py::_copy_source_once`
- `src/digitalmodel/solvers/ghs/runner.py::_read_verified`

The last reader checks the pathname before opening; that still permits a FIFO
replacement between the check and open. The workflow match in
`src/digitalmodel/workflows/openfoam_batch_decomposition.py` is commentary.
Corrections and runtime tests in that repository remain follow-up work.

## Worked example and regression method

Input: a private regular file containing `b'abc'`, with caller-supplied limits
`len(b'abc')` and `len(b'ab')`. Independent byte counting gives three and two.
The first limit accepts the exact bytes; the second rejects because three is
greater than two. `test_size_boundary` applies this calculation to the private
reader, authority reader, retained-input reader and shared attestation digest.

For the blocking example, create a FIFO without a writer. The old tree reader
exceeded the subprocess watchdog; the fixed reader opens without waiting,
observes a non-regular mode and raises its domain error without a read.
The watchdog uses the existing Git timeout from `bootstrap_git.py`; it is a
test termination bound, not a performance acceptance threshold.

`tests/security/test_descriptor_readers.py` exercises the named read surfaces
with FIFOs, symlinks, sockets, directories and a real null character device.
Only the leaf-open target is redirected for the device probe, avoiding privileged
device creation; flags, `fstat()` and reads remain real. Read spies reject any
attempt to consume special-file bytes, config probes reject parser invocation,
and rejection probes verify descriptor closure. The directory case for the tree
scanner is excluded because directory traversal is intentional. Existing module
tests cover valid files and lifecycle behavior.

### Clone normalization preflight

`bootstrap_clone_setup.py` opens config with nonblocking and no-follow flags and
rejects non-regular descriptors before its first Git child. Git preflight runs
against a temporary repository view that excludes local config and copies HEAD
through a checked regular-file descriptor. This prevents a child from reopening
a replaced config pathname or following config includes. Each Git operation
retains the existing five-second timeout. Config parsing uses the held descriptor
with includes disabled; normalization checks its identity before rewriting and
before publishing HEAD. The HEAD lock spans validation and normalization.

`test_clone_entrypoint_real_git` retains real preflight calls under the existing
subprocess watchdog. Its controls cover regular config, valid transient branch
tracking, an initial FIFO, replacements before the first preflight call and before
`status`, and a regular config whose include points to a FIFO without a writer.
The include is rejected without consuming it or changing config or HEAD. Valid
branch tracking is normalized to the canonical config. These cases supplement
the descriptor-level spies; they do not qualify every Git metadata file type.

## Limits and review

The work covers all three local slices: source inventory, hub fixes with bounded
regressions, and reusable security guidance with a worked example. The full
cross-repository remediation requested by the parent issue remains incomplete.
Windows behavior is unchanged and is not qualified by Linux tests. Nonblocking
open does not establish that every device driver honors the flag; environments
that admit arbitrary device nodes need a stronger path-only binding strategy or
an independently enforced device policy. Existing unbounded transaction and
runtime JSON sizes are not qualified as safe by this change.

Plan inspection identified missing pre-read type checks in packed refs, shared
digest, config parsing, runtime JSON and cleanup markers; these are included.
Code inspection must preserve directory traversal, exclusive creation, existing
error contracts and closure on all rejection paths. Independent provider review
remains required before merge and was not performed by this implementation.
