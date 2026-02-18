"""Horn antenna model."""

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT


@dataclass
class HornAntenna:
    """Pyramidal horn antenna.

    G = η · 4π · A_phys / λ²
    where A_phys = width × height (aperture area).
    """

    width_m: float
    height_m: float
    efficiency: float = 0.51
    name: str = ""

    def gain_db(self, frequency_hz: float) -> float:
        """Antenna gain [dBi] at given frequency."""
        wavelength = C_LIGHT / frequency_hz
        area = self.width_m * self.height_m
        gain_linear = self.efficiency * 4.0 * np.pi * area / wavelength**2
        return float(10.0 * np.log10(gain_linear))

    def beamwidth_deg(self, frequency_hz: float) -> float:
        """Approximate E-plane beamwidth [degrees]."""
        wavelength = C_LIGHT / frequency_hz
        # BW ≈ 51·λ/D for E-plane (height dimension)
        return 51.0 * wavelength / self.height_m
