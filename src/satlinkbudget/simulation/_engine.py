"""Pass simulation engine: time-step link budget over satellite passes."""

from __future__ import annotations

import numpy as np

from satlinkbudget.budget._link import compute_link_budget
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.modem._performance import ModemConfig
from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import GroundStation, OMEGA_EARTH, elevation_angle
from satlinkbudget.orbit._contact import find_contacts
from satlinkbudget.orbit._doppler import radial_velocity, doppler_shift
from satlinkbudget.atmosphere._total import compute_atmospheric_losses
from satlinkbudget.simulation._results import PassData, PassSimulationResults


class PassSimulation:
    """Time-stepping link budget simulation over satellite passes."""

    def __init__(
        self,
        orbit: Orbit,
        ground_station: GroundStation,
        transmitter: TransmitterChain,
        receiver: ReceiverChain,
        modem: ModemConfig,
        frequency_hz: float,
        data_rate_bps: float,
        atmospheric_params: dict | None = None,
    ) -> None:
        self.orbit = orbit
        self.ground_station = ground_station
        self.transmitter = transmitter
        self.receiver = receiver
        self.modem = modem
        self.frequency_hz = frequency_hz
        self.data_rate_bps = data_rate_bps
        self.atmospheric_params = atmospheric_params or {}

    def run(
        self,
        duration_orbits: float = 24.0,
        dt_s: float = 1.0,
        contact_dt_s: float = 10.0,
    ) -> PassSimulationResults:
        """Run simulation over the given number of orbits.

        Parameters
        ----------
        duration_orbits : float
            Number of orbits to simulate.
        dt_s : float
            Time step within each pass [s].
        contact_dt_s : float
            Time step for contact detection [s].

        Returns
        -------
        PassSimulationResults
            Simulation results with per-pass data.
        """
        duration_s = duration_orbits * self.orbit.period_s
        required_eb_n0 = self.modem.required_eb_n0_db()

        # Find all contacts
        contacts = find_contacts(
            self.orbit, self.ground_station, duration_s, dt_s=contact_dt_s
        )

        passes: list[PassData] = []
        freq_ghz = self.frequency_hz / 1e9

        for contact in contacts.contacts:
            times = np.arange(contact.start_time_s, contact.end_time_s, dt_s)
            if len(times) == 0:
                continue

            elevations = np.zeros(len(times))
            ranges_m = np.zeros(len(times))
            margins = np.zeros(len(times))
            doppler_shifts = np.zeros(len(times))
            data_rates = np.zeros(len(times))
            cn0_values = np.zeros(len(times))

            for i, t in enumerate(times):
                state = self.orbit.propagate(t)
                gmst = OMEGA_EARTH * t
                gs_pos = self.ground_station.eci_position(gmst)
                gs_vel = self.ground_station.eci_velocity(gmst)

                el = elevation_angle(state.position_eci, gs_pos)
                elevations[i] = el

                # Slant range from actual satellite-GS vector distance
                sr = float(np.linalg.norm(state.position_eci - gs_pos))
                ranges_m[i] = sr

                # Atmospheric losses
                atm = compute_atmospheric_losses(
                    freq_ghz=freq_ghz,
                    elevation_deg=max(el, 5.0),
                    **self.atmospheric_params,
                )

                # Link budget
                result = compute_link_budget(
                    transmitter=self.transmitter,
                    receiver=self.receiver,
                    frequency_hz=self.frequency_hz,
                    distance_m=sr,
                    data_rate_bps=self.data_rate_bps,
                    required_eb_n0_db=required_eb_n0,
                    atmospheric_loss_db=atm.total_db,
                )

                margins[i] = result.margin_db
                cn0_values[i] = result.c_over_n0_db_hz
                data_rates[i] = self.data_rate_bps if result.link_closes else 0.0

                # Doppler
                v_r = radial_velocity(
                    state.position_eci, state.velocity_eci, gs_pos, gs_vel
                )
                doppler_shifts[i] = doppler_shift(self.frequency_hz, v_r)

            # Cumulative data volume for this pass
            effective_rates = np.where(margins >= 0, self.data_rate_bps, 0.0)
            data_volume_bits = float(np.sum(effective_rates) * dt_s)

            passes.append(
                PassData(
                    pass_number=len(passes) + 1,
                    start_time_s=contact.start_time_s,
                    end_time_s=contact.end_time_s,
                    duration_s=contact.duration_s,
                    max_elevation_deg=contact.max_elevation_deg,
                    times_s=times,
                    elevations_deg=elevations,
                    ranges_m=ranges_m,
                    margins_db=margins,
                    cn0_db_hz=cn0_values,
                    doppler_shifts_hz=doppler_shifts,
                    data_rates_bps=data_rates,
                    data_volume_bits=data_volume_bits,
                )
            )

        total_data_bits = sum(p.data_volume_bits for p in passes)
        total_contact_s = sum(p.duration_s for p in passes)

        return PassSimulationResults(
            passes=passes,
            total_data_volume_bits=total_data_bits,
            total_contact_time_s=total_contact_s,
            simulation_duration_s=duration_s,
            num_passes=len(passes),
            frequency_hz=self.frequency_hz,
            data_rate_bps=self.data_rate_bps,
        )
