"""Aggregated atmospheric loss computation.

Combines gaseous, rain, cloud, and (optionally) scintillation losses
into a single convenience function and dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass

from satlinkbudget.atmosphere._cloud import cloud_attenuation
from satlinkbudget.atmosphere._gaseous import gaseous_attenuation_slant
from satlinkbudget.atmosphere._rain import rain_attenuation_exceeded
from satlinkbudget.atmosphere._scintillation import ionospheric_scintillation_loss


@dataclass
class AtmosphericLosses:
    """Container for the individual atmospheric-loss components [dB]."""

    gaseous_db: float
    rain_db: float
    cloud_db: float
    scintillation_db: float

    @property
    def total_db(self) -> float:
        """Sum of all atmospheric loss terms [dB]."""
        return (
            self.gaseous_db
            + self.rain_db
            + self.cloud_db
            + self.scintillation_db
        )


def compute_atmospheric_losses(
    freq_ghz: float,
    elevation_deg: float,
    rain_rate_001_mm_h: float = 0.0,
    latitude_deg: float = 45.0,
    altitude_km: float = 0.0,
    liquid_water_content_kg_m2: float = 0.0,
    include_scintillation: bool = False,
    polarization_tilt_deg: float = 45.0,
    pressure_hpa: float = 1013.25,
    temp_k: float = 288.15,
    rho_g_m3: float = 7.5,
    cloud_temp_k: float = 273.15,
    geomagnetic_latitude_deg: float = 45.0,
    solar_flux_index: float = 120.0,
    local_time_hours: float = 14.0,
    scintillation_percentage: float = 1.0,
) -> AtmosphericLosses:
    """Compute all atmospheric loss components for a satellite link.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    elevation_deg : float
        Elevation angle [degrees].
    rain_rate_001_mm_h : float
        Rain rate exceeded for 0.01 % of the time [mm/h].
    latitude_deg : float
        Station latitude [degrees].
    altitude_km : float
        Station altitude above MSL [km].
    liquid_water_content_kg_m2 : float
        Columnar cloud liquid-water content [kg/m^2].
    include_scintillation : bool
        If True, compute ionospheric scintillation loss.
    polarization_tilt_deg : float
        Polarisation tilt [degrees] (0 = H, 90 = V, 45 = circular).
    pressure_hpa : float
        Atmospheric pressure [hPa].
    temp_k : float
        Ambient temperature [K].
    rho_g_m3 : float
        Surface water-vapor density [g/m^3].
    cloud_temp_k : float
        Cloud temperature [K].
    geomagnetic_latitude_deg : float
        Geomagnetic latitude for scintillation model [degrees].
    solar_flux_index : float
        10.7 cm solar flux index.
    local_time_hours : float
        Local solar time [hours].
    scintillation_percentage : float
        Percentage of time for scintillation fade depth [%].

    Returns
    -------
    AtmosphericLosses
        Dataclass with gaseous_db, rain_db, cloud_db, scintillation_db
        and a total_db property.
    """
    gaseous = gaseous_attenuation_slant(
        freq_ghz, elevation_deg, pressure_hpa, temp_k, rho_g_m3
    )

    rain = rain_attenuation_exceeded(
        freq_ghz,
        elevation_deg,
        rain_rate_001_mm_h,
        latitude_deg,
        altitude_km,
        polarization_tilt_deg,
    )

    cloud = cloud_attenuation(
        freq_ghz, elevation_deg, liquid_water_content_kg_m2, cloud_temp_k
    )

    if include_scintillation:
        scint = ionospheric_scintillation_loss(
            freq_ghz,
            elevation_deg,
            geomagnetic_latitude_deg,
            solar_flux_index,
            local_time_hours,
            scintillation_percentage,
        )
    else:
        scint = 0.0

    return AtmosphericLosses(
        gaseous_db=gaseous,
        rain_db=rain,
        cloud_db=cloud,
        scintillation_db=scint,
    )
