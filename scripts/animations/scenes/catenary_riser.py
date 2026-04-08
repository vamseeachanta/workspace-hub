"""Catenary riser geometry evolution — Manim engineering explainer.

Animates a steel catenary riser (SCR) showing:
1. Static catenary shape with engineering labels
2. Vessel offset effect on riser geometry
3. Touchdown zone (TDZ) shift and fatigue hotspot callout

Usage:
    mamba run -n manim-env manim -ql scripts/animations/scenes/catenary_riser.py CatenaryRiserExplainer
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import (
    BLUE,
    BLUE_B,
    BLUE_D,
    BLUE_E,
    BOLD,
    DARK_BROWN,
    DOWN,
    GREEN,
    GREEN_B,
    GREY_BROWN,
    LEFT,
    ORANGE,
    RED,
    RED_B,
    RIGHT,
    UP,
    WHITE,
    YELLOW,
    Arrow,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Scene,
    Text,
    Transform,
    VGroup,
    VMobject,
    Write,
)
from manim import config as manim_config

# Add scripts/ to path for catenary_math import
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animations.catenary_math import (
    RiserConfig,
    catenary_profile,
    default_scr_config,
    offset_profiles,
)

# --- Colour palette ---
SEABED_COLOR = DARK_BROWN
WATER_COLOR = BLUE_E
SURFACE_COLOR = BLUE_B
RISER_COLOR = ORANGE
TDZ_COLOR = RED_B
VESSEL_COLOR = GREY_BROWN
LABEL_COLOR = WHITE
ACCENT_COLOR = GREEN_B

# --- Scale: map 1500m depth to ~5 Manim units ---
SCALE = 5.0 / 1520.0  # 1520 = depth + hangoff


def eng_to_scene(x_eng: np.ndarray, y_eng: np.ndarray) -> np.ndarray:
    """Convert engineering coords (m) to Manim scene coords.

    Engineering: x rightward, y upward from seabed.
    Scene: origin at centre, seabed at bottom (-3), surface near top.
    """
    x_s = x_eng * SCALE - 3.5  # shift left so vessel is left-of-centre
    y_s = y_eng * SCALE - 3.0  # seabed at y = -3
    points = np.column_stack([x_s, y_s, np.zeros_like(x_s)])
    return points


class CatenaryRiserExplainer(Scene):
    """Main engineering explainer scene for SCR geometry."""

    def construct(self):
        self.camera.background_color = "#0a1628"  # deep navy
        cfg = default_scr_config()

        # --- Phase 1: Environment setup ---
        env = self._build_environment(cfg)
        self.play(FadeIn(env, run_time=1.5))
        self.wait(0.5)

        # --- Phase 2: Draw static catenary ---
        x, y, _ = catenary_profile(cfg, n_points=300)
        riser_line = self._riser_from_coords(x, y)
        vessel = self._build_vessel(x, y, cfg)
        tdz_marker = self._build_tdz_marker(x, y)

        self.play(Create(riser_line, run_time=2.0))
        self.play(FadeIn(vessel, run_time=0.8))
        self.play(GrowFromCenter(tdz_marker, run_time=0.8))

        # Labels
        labels = self._build_labels(cfg, x, y)
        self.play(FadeIn(labels, run_time=1.0))
        self.wait(1.5)

        # --- Phase 3: Vessel offset animation ---
        offset_title = Text(
            "Vessel Offset Effect", font_size=28, color=ACCENT_COLOR
        ).to_edge(UP, buff=0.3)
        self.play(FadeIn(offset_title, run_time=0.5))

        offsets = np.concatenate([
            np.linspace(0, 150, 30),     # drift far
            np.linspace(150, -150, 60),   # swing near
            np.linspace(-150, 0, 30),     # return to nominal
        ])

        for offset_val in offsets:
            adjusted_cfg = RiserConfig(
                water_depth=cfg.water_depth,
                outer_diameter=cfg.outer_diameter,
                wall_thickness=cfg.wall_thickness,
                submerged_weight=cfg.submerged_weight,
                horizontal_tension=cfg.horizontal_tension * (1.0 + offset_val / 1000.0),
                hangoff_height=cfg.hangoff_height,
            )
            x_new, y_new, _ = catenary_profile(adjusted_cfg, n_points=300)
            new_line = self._riser_from_coords(x_new, y_new)
            new_vessel = self._build_vessel(x_new, y_new, adjusted_cfg)
            new_tdz = self._build_tdz_marker(x_new, y_new)

            riser_line.become(new_line)
            vessel.become(new_vessel)
            tdz_marker.become(new_tdz)
            self.wait(0.05)

        self.play(FadeOut(offset_title, run_time=0.5))
        self.wait(0.5)

        # --- Phase 4: Fatigue callout ---
        fatigue_box = self._build_fatigue_callout()
        self.play(FadeIn(fatigue_box, run_time=1.5))
        self.wait(3.0)

        # --- Fade out ---
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.5)

        # --- Credits ---
        credits = VGroup(
            Text("ACE Engineer", font_size=36, color=ACCENT_COLOR, weight=BOLD),
            Text("Steel Catenary Riser — Geometry & Fatigue", font_size=22, color=LABEL_COLOR),
            Text("aceengineer.com", font_size=18, color=BLUE_B),
        ).arrange(DOWN, buff=0.3)
        self.play(FadeIn(credits, run_time=1.0))
        self.wait(2.0)

    # --- Builder methods ---

    def _build_environment(self, cfg: RiserConfig) -> VGroup:
        """Create seabed, water column, and surface line."""
        seabed_y = -3.0
        surface_y = cfg.water_depth * SCALE - 3.0

        # Water background
        water = Rectangle(
            width=14, height=surface_y - seabed_y,
            fill_color=WATER_COLOR, fill_opacity=0.15, stroke_opacity=0,
        ).move_to([0, (seabed_y + surface_y) / 2, 0])

        # Seabed
        seabed = Line([-7, seabed_y, 0], [7, seabed_y, 0], color=SEABED_COLOR, stroke_width=4)
        seabed_label = Text("Seabed", font_size=16, color=SEABED_COLOR).next_to(seabed, DOWN, buff=0.15).shift(RIGHT * 4)

        # Surface
        surface = DashedLine(
            [-7, surface_y, 0], [7, surface_y, 0],
            color=SURFACE_COLOR, stroke_width=2, dash_length=0.15,
        )
        surface_label = Text("Water Surface", font_size=16, color=SURFACE_COLOR).next_to(surface, UP, buff=0.1).shift(RIGHT * 3.5)

        # Depth annotation
        depth_arrow = Arrow(
            [5.5, surface_y, 0], [5.5, seabed_y, 0],
            color=LABEL_COLOR, stroke_width=1.5, buff=0, max_tip_length_to_length_ratio=0.04,
        )
        depth_text = Text(f"{cfg.water_depth:.0f} m", font_size=18, color=LABEL_COLOR).next_to(depth_arrow, RIGHT, buff=0.15)

        return VGroup(water, seabed, seabed_label, surface, surface_label, depth_arrow, depth_text)

    def _riser_from_coords(self, x: np.ndarray, y: np.ndarray) -> VMobject:
        """Create a smooth riser line from engineering coordinates."""
        pts = eng_to_scene(x, y)
        line = VMobject(color=RISER_COLOR, stroke_width=3)
        line.set_points_smoothly([p for p in pts[::3]])  # subsample for performance
        return line

    def _build_vessel(self, x: np.ndarray, y: np.ndarray, cfg: RiserConfig) -> VGroup:
        """Build a simple vessel shape at the hangoff point."""
        pts = eng_to_scene(x, y)
        top = pts[-1]

        hull = RoundedRectangle(
            width=1.2, height=0.35, corner_radius=0.1,
            fill_color=VESSEL_COLOR, fill_opacity=0.9,
            stroke_color=WHITE, stroke_width=1,
        ).move_to([top[0], top[1] + 0.25, 0])

        deck = Rectangle(
            width=0.6, height=0.2,
            fill_color=VESSEL_COLOR, fill_opacity=0.7,
            stroke_color=WHITE, stroke_width=0.5,
        ).move_to([top[0], top[1] + 0.52, 0])

        hangoff = Dot(point=top, color=YELLOW, radius=0.06)

        return VGroup(hull, deck, hangoff)

    def _build_tdz_marker(self, x: np.ndarray, y: np.ndarray) -> VGroup:
        """Mark the touchdown zone with a pulsing indicator."""
        pts = eng_to_scene(x, y)
        tdz_pt = pts[0]  # first point is TDZ (seabed contact)

        dot = Dot(point=tdz_pt, color=TDZ_COLOR, radius=0.1)
        ring = Circle(radius=0.2, color=TDZ_COLOR, stroke_width=2).move_to(tdz_pt)
        label = Text("TDZ", font_size=14, color=TDZ_COLOR, weight=BOLD).next_to(ring, DOWN, buff=0.15)

        return VGroup(dot, ring, label)

    def _build_labels(self, cfg: RiserConfig, x: np.ndarray, y: np.ndarray) -> VGroup:
        """Engineering annotation labels."""
        pts = eng_to_scene(x, y)
        mid_idx = len(pts) // 2
        mid_pt = pts[mid_idx]

        # Riser specs
        spec_text = Text(
            f"SCR: {cfg.outer_diameter:.1f} mm OD × {cfg.wall_thickness:.1f} mm WT",
            font_size=16, color=LABEL_COLOR,
        ).move_to([mid_pt[0] + 1.5, mid_pt[1], 0])

        # Catenary equation (Text instead of MathTex to avoid LaTeX dep)
        eq = Text(
            "y = a cosh(x/a) - a",
            font_size=22, color=ACCENT_COLOR,
        ).to_corner(UP + LEFT, buff=0.4)

        eq_note = Text(
            f"a = H/w = {cfg.catenary_parameter:.0f} m",
            font_size=16, color=LABEL_COLOR,
        ).next_to(eq, DOWN, buff=0.15, aligned_edge=LEFT)

        return VGroup(spec_text, eq, eq_note)

    def _build_fatigue_callout(self) -> VGroup:
        """Fatigue data callout box referencing SCR TDZ assessment."""
        box = RoundedRectangle(
            width=4.5, height=2.8, corner_radius=0.15,
            fill_color="#1a1a2e", fill_opacity=0.95,
            stroke_color=TDZ_COLOR, stroke_width=2,
        ).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.5)

        title = Text(
            "TDZ Fatigue Assessment", font_size=20,
            color=TDZ_COLOR, weight=BOLD,
        ).move_to(box.get_top() + DOWN * 0.35)

        lines = VGroup(
            Text("S-N Curve: DNV E (seawater + CP)", font_size=14, color=LABEL_COLOR),
            Text("DFF: 10.0  |  Design Life: 25 yr", font_size=14, color=LABEL_COLOR),
            Text("Factored Damage: 0.32  (< 1.0  ✓)", font_size=14, color=GREEN),
            Text("Calculated Life: 781 years", font_size=14, color=GREEN),
            Text("Source: DNV-RP-C203 / DNV-OS-F201", font_size=12, color=BLUE_B),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to(box.get_center() + DOWN * 0.15)

        return VGroup(box, title, lines)


class CatenaryRiserThumbnail(Scene):
    """Static thumbnail for README / website embedding."""

    def construct(self):
        self.camera.background_color = "#0a1628"
        cfg = default_scr_config()

        env = CatenaryRiserExplainer._build_environment(None, cfg)
        x, y, _ = catenary_profile(cfg, n_points=300)
        riser = CatenaryRiserExplainer._riser_from_coords(None, x, y)
        vessel = CatenaryRiserExplainer._build_vessel(None, x, y, cfg)
        tdz = CatenaryRiserExplainer._build_tdz_marker(None, x, y)

        title = Text(
            "Steel Catenary Riser", font_size=32,
            color=ACCENT_COLOR, weight=BOLD,
        ).to_edge(UP, buff=0.4)

        subtitle = Text(
            "Geometry & Fatigue Explainer", font_size=20,
            color=LABEL_COLOR,
        ).next_to(title, DOWN, buff=0.15)

        brand = Text(
            "ACE Engineer", font_size=18, color=BLUE_B,
        ).to_edge(DOWN, buff=0.3)

        self.add(env, riser, vessel, tdz, title, subtitle, brand)
