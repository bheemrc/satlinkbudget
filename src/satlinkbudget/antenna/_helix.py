"""Axial-mode helix antenna model."""

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT


@dataclass
class HelixAntenna:
    """Axial-mode helix antenna.

    G = 10.8 + 10·log₁₀(N · S · C² / λ³)  [Kraus formula]

    where N = number of turns, S = spacing, C = circumference.
    Operates in axial mode when C ≈ λ and S ≈ λ/4.
    """

    num_turns: int
    circumference_m: float
    spacing_m: float
    name: str = ""

    def gain_db(self, frequency_hz: float) -> float:
        """Antenna gain [dBi] at given frequency."""
        wavelength = C_LIGHT / frequency_hz
        gain = 10.8 + 10.0 * np.log10(
            self.num_turns
            * self.spacing_m
            * self.circumference_m**2
            / wavelength**3
        )
        return float(gain)

    def beamwidth_deg(self, frequency_hz: float) -> float:
        """Approximate half-power beamwidth [degrees].

        BW ≈ 52 / (C/λ · sqrt(N · S/λ))
        """
        wavelength = C_LIGHT / frequency_hz
        c_lambda = self.circumference_m / wavelength
        s_lambda = self.spacing_m / wavelength
        return 52.0 / (c_lambda * np.sqrt(self.num_turns * s_lambda))
