"""Spectral physics: Cauchy dispersion and wavelength -> sRGB conversion."""
import numpy as np

from .config import CAUCHY_A, LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE


def cauchy_rotation(wavelength_nm, z, concentration, theta0_rad):
    """Polarization angle theta(z, lambda) from Cauchy's dispersion formula.

        theta = theta0 + c * z * (A / lambda^2)

    Works with scalars or NumPy arrays (broadcasting).
    """
    alpha = CAUCHY_A / (np.asarray(wavelength_nm, dtype=float) ** 2)
    return theta0_rad + concentration * z * alpha


def rotation_rate(wavelength_nm, concentration=1.0):
    """Rotation rate d(theta)/dz in rad/cm."""
    return concentration * CAUCHY_A / (wavelength_nm ** 2)


def helix_pitch(wavelength_nm, concentration):
    """Axial distance for a full 2*pi rotation: P = 2*pi*lambda^2 / (A*c)."""
    return 2.0 * np.pi * wavelength_nm ** 2 / (CAUCHY_A * concentration)


def wavelength_to_srgb(wavelength_nm):
    """Monochromatic wavelength (380-750 nm) -> RGB via a CIE-1931-style approximation."""
    wl = float(wavelength_nm)
    r = g = b = 0.0

    if 380.0 <= wl < 440.0:
        r, g, b = (440.0 - wl) / (440.0 - 380.0), 0.0, 1.0
    elif 440.0 <= wl < 490.0:
        r, g, b = 0.0, (wl - 440.0) / (490.0 - 440.0), 1.0
    elif 490.0 <= wl < 580.0:
        r, g, b = (wl - 490.0) / (580.0 - 490.0), 1.0, 0.0
    elif 580.0 <= wl < 620.0:
        r, g, b = 1.0, (620.0 - wl) / (620.0 - 580.0), 0.0
    elif 620.0 <= wl <= 750.0:
        r, g, b = 1.0, 0.0, 0.0

    # Sensitivity falloff at the spectral boundaries
    if wl < 420.0:
        factor = 0.3 + 0.7 * (wl - 380.0) / (420.0 - 380.0)
    elif wl > 680.0:
        factor = 0.3 + 0.7 * (750.0 - wl) / (750.0 - 680.0)
    else:
        factor = 1.0

    return np.array([r * factor, g * factor, b * factor])


def print_dispersion_summary():
    """Print the Cauchy coefficient for each laser line."""
    for name, lam in (("Red", LAMBDA_RED), ("Green", LAMBDA_GREEN), ("Blue", LAMBDA_BLUE)):
        print(f"  • {name:<5} ({lam:.0f} nm): Cauchy dispersion coefficient = "
              f"{CAUCHY_A / lam**2:.3f} rad/cm")
