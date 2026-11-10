"""Shared constants and default parameters."""

# Cauchy dispersion constant (lambda in nm, z in cm -> radians).
# A = 2.1e6 nm^2 rad / (unit length * concentration)
CAUCHY_A = 2.1e6

# Discrete spectral wavelengths (nm)
LAMBDA_RED = 650.0    # HeNe / red diode laser
LAMBDA_GREEN = 532.0  # frequency-doubled Nd:YAG
LAMBDA_BLUE = 450.0   # InGaN blue laser diode

# Default tube geometry (cm)
TUBE_RADIUS = 1.0
TUBE_HEIGHT = 4.0

# Default solution concentration (mol/L)
DEFAULT_CONCENTRATION = 0.85

# Plot palette
COLOR_RED = "#ef4444"
COLOR_GREEN = "#22c55e"
COLOR_BLUE = "#3b82f6"
BG_DARK = "#0b0f19"
BG_PANEL = "#0f172a"
