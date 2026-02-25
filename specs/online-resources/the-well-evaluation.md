# Evaluation: The Well (Polymathic AI) — WRK-393

**Evaluated:** 2026-02-24
**Evaluator:** Claude (WRK-393)
**Source:** https://polymathic-ai.org/the_well/
**GitHub:** https://github.com/PolymathicAI/the_well
**Paper:** NeurIPS 2024 Datasets & Benchmarks Track — arXiv:2412.00568
**Related:** WRK-391 (catalog), WRK-383 (module map), WRK-309 (doc index)

---

## Summary

The Well is a 15 TB, pip-installable collection of 23 physics simulation datasets curated
for training and benchmarking ML surrogate models (neural operators). The collection spans
fluid dynamics, acoustics, magnetohydrodynamics, reaction-diffusion, and astrophysics.
Data is stored in HDF5 on Hugging Face; Hugging Face streaming eliminates the need for
local download during prototyping.

**Verdict:** High-value ecosystem addition. Three datasets have direct module-level
integration paths today. The benchmark suite (FNO/TFNO) reduces cold-start cost for any
future physics-ML feature in `digitalmodel`.

---

## License and Terms of Use

| Item | Detail |
|------|--------|
| **Data license** | CC BY 4.0 (Creative Commons Attribution 4.0 International) |
| **Code license** | BSD 3-Clause (Python package + training harness) |
| **Commercial use** | **Permitted** — CC BY 4.0 explicitly allows commercial use and adaptation |
| **Attribution requirement** | Cite the NeurIPS 2024 paper (see citation at end of this document) |
| **Data location** | Hugging Face — `polymathic-ai/<dataset_name>` |

**Status: CLEAR for commercial integration with attribution.**

---

## Pip Install Smoke Test

Tested on ace-linux-2 (this evaluation machine), Python 3.11, using `uv`:

```bash
uv init the_well_test --no-workspace
cd the_well_test
uv add the_well          # installs the-well==1.2.0, torch==2.10.0
```

Result: **PASS.** `from the_well.data import WellDataset` imports without error.
Package version: `1.2.0`. Benchmark models require additional dependencies (`timm`,
`neuraloperator`) installable via `uv add timm neuraloperator`.

---

## Dataset Inventory and Relevance Scores

23 datasets confirmed from `the_well.data.utils.WELL_DATASETS` (package v1.2.0).
Relevance scored 1–5 against the workspace-hub module map (WRK-383).

