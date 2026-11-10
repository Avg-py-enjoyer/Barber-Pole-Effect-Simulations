"""
Generate publication-quality blue-and-white figures with large, highly legible text.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

from barber_pole.config import CAUCHY_A

# Visual styling
BG_COLOR = "#ffffff"
PANEL_COLOR = "#ffffff"
SPINE_COLOR = "#1e3a8a"      # Deep Navy
GRID_COLOR = "#e2e8f0"       # Light blue-gray
TEXT_COLOR = "#0f172a"       # Slate / Navy
TEXT_MUTED = "#334155"       # Subdued Navy
BLUE_PRIMARY = "#1d4ed8"     # Royal Blue
BLUE_SECONDARY = "#0284c7"   # Sky/Cobalt Blue
BLUE_FILL = "#dbeafe"        # Light Ice Blue
BLUE_DEEP = "#1e40af"        # Deep Blue

def apply_blue_white_theme(fig, axes):
    fig.patch.set_facecolor(BG_COLOR)
    for ax in axes:
        ax.set_facecolor(PANEL_COLOR)
        ax.tick_params(colors=TEXT_MUTED, which="both", labelsize=12, width=1.3, length=5)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        for spine in ax.spines.values():
            spine.set_color(SPINE_COLOR)
            spine.set_linewidth(1.5)
        ax.grid(True, linestyle="--", color=GRID_COLOR, alpha=0.85, linewidth=1.0)


def generate_ord_curve_blue_white(save_path, concentration=0.32, z_depth=2.0):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0), dpi=300)
    apply_blue_white_theme(fig, [ax1, ax2])

    lam = np.linspace(380.0, 750.0, 600)

    # -------------------------------------------------------------
    # Panel 1: theta vs lambda (Cauchy ORD)
    # -------------------------------------------------------------
    rot = np.degrees(concentration * z_depth * CAUCHY_A / (lam ** 2))
    ax1.plot(lam, rot, color=BLUE_PRIMARY, lw=3.6,
             label=r"$\theta(\lambda) = c \cdot z \cdot \frac{A}{\lambda^2}$")
    ax1.fill_between(lam, 0, rot, color=BLUE_FILL, alpha=0.55)

    # Benchmark markers with clear, large labels
    panel1_pts = [
        (405.0, (10, 8)),
        (450.0, (10, 8)),
        (532.0, (10, 8)),
        (632.8, (10, 8)),
        (670.0, (10, -22))
    ]
    for w_line, offset in panel1_pts:
        y_val = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax1.plot(w_line, y_val, "o", color=BLUE_DEEP, markersize=8.5,
                 markeredgecolor="#ffffff", markeredgewidth=1.8, zorder=5)
        ax1.annotate(f"{int(w_line)} nm\n({y_val:.0f}°)", (w_line, y_val),
                     textcoords="offset points", xytext=offset, color=TEXT_COLOR,
                     fontsize=10.5, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#93c5fd", alpha=0.9))

    ax1.set_title(r"$\mathbf{A.\;Optical\;Rotation}\;\;[\theta(\lambda)]$",
                  fontsize=14.5, loc="left", pad=10, color=TEXT_COLOR, fontweight="bold")
    ax1.set_xlabel(r"Wavelength $\lambda$ (nm)", fontsize=13, fontweight="bold")
    ax1.set_ylabel(rf"Optical Rotation $\theta$ (deg at $z = {z_depth:.0f}$ cm)", fontsize=13, fontweight="bold")
    ax1.set_xlim(380, 750)
    ax1.set_ylim(0, rot.max() * 1.15)
    ax1.legend(loc="upper right", facecolor="#ffffff", edgecolor="#93c5fd", labelcolor=TEXT_COLOR, fontsize=12)

    # -------------------------------------------------------------
    # Panel 2: theta vs 1/lambda^2 (Biot linearity)
    # -------------------------------------------------------------
    inv_lam2 = (1000.0 / lam) ** 2
    slope_k = np.degrees(concentration * z_depth * CAUCHY_A * 1e-6)
    ax2.plot(inv_lam2, rot, color=BLUE_SECONDARY, lw=3.6,
             label=rf"Fit: $\theta = {slope_k:.1f} \cdot \lambda^{{-2}}$")
    ax2.fill_between(inv_lam2, 0, rot, color="#eff6ff", alpha=0.7)

    panel2_pts = [
        (405.0, (-22, 10)),
        (450.0, (-22, 10)),
        (532.0, (-22, 10)),
        (632.8, (-22, 10)),
        (670.0, (-22, -18))
    ]
    for w_line, offset in panel2_pts:
        x_pt = (1000.0 / w_line) ** 2
        y_pt = np.degrees(concentration * z_depth * CAUCHY_A / (w_line ** 2))
        ax2.plot(x_pt, y_pt, "o", color=BLUE_DEEP, markersize=8.5,
                 markeredgecolor="#ffffff", markeredgewidth=1.8, zorder=5)
        ax2.annotate(f"{int(w_line)} nm", (x_pt, y_pt), textcoords="offset points",
                     xytext=offset, color=TEXT_COLOR, fontsize=10.5, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor="#93c5fd", alpha=0.9))

    ax2.set_title(r"$\mathbf{B.\;Biot's\;Law\;Linearity}\;\;[1/\lambda^2]$",
                  fontsize=14.5, loc="left", pad=10, color=TEXT_COLOR, fontweight="bold")
    ax2.set_xlabel(r"Inverse Square Wavelength $1/\lambda^2$ ($\mu\mathrm{m}^{-2}$)", fontsize=13, fontweight="bold")
    ax2.set_ylabel(rf"Optical Rotation $\theta$ (deg at $z = {z_depth:.0f}$ cm)", fontsize=13, fontweight="bold")
    ax2.legend(loc="upper left", facecolor="#ffffff", edgecolor="#93c5fd", labelcolor=TEXT_COLOR, fontsize=12)

    # Top secondary wavelength axis (well-spaced tick markers)
    ax2_top = ax2.twiny()
    ax2_top.set_xlim(ax2.get_xlim())
    tick_wls = np.array([700, 550, 480, 420])
    ax2_top.set_xticks((1000.0 / tick_wls) ** 2)
    ax2_top.set_xticklabels([f"{w} nm" for w in tick_wls], fontsize=11, color=TEXT_MUTED, fontweight="bold")
    ax2_top.set_xlabel(r"Wavelength $\lambda$", fontsize=12, color=TEXT_COLOR, labelpad=7, fontweight="bold")
    ax2_top.tick_params(colors=TEXT_MUTED, width=1.3, length=5)
    for spine in ax2_top.spines.values():
        spine.set_color(SPINE_COLOR)
        spine.set_linewidth(1.5)

    fig.tight_layout()
    fig.savefig(save_path, dpi=300, facecolor=BG_COLOR, edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved updated ORD curve to: {save_path}")


def generate_comparison_blue_white(save_path):
    from barber_pole.raymarch import simulate_barber_pole

    print("[*] Simulating raymarching cylinders for comparison...")
    kw = dict(concentration=0.85, theta0_deg=0.0, filter2_deg=None,
              tube_radius=1.0, tube_height=4.0, resolution=(360, 180))
    img_rgb = simulate_barber_pole(mode="rgb", **kw)
    img_spec = simulate_barber_pole(mode="spectrum", **kw)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 6.2), facecolor="#ffffff")
    extent = [-1.15, 1.15, 0, 4.0]

    for ax, img, title in [(ax1, img_rgb, "Discrete RGB (650, 532, 450 nm)"),
                           (ax2, img_spec, "Continuous Spectrum (White Light)")]:
        ax.imshow(img, extent=extent, origin="lower", aspect="auto")
        ax.set_title(title, color="#0f172a", fontsize=13.5, fontweight="bold", pad=10)
        ax.set_xlabel(r"Transverse $x$ (cm)", color="#1e3a8a", fontweight="bold", fontsize=12.5)
        ax.set_ylabel(r"Axial Height $z$ (cm)", color="#1e3a8a", fontweight="bold", fontsize=12.5)
        ax.tick_params(colors="#1e293b", labelsize=11.5, width=1.3, length=5)
        for spine in ax.spines.values():
            spine.set_color("#1e3a8a")
            spine.set_linewidth(1.5)

    fig.tight_layout()
    fig.savefig(save_path, dpi=250, facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)
    print(f"[+] Saved updated comparison to: {save_path}")


if __name__ == "__main__":
    out_dir = "/home/aneeshbhate/acads/ph3050/projects/optics_project/report/figures"
    generate_ord_curve_blue_white(os.path.join(out_dir, "ord_curve_theta_vs_lambda.png"))
    generate_comparison_blue_white(os.path.join(out_dir, "comparison.png"))
