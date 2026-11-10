"""Volumetric cylindrical raymarching & optical path integrator."""
import numpy as np

from .config import (CAUCHY_A, LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE,
                     TUBE_RADIUS, TUBE_HEIGHT)
from .spectral import wavelength_to_srgb


def simulate_barber_pole(
    concentration=0.8,
    theta0_deg=0.0,
    filter2_deg=None,
    mode="spectrum",
    tube_radius=TUBE_RADIUS,
    tube_height=TUBE_HEIGHT,
    resolution=(280, 140),
    n_depth_steps=32,
    camera_distance=5.0,
):
    """Numerically raymarch through a cylinder of chiral fluid.

    Parameters
    ----------
    concentration : chiral concentration c (mol/L).
    theta0_deg    : entrance polarizer angle at z = 0 (degrees).
    filter2_deg   : exit analyzer angle (Malus's law) or None for open view.
    mode          : 'spectrum' (continuous white light) or 'rgb' (laser trio).
    resolution    : (height_pixels, width_pixels).
    n_depth_steps : integration steps along each line-of-sight chord.

    Returns
    -------
    ndarray of shape (H, W, 3), float32-ish RGB in [0, 1]. Row 0 is z = 0
    (use origin='lower' with imshow).
    """
    n_z, n_x = resolution
    theta0_rad = np.radians(theta0_deg)
    filter2_rad = np.radians(filter2_deg) if filter2_deg is not None else None

    x_vals = np.linspace(-tube_radius * 1.15, tube_radius * 1.15, n_x)
    z_vals = np.linspace(0.0, tube_height, n_z)
    X, Z = np.meshgrid(x_vals, z_vals)

    img_rgb = np.zeros((n_z, n_x, 3), dtype=np.float32)

    inside_cylinder = (X ** 2) <= (tube_radius ** 2)
    chord_half_length = np.zeros_like(X)
    chord_half_length[inside_cylinder] = np.sqrt(tube_radius ** 2 - X[inside_cylinder] ** 2)

    s_steps = np.linspace(-0.5, 0.5, n_depth_steps)
    ds = 1.0 / n_depth_steps

    if mode == "rgb":
        wavelengths = [LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE]
        channel_weights = [np.array([1.0, 0.0, 0.0]),
                           np.array([0.0, 1.0, 0.0]),
                           np.array([0.0, 0.0, 1.0])]
    else:
        wavelengths = np.linspace(415.0, 675.0, 16)
        channel_weights = [wavelength_to_srgb(wl) for wl in wavelengths]

    dispersion_rates = [CAUCHY_A / (wl ** 2) for wl in wavelengths]

    for s in s_steps:
        Y = s * 2.0 * chord_half_length          # depth inside cylinder
        cam_y = camera_distance
        v_x = -X
        v_y = cam_y - Y
        phi_view = np.arctan2(v_x, v_y)          # azimuthal viewing angle

        for alpha, weight in zip(dispersion_rates, channel_weights):
            theta = theta0_rad + concentration * Z * alpha
            scatter_intensity = np.cos(theta - phi_view) ** 2   # Rayleigh dipole

            if filter2_rad is not None:
                scatter_intensity = scatter_intensity * np.cos(theta - filter2_rad) ** 2

            contribution = scatter_intensity * (2.0 * chord_half_length * ds)

            for ch in range(3):
                if weight[ch] > 0.0:
                    img_rgb[:, :, ch] += np.where(inside_cylinder, contribution * weight[ch], 0.0)

    max_val = np.percentile(img_rgb[inside_cylinder], 99.5) if np.any(inside_cylinder) else 1.0
    if max_val > 1e-6:
        img_rgb /= max_val

    # Fresnel-like edge highlight of the glass wall
    edge_proximity = np.abs(X) / tube_radius
    fresnel = np.where(inside_cylinder, np.power(edge_proximity, 4.0) * 0.22, 0.0)
    for ch in range(3):
        img_rgb[:, :, ch] = np.clip(img_rgb[:, :, ch] + fresnel, 0.0, 1.0)

    img_rgb = np.power(img_rgb, 1.0 / 2.2)       # gamma

    background = np.zeros_like(img_rgb)
    background[:, :] = [0.03, 0.04, 0.07]
    return np.where(inside_cylinder[:, :, None], img_rgb, background)
