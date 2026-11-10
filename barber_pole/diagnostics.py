"""4-panel diagnostic figure: Cauchy curves, RGB pitch, dipole pattern, chord length."""
import numpy as np
import matplotlib.pyplot as plt

from .config import LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE, COLOR_RED, COLOR_GREEN, COLOR_BLUE
from .spectral import cauchy_rotation


def plot_diagnostics(save_path=None, show=True):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Physical Principles of Optical Rotatory Dispersion & Rayleigh Scattering",
                 fontsize=15, fontweight="bold", y=0.98)

    # Panel A: theta(lambda)
    ax1 = axes[0, 0]
    lam = np.linspace(380, 750, 300)
    for c, color, label in [(0.4, "#3b82f6", "c = 0.4 mol/L"),
                            (0.8, "#10b981", "c = 0.8 mol/L"),
                            (1.2, "#f59e0b", "c = 1.2 mol/L")]:
        ax1.plot(lam, np.degrees(cauchy_rotation(lam, z=2.0, concentration=c, theta0_rad=0)),
                 color=color, lw=2.2, label=label)
    ax1.axvline(LAMBDA_BLUE, color="blue", ls="--", alpha=0.5, label="Blue (450 nm)")
    ax1.axvline(LAMBDA_GREEN, color="green", ls="--", alpha=0.5, label="Green (532 nm)")
    ax1.axvline(LAMBDA_RED, color="red", ls="--", alpha=0.5, label="Red (650 nm)")
    ax1.set_xlabel(r"Wavelength $\lambda$ (nm)", fontweight="bold")
    ax1.set_ylabel(r"Optical Rotation $\theta$ (degrees at $z = 2$ cm)", fontweight="bold")
    ax1.set_title(r"A. Cauchy Dispersion $\theta(\lambda) \propto A / \lambda^2$",
                  fontweight="bold", loc="left")
    ax1.grid(True, ls=":", alpha=0.6)
    ax1.legend(loc="upper right", framealpha=0.9)

    # Panel B: theta(z) for R, G, B
    ax2 = axes[0, 1]
    z = np.linspace(0, 4, 300)
    c_fixed = 0.8
    for lam_i, col, name in [(LAMBDA_RED, COLOR_RED, "Red"),
                             (LAMBDA_GREEN, COLOR_GREEN, "Green"),
                             (LAMBDA_BLUE, COLOR_BLUE, "Blue")]:
        ax2.plot(z, np.degrees(cauchy_rotation(lam_i, z, c_fixed, 0)),
                 color=col, lw=2.5, label=f"{name} ({lam_i:.0f} nm)")
    ax2.set_xlabel(r"Axial Tube Position $z$ (cm)", fontweight="bold")
    ax2.set_ylabel(r"Polarization Angle $\theta$ (degrees)", fontweight="bold")
    ax2.set_title(rf"B. Wavelength Helical Pitch (Concentration $c = {c_fixed}$)",
                  fontweight="bold", loc="left")
    ax2.grid(True, ls=":", alpha=0.6)
    ax2.legend(loc="upper left", framealpha=0.9)

    # Panel C: dipole radiation pattern (polar)
    axes[1, 0].remove()
    ax3 = fig.add_subplot(2, 2, 3, projection="polar")
    phi = np.linspace(0, 2 * np.pi, 360)
    for tp, col, name in [(0, COLOR_RED, r"$\theta_P = 0^\circ$"),
                          (np.pi / 4, COLOR_GREEN, r"$\theta_P = 45^\circ$"),
                          (np.pi / 2, COLOR_BLUE, r"$\theta_P = 90^\circ$")]:
        ax3.plot(phi, np.cos(phi - tp) ** 2, color=col, lw=2.0, label=name)
    ax3.set_title(r"C. Dipole Scattering Intensity $I \propto \cos^2(\theta - \phi)$",
                  fontweight="bold", pad=15)
    ax3.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), framealpha=0.9)

    # Panel D: chord length
    ax4 = axes[1, 1]
    x = np.linspace(-1.0, 1.0, 200)
    chord = 2.0 * np.sqrt(1.0 - x ** 2)
    ax4.plot(x, chord, color="#8b5cf6", lw=2.5, label=r"Optical Chord $L(x) = 2\sqrt{R^2 - x^2}$")
    ax4.fill_between(x, 0, chord, color="#8b5cf6", alpha=0.2)
    ax4.set_xlabel(r"Transverse Distance from Center $x/R$", fontweight="bold")
    ax4.set_ylabel("Optical Path Length $L$ in Solution", fontweight="bold")
    ax4.set_title("D. Cylindrical Chord Variation (Limb Darkening)", fontweight="bold", loc="left")
    ax4.grid(True, ls=":", alpha=0.6)
    ax4.legend(loc="upper right", framealpha=0.9)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=140, bbox_inches="tight")
    if show:
        plt.show()
    return fig
