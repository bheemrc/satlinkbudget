"""Transmitter chain: power + antenna gain - losses = EIRP."""

from dataclasses import dataclass

import numpy as np


@dataclass
class TransmitterChain:
    """Transmitter chain computing EIRP.

    EIRP = P_tx + G_tx - L_feed - L_pointing [dBW]
    """

    power_dbw: float
    antenna_gain_dbi: float
    feed_loss_db: float = 0.0
    pointing_loss_db: float = 0.0
    other_loss_db: float = 0.0

    @property
    def eirp_dbw(self) -> float:
        """Effective Isotropic Radiated Power [dBW]."""
        return (
            self.power_dbw
            + self.antenna_gain_dbi
            - self.feed_loss_db
            - self.pointing_loss_db
            - self.other_loss_db
        )

    @classmethod
    def from_power_dbm(
        cls,
        power_dbm: float,
        antenna_gain_dbi: float,
        feed_loss_db: float = 0.0,
        pointing_loss_db: float = 0.0,
        other_loss_db: float = 0.0,
    ) -> "TransmitterChain":
        """Create from power in dBm (converts to dBW)."""
        return cls(
            power_dbw=power_dbm - 30.0,
            antenna_gain_dbi=antenna_gain_dbi,
            feed_loss_db=feed_loss_db,
            pointing_loss_db=pointing_loss_db,
            other_loss_db=other_loss_db,
        )
