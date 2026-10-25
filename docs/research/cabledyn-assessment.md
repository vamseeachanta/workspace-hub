---
title: CableDyn software assessment
software_id: cabledyn_inha
release: v0.2.0
release_date: 2026-10-20
release_published_at: 2026-10-20T22:26:32Z
upstream_revision: d3ddfebd5b598fc593231ff17d9c8af0ca703f57
checked_at: 2026-10-22T17:11:43Z
scope: documentation-only
qualification: NOT_EVALUATED
worked_example:
  glue_step_s: '0.01'
  requested_step_s: '0.025'
  committed_step_s: '0.02'
  approximate_mean_delay_s: '0.01'
  qualification: NOT_EVALUATED
sources:
  - path: README.md
    sha256: 71539d8436b1188cd70c7b5614b1fb73333a0cfcd909a472616fcbb9c902c360
    retrieved_at: 2026-10-22T17:09:12Z
    http_status: 200
  - path: LICENSE
    sha256: c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4
    retrieved_at: 2026-10-22T17:09:12Z
    http_status: 200
  - path: NOTICE
    sha256: 688d98c5092f0e1c4d7d94f0e47cd1e52d0375afb38d0d7d1903041c7dd972be
    retrieved_at: 2026-10-22T17:09:12Z
    http_status: 200
  - path: CITATION.cff
    sha256: 9111d107d988ce956dd710926fe20fc7a585fa834f4b557f4c3141916f1a9989
    retrieved_at: 2026-10-22T17:09:12Z
    http_status: 200
  - path: CHANGELOG.md
    sha256: ac7051a4b35baae1e7a552ab4119739005289e6d94cf6e5281791800a411657e
    retrieved_at: 2026-10-22T17:09:12Z
    http_status: 200
  - path: VALIDATION.md
    sha256: 5db7e948dbcbb5a7b4374ecf147cf6933105e9224ecae893fb4bf4ec639501e6
    retrieved_at: 2026-10-22T17:09:55Z
    http_status: 200
  - path: doc/openfast.rst
    sha256: d08b77ea8871fb323d482eb268208d1ef0e99c15a2f77ba8e20a7af4c51387b1
    retrieved_at: 2026-10-22T17:09:37Z
    http_status: 200
  - path: environment.yml
    sha256: 1de0730d62e3f54eb53fe13cca831b5a4bf80c03cb9351182354e3a5f997a16d
    retrieved_at: 2026-10-22T17:09:37Z
    http_status: 200
  - path: python/pyproject.toml
    sha256: b3d795458628dd476ee74ae2ab29f6d454357c354fa9f6ad9b96ef2931560918
    retrieved_at: 2026-10-22T17:09:37Z
    http_status: 200
  - path: CMakeLists.txt
    sha256: ebd55b14774719bb57a616e4d18f3f1eeda2675dd56d349073fa8e7f9c5796a9
    retrieved_at: 2026-10-22T17:09:38Z
    http_status: 200
---

# CableDyn software assessment

## Summary

CableDyn is a reference-only candidate for mooring and dynamic power-cable
analysis. The existing [software registry](../../data/document-index/online-resource-registry.yaml)
entry is refreshed to **v0.2.0**, released **2026-10-20**, on the evidence below.
No solver installation, execution, integration or local qualification was
performed. Engineering suitability remains **NOT_EVALUATED**.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Record the current release and coupling limits because the catalog described an older release. |

## Identity and version

The home repository is [the upstream CableDyn repository][home], which identifies
an independently developed finite-element solver for offshore mooring lines and
dynamic power cables. Its [README][readme] distinguishes it from the unrelated
research initiative of the same name. The upstream issue tracker is the support
route; personal contact details are omitted here.

