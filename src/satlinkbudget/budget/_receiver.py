"""Receiver chain: antenna gain - losses - noise = G/T."""

from dataclasses import dataclass

import numpy as np


@dataclass
class ReceiverChain:
    """Receiver chain computing G/T (figure of merit).

    G/T = G_rx - L_feed - L_pointing - 10·log₁₀(T_sys)  [dB/K]
    """

    antenna_gain_dbi: float
    system_noise_temp_k: float
    feed_loss_db: float = 0.0
    pointing_loss_db: float = 0.0
    other_loss_db: float = 0.0

    @property
    def figure_of_merit_db_per_k(self) -> float:
        """G/T [dB/K]."""
        effective_gain = (
            self.antenna_gain_dbi
            - self.feed_loss_db
            - self.pointing_loss_db
            - self.other_loss_db
        )
        return effective_gain - 10.0 * np.log10(self.system_noise_temp_k)
