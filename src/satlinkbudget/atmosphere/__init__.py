"""Atmospheric propagation models (ITU-R P-series).

Submodules
----------
_gaseous : ITU-R P.676 gaseous absorption (oxygen + water vapor).
_rain : ITU-R P.838 / P.618 / P.839 rain attenuation.
_cloud : ITU-R P.840 cloud and fog attenuation.
_scintillation : ITU-R P.531 ionospheric scintillation.
_total : Aggregated atmospheric-loss computation.
"""

from satlinkbudget.atmosphere._cloud import (
    cloud_attenuation,
    cloud_specific_attenuation_coefficient,
)
from satlinkbudget.atmosphere._gaseous import (
    gaseous_attenuation_slant,
    specific_attenuation_oxygen,
    specific_attenuation_water_vapor,
)
from satlinkbudget.atmosphere._rain import (
    effective_rain_height_km,
    rain_attenuation_exceeded,
    rain_specific_attenuation,
    rain_specific_attenuation_coefficients,
)
from satlinkbudget.atmosphere._scintillation import (
    ionospheric_scintillation_loss,
    scintillation_index_s4,
)
from satlinkbudget.atmosphere._total import (
    AtmosphericLosses,
    compute_atmospheric_losses,
)

__all__ = [
    # gaseous
    "specific_attenuation_oxygen",
    "specific_attenuation_water_vapor",
    "gaseous_attenuation_slant",
    # rain
    "rain_specific_attenuation_coefficients",
    "rain_specific_attenuation",
    "effective_rain_height_km",
    "rain_attenuation_exceeded",
    # cloud
    "cloud_specific_attenuation_coefficient",
    "cloud_attenuation",
    # scintillation
    "scintillation_index_s4",
    "ionospheric_scintillation_loss",
    # total
    "AtmosphericLosses",
    "compute_atmospheric_losses",
]
