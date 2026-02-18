"""CLI entry point: satlinkbudget run/budget/list."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_run(args: argparse.Namespace) -> None:
    """Run a pass simulation from mission YAML."""
    from satlinkbudget.mission._builder import load_mission, build_pass_simulation
    from satlinkbudget.simulation._report import generate_report

    config = load_mission(args.mission_file)
    sim = build_pass_simulation(config)

    dt_s = getattr(args, "dt", None) or config.simulation.dt_s
    results = sim.run(
        duration_orbits=config.simulation.duration_orbits,
        dt_s=dt_s,
        contact_dt_s=config.simulation.contact_dt_s,
    )

    report = generate_report(results)
    print(report)

    if args.plot and results.num_passes > 0:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        save_dir = Path(args.save_plots) if args.save_plots else Path(".")

        fig = results.plot_pass_elevation(0)
        fig.savefig(save_dir / "pass_elevation.png", dpi=150)
        plt.close(fig)

        fig = results.plot_pass_margin(0)
        fig.savefig(save_dir / "pass_margin.png", dpi=150)
        plt.close(fig)

        fig = results.plot_doppler(0)
        fig.savefig(save_dir / "pass_doppler.png", dpi=150)
        plt.close(fig)

        fig = results.plot_data_volume_cumulative()
        fig.savefig(save_dir / "data_volume.png", dpi=150)
        plt.close(fig)

        print(f"\nPlots saved to {save_dir}/")


def cmd_budget(args: argparse.Namespace) -> None:
    """Compute single link budget at given elevation."""
    from satlinkbudget.mission._builder import load_mission, build_pass_simulation
    from satlinkbudget.budget._link import compute_link_budget
    from satlinkbudget.rf._path_loss import slant_range

    config = load_mission(args.mission_file)
    sim = build_pass_simulation(config)

    elevation = args.elevation
    dist = slant_range(sim.orbit.altitude_m, elevation)
    required_eb_n0 = sim.modem.required_eb_n0_db()

    result = compute_link_budget(
        transmitter=sim.transmitter,
        receiver=sim.receiver,
        frequency_hz=sim.frequency_hz,
        distance_m=dist,
        data_rate_bps=sim.data_rate_bps,
        required_eb_n0_db=required_eb_n0,
    )

    print(result.to_text())


def cmd_list(args: argparse.Namespace) -> None:
    """List available components or presets."""
    from satlinkbudget.data._registry import registry

    category = args.category
    names = registry.list_category(category)
    print(f"\nAvailable {category} ({len(names)}):")
    for name in sorted(names):
        print(f"  - {name}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="satlinkbudget",
        description="Satellite Link Budget Analysis",
    )
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run pass simulation")
    run_parser.add_argument("mission_file", help="Mission YAML file")
    run_parser.add_argument("--plot", action="store_true", help="Generate plots")
    run_parser.add_argument("--save-plots", default=None, help="Directory to save plots")
    run_parser.add_argument("--dt", type=float, default=None, help="Time step [s]")

    # budget
    budget_parser = subparsers.add_parser("budget", help="Compute single link budget")
    budget_parser.add_argument("mission_file", help="Mission YAML file")
    budget_parser.add_argument("--elevation", type=float, default=20.0, help="Elevation angle [deg]")

    # list
    list_parser = subparsers.add_parser("list", help="List components")
    list_parser.add_argument(
        "category",
        choices=["transceivers", "antennas", "groundstations", "bands", "missions"],
        help="Component category",
    )

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "budget":
        cmd_budget(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
