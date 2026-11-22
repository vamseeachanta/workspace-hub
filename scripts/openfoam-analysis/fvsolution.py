"""Generate fvSolution text without loading an OpenFOAM environment."""
import math
from pathlib import Path


def write_fvsolution(target, solver):
    """Write the dictionary; numerical settings are inherited from the base writer."""
    # Engineering basis: OpenFOAM User Guide 6.3.2 (SIMPLEC pressure rule),
    # v2312 documentation, numerics/solvers/under-relaxation (placement).
    # Maintainer defaults: issue 3811 proposed SIMPLEC block (0.9);
    # legacy SIMPLE factors: existing plan, "Resource Intelligence Summary".
    consistent = solver.get("consistent", True)
    if type(consistent) is bool:
        consistent = "yes" if consistent else "no"
    if consistent not in ("yes", "no"):
        raise ValueError("consistent must be a boolean or 'yes'/'no'")
    relax = solver.get("relaxation", {})
    if not isinstance(relax, dict):
        raise TypeError("relaxation must be a mapping")
    for key, value in relax.items():
        if key not in {"U", "p", "k", "epsilon", "omega"}:
            raise ValueError(f"unsupported relaxation key: {key}")
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"relaxation.{key} must be a finite number")
    if solver["application"] == "simpleFoam" and consistent == "yes" and "p" in relax:
        raise ValueError("pressure relaxation requires consistent: no (plain SIMPLE)")
    # All unchanged linear-solver, header and PISO numbers are inherited from
    # run-analysis.sh's base writer, '# fvSolution'; they are not qualified here.
    with Path(target).open('w') as f:
        f.write('FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }\n')
        f.write('solvers {\n')
        f.write('  p { solver GAMG; tolerance 1e-06; relTol 0.1; smoother GaussSeidel; }\n')
        f.write('  pFinal { solver GAMG; tolerance 1e-06; relTol 0; smoother GaussSeidel; }\n')
        f.write('  U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0.1; }\n')
        f.write('  UFinal { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-05; relTol 0; }\n')
        f.write('}\n')
        if solver['application'] in ['simpleFoam']:
            f.write(f'SIMPLE {{ nNonOrthogonalCorrectors 0; consistent {consistent}; }}\n')
            f.write('relaxationFactors {\n')
            if consistent == "no":
                f.write(f'  fields {{ p {relax.get("p", 0.3)}; }}\n')
            f.write('  equations {\n')
            key = '".*"' if consistent == "yes" else "U"
            default = 0.9 if consistent == "yes" else 0.7
            f.write(f'  {key} {relax.get("U", default)};\n')
            for field in ("k", "epsilon", "omega"):
                if field in relax:
                    f.write(f'  {field} {relax[field]};\n')
            f.write('  }\n}\n')
        else:
            f.write('PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }\n')
