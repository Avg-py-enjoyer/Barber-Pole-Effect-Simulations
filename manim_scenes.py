"""Manim Community scenes: polarized light through an optically active (glucose) tube.

Render (from this folder):

    manim -pql manim_scenes.py LightThroughGlucoseTube     # 3D: helices + E-field vectors
    manim -pql manim_scenes.py WalkingStripes              # side view + I(z) curves vs theta_0
    manim -pql manim_scenes.py DispersionDial              # theta(z, lambda) "clock" per color

Use -qm / -qh for medium / high quality. No LaTeX is needed (only Text is used).

The physics is imported from the `barber_pole` package:

    theta(z, lambda) = theta_0 + c * z * A / lambda^2       (Cauchy ORD)
    I(z, lambda)     ~ cos^2(theta(z, lambda) - phi_view)   (Rayleigh dipole)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import matplotlib.colors as mcolors
from manim import *  # noqa: F401,F403

from barber_pole.config import (CAUCHY_A, LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE,
                                TUBE_HEIGHT, TUBE_RADIUS)
from barber_pole.raymarch import simulate_barber_pole
from barber_pole.spectral import cauchy_rotation, helix_pitch, wavelength_to_srgb

R = TUBE_RADIUS          # tube radius  (cm == manim units)
H = TUBE_HEIGHT          # tube length

C_RED, C_GREEN, C_BLUE = "#ef4444", "#22c55e", "#3b82f6"
BANDS = [(LAMBDA_RED, C_RED, "Red 650 nm"),
         (LAMBDA_GREEN, C_GREEN, "Green 532 nm"),
         (LAMBDA_BLUE, C_BLUE, "Blue 450 nm")]
BG = "#0b0f19"


def theta(lam, z, c, theta0):
    """Polarization angle (rad) at depth z for wavelength lam (nm)."""
    return float(cauchy_rotation(lam, z, c, theta0))


def legend(font_size=22):
    """Colour legend as a VGroup of dot + label rows."""
    rows = VGroup()
    for _, col, name in BANDS:
        rows.add(VGroup(Dot(radius=0.07, color=col),
                        Text(name, font_size=font_size, color=col)).arrange(RIGHT, buff=0.2))
    return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15)


# ===========================================================================
# Scene 1 - 3D: light travelling up the glucose tube
# ===========================================================================
class LightThroughGlucoseTube(ThreeDScene):
    """Linearly polarized white light enters the bottom of a glucose-filled tube.

    Each colour's plane of polarization rotates as theta(z, lambda) = theta_0 + c z A / lambda^2,
    so blue winds up faster than red. Afterwards the entrance polarizer is rotated:
    every helix slides along the tube together (pitch unchanged) -> "walking stripes".
    """

    concentration = 0.3      # lower than the notebook default so ~1-2 turns are visible in 3D
    n_slices = 18            # number of E-field "slices" drawn along the tube

    def P(self, x, y, z):
        """Tube coordinates (z in [0, H]) -> scene coordinates (tube centred on origin)."""
        return np.array([x, y, z - H / 2])

    def caption(self, text, color=WHITE, font_size=28):
        cap = Text(text, font_size=font_size, color=color).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cap)
        return cap

    def construct(self):
        self.camera.background_color = BG
        c = self.concentration
        theta0 = ValueTracker(0.0)    # entrance polarizer angle (rad)
        zfront = ValueTracker(0.0)    # how far the light has travelled (cm)

        self.set_camera_orientation(phi=72 * DEGREES, theta=-60 * DEGREES)

        # ---- title + legend (fixed to the screen) ---------------------------
        title = Text("Optical rotatory dispersion in a glucose solution",
                     font_size=30, weight=BOLD).to_edge(UP, buff=0.3)
        leg = legend().to_corner(UR, buff=0.4)
        self.add_fixed_in_frame_mobjects(title, leg)
        self.play(FadeIn(title), FadeIn(leg))

        # ---- glass tube + entrance polarizer -------------------------------
        tube = Cylinder(radius=R, height=H, direction=OUT, show_ends=False,
                        resolution=(24, 48), fill_color="#60a5fa", fill_opacity=0.10,
                        stroke_color="#93c5fd", stroke_width=0.6, checkerboard_colors=False)
        axis = DashedLine(self.P(0, 0, 0), self.P(0, 0, H), color=GREY_B, stroke_width=2)

        pol_disc = Circle(radius=R * 1.12, color=WHITE, stroke_width=2)
        pol_disc.set_fill("#1e293b", opacity=0.55).move_to(self.P(0, 0, 0))

        def slit():
            t = theta0.get_value()
            d = R * 1.05 * np.array([np.cos(t), np.sin(t), 0])
            return Line(self.P(0, 0, 0) - d, self.P(0, 0, 0) + d, color=YELLOW, stroke_width=6)

        pol_slit = always_redraw(slit)
        pol_label = Text("entrance polarizer θ₀", font_size=22, color=YELLOW)
        self.add_fixed_in_frame_mobjects(pol_label)
        pol_label.to_corner(DL, buff=0.5).shift(UP * 0.9)

        self.play(Create(tube), Create(axis), FadeIn(pol_disc), run_time=2)
        self.add(pol_slit)
        self.play(FadeIn(pol_label))

        cap = self.caption("Linearly polarized light enters the tube at z = 0")
        self.play(FadeIn(cap))
        self.wait(1)

        # ---- E-field slices (updated from the trackers) ---------------------
        z_slices = np.linspace(0.0, H, self.n_slices)

        def make_field_line(lam, color, width, z):
            line = Line(self.P(0, 0, z), self.P(0, 0, z) + RIGHT * 0.01,
                        color=color, stroke_width=width)

            def update(m):
                th = theta(lam, z, c, theta0.get_value())
                d = 0.82 * np.array([np.cos(th), np.sin(th), 0.0])
                ctr = self.P(0, 0, z)
                m.put_start_and_end_on(ctr - d, ctr + d)
                m.set_stroke(opacity=1.0 if z <= zfront.get_value() else 0.0)

            line.add_updater(update)
            update(line)
            return line

        # draw red last-but-thickest first so thin blue stays visible on top
        slices = VGroup(*[make_field_line(lam, col, w, z)
                          for (lam, col, _), w in zip(BANDS, (7, 5, 3))
                          for z in z_slices])
        self.add(slices)

        # ---- coloured helices traced by the E-vector tip --------------------
        def make_helix(lam, color):
            def build():
                zmax = max(zfront.get_value(), 1e-3)
                th0 = theta0.get_value()
                return ParametricFunction(
                    lambda t: self.P(0.85 * np.cos(theta(lam, t, c, th0)),
                                     0.85 * np.sin(theta(lam, t, c, th0)), t),
                    t_range=[0, zmax, 0.02], color=color, stroke_width=4)
            return always_redraw(build)

        helices = [make_helix(lam, col) for lam, col, _ in BANDS]
        for h in helices:
            self.add(h)

        # travelling wavefront
        front = Circle(radius=R * 0.97, color=WHITE, stroke_width=2)
        front.set_fill(WHITE, opacity=0.12)
        front.add_updater(lambda m: m.move_to(self.P(0, 0, zfront.get_value())))
        self.add(front)

        # ---- 1. propagate ----------------------------------------------------
        new_cap = self.caption("θ(z, λ) = θ₀ + c · z · A / λ²   —   blue rotates fastest")
        self.play(FadeOut(cap), FadeIn(new_cap))
        cap = new_cap
        self.begin_ambient_camera_rotation(rate=0.10)
        self.play(zfront.animate.set_value(H), run_time=9, rate_func=linear)
        self.play(FadeOut(front))
        self.wait(2)
        self.stop_ambient_camera_rotation()

        # ---- 2. pitch summary -----------------------------------------------
        pitches = "   ".join(f"{n.split()[0]}: {helix_pitch(l, c):.1f} cm"
                             for l, _, n in BANDS)
        new_cap = self.caption(f"Helix pitch  P = 2π λ² / (A c)   →   {pitches}", font_size=24)
        self.play(FadeOut(cap), FadeIn(new_cap))
        cap = new_cap
        self.wait(3)

        # ---- 3. rotate the entrance polarizer: stripes "walk" ---------------
        new_cap = self.caption("Rotate θ₀: every helix slides along the tube, pitch unchanged",
                               color=YELLOW)
        self.play(FadeOut(cap), FadeIn(new_cap))
        cap = new_cap
        self.move_camera(phi=78 * DEGREES, theta=-80 * DEGREES, run_time=2)
        self.play(theta0.animate.set_value(TAU), run_time=10, rate_func=smooth)
        self.wait(1)

        # ---- 4. concentration note ------------------------------------------
        new_cap = self.caption("Higher concentration c  →  shorter pitch  →  more stripes")
        self.play(FadeOut(cap), FadeIn(new_cap))
        self.wait(3)


# ===========================================================================
# Scene 2 - side view of the tube (raymarched) + I(z) curves vs theta_0
# ===========================================================================
class WalkingStripes(Scene):
    """Left: raymarched side view of the tube. Right: per-colour brightness
    I(z) = cos^2(theta(z, lambda)) aligned with the tube. Sweeping theta_0 makes the
    curves - and the stripes - slide along z without changing their spacing."""

    concentration = 0.85
    tube_height_units = 5.4

    def construct(self):
        self.camera.background_color = BG
        c = self.concentration
        theta0 = ValueTracker(0.0)    # degrees

        title = Text("Rotating the entrance polarizer makes the stripes walk",
                     font_size=30, weight=BOLD).to_edge(UP, buff=0.3)
        self.play(FadeIn(title))

        # --- raymarched tube image (re-rendered every frame) ------------------
        def tube_image():
            img = simulate_barber_pole(concentration=c, theta0_deg=theta0.get_value(),
                                       mode="spectrum", resolution=(200, 100),
                                       n_depth_steps=16)
            arr = np.uint8(np.clip(img[::-1], 0, 1) * 255)          # row 0 -> top
            im = ImageMobject(arr).set_height(self.tube_height_units)
            return im.move_to(LEFT * 4.2 + DOWN * 0.35)

        tube = always_redraw(tube_image)
        tube_label = Text("white light, side view", font_size=22, color=GREY_B)
        tube_label.next_to(tube, DOWN, buff=0.15)

        # --- aligned I(z) plot (z runs vertically, same scale as the tube) ----
        axes = Axes(x_range=[0, 1, 0.5], y_range=[0, H, 1],
                    x_length=3.6, y_length=self.tube_height_units,
                    axis_config={"color": GREY_B, "include_tip": False,
                                 "font_size": 20})
        axes.move_to(RIGHT * 1.2 + DOWN * 0.35)
        # Add y-axis number labels using Text (avoids LaTeX dependency)
        for val in range(0, int(H) + 1):
            label = Text(str(val), font_size=18, color=GREY_B)
            label.next_to(axes.y_axis.n2p(val), LEFT, buff=0.15)
            axes.add(label)
        x_lab = Text("I(z) = cos²θ", font_size=22, color=GREY_B).next_to(axes, DOWN, buff=0.15)
        y_lab = Text("z (cm)", font_size=20, color=GREY_B).next_to(axes.y_axis, UP, buff=0.1)

        def curve(lam, color):
            def build():
                th0 = np.radians(theta0.get_value())
                return axes.plot_parametric_curve(
                    lambda z: np.array([np.cos(theta(lam, z, c, th0)) ** 2, z, 0]),
                    t_range=[0, H, 0.01], color=color, stroke_width=3)
            return always_redraw(build)

        curves = [curve(lam, col) for lam, col, _ in BANDS]

        # --- polarizer dial + θ0 read-out -----------------------------------
        dial = Circle(radius=0.55, color=WHITE, stroke_width=2).move_to(RIGHT * 5.1 + UP * 1.7)

        def dial_line():
            t = np.radians(theta0.get_value())
            d = 0.5 * np.array([np.cos(t), np.sin(t), 0])
            return Line(dial.get_center() - d, dial.get_center() + d, color=YELLOW, stroke_width=6)

        dial_needle = always_redraw(dial_line)
        dial_title = Text("entrance polarizer", font_size=18, color=YELLOW).next_to(dial, UP, buff=0.12)
        readout = always_redraw(lambda: Text(f"θ₀ = {theta0.get_value() % 360:5.1f}°", font_size=26,
                                             color=YELLOW).next_to(dial, DOWN, buff=0.15))
        leg = legend(18).move_to(RIGHT * 5.1 + DOWN * 0.8)

        self.play(FadeIn(tube), FadeIn(tube_label), Create(axes), FadeIn(x_lab), FadeIn(y_lab),
                  FadeIn(dial), FadeIn(dial_title), FadeIn(leg))
        self.add(*curves, dial_needle, readout)
        self.wait(1.5)

        note = Text("Δz = Δθ₀ · λ² / (A c) — shift is larger for red than blue",
                    font_size=22, color=WHITE).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.play(theta0.animate.set_value(360), run_time=12, rate_func=linear)
        self.wait(1.5)


# ===========================================================================
# Scene 3 - polarization "clock" for each colour as z increases
# ===========================================================================
class DispersionDial(Scene):
    """A probe slides up the tube; the dial shows each colour's polarization angle
    theta(z, lambda). The colours fan out (dispersion). Then theta_0 is changed at a
    fixed z: the whole fan rotates together while its spread stays the same."""

    concentration = 0.85

    def construct(self):
        self.camera.background_color = BG
        c = self.concentration
        z = ValueTracker(0.0)
        theta0 = ValueTracker(0.0)    # degrees

        title = Text("Dispersion: each colour's polarization plane turns at its own rate",
                     font_size=28, weight=BOLD).to_edge(UP, buff=0.3)

        # --- tube cross-section at left, with a probe plane -------------------
        tube_h = 5.0
        tube = Rectangle(width=1.6, height=tube_h, color="#93c5fd", stroke_width=2)
        tube.set_fill("#60a5fa", opacity=0.15).move_to(LEFT * 4.5 + DOWN * 0.3)
        tube_bottom = tube.get_bottom()

        def probe_y():
            return tube_bottom[1] + tube_h * z.get_value() / H

        probe = always_redraw(lambda: Line(
            [tube.get_left()[0] - 0.25, probe_y(), 0],
            [tube.get_right()[0] + 0.25, probe_y(), 0], color=YELLOW, stroke_width=4))
        z_text = always_redraw(lambda: Text(f"z = {z.get_value():.2f} cm", font_size=24,
                                            color=YELLOW).next_to(tube, DOWN, buff=0.2))

        # --- dial ------------------------------------------------------------
        centre = RIGHT * 1.0 + DOWN * 0.2
        ring = Circle(radius=2.2, color=GREY_B, stroke_width=2).move_to(centre)
        ticks = VGroup(*[Line(centre + 2.2 * np.array([np.cos(a), np.sin(a), 0]),
                              centre + 2.35 * np.array([np.cos(a), np.sin(a), 0]),
                              color=GREY_B, stroke_width=2)
                         for a in np.radians(np.arange(0, 360, 30))])
        centre_dot = Dot(centre, radius=0.05, color=WHITE)

        def needle(lam, color, width):
            def build():
                t = theta(lam, z.get_value(), c, np.radians(theta0.get_value()))
                d = 2.1 * np.array([np.cos(t), np.sin(t), 0])
                return Line(centre - d, centre + d, color=color, stroke_width=width)
            return always_redraw(build)

        needles = [needle(lam, col, w) for (lam, col, _), w in zip(BANDS, (9, 6, 3.5))]

        def angle_readout():
            rows = VGroup()
            for lam, col, name in BANDS:
                t = np.degrees(theta(lam, z.get_value(), c, np.radians(theta0.get_value())))
                rows.add(Text(f"{name.split()[0]:<5} θ = {t:7.1f}°", font_size=22, color=col,
                              font="Monospace"))
            return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(RIGHT * 5.0 + UP * 1.0)

        readout = always_redraw(angle_readout)
        theta0_text = always_redraw(lambda: Text(f"θ₀ = {theta0.get_value():5.1f}°", font_size=26,
                                                 color=YELLOW).move_to(RIGHT * 5.0 + DOWN * 0.7))
        spread_text = always_redraw(lambda: Text(
            f"blue − red = {np.degrees(theta(LAMBDA_BLUE, z.get_value(), c, 0) - theta(LAMBDA_RED, z.get_value(), c, 0)):.0f}°",
            font_size=22, color=WHITE).move_to(RIGHT * 5.0 + DOWN * 1.6))

        self.play(FadeIn(title))
        self.play(Create(tube), Create(ring), FadeIn(ticks), FadeIn(centre_dot))
        self.add(probe, z_text, *needles, readout, theta0_text, spread_text)
        self.wait(1)

        # 1) slide the probe up the tube: the colours fan out
        cap1 = Text("Slide up the tube: blue rotates ≈ 2.1× faster than red",
                    font_size=24).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap1))
        self.play(z.animate.set_value(H), run_time=10, rate_func=linear)
        self.wait(1)

        # 2) fix z in the middle and sweep theta0
        self.play(z.animate.set_value(2.0), run_time=3)
        cap2 = Text("Fix z, rotate θ₀: the fan turns rigidly — the spread (pitch) is unchanged",
                    font_size=24, color=YELLOW).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap1), FadeIn(cap2))
        self.play(theta0.animate.set_value(180), run_time=8, rate_func=smooth)
        self.wait(2)


# ===========================================================================
# Scene 4 - 3D: Horizontal cylinder tangent to x-axis & ORD splitting
# ===========================================================================
class ORDLightSplitting(ThreeDScene):
    """3D horizontal cylinder resting tangentially on the x-axis in the horizontal
    (x,y) plane with z extending upwards.

    Linearly polarized white light enters at x = 0. Inside the glucose solution,
    Optical Rotatory Dispersion (Cauchy dispersion θ(x, λ) = θ₀ + c · x · A / λ²)
    causes each spectral wavelength to rotate at a different rate (blue ~2.1× faster
    than red), splitting the white light into distinct spectral helices and
    polarization states along the cylinder.
    """

    tube_length = 5.0
    tube_radius = 0.80
    concentration = 0.25

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=68 * DEGREES, theta=-55 * DEGREES)

        L = self.tube_length
        R = self.tube_radius
        c = self.concentration

        # Spectral bands (wavelength, color, display name)
        spectrum = [
            (650.0, "#ef4444", "Red 650 nm"),
            (580.0, "#eab308", "Yellow 580 nm"),
            (532.0, "#22c55e", "Green 532 nm"),
            (490.0, "#06b6d4", "Cyan 490 nm"),
            (450.0, "#3b82f6", "Blue 450 nm"),
        ]

        def rot_angle(lam, x_val, th0):
            return float(cauchy_rotation(lam, x_val, c, th0))

        # Dynamic trackers
        x_front = ValueTracker(0.0)      # propagating wavefront in [0, L]
        theta0_tr = ValueTracker(0.0)    # entrance polarizer angle (rad)
        inc_x = ValueTracker(-2.5)       # incident beam position [-2.5, 0]

        # -------------------------------------------------------------------
        # 1. 3D Coordinate Axes (x, y horizontal | z vertical)
        # -------------------------------------------------------------------
        axes = ThreeDAxes(
            x_range=[-3, 6.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 3.2, 1],
            x_length=9.5,
            y_length=5.0,
            z_length=3.2,
            axis_config={"color": GREY_C, "stroke_width": 2, "include_tip": True}
        )

        x_label = Text("x", font_size=22, color=RED_B).next_to(axes.x_axis.get_end(), RIGHT, buff=0.15)
        y_label = Text("y", font_size=22, color=GREEN_B).next_to(axes.y_axis.get_end(), UP, buff=0.15)
        z_label = Text("z", font_size=22, color=BLUE_B).next_to(axes.z_axis.get_end(), OUT, buff=0.15)
        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)

        # Subtle horizontal plane grid in the (x,y) plane at z = 0
        grid_lines = VGroup()
        for gx in np.linspace(-3, 6, 10):
            grid_lines.add(Line(np.array([gx, -2.5, 0]), np.array([gx, 2.5, 0]),
                                color=GREY_D, stroke_width=1, stroke_opacity=0.3))
        for gy in np.linspace(-2.5, 2.5, 6):
            grid_lines.add(Line(np.array([-3, gy, 0]), np.array([6, gy, 0]),
                                color=GREY_D, stroke_width=1, stroke_opacity=0.3))

        # Title & subtitle
        title = Text("Optical Rotatory Dispersion: White Light Splitting in a Glucose Tube",
                     font_size=22, weight=BOLD, color=WHITE).to_edge(UP, buff=0.25)
        plane_badge = Text("x,y plane: horizontal | z axis: vertical (upwards)",
                           font_size=15, color=GREY_A).next_to(title, DOWN, buff=0.1)
        self.add_fixed_in_frame_mobjects(title, plane_badge)

        # Spectral legend (shifted lower to avoid collision with title)
        legend_rows = VGroup()
        for _, col, name in spectrum:
            legend_rows.add(VGroup(Dot(radius=0.06, color=col),
                                   Text(name, font_size=15, color=col)).arrange(RIGHT, buff=0.12))
        legend_box = legend_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UR, buff=0.4).shift(DOWN * 1.3)
        self.add_fixed_in_frame_mobjects(legend_box)

        # -------------------------------------------------------------------
        # 2. 3D Cylindrical Tube resting on x-axis (x-axis is parallel tangent)
        # -------------------------------------------------------------------
        tube_ctr = np.array([L / 2, 0, R])
        # Transparent glass cylinder without wireframe grid
        tube = Cylinder(
            radius=R,
            height=L,
            direction=RIGHT,
            show_ends=False,
            resolution=(24, 48),
            fill_color="#38bdf8",
            fill_opacity=0.08,
            stroke_width=0,
            stroke_opacity=0,
            checkerboard_colors=False
        )
        tube.move_to(tube_ctr)

        # Circular entrance and exit rims
        ring_in = Circle(radius=R, color="#93c5fd", stroke_width=2.5, stroke_opacity=0.8)
        ring_in.rotate(PI / 2, axis=UP).move_to(np.array([0, 0, R]))
        ring_out = Circle(radius=R, color="#93c5fd", stroke_width=2.5, stroke_opacity=0.8)
        ring_out.rotate(PI / 2, axis=UP).move_to(np.array([L, 0, R]))

        # Subtle longitudinal glass reflection edge lines (top & side)
        edge_top = Line(np.array([0, 0, 2 * R]), np.array([L, 0, 2 * R]),
                        color="#93c5fd", stroke_width=1.2, stroke_opacity=0.45)
        edge_side = Line(np.array([0, -R, R]), np.array([L, -R, R]),
                         color="#93c5fd", stroke_width=1.2, stroke_opacity=0.45)

        # Longitudinal center axis
        opt_axis = DashedLine(np.array([0, 0, R]), np.array([L, 0, R]),
                              color=GREY_B, stroke_width=1.5, dash_length=0.1)

        # Tangent contact line where cylinder rests on x-axis (z = 0)
        tangent_line = Line(np.array([0, 0, 0]), np.array([L, 0, 0]),
                            color=YELLOW, stroke_width=3.5)
        tangent_tag = Text("cylinder tangent to x-axis along bottom (z = 0)",
                           font_size=15, color=YELLOW)
        tangent_tag.next_to(np.array([L / 2, -0.3, 0]), DOWN, buff=0.15)
        self.add_fixed_orientation_mobjects(tangent_tag)

        self.play(
            FadeIn(title), FadeIn(plane_badge), FadeIn(legend_box),
            Create(axes), Create(grid_lines),
            run_time=2.0
        )
        self.play(
            Create(tube), Create(ring_in), Create(ring_out),
            Create(edge_top), Create(edge_side),
            Create(opt_axis), Create(tangent_line), FadeIn(tangent_tag),
            run_time=2.0
        )
        self.wait(1.0)

        # -------------------------------------------------------------------
        # 3. Incident Linear Polarized White Light (x < 0 -> x = 0)
        # -------------------------------------------------------------------
        def build_incident_beam():
            curr_x = inc_x.get_value()
            if curr_x <= -2.5:
                return VGroup()
            glow = Line(np.array([-2.5, 0, R]), np.array([curr_x, 0, R]),
                        color="#e0f2fe", stroke_width=12, stroke_opacity=0.35)
            beam = Line(np.array([-2.5, 0, R]), np.array([curr_x, 0, R]),
                        color=WHITE, stroke_width=5.5)
            wf_disc = Circle(radius=R * 0.75, color=WHITE, stroke_width=2)
            wf_disc.rotate(PI / 2, axis=UP).move_to(np.array([curr_x, 0, R]))
            th0 = theta0_tr.get_value()
            d = R * 0.65 * np.array([0, np.sin(th0), np.cos(th0)])
            e_arrow = Line(np.array([curr_x, 0, R]) - d, np.array([curr_x, 0, R]) + d,
                           color=WHITE, stroke_width=4.5)
            return VGroup(glow, beam, wf_disc, e_arrow)

        incident_beam = always_redraw(build_incident_beam)
        self.add(incident_beam)

        cap1 = Text("Linearly polarized white light approaches and enters at x = 0",
                    font_size=20, color=WHITE).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cap1)
        self.play(FadeIn(cap1))
        self.play(inc_x.animate.set_value(0.0), run_time=2.5, rate_func=linear)
        self.wait(0.5)

        # Entrance polarizer slit (indicating θ₀)
        def build_slit():
            th0 = theta0_tr.get_value()
            d = R * 0.90 * np.array([0, np.sin(th0), np.cos(th0)])
            ctr = np.array([0, 0, R])
            return Line(ctr - d, ctr + d, color=YELLOW, stroke_width=5)

        pol_slit = always_redraw(build_slit)
        self.add(pol_slit)

        # -------------------------------------------------------------------
        # 4. White Light Enters & Splits into Spectral Helices (ORD)
        # -------------------------------------------------------------------
        cap2 = Text("Inside glucose: Cauchy ORD θ(x, λ) = θ₀ + c · x · (A / λ²)\nShorter wavelengths rotate faster: white light splits into spectral components!",
                    font_size=19, color=YELLOW_B).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap1), FadeIn(cap2))

        # Dynamic helices fanning out from x = 0
        def make_helix(lam, col, r_scale=0.60):
            def build():
                xf = x_front.get_value()
                if xf <= 0.02:
                    return VGroup()
                th0 = theta0_tr.get_value()
                return ParametricFunction(
                    lambda t: np.array([
                        t,
                        r_scale * R * np.sin(rot_angle(lam, t, th0)),
                        R + r_scale * R * np.cos(rot_angle(lam, t, th0))
                    ]),
                    t_range=[0, xf, 0.02],
                    color=col,
                    stroke_width=4.0
                )
            return always_redraw(build)

        helices = [make_helix(lam, col) for lam, col, _ in spectrum]
        for h in helices:
            self.add(h)

        # Propagating wavefront with rotating polarization needles
        def build_wavefront():
            xf = x_front.get_value()
            if xf <= 0.01:
                return VGroup()
            ctr = np.array([xf, 0, R])
            wf_circle = Circle(radius=R * 0.90, color=WHITE, stroke_width=1.5, stroke_opacity=0.4)
            wf_circle.set_fill(WHITE, opacity=0.08)
            wf_circle.rotate(PI / 2, axis=UP).move_to(ctr)

            needles = VGroup(wf_circle)
            th0 = theta0_tr.get_value()
            for lam, col, _ in spectrum:
                th = rot_angle(lam, xf, th0)
                d = R * 0.72 * np.array([0, np.sin(th), np.cos(th)])
                needle = Line(ctr - d, ctr + d, color=col, stroke_width=3.5)
                needles.add(needle)
            return needles

        wavefront = always_redraw(build_wavefront)
        self.add(wavefront)

        # Propagate wavefront along the tube with ambient camera rotation
        self.begin_ambient_camera_rotation(rate=0.08)
        self.play(x_front.animate.set_value(L), run_time=8.5, rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.wait(1.5)

        # -------------------------------------------------------------------
        # 5. Dispersion Pitch Analysis
        # -------------------------------------------------------------------
        pitch_str = "   ".join([f"P({name.split()[0]}): {helix_pitch(lam, c):.1f} cm"
                                for lam, _, name in spectrum[::2]])
        cap3 = Text(f"Pitch P = 2π λ² / (A c)  →  {pitch_str}\nBlue completes 2 full turns while Red completes 1 turn in 5 cm",
                    font_size=19, color=WHITE).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap2), FadeIn(cap3))
        self.wait(2.5)

        # -------------------------------------------------------------------
        # 6. Rotate Entrance Polarizer: Helices "Walk" (The Barber Pole Effect)
        # -------------------------------------------------------------------
        cap4 = Text("Rotating entrance polarizer θ₀ makes all helices and stripes walk along x with unchanged pitch!",
                    font_size=19, color=YELLOW).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap3), FadeIn(cap4))

        self.move_camera(phi=74 * DEGREES, theta=-75 * DEGREES, run_time=2.0)
        self.play(theta0_tr.animate.set_value(TAU), run_time=8.0, rate_func=linear)
        self.wait(1.5)

        # Concluding summary
        summary = Text("Optical Rotatory Dispersion (ORD) physically separates polarization states by wavelength,\nrevealing the characteristic helical 'barber pole' dispersion pattern.",
                       font_size=18, color=WHITE).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap4), FadeIn(summary))
        self.wait(3.0)


# ===========================================================================
# Scene 5 - 3D: Horizontal cylinder with continuous light spectrum
# ===========================================================================
class ORDContinuousSpectrum(ThreeDScene):
    """3D horizontal cylinder resting tangentially on the x-axis with a continuous
    colour spectrum inside the cylinder.

    Polychromatic white light containing a continuous distribution of wavelengths
    (415 nm to 675 nm) enters at x = 0. Cauchy Optical Rotatory Dispersion continuously
    disperses the polarization angles θ(x, λ) = θ₀ + c · x · A / λ², producing a
    smooth, continuous 3D helical rainbow spectrum (the barber pole effect) inside the
    transparent cylinder. Rotating the entrance polarizer causes the continuous rainbow
    stripes to walk along the cylinder in 3D.
    """

    tube_length = 5.0
    tube_radius = 0.80
    concentration = 0.32
    n_spectral_samples = 64
    nu = 72
    nv = 36

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=68 * DEGREES, theta=-55 * DEGREES)

        L = self.tube_length
        R = self.tube_radius
        c = self.concentration

        # Continuous spectral wavelengths from 400 nm to 700 nm
        wavelengths = np.linspace(400.0, 700.0, self.n_spectral_samples)
        channel_weights = np.array([wavelength_to_srgb(wl) for wl in wavelengths])
        dispersion_rates = np.array([CAUCHY_A / (wl ** 2) for wl in wavelengths])

        def wl_to_hex(wl):
            rgb = np.clip(wavelength_to_srgb(wl), 0, 1)
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

        spectrum_colors = [wl_to_hex(wl) for wl in wavelengths]

        # Mesh midpoints along u (length) and v (azimuth)
        u_mids = np.linspace(L / (2 * self.nu), L - L / (2 * self.nu), self.nu)
        v_mids = np.linspace(PI / self.nv, TAU - PI / self.nv, self.nv)

        U = u_mids[:, None, None]      # (nu, 1, 1)
        V = v_mids[None, :, None]      # (1, nv, 1)
        rates = dispersion_rates[None, None, :]  # (1, 1, n_wl)
        u_rates = c * U * rates        # precomputed (nu, 1, n_wl)

        def get_surface_hex_colors(th0):
            Theta = th0 + u_rates
            I = np.cos(Theta - V) ** 2
            RGB = np.tensordot(I, channel_weights, axes=([2], [0])) / self.n_spectral_samples
            # Subtle baseline reduction (0.42) for distinct helical stripes while preserving
            # the natural pastel/iridescent hues seen in sugar water & 3b1b demonstrations
            min_u = np.min(RGB, axis=1, keepdims=True)
            RGB_sub = RGB - 0.42 * min_u
            max_val = np.percentile(RGB_sub, 99.5)
            if max_val > 1e-5:
                RGB_sub = RGB_sub / max_val
            RGB_norm = np.clip(RGB_sub, 0, 1)
            RGB_final = np.power(RGB_norm, 1.0 / 1.9)
            uint8_rgb = (np.clip(RGB_final, 0, 1) * 255).astype(np.uint8).reshape(-1, 3)
            return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in uint8_rgb]

        # Dynamic ValueTrackers
        x_front = ValueTracker(0.0)      # propagating wavefront in [0, L]
        theta0_tr = ValueTracker(0.0)    # entrance polarizer angle (rad)
        inc_x = ValueTracker(-2.5)       # incident beam position [-2.5, 0]

        # -------------------------------------------------------------------
        # 1. 3D Coordinate Axes (x, y horizontal | z vertical)
        # -------------------------------------------------------------------
        axes = ThreeDAxes(
            x_range=[-3, 6.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[0, 2.2, 1],
            x_length=9.5,
            y_length=5.0,
            z_length=2.2,
            axis_config={"color": GREY_C, "stroke_width": 2, "include_tip": True}
        )

        x_label = Text("x", font_size=22, color=RED_B).next_to(axes.x_axis.get_end(), RIGHT, buff=0.15)
        y_label = Text("y", font_size=22, color=GREEN_B).next_to(axes.y_axis.get_end(), UP, buff=0.15)
        z_label = Text("z", font_size=22, color=BLUE_B).next_to(axes.z_axis.get_end(), OUT, buff=0.15)
        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)

        # Subtle horizontal plane grid at z = 0
        grid_lines = VGroup()
        for gx in np.linspace(-3, 6, 10):
            grid_lines.add(Line(np.array([gx, -2.5, 0]), np.array([gx, 2.5, 0]),
                                color=GREY_D, stroke_width=1, stroke_opacity=0.3))
        for gy in np.linspace(-2.5, 2.5, 6):
            grid_lines.add(Line(np.array([-3, gy, 0]), np.array([6, gy, 0]),
                                color=GREY_D, stroke_width=1, stroke_opacity=0.3))

        # Title & subtitle banner
        title = Text("Optical Rotatory Dispersion: Continuous 3D Spectrum",
                     font_size=22, weight=BOLD, color=WHITE).to_edge(UP, buff=0.22)
        plane_badge = Text("x,y plane: horizontal | z axis: vertical (upwards)",
                           font_size=15, color=GREY_A).next_to(title, DOWN, buff=0.1)
        self.add_fixed_in_frame_mobjects(title, plane_badge)

        # Continuous Spectral Color Bar (Legend) - shifted DOWN * 1.45 to prevent collision
        bar_width = 2.8
        bar_height = 0.20
        n_segments = self.n_spectral_samples
        seg_w = bar_width / n_segments
        color_bar = VGroup()
        for i in range(n_segments):
            lam_i = 400.0 + (700.0 - 400.0) * (i / (n_segments - 1))
            col_i = wl_to_hex(lam_i)
            rect = Rectangle(width=seg_w * 1.05, height=bar_height,
                             fill_color=col_i, fill_opacity=1.0, stroke_width=0)
            rect.move_to(RIGHT * (i * seg_w - bar_width / 2 + seg_w / 2))
            color_bar.add(rect)

        bar_border = RoundedRectangle(corner_radius=0.04, width=bar_width + 0.04,
                                      height=bar_height + 0.04, color=WHITE, stroke_width=1.5)
        bar_border.move_to(color_bar.get_center())

        bar_label_v = Text("400 nm", font_size=12, color="#a78bfa").next_to(color_bar, LEFT, buff=0.10)
        bar_label_r = Text("700 nm", font_size=12, color="#ef4444").next_to(color_bar, RIGHT, buff=0.10)
        bar_title = Text("Continuous Visible Spectrum", font_size=13, color=WHITE).next_to(color_bar, UP, buff=0.08)

        legend_box = VGroup(bar_title, color_bar, bar_border, bar_label_v, bar_label_r)
        legend_box.to_corner(UR, buff=0.4).shift(DOWN * 1.45)
        self.add_fixed_in_frame_mobjects(legend_box)

        # Polarizer Dial (UI) in Upper Left - shifted DOWN * 1.45 to align with legend
        dial_circle = Circle(radius=0.40, color=GREY_A, stroke_width=2.0)
        dial_center = dial_circle.get_center()

        def build_dial_needle():
            th = theta0_tr.get_value()
            d = 0.35 * np.array([np.sin(th), np.cos(th), 0])
            return Line(dial_center - d, dial_center + d, color=YELLOW, stroke_width=4.5)

        dial_needle = always_redraw(build_dial_needle)
        dial_title = Text("Polarizer θ₀", font_size=13, color=WHITE).next_to(dial_circle, UP, buff=0.08)
        dial_readout = always_redraw(
            lambda: Text(f"{int(round(np.degrees(theta0_tr.get_value()))) % 360:3d}°",
                         font_size=14, color=YELLOW).next_to(dial_circle, DOWN, buff=0.08)
        )
        dial_group = VGroup(dial_title, dial_circle, dial_needle, dial_readout)
        dial_group.to_corner(UL, buff=0.4).shift(DOWN * 1.45)
        self.add_fixed_in_frame_mobjects(dial_group)

        # -------------------------------------------------------------------
        # 2. Transparent 3D Cylinder on x-axis (tangent along bottom at z = 0)
        # -------------------------------------------------------------------
        tube_ctr = np.array([L / 2, 0, R])
        tube = Cylinder(
            radius=R,
            height=L,
            direction=RIGHT,
            show_ends=False,
            resolution=(24, 48),
            fill_color="#38bdf8",
            fill_opacity=0.08,
            stroke_width=0,
            stroke_opacity=0,
            checkerboard_colors=False
        )
        tube.move_to(tube_ctr)

        # Circular entrance and exit rims
        ring_in = Circle(radius=R, color="#93c5fd", stroke_width=2.5, stroke_opacity=0.8)
        ring_in.rotate(PI / 2, axis=UP).move_to(np.array([0, 0, R]))
        ring_out = Circle(radius=R, color="#93c5fd", stroke_width=2.5, stroke_opacity=0.8)
        ring_out.rotate(PI / 2, axis=UP).move_to(np.array([L, 0, R]))

        # Glass silhouette reflection lines
        edge_top = Line(np.array([0, 0, 2 * R]), np.array([L, 0, 2 * R]),
                        color="#93c5fd", stroke_width=1.2, stroke_opacity=0.45)
        edge_side = Line(np.array([0, -R, R]), np.array([L, -R, R]),
                         color="#93c5fd", stroke_width=1.2, stroke_opacity=0.45)

        opt_axis = DashedLine(np.array([0, 0, R]), np.array([L, 0, R]),
                              color=GREY_B, stroke_width=1.5, dash_length=0.1)

        tangent_line = Line(np.array([0, 0, 0]), np.array([L, 0, 0]),
                            color=YELLOW, stroke_width=3.5)
        tangent_tag = Text("cylinder tangent to x-axis along bottom (z = 0)",
                           font_size=15, color=YELLOW)
        tangent_tag.next_to(np.array([L / 2, -0.3, 0]), DOWN, buff=0.15)
        self.add_fixed_orientation_mobjects(tangent_tag)

        self.play(
            FadeIn(title), FadeIn(plane_badge), FadeIn(legend_box), FadeIn(dial_group),
            Create(axes), Create(grid_lines),
            run_time=2.0
        )
        self.play(
            Create(tube), Create(ring_in), Create(ring_out),
            Create(edge_top), Create(edge_side),
            Create(opt_axis), Create(tangent_line), FadeIn(tangent_tag),
            run_time=2.0
        )
        self.wait(0.5)

        # -------------------------------------------------------------------
        # 3. Incident Linear Polarized White Light (x < 0 -> x = 0)
        # -------------------------------------------------------------------
        def build_incident_beam():
            curr_x = inc_x.get_value()
            if curr_x <= -2.5:
                return VGroup()
            glow = Line(np.array([-2.5, 0, R]), np.array([curr_x, 0, R]),
                        color="#e0f2fe", stroke_width=12, stroke_opacity=0.35)
            beam = Line(np.array([-2.5, 0, R]), np.array([curr_x, 0, R]),
                        color=WHITE, stroke_width=5.5)
            wf_disc = Circle(radius=R * 0.75, color=WHITE, stroke_width=2)
            wf_disc.rotate(PI / 2, axis=UP).move_to(np.array([curr_x, 0, R]))
            th0 = theta0_tr.get_value()
            d = R * 0.65 * np.array([0, np.sin(th0), np.cos(th0)])
            e_arrow = Line(np.array([curr_x, 0, R]) - d, np.array([curr_x, 0, R]) + d,
                           color=WHITE, stroke_width=4.5)
            return VGroup(glow, beam, wf_disc, e_arrow)

        incident_beam = always_redraw(build_incident_beam)
        self.add(incident_beam)

        cap1 = Text("Polychromatic white light (continuous visible spectrum) enters at x = 0",
                    font_size=19, color=WHITE).to_edge(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cap1)
        self.play(FadeIn(cap1))
        self.play(inc_x.animate.set_value(0.0), run_time=2.0, rate_func=linear)
        self.wait(0.5)

        # Entrance polarizer slit at x = 0
        def build_slit():
            th0 = theta0_tr.get_value()
            d = R * 0.90 * np.array([0, np.sin(th0), np.cos(th0)])
            ctr = np.array([0, 0, R])
            return Line(ctr - d, ctr + d, color=YELLOW, stroke_width=5)

        pol_slit = always_redraw(build_slit)
        self.add(pol_slit)

        # -------------------------------------------------------------------
        # 4. Continuous Spectrum 3D Surface Inside Cylinder
        # -------------------------------------------------------------------
        cap2 = Text("Continuous Cauchy ORD: θ(x, λ) = θ₀ + c · x · (A / λ²)\nSmooth, natural spectral barber pole as seen in real-life polarimetry demonstrations.",
                    font_size=18, color=YELLOW_B).to_edge(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(cap2)
        self.play(FadeOut(cap1), FadeIn(cap2))

        # Create continuous 3D Surface
        r_inner = 0.76 * R
        surf = Surface(
            lambda u, v: np.array([u, r_inner * np.sin(v), R + r_inner * np.cos(v)]),
            u_range=[0, L],
            v_range=[0, TAU],
            resolution=(self.nu, self.nv),
            checkerboard_colors=False
        )
        for sub in surf.submobjects:
            sub.set_fill(opacity=0.0)
            sub.set_stroke(width=1.1, opacity=0.0)
        self.add(surf)

        # Precompute initial colors at theta0 = 0
        initial_hex_colors = get_surface_hex_colors(0.0)

        # Wavefront disc with continuous rainbow fanning polarization needles
        def build_wavefront():
            xf = x_front.get_value()
            if xf <= 0.01 or xf >= L - 0.01:
                return VGroup()
            ctr = np.array([xf, 0, R])
            wf_circle = Circle(radius=R * 0.88, color=WHITE, stroke_width=1.5, stroke_opacity=0.4)
            wf_circle.set_fill(WHITE, opacity=0.06)
            wf_circle.rotate(PI / 2, axis=UP).move_to(ctr)

            needles = VGroup(wf_circle)
            th0 = theta0_tr.get_value()
            for lam, col in zip(wavelengths[::2], spectrum_colors[::2]):
                th = float(cauchy_rotation(lam, xf, c, th0))
                d = R * 0.72 * np.array([0, np.sin(th), np.cos(th)])
                needle = Line(ctr - d, ctr + d, color=col, stroke_width=2.0, stroke_opacity=0.9)
                needles.add(needle)
            return needles

        wavefront = always_redraw(build_wavefront)
        self.add(wavefront)

        # Propagation updater: reveals surface quads as wavefront advances
        def update_propagation(m):
            xf = x_front.get_value()
            idx = 0
            for i in range(self.nu):
                u_val = u_mids[i]
                if u_val > xf:
                    for j in range(self.nv):
                        m.submobjects[idx].set_fill(opacity=0.0)
                        m.submobjects[idx].set_stroke(opacity=0.0)
                        idx += 1
                else:
                    for j in range(self.nv):
                        col = initial_hex_colors[idx]
                        m.submobjects[idx].set_fill(col, opacity=0.92)
                        m.submobjects[idx].set_stroke(color=col, width=1.1, opacity=0.92)
                        idx += 1

        surf.add_updater(update_propagation)

        # Propagate wavefront along the tube with ambient camera rotation
        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(x_front.animate.set_value(L), run_time=5.0, rate_func=linear)
        self.stop_ambient_camera_rotation()
        surf.remove_updater(update_propagation)

        # Ensure all surface patches are visible at the end of propagation
        for idx in range(self.nu * self.nv):
            col = initial_hex_colors[idx]
            surf.submobjects[idx].set_fill(col, opacity=0.92)
            surf.submobjects[idx].set_stroke(color=col, width=1.1, opacity=0.92)
        self.wait(1.0)

        # -------------------------------------------------------------------
        # 5. Pitch Equation & Continuous Dispersion
        # -------------------------------------------------------------------
        p_v = 2 * PI * (400 ** 2) / (CAUCHY_A * c)
        p_g = 2 * PI * (532 ** 2) / (CAUCHY_A * c)
        p_r = 2 * PI * (700 ** 2) / (CAUCHY_A * c)
        cap3 = Text(f"Continuous Pitch Formula: P(λ) = 2π λ² / (A c)\nViolet (400 nm): P ≈ {p_v:.2f} cm | Green (532 nm): P ≈ {p_g:.2f} cm | Red (700 nm): P ≈ {p_r:.2f} cm\nSmooth, pastel continuous dispersion matching 3b1b & real-life polarimetry demonstrations.",
                    font_size=17, color=WHITE).to_edge(DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(cap3)
        self.play(FadeOut(cap2), FadeIn(cap3))
        self.wait(2.5)

        # -------------------------------------------------------------------
        # 6. Rotate Entrance Polarizer: Walking Continuous Spectrum Stripes
        # -------------------------------------------------------------------
        cap4 = Text("Rotating entrance polarizer θ₀ makes the continuous rainbow stripes walk along x in 3D!\n(Shift: Δx = Δθ₀ · λ² / (A c))",
                    font_size=18, color=YELLOW).to_edge(DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(cap4)
        self.play(FadeOut(cap3), FadeIn(cap4))

        self.move_camera(phi=72 * DEGREES, theta=-70 * DEGREES, run_time=1.5)

        # Rotation updater: updates colors as theta0 sweeps
        def update_walking(m):
            th = theta0_tr.get_value()
            hex_cols = get_surface_hex_colors(th)
            for idx in range(self.nu * self.nv):
                col = hex_cols[idx]
                m.submobjects[idx].set_fill(col, opacity=0.92)
                m.submobjects[idx].set_stroke(color=col, width=1.1, opacity=0.92)

        surf.add_updater(update_walking)
        self.play(theta0_tr.animate.set_value(TAU), run_time=5.0, rate_func=linear)
        surf.remove_updater(update_walking)
        self.wait(1.0)

        # -------------------------------------------------------------------
        # 7. Concluding Summary
        # -------------------------------------------------------------------
        summary = Text("Continuous Optical Rotatory Dispersion (ORD):\nInfinitesimal wavelengths dλ rotate at rates dθ/dx ∝ 1/λ²,\nforming a smooth, continuous pastel barber pole that walks with polarizer rotation.",
                       font_size=18, color=WHITE).to_edge(DOWN, buff=0.25)
        self.add_fixed_in_frame_mobjects(summary)
        self.play(FadeOut(cap4), FadeIn(summary))
        self.wait(2.5)
