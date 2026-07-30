---
name: reference_gpu_claw_hardware_and_openfoam_gpu
description: gpu-claw CFD node real hardware (2x RTX 3090 passthrough + CUDA-aware MPI) and the verdict on OpenFOAM GPU offload
metadata: 
  node_type: memory
  type: reference
  originSessionId: 25e79f63-3f61-4a4a-9bfa-db009d096990
---

**gpu-claw** (dedicated CFD node, dm #1495; SSH `undi@192.168.184.142` over WireGuard iface `Undi`, src 10.200.253.11 from ace-linux-1). Verified 2026-07-11 — **corrects the 2026-07-09 handoff** which said "compute = cores + bandwidth, not GPU":

**Hardware (real):** Proxmox/QEMU KVM VM, **8 vCPU / 62 GiB RAM**, 250G disk. **TWO NVIDIA RTX 3090 (24 GB each) in genuine PCIe pass-through** (not vGPU/MIG — GeForce can't), driver 590.48.01, **CUDA 13.1** toolkit (`/usr/local/cuda-13.1/bin/nvcc`; note PATH-limited nvcc check false-negatives — source env first). **OpenMPI 4.1.6 is CUDA-aware** (`ompi_info` MPI extensions include `cuda`). OpenFOAM ESI **v2312**, double precision (`linux64GccDPInt32Opt`). **No petsc4Foam/PETSc/AmgX libs built** — the OpenFOAM→GPU bridge does NOT exist on the node.

**Verdict for interFoam VOF sloshing (216k-cell benchmark): do NOT set up GPU offload — stay CPU/MPI-bound at `--ranks 8`.** Why: (1) case too small — GPU pressure offload needs ~0.5–1M+ cells/GPU to beat LDU→CSR conversion + PCIe transfer per solve; (2) VOF runtime is dominated by MULES interface compression + PIMPLE, which petsc4Foam does NOT offload (only pressure Poisson → Amdahl-capped); (3) RTX 3090 FP64 is ~1/64 of FP32, and OF here is double precision; (4) CUDA-aware MPI alone gives ZERO CFD speedup without a GPU-resident solver. **Highest-ROI speedup = raise VM 8→16 vCPU + re-benchmark `--ranks 16`** (zero new software), watch host NUMA/oversub. GPU only worth it at **multi-million-cell** pressure-dominated meshes: then build PETSc+CUDA+AmgX + petsc4Foam vs v2312, switch `p_rgh` solver to petsc/AmgX in fvSolution, validate vs CPU, expect pressure-solve (not whole-run) speedup. RapidCFD fork is dead (OF 2.3.x/2014, no VOF) — not viable. Related: [[project_dm1528_sloshing_reduced_order]].