| # | Dataset | Domain | Approx. Size | Relevance | Rationale |
|---|---------|--------|-------------|-----------|-----------|
| 1 | `planetswe` | Rotating shallow water on sphere | ~120 GB | **5** | Direct crossover to `worldenergydata/metocean/`; SWE is the governing equation for large-scale wave/current forecasting |
| 2 | `shear_flow` | Turbulent shear / Kelvin-Helmholtz | ~547 GB | **5** | Benchmark for turbulence closures; directly relevant to offshore wake modelling and `digitalmodel/hydrodynamics/` |
| 3 | `acoustic_scattering_maze` | Acoustic wave scattering (complex geometry) | ~311 GB | **5** | High relevance to subsea NDE sonar inspection; `digitalmodel` currently has no acoustic ML module — direct gap fill |
| 4 | `acoustic_scattering_inclusions` | Acoustic scattering (material inclusions) | ~284 GB | **5** | Same as above; inclusions variant specifically relevant to corrosion/defect detection |
| 5 | `acoustic_scattering_discontinuous` | Acoustic scattering (sharp interfaces) | ~158 GB | **5** | Supports wave-at-boundary problems; relevant to subsea structural inspection |
| 6 | `rayleigh_benard` | Buoyancy-driven convection (2D) | ~342 GB | **5** | Foundation benchmark for thermal CFD and heat transfer ML surrogates |
| 7 | `rayleigh_benard_uniform` | Same as above on uniform grid | ~342 GB | **4** | Uniform-grid variant; easier to work with for initial integration |
| 8 | `euler_multi_quadrants_openBC` | Compressible fluid dynamics (open BC) | ~200 GB est. | **5** | Riemann problems, shocks; advanced CFD benchmark for `digitalmodel/hydrodynamics/` |
| 9 | `euler_multi_quadrants_periodicBC` | Compressible fluid dynamics (periodic BC) | ~200 GB est. | **4** | Periodic variant; useful for turbulence-focused training |
| 10 | `rayleigh_taylor_instability` | Fluid instability at density interface | ~150 GB est. | **4** | Relevant to structural integrity and materials modelling in `digitalmodel/structural/` |
| 11 | `MHD_64` | Magnetohydrodynamics (64³ grid) | ~72 GB | **4** | Applicable to EM inspection methods and corrosion physics |
| 12 | `MHD_256` | Magnetohydrodynamics (256³ grid) | ~4,580 GB | **4** | High-resolution MHD; large dataset; defer to targeted download |
| 13 | `helmholtz_staircase` | Frequency-domain wave propagation | ~100 GB est. | **4** | Waveguide acoustics; relevant to subsea acoustic inspection and NDE |
| 14 | `viscoelastic_instability` | Viscoelastic / non-Newtonian flow | ~120 GB est. | **3** | Moderate relevance to specialty materials modelling; `digitalmodel` has no polymer module today |
| 15 | `gray_scott_reaction_diffusion` | Reaction-diffusion (Gray-Scott) | ~50 GB est. | **3** | Moderate relevance to corrosion growth and diffusion modelling; gap in current modules |
| 16 | `turbulence_gravity_cooling` | Turbulence with gravity and cooling | ~100 GB est. | **2** | CFD methodology crossover; domain is astrophysical, engineering value indirect |
| 17 | `turbulent_radiative_layer_2D` | Radiative turbulence (2D) | ~80 GB est. | **2** | CFD methodology crossover; astrophysical focus |
| 18 | `turbulent_radiative_layer_3D` | Radiative turbulence (3D) | ~745 GB | **2** | 3D variant; large; astrophysical focus; defer |
| 19 | `active_matter` | Biological active fluids | ~51 GB | **2** | Low direct engineering application; useful for method development |
| 20 | `convective_envelope_rsg` | Stellar convection (RSG) | ~300 GB est. | **1** | Astrophysics only; background value |
| 21 | `post_neutron_star_merger` | Relativistic MHD / astrophysics | ~50 GB est. | **1** | Astrophysics only; no engineering path |
| 22 | `supernova_explosion_64` | Supernova blast wave (64³) | ~268 GB | **1** | Astrophysics only; background |
| 23 | `supernova_explosion_128` | Supernova blast wave (128³) | ~754 GB | **1** | Astrophysics only; background |

*Sizes marked "est." are estimates from available paper/search data; exact sizes on
Hugging Face may vary. Confirmed sizes: MHD_256 ~4.58 TB, shear_flow ~547 GB,
acoustic_scattering_maze ~311 GB, acoustic_scattering_inclusions ~284 GB,
supernova_explosion_128 ~754 GB, turbulent_radiative_layer_3D ~745 GB,
acoustic_scattering_discontinuous ~158 GB, rayleigh_benard ~342 GB,
supernova_explosion_64 ~268 GB, MHD_64 ~72 GB, active_matter ~51 GB.*

---

## Top-3 Integration Candidates

### 1. Planetary Shallow Water — `planetswe`

**Target module:** `worldenergydata/metocean/`
**Dataset size:** ~120 GB (streamable; no local download needed for prototyping)
**Integration approach:**
- `planetswe` solves the rotating shallow water equations on a sphere at 256×512
  resolution over 1008 timesteps across 120 trajectories.
- The `worldenergydata/metocean/` module currently ingests ERA5/NDBC observational
  data. Adding The Well's `planetswe` provides a *ground-truth simulation* layer for
  validating metocean ML surrogates or training correction models.
