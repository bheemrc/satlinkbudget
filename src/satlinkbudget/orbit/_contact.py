"""Contact window analysis between satellite and ground station."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import (
    GroundStation,
    OMEGA_EARTH,
    elevation_angle,
)


@dataclass
class ContactWindow:
    """A single contact (pass) between satellite and ground station."""

    start_time_s: float
    end_time_s: float
    max_elevation_deg: float
    max_elevation_time_s: float

    @property
    def duration_s(self) -> float:
        return self.end_time_s - self.start_time_s


@dataclass
class ContactAnalysis:
    """Results of contact analysis over a time span."""

    contacts: list[ContactWindow] = field(default_factory=list)
    total_duration_s: float = 0.0
    analysis_duration_s: float = 0.0

    @property
    def num_contacts(self) -> int:
        return len(self.contacts)

    @property
    def contacts_per_day(self) -> float:
        if self.analysis_duration_s <= 0:
            return 0.0
        return self.num_contacts * 86400.0 / self.analysis_duration_s

    @property
    def avg_duration_s(self) -> float:
        if not self.contacts:
            return 0.0
        return self.total_duration_s / len(self.contacts)

    @property
    def max_elevation_deg(self) -> float:
        if not self.contacts:
            return 0.0
        return max(c.max_elevation_deg for c in self.contacts)


def find_contacts(
    orbit: Orbit,
    gs: GroundStation,
    duration_s: float,
    dt_s: float = 10.0,
    start_time_s: float = 0.0,
) -> ContactAnalysis:
    """Find all contact windows between satellite and ground station.

    Parameters
    ----------
    orbit : Orbit
        Satellite orbit.
    gs : GroundStation
        Ground station.
    duration_s : float
        Analysis duration [s].
    dt_s : float
        Time step [s].
    start_time_s : float
        Start time [s].

    Returns
    -------
    ContactAnalysis
        Contact windows found.
    """
    contacts: list[ContactWindow] = []
    times = np.arange(start_time_s, start_time_s + duration_s, dt_s)

    in_contact = False
    contact_start = 0.0
    max_el = 0.0
    max_el_time = 0.0

    for t in times:
        state = orbit.propagate(t)
        gmst = OMEGA_EARTH * t
        gs_pos = gs.eci_position(gmst)
        el = elevation_angle(state.position_eci, gs_pos)

        if el >= gs.min_elevation_deg:
            if not in_contact:
                # Contact start
                in_contact = True
                contact_start = t
                max_el = el
                max_el_time = t
            else:
                if el > max_el:
                    max_el = el
                    max_el_time = t
        else:
            if in_contact:
                # Contact end
                contacts.append(
                    ContactWindow(
                        start_time_s=contact_start,
                        end_time_s=t,
                        max_elevation_deg=max_el,
                        max_elevation_time_s=max_el_time,
                    )
                )
                in_contact = False

    # Handle case where contact extends beyond analysis window
    if in_contact:
        contacts.append(
            ContactWindow(
                start_time_s=contact_start,
                end_time_s=times[-1],
                max_elevation_deg=max_el,
                max_elevation_time_s=max_el_time,
            )
        )

    total = sum(c.duration_s for c in contacts)

    return ContactAnalysis(
        contacts=contacts,
        total_duration_s=total,
        analysis_duration_s=duration_s,
    )
