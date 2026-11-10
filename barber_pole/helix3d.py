"""Interactive 3D visualisation of the polarization helices (plotly)."""
import numpy as np

from .config import (LAMBDA_RED, LAMBDA_GREEN, LAMBDA_BLUE, TUBE_RADIUS, TUBE_HEIGHT,
                     DEFAULT_CONCENTRATION)
from .spectral import cauchy_rotation


def create_3d_helix_plot(concentration=DEFAULT_CONCENTRATION, theta0_deg=0.0):
    import plotly.graph_objects as go   # lazy: plotly is optional

    theta0 = np.radians(theta0_deg)
    z = np.linspace(0, TUBE_HEIGHT, 500)

    fig = go.Figure()

    # Glass tube surface
    th = np.linspace(0, 2 * np.pi, 60)
    zc = np.linspace(0, TUBE_HEIGHT, 20)
    TH, ZC = np.meshgrid(th, zc)
    fig.add_trace(go.Surface(x=TUBE_RADIUS * np.cos(TH), y=TUBE_RADIUS * np.sin(TH), z=ZC,
                             opacity=0.15, colorscale=[[0, "#60a5fa"], [1, "#93c5fd"]],
                             showscale=False, name="Glass Tube"))

    # Optical axis
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, TUBE_HEIGHT], mode="lines",
                               line=dict(color="white", width=3, dash="dash"),
                               name="Optical Axis (z)"))

    for lam, color, name in [(LAMBDA_RED, "#ef4444", "Red"),
                             (LAMBDA_GREEN, "#22c55e", "Green"),
                             (LAMBDA_BLUE, "#3b82f6", "Blue")]:
        t = cauchy_rotation(lam, z, concentration, theta0)
        fig.add_trace(go.Scatter3d(x=0.85 * np.cos(t), y=0.85 * np.sin(t), z=z, mode="lines",
                                   line=dict(color=color, width=6),
                                   name=f"{name} ({lam:.0f} nm)"))

    fig.update_layout(
        title=dict(text=(f"<b>3D Polarization Helices inside Chiral Tube</b> "
                         f"(c = {concentration} mol/L, θ₀ = {theta0_deg}°)"),
                   font=dict(color="white", size=16)),
        paper_bgcolor="#0f172a",
        scene=dict(
            xaxis=dict(title="X", backgroundcolor="#0f172a", gridcolor="#334155", range=[-1.3, 1.3]),
            yaxis=dict(title="Y", backgroundcolor="#0f172a", gridcolor="#334155", range=[-1.3, 1.3]),
            zaxis=dict(title="Z (Optical Path)", backgroundcolor="#0f172a",
                       gridcolor="#334155", range=[0, 4.2]),
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))),
        legend=dict(font=dict(color="white"), bgcolor="rgba(15, 23, 42, 0.7)"),
        margin=dict(l=0, r=0, b=0, t=40), height=620)
    return fig


def show_or_save(save_path=None, show=True, **kwargs):
    fig = create_3d_helix_plot(**kwargs)
    if save_path:
        fig.write_html(save_path)
        print(f"  saved {save_path}")
    if show:
        fig.show()
    return fig