- Use HF streaming to load batches during model training; no local BSEE-style bulk
  download required.
- Pre-trained TFNO baseline available at `polymathic-ai/TFNO-planetswe` on HF.

**Next step:** WRK-417 — integrate `planetswe` streaming into `metocean` ML feature.

---

### 2. Acoustic Scattering (all three variants)

**Target module:** `digitalmodel/specialized/` (new `subsea_nde` sub-module, or
  extension to `digitalmodel/subsea/`)
**Combined dataset size:** ~753 GB total (maze + inclusions + discontinuous)
**Integration approach:**
- The three acoustic scattering datasets (maze geometry, material inclusions, sharp
  interfaces) together provide a comprehensive training corpus for acoustic-based
  subsea defect detection and NDE signal interpretation.
- `digitalmodel` currently has no acoustic ML module. These datasets seed one directly.
- The maze dataset (complex geometry) is the most relevant to subsea pipe inspection
  scenarios; inclusions maps to corrosion pit detection; discontinuous to crack detection.
- All three can be streamed via HF for prototyping; download only the target variant
  for production training.
- Pre-trained FNO baselines available for each variant on Hugging Face.

**Next step:** WRK-418 — design `digitalmodel` acoustic NDE module using The Well
acoustic scattering datasets as training/validation corpus.

---

### 3. Shear Flow / Kelvin-Helmholtz Turbulence — `shear_flow`

**Target module:** `digitalmodel/hydrodynamics/`
**Dataset size:** ~547 GB (stream selectively; full download deferred)
**Integration approach:**
- `shear_flow` provides high-resolution simulations of Kelvin-Helmholtz instabilities,
  the dominant mechanism in turbulent wake shedding around offshore structures.
- `digitalmodel/hydrodynamics/` currently handles wave spectra, vessel dynamics, and
  BEM methods. `shear_flow` adds a turbulent wake benchmark that could validate
  or augment ML-based turbulence closure models.
- Use the pre-trained FNO/TFNO baselines as a starting point; fine-tune on
  offshore-specific Reynolds numbers.
- Stream individual simulations for exploratory work; defer full 547 GB download to
  dedicated training runs.

**Next step:** WRK-419 — integrate `shear_flow` as turbulence benchmark in
`digitalmodel/hydrodynamics/`.

---

## Benchmark Models Assessment

The Well ships a full benchmark harness with 8 pretrained neural operator model classes:

| Model | Class | Notes |
|-------|-------|-------|
| Fourier Neural Operator | `FNO` | Core baseline; most widely used |
| Tucker-Factorized FNO | `TFNO` | Memory-efficient FNO variant |
| U-Net (classic) | `UNetClassic` | Spatial encoder-decoder |
| U-Net (ConvNext blocks) | `UNetConvNext` | Modernised U-Net |
| Dilated ResNet | `DilatedResNet` | Multi-scale CNN |
| Factorized FNO | `ReFNO` | Resolution-invariant variant |
| Adaptive Vision Transformer | `AViT` | Attention-based neural operator |
| Adaptive FNO | `AFNO` | Spectral attention variant |

All models are trained on the 1-step-ahead prediction problem (predict next snapshot
from 4-step input history), benchmarked on a single NVIDIA H100 within 12 hours.
Pre-trained checkpoints are available at
`huggingface.co/collections/polymathic-ai/the-well-benchmark-models-67e69bd7cd8e60229b5cd43e`
(updated March 2025).

**Recommendation for `digitalmodel`:** FNO and TFNO are the most directly applicable
baselines. The existing `neuraloperator` library integration means these can be
dropped into any new physics-ML feature with minimal friction. Adopt the FNO benchmark
pattern as the standard baseline for any new `digitalmodel` ML surrogate module.

**Loading a pretrained checkpoint (verified API):**

