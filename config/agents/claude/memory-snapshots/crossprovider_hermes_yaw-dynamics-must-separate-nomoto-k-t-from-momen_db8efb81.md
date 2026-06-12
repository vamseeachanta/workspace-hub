---
name: crossprovider hermes yaw-dynamics-must-separate-nomoto-k-t-from-momen
description: Yaw dynamics must separate Nomoto K/T from moment-balance feedback
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [naval-architecture, dynamics, yaw-moment, engineering-boundary]
---

Implementing yaw-moment and rudder-dynamics models risks double-counting: computing rudder force/yaw moment from local inflow while also using Nomoto `r_dot = (K * alpha_R - r)/T`. Must explicitly choose one clean architecture: either Nomoto-driven with force/moment as diagnostics only, OR moment-balance-driven with inertia/damping and no Nomoto K. If source K/T values are unavailable, degrade to scenario exploration rather than claiming benchmark validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
