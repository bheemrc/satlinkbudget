"""Tests for pointing loss and polarization mismatch."""

import pytest

from satlinkbudget.antenna._pointing import (
    pointing_loss_db,
    polarization_mismatch_loss_db,
)


class TestPointingLoss:
    def test_boresight_zero(self):
        """On-axis → 0 dB loss."""
        assert pointing_loss_db(0.0, 1.0) == pytest.approx(0.0)

    def test_half_beamwidth_3db(self):
        """At half the beamwidth → 3 dB loss."""
        assert pointing_loss_db(0.5, 1.0) == pytest.approx(3.0)

    def test_full_beamwidth_12db(self):
        """At full beamwidth → 12 dB loss."""
        assert pointing_loss_db(1.0, 1.0) == pytest.approx(12.0)

    def test_small_error(self):
        """5° error with 30° beamwidth → small loss."""
        loss = pointing_loss_db(5.0, 30.0)
        assert loss == pytest.approx(12.0 * (5.0 / 30.0) ** 2, rel=1e-6)
        assert loss < 1.0

    def test_increases_with_error(self):
        losses = [pointing_loss_db(e, 10.0) for e in [0, 1, 2, 3, 5]]
        assert all(losses[i] <= losses[i + 1] for i in range(len(losses) - 1))

    def test_narrow_beam_more_sensitive(self):
        """Same pointing error, narrower beam → more loss."""
        l1 = pointing_loss_db(1.0, 10.0)
        l2 = pointing_loss_db(1.0, 1.0)
        assert l2 > l1


class TestPolarizationMismatch:
    def test_matched_linear(self):
        assert polarization_mismatch_loss_db("linear_v", "linear_v") == 0.0

    def test_matched_circular(self):
        assert polarization_mismatch_loss_db("rhcp", "rhcp") == 0.0

    def test_cross_linear(self):
        """Cross-polarized linear → high loss."""
        loss = polarization_mismatch_loss_db("linear_v", "linear_h")
        assert loss >= 20.0

    def test_counter_circular(self):
        """Counter-rotating circular → high loss."""
        loss = polarization_mismatch_loss_db("rhcp", "lhcp")
        assert loss >= 20.0

    def test_linear_to_circular(self):
        """Linear ↔ circular → 3 dB."""
        assert polarization_mismatch_loss_db("linear_v", "rhcp") == pytest.approx(3.0)
        assert polarization_mismatch_loss_db("rhcp", "linear_h") == pytest.approx(3.0)

    def test_all_losses_non_negative(self):
        pols = ["linear_v", "linear_h", "rhcp", "lhcp"]
        for tx in pols:
            for rx in pols:
                assert polarization_mismatch_loss_db(tx, rx) >= 0.0