```python
from the_well.benchmark.models import FNO, TFNO

# Load a pretrained FNO trained on planetswe
model = FNO.from_pretrained("polymathic-ai/FNO-planetswe")

# Load a pretrained TFNO trained on shear_flow
model = TFNO.from_pretrained("polymathic-ai/TFNO-shear_flow")
```

---

## Hugging Face Streaming Code Snippet

This pattern streams data directly from Hugging Face without a 15 TB local download.
Validated against the_well v1.2.0 API (batch keys confirmed from source inspection).

```python
from the_well.data import WellDataset
from torch.utils.data import DataLoader

# Stream planetswe training data from Hugging Face
trainset = WellDataset(
    well_base_path="hf://datasets/polymathic-ai/",
    well_dataset_name="planetswe",       # replace with target dataset
    well_split_name="train",             # "train", "valid", or "test"
    n_steps_input=4,                     # number of input timesteps
    n_steps_output=1,                    # number of timesteps to predict
)

# Standard PyTorch DataLoader
train_loader = DataLoader(trainset, batch_size=4, shuffle=True)

for batch in train_loader:
    # Confirmed batch keys (from WellDataset._construct_sample):
    #   input_fields:      [B, T_in, H, W, C]  — time-varying input fields
    #   output_fields:     [B, T_out, H, W, C] — target prediction fields
    #   constant_fields:   [B, H, W, C_const]  — time-invariant fields
    #   input_scalars:     [B, T_in, S]         — scalar parameters (input)
    #   output_scalars:    [B, T_out, S]        — scalar parameters (output)
    #   constant_scalars:  [B, S_const]         — constant scalar parameters
    #   space_grid:        [B, H, W, D]         — spatial coordinates (if return_grid=True)
    #   input_time_grid:   [B, T_in]            — input timestep values
    #   output_time_grid:  [B, T_out]           — output timestep values
    x = batch["input_fields"]
    y = batch["output_fields"]
    print(f"Input shape: {x.shape}, Target shape: {y.shape}")
    break
```

**Note:** `batch['fields']` is NOT a valid key (incorrect in prior draft).
Use `batch['input_fields']` and `batch['output_fields']` per v1.2.0 API.

---

## Integration Feasibility Summary

| Criterion | Status |
|-----------|--------|
| License (data) | CC BY 4.0 — commercial use permitted with attribution |
| License (code) | BSD 3-Clause — permissive |
| Pip install | `pip install the_well` — PASS (v1.2.0, Python 3.11+) |
| HF streaming | Works without bulk download |
| PyTorch DataLoader | Standard `torch.utils.data.DataLoader` compatible |
| Pretrained baselines | 8 model types × ~20 datasets on Hugging Face |
| Module integration (top-3) | Clear paths in `metocean`, `hydrodynamics`, `subsea/specialized` |
| Legal scan risk | No client identifiers; generic physics terminology throughout |

---

## Proposed Follow-On WRK Items

| ID | Title | Target | Priority |
|----|-------|--------|----------|
| WRK-417 | Integrate `planetswe` streaming into `worldenergydata/metocean/` ML feature | worldenergydata | medium |
| WRK-418 | Design `digitalmodel` acoustic NDE module seeded by The Well acoustic scattering datasets | digitalmodel | medium |
| WRK-419 | Integrate `shear_flow` as turbulence ML benchmark in `digitalmodel/hydrodynamics/` | digitalmodel | low |

---

## Required Citation

Ohana, R. et al. (2024). "The Well: a Large-Scale Collection of Diverse Physics
Simulations for Machine Learning." *Advances in Neural Information Processing Systems*,
37, 44989–45037.

BibTeX:
```bibtex
@inproceedings{ohana2024well,
  title={The Well: a Large-Scale Collection of Diverse Physics Simulations
         for Machine Learning},
  author={Ohana, Ruben and others},
  booktitle={Advances in Neural Information Processing Systems},
  volume={37},
  pages={44989--45037},
  year={2024}
}
```
