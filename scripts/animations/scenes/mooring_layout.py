"""Mooring layout / force explainer — Manim engineering animation.

Animates an 8-line spread mooring arrangement showing:
1. Plan view: vessel outline, mooring lines, anchor positions
2. Force vectors under environmental loading
3. Vessel excursion and tension redistribution
4. Code check callout (utilisation vs API RP 2SK criteria)

Usage:
    mamba run -n manim-env manim -ql --media_dir scripts/animations/media \\
      scripts/animations/scenes/mooring_layout.py MooringLayoutExplainer

    # Create GIF
    ffmpeg -y -i scripts/animations/media/videos/mooring_layout/480p15/MooringLayoutExplainer.mp4 \\
      -vf "fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither:bayer" \\
      scripts/animations/media/mooring_layout_explainer.gif
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from manim import (
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
    ORIGIN,
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
    VGroup,
    VMobject,
    Write,
)
from manim import config as manim_config

# Add scripts/ to path for sibling module imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animations.mooring_math import (
    EnvironmentalLoad,
    MooringConfig,
    compute_excursion,
    compute_line_tensions,
    default_spread_mooring,
    excursion_envelope,
    line_anchor_positions,
    max_utilisation,
)

# --- Colour palette (shared with template.py) ---
BACKGROUND_COLOR = "#0a1628"
SEABED_COLOR = DARK_BROWN
WATER_COLOR = BLUE_E
SURFACE_COLOR = BLUE_B
PRIMARY_COLOR = ORANGE       # mooring lines
HOTSPOT_COLOR = RED_B        # high-tension lines
VESSEL_COLOR = GREY_BROWN
LABEL_COLOR = WHITE
ACCENT_COLOR = GREEN_B       # callouts, highlights
BRAND_COLOR = BLUE_B
ANCHOR_COLOR = YELLOW
FORCE_COLOR = RED
ENVELOPE_COLOR = BLUE_D

# --- Scale: map 800m anchor radius to ~3 Manim units ---
PLAN_SCALE = 3.0 / 800.0


def eng_to_plan(x_m: float, y_m: float) -> np.ndarray:
    """Convert engineering plan coords (metres) to Manim scene coords."""
    return np.array([x_m * PLAN_SCALE, y_m * PLAN_SCALE, 0.0])


def tension_color(tension: float, mbl: float) -> str:
    """Return colour based on tension utilisation."""
    util = tension / mbl if mbl > 0 else 0
    if util > 0.6:
        return RED_B
    elif util > 0.4:
        return ORANGE
    elif util > 0.2:
        return YELLOW
    else:
        return GREEN


class MooringLayoutExplainer(Scene):
    """Plan-view mooring layout with force and excursion animation."""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        config = default_spread_mooring(n_lines=8)

        # --- Phase 1: Environment & vessel setup ---
        title = Text(
            "Spread Mooring — LNG Terminal Berth",
            font_size=28, color=ACCENT_COLOR, weight=BOLD,
        ).to_edge(UP, buff=0.3)

        subtitle = Text(
            "Plan View — 8-Line Symmetric Arrangement",
            font_size=18, color=LABEL_COLOR,
        ).next_to(title, DOWN, buff=0.15)

        vessel = self._build_vessel(config)
        compass = self._build_compass()

        self.play(FadeIn(title, run_time=0.8))
        self.play(FadeIn(subtitle, run_time=0.5))
        self.play(FadeIn(vessel, run_time=1.0))
        self.play(FadeIn(compass, run_time=0.5))
        self.wait(0.5)

        # --- Phase 2: Draw mooring lines and anchors ---
        mooring_group, anchor_group, line_labels = self._build_mooring_system(config)

        self.play(Create(mooring_group, run_time=2.0))
        self.play(FadeIn(anchor_group, run_time=1.0))
        self.play(FadeIn(line_labels, run_time=0.8))

        # Pretension annotations
        pretension_text = Text(
            f"Pretension: {config.lines[0].pretension:.0f} kN each",
            font_size=16, color=LABEL_COLOR,
        ).to_edge(DOWN, buff=0.5).shift(LEFT * 3)
        spec_text = Text(
            f"Chain: 76 mm R4  |  MBL: {config.lines[0].mbl:.0f} kN",
            font_size=16, color=LABEL_COLOR,
        ).next_to(pretension_text, RIGHT, buff=1.0)

        self.play(FadeIn(pretension_text, run_time=0.5), FadeIn(spec_text, run_time=0.5))
        self.wait(1.5)

        # --- Phase 3: Environmental loading + excursion animation ---
        self.play(
            FadeOut(pretension_text, run_time=0.3),
            FadeOut(spec_text, run_time=0.3),
            FadeOut(line_labels, run_time=0.3),
        )

        load_title = Text(
            "Environmental Loading — Vessel Excursion",
            font_size=22, color=ACCENT_COLOR,
        ).to_edge(DOWN, buff=0.8)
        self.play(FadeIn(load_title, run_time=0.5))

        # Draw excursion envelope
        envelope_group = self._build_excursion_envelope(config)
        self.play(Create(envelope_group, run_time=1.5))
        self.wait(0.5)

        # Animate vessel drift through load directions
        self._animate_excursion(
            config, vessel, mooring_group, anchor_group,
        )

        self.play(FadeOut(load_title, run_time=0.3))
        self.wait(0.5)

        # --- Phase 4: Code check callout ---
        # Compute peak tensions at maximum excursion
        peak_load = EnvironmentalLoad(force_x=1200, force_y=800, label="100-yr")
        dx, dy = compute_excursion(config, peak_load)
        peak_tensions = compute_line_tensions(config, (dx, dy))
        peak_util = max_utilisation(peak_tensions, config)

        callout = self._build_code_check_callout(peak_util, peak_tensions, config)
        self.play(FadeIn(callout, run_time=1.5))
        self.wait(3.0)

        # --- Fade out and credits ---
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5,
        )

        credits = VGroup(
            Text("ACE Engineer", font_size=36, color=ACCENT_COLOR, weight=BOLD),
            Text("Mooring Layout — Force & Excursion", font_size=22, color=LABEL_COLOR),
            Text("aceengineer.com", font_size=18, color=BRAND_COLOR),
        ).arrange(DOWN, buff=0.3)
        self.play(FadeIn(credits, run_time=1.0))
        self.wait(2.0)

    # --- Builder methods ---

    def _build_vessel(self, config: MooringConfig) -> VGroup:
        """Build a plan-view vessel outline (simplified hull shape)."""
        # Vessel dimensions in scene coords
        l = config.vessel_length * PLAN_SCALE
        b = config.vessel_beam * PLAN_SCALE

        # Simplified ship outline: rectangular hull with pointed bow
        bow_point = np.array([0, l / 2 + b * 0.3, 0])
        stern_port = np.array([-b / 2, -l / 2, 0])
        stern_stbd = np.array([b / 2, -l / 2, 0])
        mid_port = np.array([-b / 2, 0, 0])
        mid_stbd = np.array([b / 2, 0, 0])
        bow_port = np.array([-b / 4, l / 2, 0])
        bow_stbd = np.array([b / 4, l / 2, 0])

        hull = Polygon(
            stern_port, mid_port, bow_port, bow_point,
            bow_stbd, mid_stbd, stern_stbd,
            fill_color=VESSEL_COLOR, fill_opacity=0.6,
            stroke_color=WHITE, stroke_width=1.5,
        )

        # Centre dot
        centre = Dot(ORIGIN, color=WHITE, radius=0.04)

        # Heading indicator
        heading_arrow = Arrow(
            ORIGIN, np.array([0, l / 2 * 0.6, 0]),
            color=WHITE, stroke_width=1.5,
            max_tip_length_to_length_ratio=0.15,
            buff=0,
        )

        vessel_label = Text(
            "LNG Carrier", font_size=14, color=LABEL_COLOR,
        ).move_to(np.array([0, -l / 4, 0]))

        return VGroup(hull, centre, heading_arrow, vessel_label)

    def _build_compass(self) -> VGroup:
        """Build a small compass rose in the corner."""
        pos = np.array([-5.5, 3.0, 0])
        n_arrow = Arrow(
            pos, pos + np.array([0, 0.5, 0]),
            color=WHITE, stroke_width=1.5, buff=0,
            max_tip_length_to_length_ratio=0.2,
        )
        n_label = Text("N", font_size=14, color=WHITE).next_to(n_arrow, UP, buff=0.05)
        return VGroup(n_arrow, n_label)

    def _build_mooring_system(
        self, config: MooringConfig,
    ) -> tuple[VGroup, VGroup, VGroup]:
        """Build mooring lines and anchors in plan view.

        Returns (lines_group, anchors_group, labels_group).
        """
        anchors = line_anchor_positions(config)
        lines_group = VGroup()
        anchor_group = VGroup()
        label_group = VGroup()

        for i, (line_cfg, (ax, ay)) in enumerate(zip(config.lines, anchors)):
            anchor_pt = eng_to_plan(ax, ay)
            fairlead_pt = ORIGIN  # vessel centre (simplified)

            # Mooring line
            ml = Line(
                fairlead_pt, anchor_pt,
                color=PRIMARY_COLOR, stroke_width=2,
            )
            lines_group.add(ml)

            # Anchor marker
            anchor_dot = Dot(anchor_pt, color=ANCHOR_COLOR, radius=0.06)
            anchor_group.add(anchor_dot)

            # Line number label
            mid = (fairlead_pt + anchor_pt) / 2
            label = Text(
                str(i + 1), font_size=12, color=LABEL_COLOR,
            ).move_to(mid + np.array([0.12, 0.12, 0]))
            label_group.add(label)

        return lines_group, anchor_group, label_group

    def _build_excursion_envelope(self, config: MooringConfig) -> VGroup:
        """Draw excursion envelope circles for operational and extreme loads."""
        envelopes = excursion_envelope(
            config,
            load_magnitudes=[500.0, 1200.0],  # operational, extreme
            n_directions=36,
        )

        group = VGroup()
        colors = [ACCENT_COLOR, HOTSPOT_COLOR]
        labels = ["Operational", "Extreme (100-yr)"]

        for env_pts, color, label in zip(envelopes, colors, labels):
            points_3d = [eng_to_plan(x, y) for x, y in env_pts]
            envelope_line = VMobject(color=color, stroke_width=1.5, stroke_opacity=0.7)
            envelope_line.set_points_smoothly(points_3d)
            group.add(envelope_line)

            # Label at the rightmost point
            max_x_pt = max(points_3d, key=lambda p: p[0])
            env_label = Text(
                label, font_size=11, color=color,
            ).next_to(max_x_pt, RIGHT, buff=0.1)
            group.add(env_label)

        return group

    def _animate_excursion(
        self,
        config: MooringConfig,
        vessel: VGroup,
        mooring_group: VGroup,
        anchor_group: VGroup,
    ) -> None:
        """Animate vessel drifting under rotating environmental load."""
        anchors = line_anchor_positions(config)
        anchor_pts = [eng_to_plan(ax, ay) for ax, ay in anchors]

        # Force arrow (visible during animation)
        force_arrow = Arrow(
            ORIGIN, np.array([1, 0, 0]),
            color=FORCE_COLOR, stroke_width=3, buff=0,
            max_tip_length_to_length_ratio=0.15,
        )
        force_label = Text(
            "F_env", font_size=14, color=FORCE_COLOR,
        ).next_to(force_arrow.get_end(), RIGHT, buff=0.1)
        force_group = VGroup(force_arrow, force_label)
        self.play(FadeIn(force_group, run_time=0.3))

        # Tension display
        tension_texts = VGroup()
        for i in range(len(config.lines)):
            tt = Text(
                f"L{i+1}: {config.lines[i].pretension:.0f} kN",
                font_size=10, color=LABEL_COLOR,
            )
            tension_texts.add(tt)
        tension_texts.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        tension_texts.to_edge(RIGHT, buff=0.3).shift(DOWN * 0.5)

        tension_box_bg = RoundedRectangle(
            width=2.2,
            height=tension_texts.height + 0.6,
            corner_radius=0.1,
            fill_color="#1a1a2e", fill_opacity=0.9,
            stroke_color=LABEL_COLOR, stroke_width=1,
        ).move_to(tension_texts.get_center())

        tension_title = Text(
            "Line Tensions", font_size=13, color=ACCENT_COLOR, weight=BOLD,
        ).next_to(tension_box_bg, UP, buff=0.1)

        self.play(
            FadeIn(tension_box_bg, run_time=0.3),
            FadeIn(tension_title, run_time=0.3),
            FadeIn(tension_texts, run_time=0.3),
        )

        # Rotate the environmental load through 360 degrees
        n_steps = 72
        load_magnitude = 1000.0  # kN
        stiffness = 50.0

        for step in range(n_steps + 1):
            angle = 2 * math.pi * step / n_steps
            fx = load_magnitude * math.cos(angle)
            fy = load_magnitude * math.sin(angle)

            load = EnvironmentalLoad(force_x=fx, force_y=fy)
            dx, dy = compute_excursion(config, load, stiffness)
            tensions = compute_line_tensions(config, (dx, dy))

            offset_scene = eng_to_plan(dx, dy)

            # Update vessel position
            vessel.move_to(offset_scene)

            # Update force arrow
            arrow_dir = np.array([math.cos(angle), math.sin(angle), 0])
            new_arrow = Arrow(
                offset_scene,
                offset_scene + arrow_dir * 0.8,
                color=FORCE_COLOR, stroke_width=3, buff=0,
                max_tip_length_to_length_ratio=0.15,
            )
            new_label = Text(
                "F_env", font_size=14, color=FORCE_COLOR,
            ).next_to(new_arrow.get_end(), RIGHT, buff=0.1)
            force_arrow.become(new_arrow)
            force_label.become(new_label)

            # Update mooring lines (fairlead moves with vessel)
            for i, ml in enumerate(mooring_group):
                t_color = tension_color(tensions[i], config.lines[i].mbl)
                new_line = Line(
                    offset_scene, anchor_pts[i],
                    color=t_color, stroke_width=2,
                )
                ml.become(new_line)

            # Update tension text
            for i, tt in enumerate(tension_texts):
                t = tensions[i]
                util = t / config.lines[i].mbl
                tc = tension_color(t, config.lines[i].mbl)
                new_tt = Text(
                    f"L{i+1}: {t:6.0f} kN ({util:.0%})",
                    font_size=10, color=tc,
                )
                new_tt.move_to(tt.get_center())
                tt.become(new_tt)

            self.wait(0.05)

        # Return vessel to centre
        vessel.move_to(ORIGIN)
        for i, ml in enumerate(mooring_group):
            new_line = Line(
                ORIGIN, anchor_pts[i],
                color=PRIMARY_COLOR, stroke_width=2,
            )
            ml.become(new_line)

        self.play(
            FadeOut(force_group, run_time=0.3),
            FadeOut(tension_box_bg, run_time=0.3),
            FadeOut(tension_title, run_time=0.3),
            FadeOut(tension_texts, run_time=0.3),
        )
        self.wait(0.5)

    def _build_code_check_callout(
        self,
        peak_util: float,
        peak_tensions: list[float],
        config: MooringConfig,
    ) -> VGroup:
        """Build the code-check results callout."""
        max_tension = max(peak_tensions)
        max_line_idx = peak_tensions.index(max_tension) + 1
        sf_intact = 1.67  # API RP 2SK
        allowable = config.lines[0].mbl / sf_intact
        status = "PASS" if max_tension < allowable else "FAIL"
        status_color = GREEN if status == "PASS" else RED_B

        box = RoundedRectangle(
            width=5.0, height=3.2, corner_radius=0.15,
            fill_color="#1a1a2e", fill_opacity=0.95,
            stroke_color=HOTSPOT_COLOR, stroke_width=2,
        ).to_edge(RIGHT, buff=0.3).shift(DOWN * 0.3)

        title = Text(
            "Mooring Code Check", font_size=20,
            color=HOTSPOT_COLOR, weight=BOLD,
        ).move_to(box.get_top() + DOWN * 0.35)

        lines = VGroup(
            Text(
                f"Max Tension: {max_tension:.0f} kN (Line {max_line_idx})",
                font_size=14, color=LABEL_COLOR,
            ),
            Text(
                f"MBL: {config.lines[0].mbl:.0f} kN  |  SF: {sf_intact:.2f}",
                font_size=14, color=LABEL_COLOR,
            ),
            Text(
                f"Allowable: {allowable:.0f} kN",
                font_size=14, color=LABEL_COLOR,
            ),
            Text(
                f"Utilisation: {peak_util:.0%}  —  {status}",
                font_size=14, color=status_color, weight=BOLD,
            ),
            Text(
                "Ref: API RP 2SK / DNV-OS-E301",
                font_size=12, color=BRAND_COLOR,
            ),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to(
            box.get_center() + DOWN * 0.1,
        )

        return VGroup(box, title, lines)


class MooringLayoutThumbnail(Scene):
    """Static thumbnail for README / website embedding."""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        config = default_spread_mooring(n_lines=8)

        vessel = MooringLayoutExplainer._build_vessel(None, config)
        mooring_group, anchor_group, _ = MooringLayoutExplainer._build_mooring_system(
            None, config,
        )

        title = Text(
            "Spread Mooring Layout", font_size=32,
            color=ACCENT_COLOR, weight=BOLD,
        ).to_edge(UP, buff=0.4)

        subtitle = Text(
            "Force & Excursion Explainer", font_size=20,
            color=LABEL_COLOR,
        ).next_to(title, DOWN, buff=0.15)

        brand = Text(
            "ACE Engineer", font_size=18, color=BRAND_COLOR,
        ).to_edge(DOWN, buff=0.3)

        self.add(vessel, mooring_group, anchor_group, title, subtitle, brand)
