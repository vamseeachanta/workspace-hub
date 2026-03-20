"""
ABOUTME: Generate Stroud parachute sizing chart with GT1R R35 data points
ABOUTME: Visual aid for WRK-1362 — shows single vs dual chute regions
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(
        "Stroud Parachute Sizing Charts — GT1R R35 (3,600 lbs)",
        fontsize=14, fontweight="bold", y=0.98,
    )

    # ── Panel 1: Single Chute Sizing ──
    # Stroud single chute data: (weight_min, weight_max, model)
    single_data = [
        (1800, 2200, "400", "#4CAF50"),
        (2200, 2800, "410", "#2196F3"),
        (2800, 3200, "420", "#FF9800"),
        (3200, 4000, "430 Std. 32", "#F44336"),
    ]

    y_positions = range(len(single_data))
    for i, (w_min, w_max, model, color) in enumerate(single_data):
        ax1.barh(i, w_max - w_min, left=w_min, height=0.6,
                 color=color, alpha=0.7, edgecolor="black", linewidth=0.8)
        ax1.text((w_min + w_max) / 2, i, model,
                 ha="center", va="center", fontweight="bold", fontsize=10)

    # GT1R marker on single chart
    ax1.axvline(x=3600, color="red", linewidth=2.5, linestyle="--",
                label="GT1R R35 (3,600 lbs)")
    ax1.plot(3600, 3, marker="*", color="red", markersize=20, zorder=5)
    ax1.annotate("GT1R\n3,600 lbs", xy=(3600, 3), xytext=(3750, 2.2),
                 fontsize=9, fontweight="bold", color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5))

    ax1.set_xlabel("Vehicle Weight (lbs)", fontsize=11)
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels([d[2] for d in single_data])
    ax1.set_title("Single Chute (speeds up to ~200 MPH)", fontsize=12)
    ax1.set_xlim(1500, 4500)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(axis="x", alpha=0.3)

    # ── Panel 2: Dual Chute Sizing (weight vs speed) ──
    # Stroud dual chute data: (weight_min, weight_max, speed_min, speed_max, model)
    dual_data = [
        (2000, 2800, 200, 260, "430-24\nPro Stock", "#4CAF50"),
        (2400, 3200, 210, 280, "430-24/430-30\nPro-Mod", "#2196F3"),
        (2800, 3800, 220, 300, "430-28/430-30\nPro-Mod", "#FF9800"),
        (3000, 4000, 240, 320, "430-26", "#9C27B0"),
        (3500, 4000, 280, 320, "450 / 470", "#F44336"),
    ]

    for w_min, w_max, s_min, s_max, model, color in dual_data:
        rect = mpatches.FancyBboxPatch(
            (w_min, s_min), w_max - w_min, s_max - s_min,
            boxstyle="round,pad=10", facecolor=color, alpha=0.25,
            edgecolor=color, linewidth=1.5,
        )
        ax2.add_patch(rect)
        ax2.text((w_min + w_max) / 2, (s_min + s_max) / 2, model,
                 ha="center", va="center", fontsize=8, fontweight="bold",
                 color=color)

    # GT1R data points
    gt1r_cases = [
        (3600, 200, "Case 1\n200 MPH\nSingle", "blue"),
        (3600, 250, "Case 2-3\n250 MPH\nDual Required", "red"),
    ]
    for w, s, label, color in gt1r_cases:
        ax2.plot(w, s, marker="*", color=color, markersize=18, zorder=5)
        offset_x = 150 if color == "blue" else -500
        offset_y = -15 if color == "blue" else 12
        ax2.annotate(label, xy=(w, s),
                     xytext=(w + offset_x, s + offset_y),
                     fontsize=8, fontweight="bold", color=color,
                     arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                               edgecolor=color, alpha=0.9))

    # NHRA 200 MPH dual chute threshold line
    ax2.axhline(y=200, color="black", linewidth=2, linestyle="-.",
                label="NHRA dual chute threshold (200 MPH)")
    ax2.fill_between([1800, 4200], 200, 330, color="red", alpha=0.05)
    ax2.text(1850, 195, "SINGLE OK below", fontsize=8, color="green",
             fontstyle="italic")
    ax2.text(1850, 205, "DUAL REQUIRED above", fontsize=8, color="red",
             fontstyle="italic")

    ax2.set_xlabel("Vehicle Weight (lbs)", fontsize=11)
    ax2.set_ylabel("Speed (MPH)", fontsize=11)
    ax2.set_title("Dual Chute Sizing (speeds over 200 MPH)", fontsize=12)
    ax2.set_xlim(1800, 4200)
    ax2.set_ylim(180, 330)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    out_dir = Path(__file__).parent
    out_path = out_dir / "stroud-sizing-chart.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved: {out_path}")
    plt.close()


if __name__ == "__main__":
    main()
