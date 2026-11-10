"""Interactive dashboard built with matplotlib widgets (replaces ipywidgets).

Works in any desktop matplotlib backend (Qt / Tk / macOS) and in Jupyter with
``%matplotlib widget`` (ipympl).
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons, RadioButtons

from .config import (LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE, DEFAULT_CONCENTRATION,
                     BG_PANEL)
from .raymarch import simulate_barber_pole
from .spectral import cauchy_rotation

MODES = ("Continuous Spectrum (White Light)", "Discrete RGB Bands (Laser Trio)")


def format_info(concentration, theta0, filter2_enabled, filter2_angle, mode):
    """Text for the metrics panel."""
    def ang(lam, z):
        return np.degrees(cauchy_rotation(lam, z, concentration, np.radians(theta0))) % 360

    exit_txt = f"{filter2_angle:.1f}°" if filter2_enabled else "None (Open)"
    return (
        "OPTICAL ROTATORY DISPERSION METRICS\n"
        "──────────────────────────────────────────────\n"
        f"• Chiral Concentration (c):     {concentration:.2f} mol/L\n"
        f"• Entrance Polarizer (θ₀):      {theta0:.1f}°\n"
        f"• Exit Analyzer (θ₂):           {exit_txt}\n"
        f"• Spectral Mode:                {mode}\n\n"
        "POLARIZATION AT MID-TUBE (z = 2.0 cm):\n"
        f"  - Red   (650 nm):  θ = {ang(LAMBDA_RED, 2.0):6.1f}°\n"
        f"  - Green (532 nm):  θ = {ang(LAMBDA_GREEN, 2.0):6.1f}°\n"
        f"  - Blue  (450 nm):  θ = {ang(LAMBDA_BLUE, 2.0):6.1f}°\n\n"
        "POLARIZATION AT EXIT (z = 4.0 cm):\n"
        f"  - Red   (650 nm):  θ = {ang(LAMBDA_RED, 4.0):6.1f}°\n"
        f"  - Green (532 nm):  θ = {ang(LAMBDA_GREEN, 4.0):6.1f}°\n"
        f"  - Blue  (450 nm):  θ = {ang(LAMBDA_BLUE, 4.0):6.1f}°\n\n"
        "PHYSICAL OBSERVATIONS:\n"
        "──────────────────────────────────────────────\n"
        "1. Dragging θ₀ causes the helical bands to\n"
        "   'walk' along the cylinder without changing\n"
        "   the optical pitch.\n"
        "2. Higher concentration compresses the pitch\n"
        "   increasing the number of diagonal stripes."
    )


def build_dashboard(resolution=(240, 120), n_depth_steps=24):
    """Create the figure and return (fig, widgets). Keep a reference to widgets!"""
    fig = plt.figure(figsize=(13, 8.5), facecolor=BG_PANEL)
    ax_tube = fig.add_axes([0.06, 0.32, 0.36, 0.60])
    ax_info = fig.add_axes([0.47, 0.32, 0.50, 0.60])
    ax_info.axis("off")

    state = dict(c=DEFAULT_CONCENTRATION, th0=0.0, f2_on=False, f2=0.0, mode=MODES[0])

    def render():
        return simulate_barber_pole(
            concentration=state["c"], theta0_deg=state["th0"],
            filter2_deg=state["f2"] if state["f2_on"] else None,
            mode="spectrum" if "Continuous" in state["mode"] else "rgb",
            resolution=resolution, n_depth_steps=n_depth_steps)

    im = ax_tube.imshow(render(), extent=[-1.15, 1.15, 0, 4.0], origin="lower", aspect="auto")
    title = ax_tube.set_title(f"Simulated Chiral Tube ({state['mode']})", color="white",
                              fontweight="bold", fontsize=12, pad=10)
    ax_tube.set_xlabel("Transverse Coordinate x (cm)", color="#94a3b8", fontweight="bold")
    ax_tube.set_ylabel("Axial Height z (cm)", color="#94a3b8", fontweight="bold")
    ax_tube.tick_params(colors="#64748b")
    for s in ax_tube.spines.values():
        s.set_color("#334155")

    info = ax_info.text(0.02, 0.98, "", transform=ax_info.transAxes, fontsize=10,
                        family="monospace", color="#38bdf8", va="top",
                        bbox=dict(boxstyle="round,pad=1", facecolor="#0f172a",
                                  edgecolor="#38bdf8", alpha=0.8))

    def refresh(_=None):
        im.set_data(render())
        title.set_text(f"Simulated Chiral Tube ({state['mode']})")
        info.set_text(format_info(state["c"], state["th0"], state["f2_on"],
                                  state["f2"], state["mode"]))
        fig.canvas.draw_idle()

    # --- widgets ------------------------------------------------------------
    kw = dict(color="#38bdf8")
    s_c = Slider(fig.add_axes([0.14, 0.22, 0.32, 0.03]), "Concentration c",
                 0.1, 2.0, valinit=state["c"], valstep=0.05, **kw)
    s_th0 = Slider(fig.add_axes([0.14, 0.17, 0.32, 0.03]), "Entrance θ₀ (°)",
                   0, 360, valinit=0, valstep=5, **kw)
    s_f2 = Slider(fig.add_axes([0.14, 0.12, 0.32, 0.03]), "Exit θ₂ (°)",
                  0, 360, valinit=0, valstep=5, **kw)
    chk = CheckButtons(fig.add_axes([0.55, 0.12, 0.20, 0.12], facecolor=BG_PANEL),
                       ["Enable exit polarizer"], [False])
    rad = RadioButtons(fig.add_axes([0.55, 0.01, 0.35, 0.10], facecolor=BG_PANEL),
                       MODES, active=0)

    for w in (s_c, s_th0, s_f2):
        w.label.set_color("white")
        w.valtext.set_color("white")
    for lbl in chk.labels + rad.labels:
        lbl.set_color("white")

    def on_c(v): state["c"] = v; refresh()
    def on_th0(v): state["th0"] = v; refresh()
    def on_f2(v): state["f2"] = v; refresh()
    def on_chk(_): state["f2_on"] = chk.get_status()[0]; refresh()
    def on_mode(label): state["mode"] = label; refresh()

    s_c.on_changed(on_c)
    s_th0.on_changed(on_th0)
    s_f2.on_changed(on_f2)
    chk.on_clicked(on_chk)
    rad.on_clicked(on_mode)

    refresh()
    return fig, (s_c, s_th0, s_f2, chk, rad)


def run_dashboard():
    fig, widgets_ = build_dashboard()   # noqa: F841  (keep references alive)
    plt.show()
