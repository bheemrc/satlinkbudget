"""Core RF math: constants, conversions, path loss, noise."""

from satlinkbudget.rf._constants import (
    BOLTZMANN_DBW,
    BOLTZMANN_J_PER_K,
    C_LIGHT,
    J2_EARTH,
    MU_EARTH,
    R_EARTH,
    T_REF,
)
from satlinkbudget.rf._conversions import (
    dbm_to_watts,
    dbw_to_watts,
    frequency_to_wavelength,
    from_db,
    to_db,
    watts_to_dbm,
    watts_to_dbw,
    wavelength_to_frequency,
)
from satlinkbudget.rf._noise import (
    antenna_noise_temperature,
    figure_of_merit_db,
    noise_figure_to_temperature,
    rain_noise_temperature,
    system_noise_temperature,
)
from satlinkbudget.rf._path_loss import free_space_path_loss_db, slant_range

__all__ = [
    "C_LIGHT",
    "BOLTZMANN_J_PER_K",
    "BOLTZMANN_DBW",
    "R_EARTH",
    "MU_EARTH",
    "J2_EARTH",
    "T_REF",
    "to_db",
    "from_db",
    "watts_to_dbw",
    "dbw_to_watts",
    "watts_to_dbm",
    "dbm_to_watts",
    "frequency_to_wavelength",
    "wavelength_to_frequency",
    "free_space_path_loss_db",
    "slant_range",
    "system_noise_temperature",
    "noise_figure_to_temperature",
    "figure_of_merit_db",
    "antenna_noise_temperature",
    "rain_noise_temperature",
]
