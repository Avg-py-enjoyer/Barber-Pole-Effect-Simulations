#!/usr/bin/env python3
"""Command-line entry point for the Barber Pole simulation.

Examples
--------
    python main.py diagnostics
    python main.py comparison --save-dir out
    python main.py dashboard
    python main.py helix3d --save-dir out --no-show
    python main.py animate --save-dir out
    python main.py all --save-dir out --no-show
"""
import argparse
import os


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["diagnostics", "comparison", "dashboard",
                                       "helix3d", "animate", "ord", "all"])
    p.add_argument("--save-dir", default=None, help="Directory for saved figures/animations.")
    p.add_argument("--no-show", action="store_true", help="Do not open windows (headless).")
    p.add_argument("-c", "--concentration", type=float, default=0.85)
    p.add_argument("--theta0", type=float, default=0.0, help="Entrance polarizer angle (deg).")
    return p.parse_args()


def main():
    args = parse_args()

    import matplotlib
    if args.no_show:
        matplotlib.use("Agg")

    from barber_pole.spectral import print_dispersion_summary
    print("✓ Spectral color engine initialized.")
    print_dispersion_summary()

    show = not args.no_show
    out = args.save_dir
    if out:
        os.makedirs(out, exist_ok=True)

    def path(name):
        return os.path.join(out, name) if out else None

    cmd = args.command
    if cmd in ("diagnostics", "all"):
        from barber_pole.diagnostics import plot_diagnostics
        plot_diagnostics(save_path=path("diagnostics.png"), show=show)
    if cmd in ("comparison", "all"):
        from barber_pole.comparison import plot_comparison
        plot_comparison(concentration=args.concentration, theta0_deg=args.theta0,
                        save_path=path("comparison.png"), show=show)
    if cmd in ("helix3d", "all"):
        try:
            from barber_pole.helix3d import show_or_save
            show_or_save(save_path=path("helix3d.html"), show=show,
                         concentration=args.concentration, theta0_deg=args.theta0)
        except ImportError:
            print("plotly not installed — skipping 3D helix (pip install plotly).")
    if cmd in ("animate", "all"):
        from barber_pole.animation import save_walking_animation
        save_walking_animation(path=path("walking_stripes.gif") or "walking_stripes.gif",
                               concentration=args.concentration)
    if cmd in ("ord", "all"):
        from plot_ord_relations import plot_comprehensive_dashboard, plot_focused_dispersion_curve
        plot_comprehensive_dashboard(save_path=path("ord_dispersion_comprehensive.png") or "out/ord_dispersion_comprehensive.png",
                                     concentration=args.concentration)
        plot_focused_dispersion_curve(save_path=path("ord_curve_theta_vs_lambda.png") or "out/ord_curve_theta_vs_lambda.png",
                                     concentration=args.concentration)
    if cmd == "dashboard":
        from barber_pole.dashboard import run_dashboard
        run_dashboard()

    if show and cmd in ("diagnostics", "comparison", "all"):
        pass  # figures already shown by their modules


if __name__ == "__main__":
    main()
