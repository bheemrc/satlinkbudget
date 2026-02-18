"""Tests for modulation schemes and BER calculations."""

import pytest

from satlinkbudget.modem import BPSK, PSK8, QAM16, QPSK, ModulationScheme, ModulationType


class TestModulationType:
    """Tests for the ModulationType enum."""

    def test_bpsk_value(self):
        assert ModulationType.BPSK == "BPSK"

    def test_qpsk_value(self):
        assert ModulationType.QPSK == "QPSK"

    def test_psk8_value(self):
        assert ModulationType.PSK8 == "8PSK"

    def test_qam16_value(self):
        assert ModulationType.QAM16 == "16QAM"


class TestPrebuiltSchemes:
    """Tests for pre-built modulation scheme instances."""

    def test_bpsk_bits_per_symbol(self):
        assert BPSK.bits_per_symbol == 1

    def test_qpsk_bits_per_symbol(self):
        assert QPSK.bits_per_symbol == 2

    def test_psk8_bits_per_symbol(self):
        assert PSK8.bits_per_symbol == 3

    def test_qam16_bits_per_symbol(self):
        assert QAM16.bits_per_symbol == 4

    def test_bpsk_spectral_efficiency(self):
        assert BPSK.spectral_efficiency == 1.0

    def test_qpsk_spectral_efficiency(self):
        assert QPSK.spectral_efficiency == 2.0

    def test_psk8_spectral_efficiency(self):
        assert PSK8.spectral_efficiency == 3.0

    def test_qam16_spectral_efficiency(self):
        assert QAM16.spectral_efficiency == 4.0


class TestBER:
    """Tests for BER computation."""

    def test_bpsk_ber_at_10db(self):
        """BPSK BER at Eb/N0=10 dB should be approximately 3.87e-6."""
        ber = BPSK.ber(10.0)
        assert ber == pytest.approx(3.872e-6, rel=1e-2)

    def test_qpsk_ber_same_as_bpsk(self):
        """QPSK has the same Eb/N0 performance as BPSK."""
        for eb_n0 in [0.0, 5.0, 10.0, 15.0]:
            assert QPSK.ber(eb_n0) == pytest.approx(BPSK.ber(eb_n0), rel=1e-10)

    def test_bpsk_ber_at_0db(self):
        """BPSK BER at Eb/N0=0 dB should be 0.5*erfc(1) ~ 0.0786."""
        ber = BPSK.ber(0.0)
        assert ber == pytest.approx(0.07865, rel=1e-3)

    def test_8psk_needs_more_eb_n0_than_qpsk(self):
        """8PSK requires more Eb/N0 than QPSK for the same BER."""
        # At the same Eb/N0, 8PSK has worse (higher) BER
        for eb_n0 in [5.0, 8.0, 12.0]:
            assert PSK8.ber(eb_n0) > QPSK.ber(eb_n0)

    def test_16qam_needs_more_eb_n0_than_8psk(self):
        """16QAM requires more Eb/N0 than 8PSK for the same target BER."""
        # At low target BER (where these approximations are designed),
        # 16QAM needs higher Eb/N0 than 8PSK.
        qam16_req = QAM16.required_eb_n0_db(1e-5)
        psk8_req = PSK8.required_eb_n0_db(1e-5)
        assert qam16_req > psk8_req

    def test_ber_decreases_monotonically_bpsk(self):
        """BER should decrease as Eb/N0 increases for BPSK."""
        eb_n0_values = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]
        ber_values = [BPSK.ber(x) for x in eb_n0_values]
        for i in range(len(ber_values) - 1):
            assert ber_values[i] > ber_values[i + 1]

    def test_ber_decreases_monotonically_8psk(self):
        """BER should decrease as Eb/N0 increases for 8PSK."""
        eb_n0_values = [0.0, 4.0, 8.0, 12.0, 16.0]
        ber_values = [PSK8.ber(x) for x in eb_n0_values]
        for i in range(len(ber_values) - 1):
            assert ber_values[i] > ber_values[i + 1]

    def test_ber_decreases_monotonically_16qam(self):
        """BER should decrease as Eb/N0 increases for 16QAM."""
        eb_n0_values = [0.0, 4.0, 8.0, 12.0, 16.0]
        ber_values = [QAM16.ber(x) for x in eb_n0_values]
        for i in range(len(ber_values) - 1):
            assert ber_values[i] > ber_values[i + 1]

    def test_8psk_ber_at_10db(self):
        """8PSK BER at 10 dB should be approximately 2.02e-3."""
        ber = PSK8.ber(10.0)
        assert ber == pytest.approx(2.023e-3, rel=1e-2)

    def test_16qam_ber_at_10db(self):
        """16QAM BER at 10 dB should be approximately 1.75e-3."""
        ber = QAM16.ber(10.0)
        assert ber == pytest.approx(1.754e-3, rel=1e-2)

    def test_ber_positive(self):
        """BER should always be positive."""
        for scheme in [BPSK, QPSK, PSK8, QAM16]:
            for eb_n0 in [0.0, 5.0, 10.0]:
                assert scheme.ber(eb_n0) > 0.0


class TestRequiredEbN0:
    """Tests for the required Eb/N0 bisection search."""

    def test_bpsk_required_eb_n0_default_ber(self):
        """BPSK required Eb/N0 for BER=1e-5 should be approximately 9.6 dB."""
        result = BPSK.required_eb_n0_db()
        assert result == pytest.approx(9.6, abs=0.1)

    def test_higher_order_needs_more_eb_n0(self):
        """Higher-order modulation requires more Eb/N0 for the same BER."""
        bpsk_req = BPSK.required_eb_n0_db(1e-5)
        qpsk_req = QPSK.required_eb_n0_db(1e-5)
        psk8_req = PSK8.required_eb_n0_db(1e-5)
        qam16_req = QAM16.required_eb_n0_db(1e-5)

        # BPSK and QPSK should be essentially equal
        assert bpsk_req == pytest.approx(qpsk_req, abs=0.01)
        # 8PSK needs more than QPSK
        assert psk8_req > qpsk_req
        # 16QAM needs more than 8PSK
        assert qam16_req > psk8_req

    def test_lower_ber_needs_more_eb_n0(self):
        """A lower target BER requires more Eb/N0."""
        req_1e4 = BPSK.required_eb_n0_db(1e-4)
        req_1e5 = BPSK.required_eb_n0_db(1e-5)
        req_1e6 = BPSK.required_eb_n0_db(1e-6)
        assert req_1e5 > req_1e4
        assert req_1e6 > req_1e5
