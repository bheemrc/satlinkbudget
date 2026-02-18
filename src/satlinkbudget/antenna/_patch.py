"""Patch array antenna model."""

from dataclasses import dataclass

import numpy as np


@dataclass
class PatchAntenna:
    """Patch array antenna.

    Array gain: G = N_elements × G_element (in linear)
    Beamwidth narrows with array size.
    """

    element_gain_dbi: float
    num_elements: int
    rows: int = 1
    cols: int = 1
    name: str = ""

    def gain_db(self, frequency_hz: float = 0.0) -> float:
        """Array gain [dBi]. Frequency-independent for ideal patch."""
        array_gain_db = 10.0 * np.log10(self.num_elements)
        return self.element_gain_dbi + array_gain_db

    def beamwidth_deg(self, frequency_hz: float = 0.0) -> float:
        """Approximate beamwidth of the array [degrees]."""
        # Single patch ~65-90°, narrows with sqrt(N) in each dimension
        single_bw = 70.0  # typical single patch beamwidth
        # Use the larger dimension for beamwidth estimate
        n_max = max(self.rows, self.cols)
        return single_bw / n_max if n_max > 0 else single_bw