The [release page][release] and [CITATION.cff][citation] agree on v0.2.0 and the
release date above. The release API reports publication at
`2026-10-20T22:26:32Z`. The annotated release tag resolves to the commit in this
page's metadata; that commit was also the observed default-branch head. These
are dated observations, not a claim that a moving branch will remain unchanged.
All source-file citations below are pinned to that release commit.

The [README][readme] describes tension-only elements for moorings and a
cubic-Hermite formulation for bending-sensitive cables, static equilibrium and
implicit time-domain dynamics. Reading a MoorDyn-format input deck does not
establish equivalent formulation, keyword support or results. The README states
that unsupported combinations terminate with an error and that interfaces may
change before the first major release.

## License and distribution

The opened [LICENSE][license] identifies Apache-2.0. Its Grant of Copyright
License and Redistribution sections permit use, modification and redistribution
subject to the stated conditions. Redistribution calls for the license, retained
notices, identification of modifications and applicable NOTICE content. The
Trademarks section does not grant branding rights. The [NOTICE][notice] explains
the official-name restriction and the OpenFAST modifications and statically
linked LAPACK/BLAS notices. This establishes a candidate for optional toolkit
use; it does not establish license compatibility of an unexamined combined
work or authorize redistribution of third-party experimental data.

The release page and [README][readme] list source, Windows executables, a Python
wheel, a Python source distribution and a checksum file. No native Linux binary
appears in the observed release assets. No package-index availability claim is
made. The assets and their checksums were not downloaded or verified.

## Integration requirements

| Route | Requirements read from upstream | Limit of this assessment |
|---|---|---|
| Standalone source | Fortran and C toolchains, CMake, Ninja and BLAS/LAPACK; see [build configuration][build] and [environment][environment]. | No build or platform compatibility test. |
| Python tools | The [package metadata][python] declares Python and NumPy dependencies. The [README][readme] requires a driver executable for command-line runs; native coupling requires a built library. | A portable wheel is not evidence of a bundled native solver. No package installed. |
| OpenFAST / FAST.Farm | The [README][readme], [NOTICE][notice] and [coupling guide][coupling] require the CableDyn modifications; `CompMooring = 5` is the documented OpenFAST selector. | Stock OpenFAST is not established as compatible. No host program executed. |

The [v0.2.0 changelog][changes], Added and Changed, expands coupled torsion and
active tensioning support and changes finite-bending output recovery. Therefore,
the older restriction of torsion to standalone execution must not be carried
forward as a current restriction. Comparisons across releases need their output
recovery definition recorded. The changelog's Known issues and the coupling
guide's Time step section still warn about held loads when the committed mooring
step exceeds the host glue step.

## Validation limits

The opened [validation record][validation] reports analytical checks,
comparisons with other programs, physical experiments, coupled runs and
performance/robustness studies. Its Summary distinguishes results meeting a
stated criterion from measured comparisons without a criterion and from
informative results. Its opening discussion says that full commercial-solver
output is not redistributed. Its Static-initialisation robustness section also
records known failures. These are upstream reports, not independent reproduction.

| Intended conclusion | Status here | Evidence still needed |
|---|---|---|
| Current release identity and license text | Source inspected | Refresh the observation when choosing another release. |
| Numerical accuracy for a selected mooring or cable | NOT_EVALUATED | Independently reproduce relevant cases, with units, inputs, response metrics and an intended-use criterion. |
| Mesh and time-step convergence | NOT_EVALUATED | Demonstrate convergence of the required tensions, curvature and any fatigue metric. |
| Coupled response and torsion suitability | NOT_EVALUATED | Verify supported topology, host build, load transfer, output definitions and restart behavior for the chosen case. |
| Design-code compliance or engineering qualification | NOT_EVALUATED | Supply the applicable criteria and reviewed engineering basis; upstream pass labels are insufficient. |
| Relative speed or replacement of another solver | NOT_EVALUATED | A matched, reproducible comparison on the intended workloads. |

