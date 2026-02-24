# Evaluation: The Well (Polymathic AI)

## Summary
The Well is a 15 TB collection of 16 diverse physics simulation datasets, curated for training machine learning surrogate models. It is highly permissive (CC BY 4.0) and offers high-fidelity data across fluid dynamics, acoustics, and magnetohydrodynamics, with low-friction integration via a pip-installable Python API and Hugging Face streaming.

| Criterion | Result |
|-----------|--------|
| **License** | CC BY 4.0 (Commercial use permitted with attribution) |
| **Code License**| BSD 3-Clause |
| **Access** | `pip install the_well` + Hugging Face streaming |
| **Relevance** | High (Fluid dynamics, Metocean, Subsea NDE) |
| **Integrity** | High (High-fidelity numerical simulations) |

## Dataset Relevance Scores (1–5)

| Dataset | Relevance | Rationale |
|---------|-----------|-----------|
| `planetswe` | 5 | Shallow water equations on a sphere; direct crossover to metocean/oceanographic wave modelling. |
| `shear_flow` | 5 | Kelvin-Helmholtz instabilities; essential for turbulent wake models in offshore wind and structural flow. |
| `acoustic_scattering`| 5 | Acoustic wave interaction with obstacles; high relevance to subsea NDE and sonar inspection. |
| `rayleigh_benard` | 5 | Buoyancy-driven convection; foundation for thermal CFD and heat transfer ML surrogates. |
| `euler_multi_quadrants`| 5 | Compressible fluid dynamics; captures shocks and Riemann problems for advanced CFD. |
| `rayleigh_taylor` | 4 | Fluid instability at density interfaces; relevant to structural integrity and materials modelling. |
| `MHD_64` / `MHD_256` | 4 | Magnetohydrodynamics; applicable to corrosion physics and electromagnetic inspection methods. |
| `helmholtz_staircase`| 4 | Frequency-domain wave propagation; relevant for subsea acoustics and waveguide design. |
| `viscoelastic` | 3 | Non-Newtonian flow; moderate relevance to specialized materials/polymer modelling. |
| `gray_scott` | 3 | Reaction-diffusion systems; moderate relevance to corrosion growth and diffusion modelling. |
| `active_matter` | 2 | Biological active fluids; interesting for method development but low direct engineering application. |
| `turbulence_gravity` | 2 | Astrophysics turbulence; some crossover for CFD method validation but domain is stellar. |
| `turbulent_radiative`| 2 | Radiative turbulence; methodology crossover for complex CFD but stellar focus. |
| `convective_envelope`| 1 | Stellar convection; background/astrophysics only. |
| `supernova_explosion`| 1 | Astrophysics; background only. |
| `post_neutron_star` | 1 | Relativistic MHD; background only. |

## Top-3 Integration Candidates

1. **Planetary Shallow Water (`planetswe`)**
   - **Target Module:** `worldenergydata/metocean/`
   - **Use Case:** Seed ML models for global wave and current forecasting. The dataset provides ground truth for rotating spherical fluid dynamics that can be used to validate or train metocean surrogate models.

2. **Acoustic Scattering (`acoustic_scattering`)**
   - **Target Module:** `digitalmodel/specialized/inspection/subsea_nde/`
   - **Use Case:** Generate training data for acoustic-based subsea defect detection. The scattering data from complex geometries can be used to train neural operators for sonar signal interpretation.

3. **Shear Flow / Turbulence (`shear_flow`)**
   - **Target Module:** `digitalmodel/modules/hydrodynamics/`
   - **Use Case:** Benchmark for turbulence closures and wake modelling. High-resolution Kelvin-Helmholtz simulations provide a base for validating ML-augmented turbulence models for offshore structures.

## Benchmark Models Assessment
The Well provides reference implementations and benchmarks for **Fourier Neural Operators (FNO)** and other neural operators. 
- **Opportunity:** These pre-trained baselines can be used to jump-start ML surrogate work in `digitalmodel`.
- **Recommendation:** Adopt the FNO benchmark patterns for any new "physics-ML" features.

## Hugging Face Streaming Code Snippet
This pattern avoids the 15 TB download and allows agents to load data on-demand.

```python
from the_well.data import WellDataset
from torch.utils.data import DataLoader

# Initialize the dataset for streaming
trainset = WellDataset(
    well_base_path="hf://datasets/polymathic-ai/",
    well_dataset_name="active_matter",  # replace with target dataset
    well_split_name="train",
)

# Standard PyTorch DataLoader
train_loader = DataLoader(trainset, batch_size=8, shuffle=True)

for batch in train_loader:
    # batch['fields'] contains the simulation data
    # batch['coords'] contains the spatial coordinates
    print(f"Loaded batch with fields shape: {batch['fields'].shape}")
    break
```

## Catalog Entry Data
```yaml
- name: The Well
  category: science/physics-ml
  subcategory: datasets
  url: https://polymathic-ai.org/the_well/
  auth_required: false
  cost_model: free
  relevance_score: 5
  related_module: digitalmodel/hydrodynamics
  maturity: live
  notes: 15TB physics simulation dataset; CC BY 4.0; Hugging Face streaming support.
  discovery_status: new
```
