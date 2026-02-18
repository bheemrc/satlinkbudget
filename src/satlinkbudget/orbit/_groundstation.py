"""Ground station model with geometry calculations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._constants import R_EARTH


# Earth rotation rate [rad/s]
OMEGA_EARTH = 7.2921159e-5


@dataclass
class GroundStation:
    """Ground station with geographic coordinates."""

    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_m: float = 0.0
    min_elevation_deg: float = 5.0

    @classmethod
    def from_datasheet(cls, name: str) -> GroundStation:
        from satlinkbudget.data._registry import registry

        gs_data = registry.get_groundstation(name)
        return cls(
            name=gs_data.name,
            latitude_deg=gs_data.latitude_deg,
            longitude_deg=gs_data.longitude_deg,
            altitude_m=gs_data.altitude_m,
            min_elevation_deg=gs_data.min_elevation_deg,
        )

    def ecef_position(self) -> np.ndarray:
        """Ground station position in ECEF frame [m]."""
        lat = np.radians(self.latitude_deg)
        lon = np.radians(self.longitude_deg)
        r = R_EARTH + self.altitude_m

        return np.array([
            r * np.cos(lat) * np.cos(lon),
            r * np.cos(lat) * np.sin(lon),
            r * np.sin(lat),
        ])

    def eci_position(self, gmst_rad: float) -> np.ndarray:
        """Ground station position in ECI frame [m].

        Parameters
        ----------
        gmst_rad : float
            Greenwich Mean Sidereal Time [rad].
        """
        lat = np.radians(self.latitude_deg)
        lon = np.radians(self.longitude_deg) + gmst_rad
        r = R_EARTH + self.altitude_m

        return np.array([
            r * np.cos(lat) * np.cos(lon),
            r * np.cos(lat) * np.sin(lon),
            r * np.sin(lat),
        ])

    def eci_velocity(self, gmst_rad: float) -> np.ndarray:
        """Ground station velocity in ECI frame due to Earth rotation [m/s]."""
        lat = np.radians(self.latitude_deg)
        lon = np.radians(self.longitude_deg) + gmst_rad
        r = R_EARTH + self.altitude_m
        v = OMEGA_EARTH * r * np.cos(lat)

        return np.array([
            -v * np.sin(lon),
            v * np.cos(lon),
            0.0,
        ])


def elevation_angle(
    sat_pos_eci: np.ndarray, gs_pos_eci: np.ndarray
) -> float:
    """Compute elevation angle of satellite as seen from ground station.

    Parameters
    ----------
    sat_pos_eci : np.ndarray
        Satellite position in ECI [m].
    gs_pos_eci : np.ndarray
        Ground station position in ECI [m].

    Returns
    -------
    float
        Elevation angle [degrees].
    """
    range_vec = sat_pos_eci - gs_pos_eci
    range_mag = np.linalg.norm(range_vec)

    # Local zenith direction at ground station = normalized gs position
    zenith = gs_pos_eci / np.linalg.norm(gs_pos_eci)

    # Elevation = 90° - angle between range vector and zenith
    cos_zenith_angle = np.dot(range_vec, zenith) / range_mag
    zenith_angle_rad = np.arccos(np.clip(cos_zenith_angle, -1.0, 1.0))
    elevation_rad = np.pi / 2.0 - zenith_angle_rad

    return float(np.degrees(elevation_rad))


def azimuth_angle(
    sat_pos_eci: np.ndarray,
    gs_pos_eci: np.ndarray,
    gs_lat_rad: float,
    gs_lon_gmst_rad: float,
) -> float:
    """Compute azimuth angle of satellite from ground station.

    Returns
    -------
    float
        Azimuth angle [degrees], 0=North, 90=East.
    """
    range_vec = sat_pos_eci - gs_pos_eci

    # Local coordinate system (East, North, Up)
    sin_lat = np.sin(gs_lat_rad)
    cos_lat = np.cos(gs_lat_rad)
    sin_lon = np.sin(gs_lon_gmst_rad)
    cos_lon = np.cos(gs_lon_gmst_rad)

    # East unit vector
    e_east = np.array([-sin_lon, cos_lon, 0.0])
    # North unit vector
    e_north = np.array([-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat])

    east = np.dot(range_vec, e_east)
    north = np.dot(range_vec, e_north)

    az = np.degrees(np.arctan2(east, north)) % 360.0
    return float(az)
