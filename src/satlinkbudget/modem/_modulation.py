"""Modulation schemes and BER calculations."""

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.special import erfc


class ModulationType(str, Enum):
    """Supported modulation types."""

    BPSK = "BPSK"
    QPSK = "QPSK"
    PSK8 = "8PSK"
    QAM16 = "16QAM"


@dataclass
class ModulationScheme:
    """A modulation scheme with BER performance model.

    Parameters
    ----------
    mod_type : ModulationType
        The modulation type.
    bits_per_symbol : int
        Number of bits encoded per symbol.
    spectral_efficiency : float
        Spectral efficiency in bits/s/Hz.
    """

    mod_type: ModulationType
    bits_per_symbol: int
    spectral_efficiency: float  # bits/s/Hz

    def ber(self, eb_n0_db: float) -> float:
        """Compute BER for a given Eb/N0 in dB.

        Parameters
        ----------
        eb_n0_db : float
            Energy-per-bit to noise spectral density ratio in dB.

        Returns
        -------
        float
            Bit error rate.

        Formulas
        --------
        BPSK:  0.5 * erfc(sqrt(Eb/N0))
        QPSK:  0.5 * erfc(sqrt(Eb/N0))   (same Eb/N0 performance as BPSK)
        8PSK:  (2/3) * erfc(sqrt(3 * Eb/N0) * sin(pi/8))
        16QAM: (3/8) * erfc(sqrt(2 * Eb/N0 / 5))
        """
        eb_n0_linear = 10.0 ** (eb_n0_db / 10.0)

        if self.mod_type == ModulationType.BPSK:
            return float(0.5 * erfc(np.sqrt(eb_n0_linear)))

        if self.mod_type == ModulationType.QPSK:
            return float(0.5 * erfc(np.sqrt(eb_n0_linear)))

        if self.mod_type == ModulationType.PSK8:
            return float(
                (2.0 / 3.0) * erfc(np.sqrt(3.0 * eb_n0_linear) * np.sin(np.pi / 8.0))
            )

        if self.mod_type == ModulationType.QAM16:
            return float((3.0 / 8.0) * erfc(np.sqrt(2.0 * eb_n0_linear / 5.0)))

        msg = f"Unsupported modulation type: {self.mod_type}"
        raise ValueError(msg)

    def required_eb_n0_db(self, target_ber: float = 1e-5) -> float:
        """Find Eb/N0 [dB] required for a target BER using bisection search.

        Parameters
        ----------
        target_ber : float
            Target bit error rate (default 1e-5).

        Returns
        -------
        float
            Required Eb/N0 in dB.
        """
        low, high = -5.0, 30.0
        for _ in range(100):
            mid = (low + high) / 2.0
            if self.ber(mid) > target_ber:
                low = mid
            else:
                high = mid
        return (low + high) / 2.0


# Pre-built modulation scheme instances
BPSK = ModulationScheme(ModulationType.BPSK, bits_per_symbol=1, spectral_efficiency=1.0)
QPSK = ModulationScheme(ModulationType.QPSK, bits_per_symbol=2, spectral_efficiency=2.0)
PSK8 = ModulationScheme(ModulationType.PSK8, bits_per_symbol=3, spectral_efficiency=3.0)
QAM16 = ModulationScheme(
    ModulationType.QAM16, bits_per_symbol=4, spectral_efficiency=4.0
)
