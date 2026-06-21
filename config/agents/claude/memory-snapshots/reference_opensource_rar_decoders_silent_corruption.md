---
name: reference_opensource_rar_decoders_silent_corruption
description: "Open-source RAR decoders (p7zip, libarchive/bsdtar) silently corrupt some RAR4 entries — right size, wrong bytes; CRC-verify against the archive"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 68ac9897-cb84-4dc4-b90b-6928cef90169
---

2026-06-20, extracting `/home/vamsee/Desktop/cpanel-backup.rar` (205MB RAR4, non-solid, 2826 files). No `unrar`/`unar` installed; only `7z`/`7za` (p7zip) + `bsdtar` (libarchive).

KEY FINDING: both open-source decoders **silently corrupt** a class of RAR4 entries — file lands at the **correct size** but with **wrong bytes**, no fatal error. Only catchable by re-hashing each file's CRC32 against the archive's stored per-entry CRC. Here 2745/2826 byte-perfect, **81 silently corrupt** (mostly `.war`, struts `.tld`, larger `.js`/`.jsp`/`.css`). Presence and size are NOT fidelity.

Decoder failure modes (complementary blind spots, same archive):
- `7z x`: `Unsupported Method` on ~2008 entries AND **cascade-desyncs** — after one bad block it mislabels many *good* following files too, so its failure list is unreliable.
- `bsdtar`: decodes what 7z can't, but **aborts the whole stream** at first `File CRC error`/`Bad RAR file data`/`Invalid location to Huffman tree`, zeroing everything after.
- Non-solid (`Solid = -`) → per-file fallback/recovery possible (each file independent). Combining 7z+bsdtar recovers more than either alone, but the 81 defeat BOTH → need official RARLAB `unrar`.

GOTCHAS:
- Auto-mode classifier BLOCKS downloading+running an external binary (rarlab.com `unrar`) — "Code from External". User must install (`sudo apt install unrar`) or approve.
- `7z l -slt` with an ABSOLUTE archive path emits the archive's own header as a pseudo-entry (has `Physical Size`/`Type` keys) — skip those when parsing, else off-by-one count.
- Python `zlib.crc32` matches RAR/ZIP stored CRC32 — the verification oracle.

Distilled into skill [[project_llm_ingestion_playbook_public_repo]] → `skills/archive-extraction-integrity/` (SKILL.md + `verify_extraction.py` CRC gate + 5 evals). MERGED to main via PR #47 (squash, f3abc74, CI green). Reuse entry point: `uv run skills/archive-extraction-integrity/verify_extraction.py <archive> <extracted_dir>` → byte-faithful vs silently-corrupt for any RAR/ZIP/7z. Official `unrar` 7.0.7 now installed on ace-linux-1 (apt multiverse). See [[feedback_verify_generated_state_against_origin_not_working_copy]].