The journal article cited by upstream was not opened and is not used as evidence
for any result here. No numerical solver acceptance limit or material coefficient
is adopted. The [README][readme] identifies the software as research software and
assigns model selection, convergence and code compliance to its users.

## Worked example

This is a documentation-based assessment of a coupling setting, not a solver run.
**Inputs:** the published example in CableDyn v0.2.0 (2026), [coupling guide,
Time step][coupling], requests `dtM = 0.025 s` with glue step `DT = 0.01 s`.
Those input values are taken from that example, not selected engineering defaults.

**Method:** the guide specifies the largest whole multiple of `DT` that does not
exceed the requested step. By hand, `0.025 / 0.01 = 2.5`; taking the whole part
and multiplying by `0.01 s` gives a committed step of **0.02 s**. The same section
states an approximate mean load delay of half the committed step. Thus
`mean delay ≈ committed dtM / 2 = 0.02 s / 2 = 0.01 s`. The divisor comes from
that cited time-hold description, not a design coefficient.

**Answer:** the requested step is shortened, but it still holds loads between
commits. The delay estimate is **0.01 s**; it is not a measured response or an
acceptance limit. Suitability remains **NOT_EVALUATED** without a convergence
study and intended-use criterion. The guide calls for checking sensitive
responses at a smaller step, down to the glue step. The offline test docstring
records this independent hand calculation; it never imports CableDyn.

## Ecosystem and follow-up

The existing registry remains the discovery authority for CableDyn, MoorDyn,
MoorPy and OpenFAST; this page creates no second software catalog. Their entries
are discovery links, not evidence of interchangeable models. The private curated
source remains `llm-wiki:wikis/marine-engineering/wiki/sources/cabledyn.md`
(access required), with its existing pinned evidence link retained in the catalog.
This public note is derived only from the opened public sources below; no private
wiki text is reproduced. Refreshing the privately owned page remains separate.

All three bounded slices in the [refresh plan](../plans/2026-10-22-cabledyn-refresh.md)
are covered here: existing-entry refresh, sourced assessment, and a worked
example with offline regression checks. Later work would require separate scope
for acquisition, build, solver integration, benchmark reproduction and qualification.

## Review and verification boundary

The implementing provider's artifact review checks release/tag agreement,
license/software-rights separation, stale torsion restrictions, preservation of
catalog identity/counts and the distinction between reported and reproduced
validation. No unresolved content finding was identified in that review.
Independent provider review is pending; no second-provider approval is claimed.
The original intake review record remains historical evidence for the earlier
release, not review of this refresh.

Tests cover catalog counts and identity, source/observation metadata consistency,
pinned citations, local links, scope and the independent worked example.
They do not establish that an upstream reported result is correct.

The new catalog tests and existing registry-builder tests passed together:
**23 passed**. Ruff passed on the new Python test file. Direct engineering-register
checks passed on this assessment and its plan, and the whitespace check passed.
These checks ran on the uncommitted tree; repository hooks will run at commit.

## Sources and provenance

Source files were retrieved read-only with HTTP success responses; addresses,
UTC timestamps and statuses were retained with the downloaded bytes in temporary
evidence storage. The frontmatter records their SHA-256 digests and timestamps.
No downloaded source or executable is redistributed in this change. The release
API and annotated tag API were also opened successfully on the observation date.

[readme]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/README.md
[license]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/LICENSE
[notice]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/NOTICE
[citation]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/CITATION.cff
[changes]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/CHANGELOG.md
[validation]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/VALIDATION.md
[coupling]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/doc/openfast.rst
[environment]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/environment.yml
[python]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/python/pyproject.toml
[build]: https://github.com/SMI-Lab-Inha/CableDyn/blob/d3ddfebd5b598fc593231ff17d9c8af0ca703f57/CMakeLists.txt
[home]: https://github.com/SMI-Lab-Inha/CableDyn
[release]: https://github.com/SMI-Lab-Inha/CableDyn/releases/tag/v0.2.0
