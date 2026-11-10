"""
Script to generate publication-quality figures demonstrating the mathematical
and physical relations between Optical Rotation and Wavelength (Cauchy ORD).

Produces:
  1. out/ord_dispersion_comprehensive.png : 6-panel comprehensive physics dashboard
  2. out/ord_curve_theta_vs_lambda.png     : Focused theta(lambda) vs 1/lambda^2 plot
  3. out/ord_polarization_fan.png         : Real-space polarization angle fan
  4. out/ord_analyzer_transmission.png    : Malus analyzer transmission spectra
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.ticker as ticker

from barber_pole.config import CAUCHY_A
from barber_pole.spectral import wavelength_to_srgb

# Visual Style Config
BG_COLOR = "#0b0f19"
PANEL_COLOR = "#111827"
BORDER_COLOR = "#1f2937"
GRID_COLOR = "#374151"
TEXT_COLOR = "#f3f4f6"
TEXT_MUTED = "#9ca3af"

LASER_LINES = [
    (405.0, "Violet (405 nm)", "#8b5cf6"),
    (450.0, "Blue (450 nm)",   "#3b82f6"),
    (532.0, "Green (532 nm)",  "#22c55e"),
    (589.3, "Na D (589 nm)",   "#eab308"),
    (632.8, "HeNe (633 nm)",   "#f97316"),
    (670.0, "Red (670 nm)",    "#ef4444"),
]


def apply_theme(fig, axes):
    """Apply dark scientific theme to figure and all axes."""
    fig.patch.set_facecolor(BG_COLOR)
    for ax in axes:
        ax.set_facecolor(PANEL_COLOR)
        ax.tick_params(colors=TEXT_MUTED, which="both", labelsize=10)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)
            spine.set_linewidth(1.2)
        ax.grid(True, linestyle="--", color=GRID_COLOR, alpha=0.5, linewidth=0.8)


def get_rainbow_colormap():
    """Build a continuous Matplotlib colormap from true physical visible spectrum."""
    wls = np.linspace(380.0, 750.0, 256)
    rgb_list = [wavelength_to_srgb(w) for w in wls]
    from matplotlib.colors import ListedColormap
    return ListedColormap(rgb_list)


def plot_comprehensive_dashboard(save_path="out/ord_dispersion_comprehensive.png",
                                 concentration=0.32, z_depth=2.0):
    """Generate 6-panel comprehensive ORD diagnostic dashboard."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig = plt.figure(figsize=(18, 12), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)

    gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.28,
                          left=0.06, right=0.96, top=0.86, bottom=0.07)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, 0], projection="polar")
    ax5 = fig.add_subplot(gs[1, 1])
    ax6 = fig.add_subplot(gs[1, 2])

    all_axes = [ax1, ax2, ax3, ax4, ax5, ax6]
    apply_theme(fig, all_axes)

    lam = np.linspace(380.0, 750.0, 600)
    inv_lam2 = 1.0 / (lam ** 2)

    # -------------------------------------------------------------------------
    # Panel 1: Optical Rotation theta(lambda) with Spectral Underfill
    # -------------------------------------------------------------------------
    for c_val, alpha_val, ls_val in [(0.15, 0.65, ":"), (concentration, 1.0, "-"), (0.60, 0.75, "--")]:
        rot_deg = np.degrees(c_val * z_depth * CAUCHY_A / (lam ** 2))
        lbl = f"c = {c_val:.2f} mol/L" + (" (current)" if abs(c_val - concentration) < 1e-3 else "")
        ax1.plot(lam, rot_deg, color="#38bdf8" if c_val == concentration else TEXT_MUTED,
                 lw=2.8 if c_val == concentration else 1.8, linestyle=ls_val, alpha=alpha_val, label=lbl)

    # Colored gradient fill under the main curve
    main_rot = np.degrees(concentration * z_depth * CAUCHY_A / (lam ** 2))
    cmap = get_rainbow_colormap()
    norm = plt.Normalize(vmin=380, vmax=750)
    for i in range(len(lam) - 1):
        ax1.fill_between(lam[i:i+2], 0, main_rot[i:i+2],
                         color=cmap(norm(lam[i])), alpha=0.35, edgecolor="none")

    # Callouts for laser lines
    for w_line, name_line, col_line in LASER_LINES:
        theta_line = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax1.plot(w_line, theta_line, "o", color=col_line, markersize=6, markeredgecolor="white", markeredgewidth=1)
        ax1.axvline(w_line, color=col_line, linestyle=":", alpha=0.35, linewidth=0.8)

    ax1.set_title(r"$\mathbf{1.\;Optical\;Rotation\;vs.\;Wavelength}\;\;[\theta(\lambda) \propto 1/\lambda^2]$",
                  fontsize=12, loc="left", pad=10, color=TEXT_COLOR)
    ax1.set_xlabel(r"Wavelength $\lambda$ (nm)", fontsize=11, fontweight="bold")
    ax1.set_ylabel(rf"Rotation $\theta$ (deg at $z = {z_depth:.1f}$ cm)", fontsize=11, fontweight="bold")
    ax1.set_xlim(380, 750)
    ax1.set_ylim(0, np.degrees(concentration * z_depth * CAUCHY_A / (380 ** 2)) * 1.08)
    ax1.legend(loc="upper right", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # -------------------------------------------------------------------------
    # Panel 2: Biot's Law Linear Verification (theta vs 1/lambda^2)
    # -------------------------------------------------------------------------
    inv_lam2_scaled = (1000.0 / lam) ** 2  # (1/micron)^2
    slope_k = np.degrees(concentration * z_depth * CAUCHY_A * 1e-6)  # deg / (micron)^-2
    ax2.plot(inv_lam2_scaled, main_rot, color="#34d399", lw=2.6, label=rf"Biot Fit: $\theta = {slope_k:.1f} \cdot (1/\lambda^2)$")

    for w_line, name_line, col_line in LASER_LINES:
        x_pt = (1000.0 / w_line) ** 2
        y_pt = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax2.plot(x_pt, y_pt, "o", color=col_line, markersize=6, markeredgecolor="white", markeredgewidth=1)
        ax2.annotate(f"{int(w_line)} nm", (x_pt, y_pt), textcoords="offset points",
                     xytext=(-18, 8), color=TEXT_COLOR, fontsize=8, fontweight="bold")

    ax2.set_title(r"$\mathbf{2.\;Biot's\;Dispersion\;Law}\;\;[\theta \;\mathrm{is\;strictly\;linear\;in\;} 1/\lambda^2]$",
                  fontsize=12, loc="left", pad=10, color=TEXT_COLOR)
    ax2.set_xlabel(r"Inverse Square Wavelength $1/\lambda^2$ ($\mu\mathrm{m}^{-2}$)", fontsize=11, fontweight="bold")
    ax2.set_ylabel(rf"Rotation $\theta$ (deg at $z = {z_depth:.1f}$ cm)", fontsize=11, fontweight="bold")
    ax2.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # Secondary top axis showing wavelength in nm
    ax2_top = ax2.twiny()
    ax2_top.set_xlim(ax2.get_xlim())
    tick_wls = np.array([700, 600, 500, 450, 400])
    ax2_top.set_xticks((1000.0 / tick_wls) ** 2)
    ax2_top.set_xticklabels([f"{w} nm" for w in tick_wls], color=TEXT_MUTED, fontsize=9)
    ax2_top.spines["top"].set_color(BORDER_COLOR)

    # -------------------------------------------------------------------------
    # Panel 3: Helical Pitch P(lambda) = 2*pi*lambda^2 / (A * c)
    # -------------------------------------------------------------------------
    pitch_cm = (2.0 * np.pi * (lam ** 2)) / (CAUCHY_A * concentration)
    ax3.plot(lam, pitch_cm, color="#f43f5e", lw=2.8, label=r"$P(\lambda) = \frac{2\pi \lambda^2}{A \cdot c}$ (spatial pitch)")

    # Fill under pitch curve
    ax3.fill_between(lam, 0, pitch_cm, color="#f43f5e", alpha=0.15)

    for w_line, name_line, col_line in LASER_LINES:
        p_val = (2.0 * np.pi * (w_line ** 2)) / (CAUCHY_A * concentration)
        ax3.plot(w_line, p_val, "o", color=col_line, markersize=6, markeredgecolor="white", markeredgewidth=1)
        ax3.annotate(f"P={p_val:.2f} cm", (w_line, p_val), textcoords="offset points",
                     xytext=(6, -6), color=col_line, fontsize=8, fontweight="bold")

    ax3.set_title(r"$\mathbf{3.\;3D\;Helical\;Pitch\;vs.\;Wavelength}\;\;[P(\lambda) \propto \lambda^2]$",
                  fontsize=12, loc="left", pad=10, color=TEXT_COLOR)
    ax3.set_xlabel(r"Wavelength $\lambda$ (nm)", fontsize=11, fontweight="bold")
    ax3.set_ylabel(r"Barber Pole Spatial Pitch $P$ (cm / $360^\circ$)", fontsize=11, fontweight="bold")
    ax3.set_xlim(380, 750)
    ax3.set_ylim(0, pitch_cm.max() * 1.15)
    ax3.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # -------------------------------------------------------------------------
    # Panel 4: Polarization Angle Fan in Real Space (Polar Dial Compass)
    # -------------------------------------------------------------------------
    ax4.set_theta_zero_location("N")   # 0 deg points upwards (vertical y polarization)
    ax4.set_theta_direction(-1)        # Clockwise rotation (dextrorotatory)
    ax4.set_facecolor(PANEL_COLOR)

    # Plot polarization vectors for 32 continuous spectral slices at z = z_depth
    sample_wls = np.linspace(400.0, 700.0, 48)
    for w in sample_wls:
        th_rad = (concentration * z_depth * CAUCHY_A) / (w ** 2)
        rgb_col = wavelength_to_srgb(w)
        ax4.plot([th_rad, th_rad], [0, 1.0], color=rgb_col, lw=2.2, alpha=0.85)

    # Incident polarization arrow (white line at theta = 0)
    ax4.plot([0, 0], [0, 1.08], color="white", lw=3.0, label="Incident (x = 0)")

    # Key laser needles
    for w_line, name_line, col_line in LASER_LINES:
        th_line = (concentration * z_depth * CAUCHY_A) / (w_line ** 2)
        ax4.plot([th_line, th_line], [0, 1.04], color=col_line, lw=2.5)
        ax4.plot([th_line], [1.04], "o", color=col_line, markersize=5)

    ax4.set_ylim(0, 1.15)
    ax4.set_yticks([])
    ax4.set_title(r"$\mathbf{4.\;Polarization\;Fan\;at\;} z = " + f"{z_depth:.1f}" + r"\;\mathrm{cm}$" + "\n" +
                  r"(White light fans into continuous rainbow dial)",
                  fontsize=12, pad=18, color=TEXT_COLOR)
    ax4.legend(loc="lower left", bbox_to_anchor=(-0.12, -0.05), facecolor=PANEL_COLOR,
               edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # -------------------------------------------------------------------------
    # Panel 5: Analyzer Transmission Spectra (Malus Law chromatic filtering)
    # -------------------------------------------------------------------------
    analyzer_angles = [0, 45, 90, 135]
    colors_angles = ["#38bdf8", "#a855f7", "#ec4899", "#f59e0b"]
    for beta_deg, col_a in zip(analyzer_angles, colors_angles):
        beta_rad = np.radians(beta_deg)
        th_rad = (concentration * z_depth * CAUCHY_A) / (lam ** 2)
        # Malus law: T = cos^2(theta - beta)
        T_val = np.cos(th_rad - beta_rad) ** 2
        ax5.plot(lam, T_val, color=col_a, lw=2.2, label=rf"Analyzer $\beta = {beta_deg}^\circ$")

    ax5.set_title(r"$\mathbf{5.\;Transmitted\;Spectrum\;Through\;Analyzer}\;\;[T = \cos^2(\theta - \beta)]$",
                  fontsize=12, loc="left", pad=10, color=TEXT_COLOR)
    ax5.set_xlabel(r"Wavelength $\lambda$ (nm)", fontsize=11, fontweight="bold")
    ax5.set_ylabel(r"Transmitted Fraction $T(\lambda)$", fontsize=11, fontweight="bold")
    ax5.set_xlim(380, 750)
    ax5.set_ylim(0, 1.05)
    ax5.legend(loc="upper right", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=9)

    # -------------------------------------------------------------------------
    # Panel 6: Spectral Dispersion Spread Delta_theta vs Path Length z
    # -------------------------------------------------------------------------
    z_arr = np.linspace(0.0, 5.0, 200)
    for w_line, name_line, col_line in [(400.0, "Violet (400 nm)", "#8b5cf6"),
                                        (480.0, "Cyan (480 nm)",   "#06b6d4"),
                                        (550.0, "Green (550 nm)",  "#22c55e"),
                                        (700.0, "Red (700 nm)",    "#ef4444")]:
        rot_z = np.degrees(concentration * z_arr * CAUCHY_A / (w_line ** 2))
        ax6.plot(z_arr, rot_z, color=col_line, lw=2.2, label=name_line)

    # Shading the dispersion spread between violet and red
    rot_v = np.degrees(concentration * z_arr * CAUCHY_A / (400.0 ** 2))
    rot_r = np.degrees(concentration * z_arr * CAUCHY_A / (700.0 ** 2))
    ax6.fill_between(z_arr, rot_r, rot_v, color="#8b5cf6", alpha=0.15,
                     label=r"Angular spread $\Delta\theta = \theta_{\mathrm{violet}} - \theta_{\mathrm{red}}$")

    ax6.set_title(r"$\mathbf{6.\;Rotation\;Growth\;Along\;Tube\;Depth}\;\;[\theta(z, \lambda) = c \cdot z \cdot A/\lambda^2]$",
                  fontsize=12, loc="left", pad=10, color=TEXT_COLOR)
    ax6.set_xlabel(r"Propagation Distance $z$ along tube (cm)", fontsize=11, fontweight="bold")
    ax6.set_ylabel(r"Optical Rotation $\theta$ (degrees)", fontsize=11, fontweight="bold")
    ax6.set_xlim(0, 5.0)
    ax6.set_ylim(0, rot_v.max() * 1.05)
    ax6.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=8.5)

    # Suptitle
    fig.suptitle(f"Optical Rotatory Dispersion (ORD) & Wavelength Relations in Chiral Solution\n"
                 rf"Cauchy Constant $A = {CAUCHY_A:.1e}\;\mathrm{{nm}}^2\cdot\mathrm{{rad/cm}}$, "
                 rf"Concentration $c = {concentration}\;\mathrm{{mol/L}}$",
                 fontsize=15, fontweight="bold", color=TEXT_COLOR, y=0.96)

    fig.savefig(save_path, dpi=250, facecolor=BG_COLOR, edgecolor="none")
    plt.close(fig)
    print(f"  [+] Saved comprehensive ORD dashboard to: {save_path}")


def plot_focused_dispersion_curve(save_path="out/ord_curve_theta_vs_lambda.png",
                                  concentration=0.32, z_depth=2.0):
    """Generate high-resolution 2-panel focused figure on theta(lambda) and 1/lambda^2."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), dpi=250)
    apply_theme(fig, [ax1, ax2])

    lam = np.linspace(380.0, 750.0, 600)
    cmap = get_rainbow_colormap()
    norm = plt.Normalize(vmin=380, vmax=750)

    # Panel 1: theta vs lambda
    rot = np.degrees(concentration * z_depth * CAUCHY_A / (lam ** 2))
    ax1.plot(lam, rot, color="#38bdf8", lw=3.0, label=r"Cauchy ORD: $\theta(\lambda) = c \cdot z \cdot \frac{A}{\lambda^2}$")
    for i in range(len(lam) - 1):
        ax1.fill_between(lam[i:i+2], 0, rot[i:i+2], color=cmap(norm(lam[i])), alpha=0.38)

    for w_line, name_line, col_line in LASER_LINES:
        y_val = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax1.plot(w_line, y_val, "o", color=col_line, markersize=7, markeredgecolor="white", markeredgewidth=1.2)
        ax1.annotate(f"{int(w_line)} nm\n({y_val:.1f}°)", (w_line, y_val),
                     textcoords="offset points", xytext=(8, 8), color=col_line, fontsize=9, fontweight="bold")

    ax1.set_title(r"$\mathbf{A.\;Optical\;Rotation\;vs.\;Wavelength}\;\;[\theta(\lambda)]$", fontsize=13, loc="left", pad=12, color=TEXT_COLOR)
    ax1.set_xlabel(r"Wavelength $\lambda$ (nm)", fontsize=12, fontweight="bold")
    ax1.set_ylabel(rf"Optical Rotation $\theta$ (degrees at $z = {z_depth:.1f}$ cm)", fontsize=12, fontweight="bold")
    ax1.set_xlim(380, 750)
    ax1.set_ylim(0, rot.max() * 1.15)
    ax1.legend(loc="upper right", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=10)

    # Panel 2: theta vs 1/lambda^2 (Biot linearity)
    inv_lam2 = (1000.0 / lam) ** 2
    slope_k = np.degrees(concentration * z_depth * CAUCHY_A * 1e-6)
    ax2.plot(inv_lam2, rot, color="#34d399", lw=3.0, label=rf"Linear Fit: $\theta = {slope_k:.1f} \cdot (1/\lambda^2)$")
    ax2.fill_between(inv_lam2, 0, rot, color="#34d399", alpha=0.15)

    for w_line, name_line, col_line in LASER_LINES:
        x_pt = (1000.0 / w_line) ** 2
        y_pt = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax2.plot(x_pt, y_pt, "o", color=col_line, markersize=7, markeredgecolor="white", markeredgewidth=1.2)
        ax2.annotate(f"{int(w_line)} nm", (x_pt, y_pt), textcoords="offset points",
                     xytext=(-20, 8), color=col_line, fontsize=9, fontweight="bold")

    ax2.set_title(r"$\mathbf{B.\;Linearity\;in\;} 1/\lambda^2\;\;[\mathrm{Biot's\;Dispersion\;Law}]$", fontsize=13, loc="left", pad=12, color=TEXT_COLOR)
    ax2.set_xlabel(r"Inverse Square Wavelength $1/\lambda^2$ ($\mu\mathrm{m}^{-2}$)", fontsize=12, fontweight="bold")
    ax2.set_ylabel(rf"Optical Rotation $\theta$ (degrees at $z = {z_depth:.1f}$ cm)", fontsize=12, fontweight="bold")
    ax2.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor=BORDER_COLOR, labelcolor=TEXT_COLOR, fontsize=10)

    fig.suptitle(f"Optical Rotatory Dispersion: Mathematical Law $\\theta \\propto 1/\\lambda^2$\n"
                 rf"($c = {concentration}\;\mathrm{{mol/L}},\;z = {z_depth}\;\mathrm{{cm}}$)",
                 fontsize=15, fontweight="bold", color=TEXT_COLOR, y=1.02)
    fig.tight_layout()
    fig.savefig(save_path, dpi=250, facecolor=BG_COLOR, edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"  [+] Saved focused dispersion curve to: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate ORD vs Wavelength scientific graphs.")
    parser.add_argument("--conc", type=float, default=0.32, help="Chiral concentration (mol/L)")
    parser.add_argument("--depth", type=float, default=2.0, help="Optical path depth z (cm)")
    parser.add_argument("--outdir", type=str, default="out", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    comp_path = os.path.join(args.outdir, "ord_dispersion_comprehensive.png")
    focused_path = os.path.join(args.outdir, "ord_curve_theta_vs_lambda.png")

    plot_comprehensive_dashboard(save_path=comp_path, concentration=args.conc, z_depth=args.depth)
    plot_focused_dispersion_curve(save_path=focused_path, concentration=args.conc, z_depth=args.depth)
    print("Done! All helper graphs successfully generated.")


if __name__ == "__main__":
    main()
