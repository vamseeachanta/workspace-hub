<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaFlex/Content/WaveKinematics.htm -->

# Wave Kinematics

Wave kinematics describe the velocity and acceleration fields in the fluid domain.

## Linear Wave Theory

For regular waves with angular frequency ω and wave number k:

```
η = A cos(kx - ωt)
u = Aω cosh(k(z+d)) / sinh(kd) cos(kx - ωt)
w = Aω sinh(k(z+d)) / sinh(kd) sin(kx - ωt)
```

## Dispersion Relation

The dispersion relation: ω² = gk tanh(kd)

### Deep Water

For deep water (d → ∞): ω² ≈ gk, so c = ω/k = √(g/k).
