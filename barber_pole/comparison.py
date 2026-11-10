"""High-resolution comparison: discrete RGB lasers vs continuous white light."""
import matplotlib.pyplot as plt

from .config import BG_DARK
from .raymarch import simulate_barber_pole


def _style(ax, title):
    ax.set_title(title, color="white", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel(r"Transverse Coordinate $x$ (cm)", color="#cccccc", fontweight="bold")
    ax.set_ylabel(r"Axial Tube Height $z$ (cm)", color="#cccccc", fontweight="bold")
    ax.tick_params(colors="#aaaaaa")
    for spine in ax.spines.values():
        spine.set_color("#334155")


def plot_comparison(concentration=0.85, theta0_deg=0.0, resolution=(360, 180),
                    save_path=None, show=True):
    print("Rendering high-resolution comparison (Discrete RGB vs Continuous Spectrum)...")
    kw = dict(concentration=concentration, theta0_deg=theta0_deg, filter2_deg=None,
              tube_radius=1.0, tube_height=4.0, resolution=resolution)
    img_rgb = simulate_barber_pole(mode="rgb", **kw)
    img_spec = simulate_barber_pole(mode="spectrum", **kw)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8), facecolor=BG_DARK)
    extent = [-1.15, 1.15, 0, 4.0]
    ax1.imshow(img_rgb, extent=extent, origin="lower", aspect="auto")
    _style(ax1, "Discrete RGB Mode (Laser Trio: 650, 532, 450 nm)")
    ax2.imshow(img_spec, extent=extent, origin="lower", aspect="auto")
    _style(ax2, "Continuous Spectrum Mode (Polarized White Light)")

    fig.suptitle("The Barber Pole Effect: Volumetric Optical Simulation Comparison",
                 color="white", fontsize=16, fontweight="bold", y=0.98)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
    if show:
        plt.show()
    return fig
