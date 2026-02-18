"""Serializers: convert simulation results to structured JSON or base64 PNG."""

from __future__ import annotations

import base64
import io
import json
from typing import Any

import numpy as np

from satlinkbudget.api._schemas import PlotData, PlotFormat, TimeSeriesData
from satlinkbudget.simulation._results import PassSimulationResults


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles NumPy types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def figure_to_base64(fig: Any) -> str:
    """Convert matplotlib Figure to base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    buf.close()
    import matplotlib.pyplot as plt
    plt.close(fig)
    return encoded


def serialize_results(data: dict) -> str:
    """Serialize a dict with potential NumPy values to JSON string."""
    return json.dumps(data, cls=NumpyEncoder)


# --- Pass simulation plot serializers ---


def serialize_plot_elevation(
    results: PassSimulationResults, fmt: PlotFormat, pass_idx: int = 0
) -> PlotData:
    """Serialize elevation plot for a specific pass."""
    p = results.passes[pass_idx]
    t_min = ((p.times_s - p.times_s[0]) / 60.0).tolist()

    if fmt == PlotFormat.STRUCTURED:
        return PlotData(
            plot_type="elevation",
            format=fmt,
            time_series=[
                TimeSeriesData(
                    label=f"Pass {p.pass_number} Elevation",
                    unit="deg",
                    x=t_min,
                    y=p.elevations_deg.tolist(),
                )
            ],
        )

    fig = results.plot_pass_elevation(pass_idx)
    return PlotData(
        plot_type="elevation",
        format=fmt,
        png_base64=figure_to_base64(fig),
    )


def serialize_plot_margin(
    results: PassSimulationResults, fmt: PlotFormat, pass_idx: int = 0
) -> PlotData:
    """Serialize link margin plot for a specific pass."""
    p = results.passes[pass_idx]
    t_min = ((p.times_s - p.times_s[0]) / 60.0).tolist()

    if fmt == PlotFormat.STRUCTURED:
        return PlotData(
            plot_type="margin",
            format=fmt,
            time_series=[
                TimeSeriesData(
                    label=f"Pass {p.pass_number} Link Margin",
                    unit="dB",
                    x=t_min,
                    y=p.margins_db.tolist(),
                )
            ],
        )

    fig = results.plot_pass_margin(pass_idx)
    return PlotData(
        plot_type="margin",
        format=fmt,
        png_base64=figure_to_base64(fig),
    )


def serialize_plot_doppler(
    results: PassSimulationResults, fmt: PlotFormat, pass_idx: int = 0
) -> PlotData:
    """Serialize Doppler shift plot for a specific pass."""
    p = results.passes[pass_idx]
    t_min = ((p.times_s - p.times_s[0]) / 60.0).tolist()

    if fmt == PlotFormat.STRUCTURED:
        return PlotData(
            plot_type="doppler",
            format=fmt,
            time_series=[
                TimeSeriesData(
                    label=f"Pass {p.pass_number} Doppler Shift",
                    unit="kHz",
                    x=t_min,
                    y=(p.doppler_shifts_hz / 1e3).tolist(),
                )
            ],
        )

    fig = results.plot_doppler(pass_idx)
    return PlotData(
        plot_type="doppler",
        format=fmt,
        png_base64=figure_to_base64(fig),
    )


def serialize_plot_data_volume(
    results: PassSimulationResults, fmt: PlotFormat
) -> PlotData:
    """Serialize cumulative data volume plot."""
    if fmt == PlotFormat.STRUCTURED:
        x = [p.start_time_s / 3600.0 for p in results.passes]
        y = [p.data_volume_bits / 8.0 / 1024.0 for p in results.passes]
        return PlotData(
            plot_type="data_volume",
            format=fmt,
            time_series=[
                TimeSeriesData(
                    label="Data Volume per Pass",
                    unit="KB",
                    x=x,
                    y=y,
                )
            ],
        )

    fig = results.plot_data_volume_cumulative()
    return PlotData(
        plot_type="data_volume",
        format=fmt,
        png_base64=figure_to_base64(fig),
    )


def serialize_plot_waterfall(result: Any, fmt: PlotFormat) -> PlotData:
    """Serialize link budget waterfall chart."""
    if fmt == PlotFormat.STRUCTURED:
        items = [
            ("TX Power", result.tx_power_dbw),
            ("TX Gain", result.tx_antenna_gain_dbi),
            ("TX Losses", -(result.tx_feed_loss_db + result.tx_pointing_loss_db + result.tx_other_loss_db)),
            ("FSPL", -result.free_space_path_loss_db),
            ("Atm Loss", -result.atmospheric_loss_db),
            ("Pol Loss", -result.polarization_loss_db),
            ("RX Gain", result.rx_antenna_gain_dbi),
            ("RX Losses", -(result.rx_feed_loss_db + result.rx_pointing_loss_db + result.rx_other_loss_db)),
        ]
        return PlotData(
            plot_type="waterfall",
            format=fmt,
            time_series=[
                TimeSeriesData(
                    label=label,
                    unit="dB",
                    x=[float(i)],
                    y=[float(val)],
                )
                for i, (label, val) in enumerate(items)
            ],
        )

    fig = result.plot_waterfall()
    return PlotData(
        plot_type="waterfall",
        format=fmt,
        png_base64=figure_to_base64(fig),
    )
