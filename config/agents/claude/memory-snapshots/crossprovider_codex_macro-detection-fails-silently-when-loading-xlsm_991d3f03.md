---
name: crossprovider codex macro-detection-fails-silently-when-loading-xlsm
description: Macro detection fails silently when loading .xlsm with default keep_vba=False
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [xlsx-parsing, silent-failure, security]
---

Loading `.xlsm` files with the default `openpyxl.load_workbook(keep_vba=False)` means the `vba_archive` attribute will always be empty/None, so macro detection via that field always returns false even if the file contains macros. Detect macros via ZIP member `xl/vbaProject.bin` or explicitly load with `keep_vba=True`, then test with a real macro-containing `.xlsm` fixture.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
