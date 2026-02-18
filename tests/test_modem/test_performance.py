"""Tests for ModemConfig combining modulation and coding."""

import pytest

from satlinkbudget.modem import (
    BPSK,
    CONV_R12_K7,
    LDPC_R12,
    LDPC_R34,
    LDPC_R78,
    PSK8,
    QAM16,
    QPSK,
    TURBO_R12,
    UNCODED,
    ModemConfig,
)


class TestRequiredEbN0:
    """Tests for the required Eb/N0 with coding and implementation loss."""

    def test_coding_reduces_required_eb_n0(self):
        """Coding gain should reduce the required Eb/N0 compared to uncoded."""
        uncoded_cfg = ModemConfig(BPSK, UNCODED, implementation_loss_db=0.0)
        coded_cfg = ModemConfig(BPSK, LDPC_R12, implementation_loss_db=0.0)
        assert coded_cfg.required_eb_n0_db() < uncoded_cfg.required_eb_n0_db()

    def test_stronger_code_lower_eb_n0(self):
        """A stronger code (more gain) should require less Eb/N0."""
        cfg_conv = ModemConfig(BPSK, CONV_R12_K7, implementation_loss_db=0.0)
        cfg_turbo = ModemConfig(BPSK, TURBO_R12, implementation_loss_db=0.0)
        assert cfg_turbo.required_eb_n0_db() < cfg_conv.required_eb_n0_db()

    def test_implementation_loss_increases_required_eb_n0(self):
        """Implementation loss should increase the required Eb/N0."""
        cfg_no_loss = ModemConfig(BPSK, LDPC_R12, implementation_loss_db=0.0)
        cfg_with_loss = ModemConfig(BPSK, LDPC_R12, implementation_loss_db=2.0)
        assert cfg_with_loss.required_eb_n0_db() > cfg_no_loss.required_eb_n0_db()

    def test_implementation_loss_difference(self):
        """Implementation loss difference should be exact."""
        cfg_1db = ModemConfig(BPSK, LDPC_R12, implementation_loss_db=1.0)
        cfg_3db = ModemConfig(BPSK, LDPC_R12, implementation_loss_db=3.0)
        diff = cfg_3db.required_eb_n0_db() - cfg_1db.required_eb_n0_db()
        assert diff == pytest.approx(2.0, abs=0.01)

    def test_uncoded_bpsk_required_eb_n0(self):
        """Uncoded BPSK with 1 dB impl loss should be ~10.6 dB for BER=1e-5."""
        cfg = ModemConfig(BPSK, UNCODED, implementation_loss_db=1.0)
        result = cfg.required_eb_n0_db()
        # ~9.6 (uncoded BPSK) - 0 (no gain) + 1 (impl loss) = ~10.6
        assert result == pytest.approx(10.6, abs=0.2)


class TestDataRate:
    """Tests for the data rate calculation."""

    def test_bpsk_ldpc_r12_25khz(self):
        """BPSK + LDPC R=1/2 with 25 kHz BW = 12500 bps."""
        cfg = ModemConfig(BPSK, LDPC_R12)
        rate = cfg.data_rate(25000.0)
        assert rate == pytest.approx(12500.0)

    def test_qpsk_uncoded_10khz(self):
        """QPSK uncoded with 10 kHz BW = 20000 bps."""
        cfg = ModemConfig(QPSK, UNCODED)
        rate = cfg.data_rate(10000.0)
        assert rate == pytest.approx(20000.0)

    def test_qam16_ldpc_r34_1mhz(self):
        """16QAM + LDPC R=3/4 with 1 MHz BW = 3000000 bps."""
        cfg = ModemConfig(QAM16, LDPC_R34)
        rate = cfg.data_rate(1e6)
        assert rate == pytest.approx(3e6)

    def test_data_rate_zero_bandwidth(self):
        """Zero bandwidth should give zero data rate."""
        cfg = ModemConfig(BPSK, UNCODED)
        assert cfg.data_rate(0.0) == 0.0

    def test_data_rate_proportional_to_bandwidth(self):
        """Data rate should be proportional to bandwidth."""
        cfg = ModemConfig(QPSK, LDPC_R12)
        rate_1 = cfg.data_rate(1000.0)
        rate_2 = cfg.data_rate(2000.0)
        assert rate_2 == pytest.approx(2.0 * rate_1)


class TestSpectralEfficiency:
    """Tests for the spectral efficiency property."""

    def test_bpsk_uncoded(self):
        """BPSK uncoded: 1.0 * 1.0 = 1.0 bits/s/Hz."""
        cfg = ModemConfig(BPSK, UNCODED)
        assert cfg.spectral_efficiency == pytest.approx(1.0)

    def test_qpsk_ldpc_r12(self):
        """QPSK + LDPC R=1/2: 2.0 * 0.5 = 1.0 bits/s/Hz."""
        cfg = ModemConfig(QPSK, LDPC_R12)
        assert cfg.spectral_efficiency == pytest.approx(1.0)

    def test_qam16_ldpc_r78(self):
        """16QAM + LDPC R=7/8: 4.0 * 0.875 = 3.5 bits/s/Hz."""
        cfg = ModemConfig(QAM16, LDPC_R78)
        assert cfg.spectral_efficiency == pytest.approx(3.5)

    def test_psk8_ldpc_r34(self):
        """8PSK + LDPC R=3/4: 3.0 * 0.75 = 2.25 bits/s/Hz."""
        cfg = ModemConfig(PSK8, LDPC_R34)
        assert cfg.spectral_efficiency == pytest.approx(2.25)

    def test_spectral_efficiency_matches_data_rate(self):
        """spectral_efficiency * bandwidth should equal data_rate."""
        cfg = ModemConfig(QAM16, LDPC_R34)
        bw = 50000.0
        assert cfg.data_rate(bw) == pytest.approx(cfg.spectral_efficiency * bw)
