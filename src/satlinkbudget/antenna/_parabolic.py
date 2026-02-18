"""Parabolic dish antenna model."""

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT


@dataclass
class ParabolicAntenna:
    """Parabolic dish antenna.

    Gain: G = η · (π·D·f/c)²
    Beamwidth: BW ≈ 21 / (f_GHz · D_m) degrees (approximate)
    """

    diameter_m: float
    efficiency: float = 0.55
    name: str = ""

    def gain_db(self, frequency_hz: float) -> float:
        """Antenna gain [dBi] at given frequency."""
        wavelength = C_LIGHT / frequency_hz
        gain_linear = self.efficiency * (np.pi * self.diameter_m / wavelength) ** 2
        return float(10.0 * np.log10(gain_linear))

    def beamwidth_deg(self, frequency_hz: float) -> float:
        """Approximate 3 dB beamwidth [degrees]."""
        freq_ghz = frequency_hz / 1e9
        return 21.0 / (freq_ghz * self.diameter_m)
