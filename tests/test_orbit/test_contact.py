"""Tests for contact window analysis."""

import numpy as np
import pytest

from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import GroundStation
from satlinkbudget.orbit._contact import find_contacts


class TestContactAnalysis:
    @pytest.fixture
    def sso_orbit(self):
        return Orbit.circular(500.0, 97.4, raan_deg=0.0)

    @pytest.fixture
    def svalbard(self):
        return GroundStation("Svalbard", 78.23, 15.39, 450.0, min_elevation_deg=5.0)

    @pytest.fixture
    def equatorial_gs(self):
        return GroundStation("Equator", 0.0, 0.0, 0.0, min_elevation_deg=5.0)

    def test_contacts_found(self, sso_orbit, svalbard):
        """SSO at Svalbard should find contacts in 24h."""
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        assert result.num_contacts > 0

    def test_svalbard_many_passes(self, sso_orbit, svalbard):
        """Svalbard should see many passes of SSO satellite (~10-14/day)."""
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        assert result.contacts_per_day >= 6  # Conservative lower bound

    def test_contact_duration_reasonable(self, sso_orbit, svalbard):
        """Contact duration should be 2-15 minutes for LEO."""
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        for contact in result.contacts:
            assert 60 < contact.duration_s < 1000  # 1-17 minutes

    def test_max_elevation_positive(self, sso_orbit, svalbard):
        """Max elevation should be above min elevation."""
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        for contact in result.contacts:
            assert contact.max_elevation_deg >= 5.0

    def test_total_duration(self, sso_orbit, svalbard):
        """Total contact time should be sum of individual contacts."""
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        total = sum(c.duration_s for c in result.contacts)
        assert result.total_duration_s == pytest.approx(total, rel=1e-6)

    def test_analysis_duration(self, sso_orbit, svalbard):
        result = find_contacts(sso_orbit, svalbard, 86400.0)
        assert result.analysis_duration_s == 86400.0

    def test_no_contacts_wrong_geometry(self):
        """Equatorial orbit with high-latitude station → few contacts."""
        orb = Orbit.circular(500.0, 0.0)  # Equatorial orbit
        gs = GroundStation("Svalbard", 78.23, 15.39, 450.0, min_elevation_deg=5.0)
        result = find_contacts(orb, gs, 86400.0, dt_s=10.0)
        # Equatorial orbit can't reach 78° latitude
        assert result.num_contacts == 0

    def test_contact_window_properties(self, sso_orbit, svalbard):
        result = find_contacts(sso_orbit, svalbard, 86400.0, dt_s=10.0)
        for c in result.contacts:
            assert c.end_time_s > c.start_time_s
            assert c.duration_s > 0
            assert c.max_elevation_time_s >= c.start_time_s
            assert c.max_elevation_time_s <= c.end_time_s
