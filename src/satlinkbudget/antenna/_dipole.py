"""Dipole and monopole antenna models."""

from dataclasses import dataclass


@dataclass
class DipoleAntenna:
    """Half-wave dipole antenna. Fixed gain of 2.15 dBi."""

    name: str = "Dipole"

    def gain_db(self, frequency_hz: float = 0.0) -> float:
        return 2.15

    def beamwidth_deg(self, frequency_hz: float = 0.0) -> float:
        return 78.0  # E-plane half-power beamwidth


@dataclass
class MonopoleAntenna:
    """Quarter-wave monopole antenna. Fixed gain of 5.15 dBi over ground plane."""

    name: str = "Monopole"

    def gain_db(self, frequency_hz: float = 0.0) -> float:
        return 5.15

    def beamwidth_deg(self, frequency_hz: float = 0.0) -> float:
        return 45.0  # Approximate elevation beamwidth
