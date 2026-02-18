"""Modem module: modulation, coding, and combined performance."""

from satlinkbudget.modem._coding import (
    CONV_R12_K7,
    LDPC_R12,
    LDPC_R34,
    LDPC_R78,
    TURBO_R12,
    UNCODED,
    CodingScheme,
    CodingType,
)
from satlinkbudget.modem._modulation import (
    BPSK,
    PSK8,
    QAM16,
    QPSK,
    ModulationScheme,
    ModulationType,
)
from satlinkbudget.modem._performance import ModemConfig

__all__ = [
    "ModulationType",
    "ModulationScheme",
    "CodingType",
    "CodingScheme",
    "ModemConfig",
    "BPSK",
    "QPSK",
    "PSK8",
    "QAM16",
    "UNCODED",
    "CONV_R12_K7",
    "TURBO_R12",
    "LDPC_R12",
    "LDPC_R34",
    "LDPC_R78",
]
