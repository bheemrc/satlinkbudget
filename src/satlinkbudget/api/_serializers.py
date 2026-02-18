"""Serialization utilities for API responses."""

from __future__ import annotations

import base64
import io
import json
from typing import Any

import numpy as np


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
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def serialize_results(data: dict) -> str:
    """Serialize a dict with potential NumPy values to JSON string."""
    return json.dumps(data, cls=NumpyEncoder)
