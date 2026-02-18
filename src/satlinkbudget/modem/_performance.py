"""Modem configuration combining modulation and coding."""

from dataclasses import dataclass, field

from satlinkbudget.modem._coding import CodingScheme
from satlinkbudget.modem._modulation import ModulationScheme


@dataclass
class ModemConfig:
    """Combined modulation and coding configuration.

    Parameters
    ----------
    modulation : ModulationScheme
        The modulation scheme.
    coding : CodingScheme
        The coding scheme.
    implementation_loss_db : float
        Implementation loss in dB (default 1.0).
    """

    modulation: ModulationScheme
    coding: CodingScheme
    implementation_loss_db: float = field(default=1.0)

    def required_eb_n0_db(self, target_ber: float = 1e-5) -> float:
        """Required Eb/N0 accounting for coding gain and implementation loss.

        Parameters
        ----------
        target_ber : float
            Target bit error rate (default 1e-5).

        Returns
        -------
        float
            Required Eb/N0 in dB:
            uncoded_required - coding_gain + implementation_loss
        """
        uncoded = self.modulation.required_eb_n0_db(target_ber)
        return uncoded - self.coding.coding_gain_db + self.implementation_loss_db

    def data_rate(self, bandwidth_hz: float) -> float:
        """Achievable data rate for a given bandwidth.

        Parameters
        ----------
        bandwidth_hz : float
            Available bandwidth in Hz.

        Returns
        -------
        float
            Data rate in bits per second:
            bandwidth * spectral_efficiency * code_rate
        """
        return bandwidth_hz * self.modulation.spectral_efficiency * self.coding.code_rate

    @property
    def spectral_efficiency(self) -> float:
        """Effective spectral efficiency in bits/s/Hz.

        Returns
        -------
        float
            modulation spectral_efficiency * code_rate
        """
        return self.modulation.spectral_efficiency * self.coding.code_rate
