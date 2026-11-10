"""Optical Rotatory Dispersion & the Barber Pole Effect.

Modules
-------
config       Physical constants, default geometry and plot palette.
spectral     Cauchy dispersion + wavelength -> sRGB conversion.
raymarch     Volumetric raymarching engine for the cylindrical tube.
diagnostics  4-panel physics diagnostic figure.
comparison   Discrete RGB vs continuous spectrum comparison figure.
dashboard    Interactive matplotlib dashboard (replaces ipywidgets).
helix3d      Interactive 3D polarization helices (plotly).
animation    "Walking stripes" animation exported to GIF / MP4.
"""
from .config import (CAUCHY_A, LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE,
                     TUBE_RADIUS, TUBE_HEIGHT)
from .spectral import cauchy_rotation, wavelength_to_srgb, helix_pitch
from .raymarch import simulate_barber_pole

__all__ = [
    "CAUCHY_A", "LAMBDA_RED", "LAMBDA_GREEN", "LAMBDA_BLUE",
    "TUBE_RADIUS", "TUBE_HEIGHT",
    "cauchy_rotation", "wavelength_to_srgb", "helix_pitch",
    "simulate_barber_pole",
]
