"""Core link budget computation."""

from __future__ import annotations

import numpy as np

from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.budget._results import LinkBudgetResult
from satlinkbudget.rf._constants import BOLTZMANN_DBW
from satlinkbudget.rf._path_loss import free_space_path_loss_db


def compute_link_budget(
    transmitter: TransmitterChain,
    receiver: ReceiverChain,
    frequency_hz: float,
    distance_m: float,
    data_rate_bps: float,
    required_eb_n0_db: float,
    atmospheric_loss_db: float = 0.0,
    polarization_loss_db: float = 0.0,
    misc_loss_db: float = 0.0,
) -> LinkBudgetResult:
    """Compute full link budget.

    C/N₀ = EIRP + G/T - FSPL - L_atm - L_pol - L_misc - k_B
    Eb/N₀ = C/N₀ - 10·log₁₀(R_bit)
    Margin = Eb/N₀_received - Eb/N₀_required

    Parameters
    ----------
    transmitter : TransmitterChain
        Transmitter chain.
    receiver : ReceiverChain
        Receiver chain.
    frequency_hz : float
        Carrier frequency [Hz].
    distance_m : float
        Propagation distance [m].
    data_rate_bps : float
        Data rate [bps].
    required_eb_n0_db : float
        Required Eb/N₀ for target BER [dB].
    atmospheric_loss_db : float
        Total atmospheric loss [dB].
    polarization_loss_db : float
        Polarization mismatch loss [dB].
    misc_loss_db : float
        Miscellaneous additional losses [dB].

    Returns
    -------
    LinkBudgetResult
        Complete link budget with all line items.
    """
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if distance_m <= 0.0:
        raise ValueError("distance_m must be positive")
    if data_rate_bps <= 0.0:
        raise ValueError("data_rate_bps must be positive")

    eirp = transmitter.eirp_dbw
    g_over_t = receiver.figure_of_merit_db_per_k
    fspl = free_space_path_loss_db(distance_m, frequency_hz)

    # C/N₀ = EIRP + G/T - FSPL - L_atm - L_pol - L_misc - k_B(dBW)
    # Note: k_B in dBW is negative (~-228.6), so subtracting it ADDS
    c_over_n0 = (
        eirp
        + g_over_t
        - fspl
        - atmospheric_loss_db
        - polarization_loss_db
        - misc_loss_db
        - BOLTZMANN_DBW  # subtracting a negative = adding
    )

    # Eb/N₀ = C/N₀ - 10·log₁₀(data_rate)
    eb_n0 = c_over_n0 - 10.0 * np.log10(data_rate_bps)

    margin = eb_n0 - required_eb_n0_db

    return LinkBudgetResult(
        tx_power_dbw=transmitter.power_dbw,
        tx_antenna_gain_dbi=transmitter.antenna_gain_dbi,
        tx_feed_loss_db=transmitter.feed_loss_db,
        tx_pointing_loss_db=transmitter.pointing_loss_db,
        tx_other_loss_db=transmitter.other_loss_db,
        eirp_dbw=eirp,
        frequency_hz=frequency_hz,
        distance_m=distance_m,
        free_space_path_loss_db=fspl,
        atmospheric_loss_db=atmospheric_loss_db,
        polarization_loss_db=polarization_loss_db,
        misc_loss_db=misc_loss_db,
        rx_antenna_gain_dbi=receiver.antenna_gain_dbi,
        rx_feed_loss_db=receiver.feed_loss_db,
        rx_pointing_loss_db=receiver.pointing_loss_db,
        rx_other_loss_db=receiver.other_loss_db,
        system_noise_temp_k=receiver.system_noise_temp_k,
        figure_of_merit_db_per_k=g_over_t,
        data_rate_bps=data_rate_bps,
        required_eb_n0_db=required_eb_n0_db,
        c_over_n0_db_hz=c_over_n0,
        eb_n0_db=eb_n0,
        margin_db=margin,
    )


def compute_max_data_rate(
    transmitter: TransmitterChain,
    receiver: ReceiverChain,
    frequency_hz: float,
    distance_m: float,
    required_eb_n0_db: float,
    target_margin_db: float = 3.0,
    atmospheric_loss_db: float = 0.0,
    polarization_loss_db: float = 0.0,
    misc_loss_db: float = 0.0,
) -> float:
    """Compute maximum data rate that closes the link with given margin.

    R_max = 10^((C/N₀ - Eb/N₀_req - margin) / 10)

    Returns
    -------
    float
        Maximum data rate [bps]. Returns 0 if link cannot close.
    """
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if distance_m <= 0.0:
        raise ValueError("distance_m must be positive")

    eirp = transmitter.eirp_dbw
    g_over_t = receiver.figure_of_merit_db_per_k
    fspl = free_space_path_loss_db(distance_m, frequency_hz)

    c_over_n0 = (
        eirp
        + g_over_t
        - fspl
        - atmospheric_loss_db
        - polarization_loss_db
        - misc_loss_db
        - BOLTZMANN_DBW
    )

    # R_max = C/N₀ / (Eb/N₀_req × margin) in linear
    # In dB: 10·log₁₀(R_max) = C/N₀ - Eb/N₀_req - margin
    log_rate = c_over_n0 - required_eb_n0_db - target_margin_db
    if log_rate < 0:
        return 0.0
    return 10.0 ** (log_rate / 10.0)


def compute_required_power_dbw(
    receiver: ReceiverChain,
    frequency_hz: float,
    distance_m: float,
    data_rate_bps: float,
    required_eb_n0_db: float,
    target_margin_db: float = 3.0,
    tx_antenna_gain_dbi: float = 0.0,
    tx_feed_loss_db: float = 0.0,
    atmospheric_loss_db: float = 0.0,
    polarization_loss_db: float = 0.0,
    misc_loss_db: float = 0.0,
) -> float:
    """Compute minimum TX power to close the link.

    Returns
    -------
    float
        Required TX power [dBW].
    """
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if distance_m <= 0.0:
        raise ValueError("distance_m must be positive")
    if data_rate_bps <= 0.0:
        raise ValueError("data_rate_bps must be positive")

    g_over_t = receiver.figure_of_merit_db_per_k
    fspl = free_space_path_loss_db(distance_m, frequency_hz)

    # Need: P_tx + G_tx - L_feed + G/T - FSPL - L_atm - L_pol - L_misc - k_B
    #       - 10·log₁₀(R) >= Eb/N₀_req + margin
    required_c_over_n0 = (
        required_eb_n0_db + target_margin_db + 10.0 * np.log10(data_rate_bps)
    )

    required_eirp = (
        required_c_over_n0
        - g_over_t
        + fspl
        + atmospheric_loss_db
        + polarization_loss_db
        + misc_loss_db
        + BOLTZMANN_DBW
    )

    return required_eirp - tx_antenna_gain_dbi + tx_feed_loss_db
