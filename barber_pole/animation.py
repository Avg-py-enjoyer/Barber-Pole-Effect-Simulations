"""'Walking stripes' animation: rotate the entrance polarizer theta_0 through 360 deg."""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

from .config import BG_DARK, DEFAULT_CONCENTRATION
from .raymarch import simulate_barber_pole


def build_walking_animation(concentration=DEFAULT_CONCENTRATION, frames=24,
                            step_deg=15, resolution=(180, 90), n_depth_steps=16):
    fig, ax = plt.subplots(figsize=(6, 8), facecolor=BG_DARK)
    im = ax.imshow(
        simulate_barber_pole(concentration=concentration, theta0_deg=0, mode="spectrum",
                             resolution=resolution, n_depth_steps=n_depth_steps),
        extent=[-1.15, 1.15, 0, 4.0], origin="lower", aspect="auto")
    title = ax.set_title("Entrance Polarizer θ₀ = 0°\n(Watch the stripes walk!)",
                         color="white", fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Transverse Coordinate x (cm)", color="#cccccc", fontweight="bold")
    ax.set_ylabel("Axial Tube Height z (cm)", color="#cccccc", fontweight="bold")
    ax.tick_params(colors="#aaaaaa")
    for sp in ax.spines.values():
        sp.set_color("#334155")

    def animate(frame):
        angle = frame * step_deg
        im.set_data(simulate_barber_pole(concentration=concentration, theta0_deg=angle,
                                         mode="spectrum", resolution=resolution,
                                         n_depth_steps=n_depth_steps))
        title.set_text(f"Entrance Polarizer θ₀ = {angle}°\n(Watch the stripes walk!)")
        return [im, title]

    anim = FuncAnimation(fig, animate, frames=frames, interval=120, blit=False)
    return fig, anim


def save_walking_animation(path="walking_stripes.gif", fps=8, **kwargs):
    """Save as .gif (Pillow) or .mp4 (needs ffmpeg), chosen by file extension."""
    fig, anim = build_walking_animation(**kwargs)
    writer = FFMpegWriter(fps=fps) if str(path).lower().endswith(".mp4") else PillowWriter(fps=fps)
    anim.save(path, writer=writer, dpi=100)
    plt.close(fig)
    print(f"  saved {path}")
    return path
