# WRK-1251 Constraints

## Hard Constraints
1. **Headless execution only** — all FreeCAD ops via `freecadcmd`, no GUI
2. **CalculiX not installed** — must install `ccx` before FEM chain work begins
3. **TDD mandatory** — tests before implementation per workspace rules
4. **FreeCAD 0.21.2** — limited to this version's API (no 1.0 features)
5. **ace-linux-2 only** — execution workstation (NVIDIA T400, not relevant for FEM)

## Soft Constraints
1. **ParaView SIGSEGV** — use VTK 9.6.0 Python fallback for result visualization
2. **Gmsh version split** — pip 4.15.1 vs system 4.12.1; prefer pip version
3. **SSHFS mount** — git commands must run via SSH to ace-linux-1
4. **Existing hull_library** — new FreeCAD hull code should complement, not duplicate panel mesh pipeline
