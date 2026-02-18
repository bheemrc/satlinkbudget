"""Tests for forward error correction coding schemes."""

import pytest

from satlinkbudget.modem import (
    CONV_R12_K7,
    LDPC_R12,
    LDPC_R34,
    LDPC_R78,
    TURBO_R12,
    UNCODED,
    CodingScheme,
    CodingType,
)


class TestCodingType:
    """Tests for the CodingType enum."""

    def test_uncoded_value(self):
        assert CodingType.UNCODED == "uncoded"

    def test_convolutional_value(self):
        assert CodingType.CONVOLUTIONAL == "convolutional"

    def test_turbo_value(self):
        assert CodingType.TURBO == "turbo"

    def test_ldpc_value(self):
        assert CodingType.LDPC == "ldpc"


class TestUncodedScheme:
    """Tests for the UNCODED scheme."""

    def test_uncoded_gain_is_zero(self):
        assert UNCODED.coding_gain_db == 0.0

    def test_uncoded_rate_is_one(self):
        assert UNCODED.code_rate == 1.0

    def test_uncoded_type(self):
        assert UNCODED.coding_type == CodingType.UNCODED


class TestCodedSchemes:
    """Tests for coded schemes."""

    @pytest.mark.parametrize(
        "scheme",
        [CONV_R12_K7, TURBO_R12, LDPC_R12, LDPC_R34, LDPC_R78],
        ids=["conv", "turbo", "ldpc_r12", "ldpc_r34", "ldpc_r78"],
    )
    def test_coding_gain_positive(self, scheme):
        """All coded schemes should have positive coding gain."""
        assert scheme.coding_gain_db > 0.0

    @pytest.mark.parametrize(
        "scheme",
        [CONV_R12_K7, TURBO_R12, LDPC_R12, LDPC_R34, LDPC_R78, UNCODED],
        ids=["conv", "turbo", "ldpc_r12", "ldpc_r34", "ldpc_r78", "uncoded"],
    )
    def test_code_rate_in_valid_range(self, scheme):
        """Code rate should be in (0, 1]."""
        assert 0.0 < scheme.code_rate <= 1.0

    def test_turbo_has_highest_gain(self):
        """Turbo code should have the highest coding gain."""
        all_schemes = [CONV_R12_K7, TURBO_R12, LDPC_R12, LDPC_R34, LDPC_R78]
        gains = [s.coding_gain_db for s in all_schemes]
        assert TURBO_R12.coding_gain_db == max(gains)

    def test_ldpc_rates_ordered(self):
        """LDPC code rates should be ordered: R12 < R34 < R78."""
        assert LDPC_R12.code_rate < LDPC_R34.code_rate < LDPC_R78.code_rate

    def test_ldpc_gains_ordered(self):
        """LDPC coding gains should decrease as rate increases (less redundancy)."""
        assert LDPC_R12.coding_gain_db > LDPC_R34.coding_gain_db > LDPC_R78.coding_gain_db

    def test_scheme_has_name(self):
        """All pre-built schemes should have non-empty names."""
        for scheme in [UNCODED, CONV_R12_K7, TURBO_R12, LDPC_R12, LDPC_R34, LDPC_R78]:
            assert scheme.name != ""

    def test_custom_scheme_creation(self):
        """A custom CodingScheme can be created."""
        custom = CodingScheme(
            coding_type=CodingType.LDPC,
            code_rate=0.6,
            coding_gain_db=6.5,
            name="Custom LDPC",
        )
        assert custom.code_rate == 0.6
        assert custom.coding_gain_db == 6.5
