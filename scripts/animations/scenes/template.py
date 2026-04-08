"""Reusable template for engineering explainer animations.

Copy this file and customize for new engineering scenarios.
See catenary_riser.py for a complete working example.

Usage:
    mamba run -n manim-env manim -ql scripts/animations/scenes/<your_scene>.py YourSceneClass
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import (
    BLUE_B,
    BLUE_E,
    BOLD,
    DARK_BROWN,
    DOWN,
    GREEN,
    GREEN_B,
    GREY_BROWN,
    ORANGE,
    RED_B,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    Rectangle,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    VMobject,
)

# --- Customise these for your scenario ---
SCENE_TITLE = "Engineering Explainer Title"
SCENE_SUBTITLE = "Subtitle — method or standard"
BACKGROUND_COLOR = "#0a1628"

# Colour palette (reuse across all engineering animations)
SEABED_COLOR = DARK_BROWN
WATER_COLOR = BLUE_E
SURFACE_COLOR = BLUE_B
PRIMARY_COLOR = ORANGE      # main geometry (riser, pipeline, mooring)
HOTSPOT_COLOR = RED_B       # critical location
VESSEL_COLOR = GREY_BROWN
LABEL_COLOR = WHITE
ACCENT_COLOR = GREEN_B      # equations, highlights
BRAND_COLOR = BLUE_B


class EngineeringExplainerTemplate(Scene):
    """Template scene — four-phase structure for engineering animations.

    Phase 1: Environment setup (seabed, water, vessel, labels)
    Phase 2: Static geometry with engineering annotations
    Phase 3: Dynamic animation (parameter sweep, offset, load case)
    Phase 4: Results callout (code check, fatigue, utilisation)

    Override the _phase_* and _build_* methods for your scenario.
    """

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # Phase 1: Environment
        env = self._build_environment()
        self.play(FadeIn(env, run_time=1.5))
        self.wait(0.5)

        # Phase 2: Static geometry
        geometry = self._build_geometry()
        self.play(Create(geometry, run_time=2.0))
        labels = self._build_labels()
        self.play(FadeIn(labels, run_time=1.0))
        self.wait(1.5)

        # Phase 3: Dynamic animation
        self._animate_parameter_sweep(geometry)

        # Phase 4: Results callout
        callout = self._build_results_callout()
        self.play(FadeIn(callout, run_time=1.5))
        self.wait(3.0)

        # Fade out and credits
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1.5)
        credits = VGroup(
            Text("ACE Engineer", font_size=36, color=ACCENT_COLOR, weight=BOLD),
            Text(SCENE_TITLE, font_size=22, color=LABEL_COLOR),
            Text("aceengineer.com", font_size=18, color=BRAND_COLOR),
        ).arrange(DOWN, buff=0.3)
        self.play(FadeIn(credits, run_time=1.0))
        self.wait(2.0)

    # --- Override these methods for your scenario ---

    def _build_environment(self) -> VGroup:
        """Create the physical environment (seabed, water, surface, depth)."""
        raise NotImplementedError("Override _build_environment()")

    def _build_geometry(self) -> VMobject:
        """Create the primary engineering geometry."""
        raise NotImplementedError("Override _build_geometry()")

    def _build_labels(self) -> VGroup:
        """Create engineering annotation labels."""
        raise NotImplementedError("Override _build_labels()")

    def _animate_parameter_sweep(self, geometry: VMobject) -> None:
        """Animate the key engineering parameter (offset, load, etc)."""
        raise NotImplementedError("Override _animate_parameter_sweep()")

    def _build_results_callout(self) -> VGroup:
        """Create the results/assessment callout box."""
        raise NotImplementedError("Override _build_results_callout()")

    # --- Reusable helpers (use directly in your overrides) ---

    @staticmethod
    def make_callout_box(
        title: str,
        lines: list[tuple[str, str]],
        width: float = 4.5,
    ) -> VGroup:
        """Create a branded results callout box.

        Args:
            title: Box title text
            lines: List of (text, color_name) tuples. Use GREEN for pass, RED_B for fail.
            width: Box width in Manim units
        """
        height = 1.2 + 0.35 * len(lines)
        box = RoundedRectangle(
            width=width, height=height, corner_radius=0.15,
            fill_color="#1a1a2e", fill_opacity=0.95,
            stroke_color=HOTSPOT_COLOR, stroke_width=2,
        ).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.5)

        title_text = Text(
            title, font_size=20, color=HOTSPOT_COLOR, weight=BOLD,
        ).move_to(box.get_top() + DOWN * 0.35)

        line_group = VGroup(*[
            Text(text, font_size=14, color=color)
            for text, color in lines
        ]).arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to(
            box.get_center() + DOWN * 0.15
        )

        return VGroup(box, title_text, line_group)

    @staticmethod
    def make_depth_environment(
        water_depth: float,
        scale: float,
        seabed_y: float = -3.0,
    ) -> VGroup:
        """Create standard seabed + water surface + depth annotation."""
        surface_y = water_depth * scale + seabed_y

        water = Rectangle(
            width=14, height=surface_y - seabed_y,
            fill_color=WATER_COLOR, fill_opacity=0.15, stroke_opacity=0,
        ).move_to([0, (seabed_y + surface_y) / 2, 0])

        seabed = Line(
            [-7, seabed_y, 0], [7, seabed_y, 0],
            color=SEABED_COLOR, stroke_width=4,
        )
        seabed_label = Text(
            "Seabed", font_size=16, color=SEABED_COLOR,
        ).next_to(seabed, DOWN, buff=0.15).shift(RIGHT * 4)

        surface = DashedLine(
            [-7, surface_y, 0], [7, surface_y, 0],
            color=SURFACE_COLOR, stroke_width=2, dash_length=0.15,
        )
        surface_label = Text(
            "Water Surface", font_size=16, color=SURFACE_COLOR,
        ).next_to(surface, UP, buff=0.1).shift(RIGHT * 3.5)

        depth_arrow = Arrow(
            [5.5, surface_y, 0], [5.5, seabed_y, 0],
            color=LABEL_COLOR, stroke_width=1.5, buff=0,
            max_tip_length_to_length_ratio=0.04,
        )
        depth_text = Text(
            f"{water_depth:.0f} m", font_size=18, color=LABEL_COLOR,
        ).next_to(depth_arrow, RIGHT, buff=0.15)

        return VGroup(
            water, seabed, seabed_label, surface, surface_label,
            depth_arrow, depth_text,
        )
