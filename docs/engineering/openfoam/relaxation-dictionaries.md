# OpenFOAM relaxation dictionaries

The analysis writer targets OpenFOAM.com v2312. SIMPLEC omits pressure relaxation;
plain SIMPLE places pressure relaxation under `fields`. Both put equation
relaxation under `equations`. The text preflight checks this structure before
meshing and execution; it does not certify convergence or numerical accuracy.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| A | 2026-10-22 | Explain mode selection, pressure placement and dictionary preflight to prevent contradictory generated controls. |

## Basis and limits

The public [User Guide, section 6.3.2, Solution under-relaxation](https://www.openfoam.com/documentation/user-guide/6-solving/6.3-solution-and-algorithm-control)
states: “There is no need to use any relaxation on pressure.” This is the SIMPLEC
paragraph following `consistent yes`. The guide URL does not identify an edition;
it must not be presented as an independently archived v2312 edition.

Versioned [v2312 documentation, Under relaxation, Usage](https://doc.openfoam.com/2312/tools/processing/numerics/solvers/under-relaxation/#usage)
shows the `fields` and `equations` split. Its
[SIMPLE algorithm page](https://doc.openfoam.com/2312/tools/processing/solvers/pressure-velocity/simple/)
describes pressure relaxation in plain SIMPLE. The local policy rejects an
explicit pressure factor under SIMPLEC, rather than silently discarding it.

The SIMPLEC equation default `0.9` is a maintainer choice from issue #3811's
proposed block, not a universal published optimum. Plain SIMPLE retains the
original writer's `U: 0.7` and `p: 0.3` defaults, recorded in the existing
[relaxation-fix plan](../../plans/2026-08-26-issue-3811-openfoam-simplec-relaxation-fix.md).
Those numbers and the unchanged linear-solver/PISO settings are inherited inputs;
their numerical suitability is **NOT_EVALUATED**. No new numerical acceptance
limit is introduced.

## Configuration

`solver.consistent` accepts a boolean or the strings `yes` and `no`. It defaults
to `yes` for the SIMPLE-family writer. For plain SIMPLE, set it to `false` or
quote `"no"` in YAML. The existing `relaxation: {U, p}` shape is retained:

- SIMPLEC: `U` supplies the wildcard equation factor. `p` is rejected with an
  instruction to select `consistent: no`. Optional `k`, `epsilon` and `omega`
  entries override the wildcard for those equations.
- SIMPLE: `p` supplies `fields.p`; `U` and any supplied turbulence factors go
  under `equations`.

The existing current-drag configuration includes a pressure factor. It must be
migrated explicitly: select plain SIMPLE, or remove `p` to select SIMPLEC.
No existing configuration is silently reinterpreted as plain SIMPLE.

## Worked example

Input to the extracted writer (dictionary generation only):

```yaml
application: simpleFoam
consistent: true
relaxation: {}
```

Method: select SIMPLEC, omit pressure relaxation, and use the maintainer-selected
`0.9` equation default from issue #3811. The former writer emitted the following
algorithm and relaxation tail, with the original defaults documented above:

```text
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { equations {
  U 0.7; p 0.3;
} }
```

Answer after correction (the unchanged `FoamFile` and `solvers` blocks are omitted):

```text
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors {
  equations {
  ".*" 0.9;
  }
}
```

The structural validator rejects the former tail for pressure under `equations`
and for pressure relaxation with SIMPLEC. It accepts the corrected tail. This
is a structural verdict, not a computed flow result. The non-orthogonal correction
count is the unchanged base writer setting; its suitability is NOT_EVALUATED.

To retain the original factors with pressure relaxation, use:

```yaml
application: simpleFoam
consistent: false
relaxation: {U: 0.7, p: 0.3}
```

The accepted tail then contains:

```text
SIMPLE { nNonOrthogonalCorrectors 0; consistent no; }
relaxationFactors {
  fields { p 0.3; }
  equations {
  U 0.7;
  }
}
```

Tests independently transcribe these expected tails and exercise the actual
shell dictionary-writing Python with temporary stub configurations. They never
source OpenFOAM or execute a solver. The neutral extraction first matched the
original SIMPLE-family and PISO outputs byte for byte; the SIMPLE-family golden
was then changed precisely for explicit plain mode and pressure placement.
The original writer had no way to select `consistent no`.

## Preflight and audit

`validate-analysis.py CASE --dictionaries-only` parses `system/fvSolution`,
`system/fvSchemes` and `system/controlDict`. `run-analysis.sh` invokes this check
before meshing. The ordinary results-validation command also includes it.
The parser supports generated scalar entries, nested dictionaries, quoted keys
and comments. It rejects duplicate keys, missing semicolons and malformed braces.
Directives, substitutions and general OpenFOAM list dictionaries are outside its
supported subset and require the full OpenFOAM reader.

[User Guide section 6.3.3, PISO and SIMPLE algorithms](https://www.openfoam.com/documentation/user-guide/6-solving/6.3-solution-and-algorithm-control),
[v2312 simpleFoam, Overview and Time schemes](https://doc.openfoam.com/2312/tools/processing/solvers/rtm/incompressible/simpleFoam/),
and [v2312 pisoFoam, Overview and Equations](https://doc.openfoam.com/2312/tools/processing/solvers/rtm/incompressible/pisoFoam/)
provide the algorithm/time-category basis. The check requires SIMPLE plus
`steadyState` for `simpleFoam`, and PISO plus a non-`steadyState` time scheme for
`icoFoam` and `pisoFoam`. Field-specific time overrides are checked too.
Unknown applications produce a blocking `NOT_EVALUATED` diagnostic; they are no
longer implicitly accepted with the fallback PISO block.

The other committed SIMPLEC examples in `docs/research/openfoam-dict-patterns.md`
and `docs/research/openfoam-version-landscape.md` use explicit velocity and
turbulence equation factors with no pressure entry. The drift tests read those
blocks directly, supply their factors as configuration inputs, and compare the
effective factors after resolving wildcard defaults and explicit overrides.
Their coefficient suitability is NOT_EVALUATED.

The audit also inspected the conditional `fvSchemes`/`controlDict`/PIMPLE examples
in the dictionary-pattern reference and the tutorial wrapper, which copies
external tutorial dictionaries. No further source-proven contradiction was found
in those committed examples. Follow-up checks remain:

- The analysis writer applies `bounded` convection to transient cases too.
  [v2312 Divergence schemes, Special cases: Steady state](https://doc.openfoam.com/2312/tools/processing/numerics/schemes/divergence/#special-cases-steady-state)
  describes its steady use, but does not establish a universal prohibition for
  transient use. A rejection or coefficient change is NOT_EVALUATED.
- Turbulence transport dictionaries, boundary conditions and solver-specific
  requirements beyond the supported algorithm/time categories are NOT_EVALUATED.
- `controlDict` time-step values, output intervals, linear-solver tolerances and
  correction counts require case-specific numerical qualification. No limits
  have been inferred from memory or from solver-free text tests.
- The v2312 API archive URL attempted for `simpleControl.C` returned HTTP 404;
  no claim relies on that unavailable source. The unversioned guide quotation's
  exact v2312-edition provenance still requires an archived guide copy.

The archived `openfoam/15-fvsolution` skill supplies another SIMPLEC example with
matching explicit velocity and wildcard factors. A third drift test reads it
without modifying the skill. The archived `openfoam/11-case-directory-structure`
examples were also inspected. Their transient `writeControl adjustable` entries
(lines 98 and 113) remain a follow-up: the opened
[v2312 controlDict documentation](https://doc.openfoam.com/2312/fundamentals/case-structure/controldict/)
provides a `timeStep` example but no complete enumeration sufficient to qualify
those entries. They are NOT_EVALUATED, and archived skill changes are excluded
from this change.
