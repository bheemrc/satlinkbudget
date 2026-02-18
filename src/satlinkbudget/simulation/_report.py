"""Link budget report generation."""

from __future__ import annotations

from satlinkbudget.simulation._results import PassSimulationResults


def generate_report(results: PassSimulationResults) -> str:
    """Generate text report from simulation results."""
    lines = [
        "=" * 70,
        "SATELLITE LINK BUDGET - PASS SIMULATION REPORT",
        "=" * 70,
        "",
        f"Frequency:           {results.frequency_hz / 1e6:.1f} MHz",
        f"Data Rate:           {results.data_rate_bps:.0f} bps",
        f"Simulation Duration: {results.simulation_duration_s / 3600:.1f} hours",
        "",
        "CONTACT SUMMARY",
        "-" * 40,
        f"Total Passes:        {results.num_passes}",
        f"Passes per Day:      {results.passes_per_day:.1f}",
        f"Total Contact Time:  {results.total_contact_time_s / 60:.1f} min",
        f"Avg Pass Duration:   {results.avg_pass_duration_s / 60:.1f} min",
        "",
        "DATA VOLUME",
        "-" * 40,
        f"Total Data Volume:   {results.total_data_volume_mbytes:.3f} MB",
        f"Total Data Volume:   {results.total_data_volume_bits:.0f} bits",
        "",
        "PER-PASS DETAILS",
        "-" * 70,
        f"{'Pass':>4} {'Duration':>10} {'Max El':>8} {'Min Margin':>12} {'Data':>10}",
        f"{'#':>4} {'[min]':>10} {'[deg]':>8} {'[dB]':>12} {'[KB]':>10}",
        "-" * 70,
    ]

    for p in results.passes:
        lines.append(
            f"{p.pass_number:>4} "
            f"{p.duration_s / 60.0:>10.1f} "
            f"{p.max_elevation_deg:>8.1f} "
            f"{p.min_margin_db:>12.1f} "
            f"{p.data_volume_kbytes:>10.1f}"
        )

    lines.extend(["", "=" * 70])
    return "\n".join(lines)
