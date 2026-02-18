"""Circular orbit propagator with J2 perturbation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._constants import J2_EARTH, MU_EARTH, R_EARTH


@dataclass
class OrbitState:
    """Satellite state at a given time."""

    time_s: float
    position_eci: np.ndarray  # [x, y, z] in ECI frame [m]
    velocity_eci: np.ndarray  # [vx, vy, vz] in ECI frame [m/s]


class Orbit:
    """Circular orbit with optional J2 secular perturbation."""

    def __init__(
        self,
        altitude_km: float,
        inclination_deg: float,
        raan_deg: float = 0.0,
        arg_latitude_deg: float = 0.0,
        epoch_s: float = 0.0,
        j2: bool = True,
    ) -> None:
        self.altitude_m = altitude_km * 1e3
        self.inclination_rad = np.radians(inclination_deg)
        self.raan_rad = np.radians(raan_deg)
        self.arg_latitude_rad = np.radians(arg_latitude_deg)
        self.epoch_s = epoch_s
        self.j2_enabled = j2

        self.semi_major_axis = R_EARTH + self.altitude_m
        self.period_s = 2.0 * np.pi * np.sqrt(
            self.semi_major_axis**3 / MU_EARTH
        )
        self.mean_motion = 2.0 * np.pi / self.period_s
        self.velocity = np.sqrt(MU_EARTH / self.semi_major_axis)

        # J2 secular rates
        if self.j2_enabled:
            p = self.semi_major_axis / R_EARTH
            self.raan_rate = (
                -1.5
                * self.mean_motion
                * J2_EARTH
                / p**2
                * np.cos(self.inclination_rad)
            )
            self.arg_lat_rate_correction = (
                0.75
                * self.mean_motion
                * J2_EARTH
                / p**2
                * (5.0 * np.cos(self.inclination_rad) ** 2 - 1.0)
            )
        else:
            self.raan_rate = 0.0
            self.arg_lat_rate_correction = 0.0

    @classmethod
    def circular(
        cls,
        altitude_km: float,
        inclination_deg: float,
        raan_deg: float = 0.0,
        j2: bool = True,
    ) -> Orbit:
        return cls(
            altitude_km=altitude_km,
            inclination_deg=inclination_deg,
            raan_deg=raan_deg,
            j2=j2,
        )

    def propagate(self, time_s: float) -> OrbitState:
        """Propagate orbit to given time and return state."""
        dt = time_s - self.epoch_s

        # Argument of latitude (in-orbit angle)
        u = self.arg_latitude_rad + (self.mean_motion + self.arg_lat_rate_correction) * dt
        # RAAN with J2 drift
        raan = self.raan_rad + self.raan_rate * dt
        inc = self.inclination_rad
        r = self.semi_major_axis

        # Position in orbital plane
        x_orb = r * np.cos(u)
        y_orb = r * np.sin(u)

        # Transform to ECI
        cos_raan = np.cos(raan)
        sin_raan = np.sin(raan)
        cos_inc = np.cos(inc)
        sin_inc = np.sin(inc)

        x = x_orb * cos_raan - y_orb * sin_raan * cos_inc
        y = x_orb * sin_raan + y_orb * cos_raan * cos_inc
        z = y_orb * sin_inc

        pos = np.array([x, y, z])

        # Velocity: derivative of position
        u_dot = self.mean_motion + self.arg_lat_rate_correction
        vx_orb = -r * np.sin(u) * u_dot
        vy_orb = r * np.cos(u) * u_dot

        raan_dot = self.raan_rate

        vx = (
            vx_orb * cos_raan
            - vy_orb * sin_raan * cos_inc
            - (x_orb * sin_raan + y_orb * cos_raan * cos_inc) * raan_dot
        )
        vy = (
            vx_orb * sin_raan
            + vy_orb * cos_raan * cos_inc
            + (x_orb * cos_raan - y_orb * sin_raan * cos_inc) * raan_dot
        )
        vz = vy_orb * sin_inc

        vel = np.array([vx, vy, vz])

        return OrbitState(time_s=time_s, position_eci=pos, velocity_eci=vel)

    def propagate_array(self, times_s: np.ndarray) -> list[OrbitState]:
        """Propagate orbit to multiple times."""
        return [self.propagate(t) for t in times_s]
