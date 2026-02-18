"""Forward error correction coding schemes."""

from dataclasses import dataclass, field
from enum import Enum


class CodingType(str, Enum):
    """Supported coding types."""

    UNCODED = "uncoded"
    CONVOLUTIONAL = "convolutional"
    TURBO = "turbo"
    LDPC = "ldpc"


@dataclass
class CodingScheme:
    """A forward error correction coding scheme.

    Parameters
    ----------
    coding_type : CodingType
        The type of coding.
    code_rate : float
        Code rate, e.g. 0.5 for rate-1/2.
    coding_gain_db : float
        Coding gain at BER=1e-5 in dB.
    name : str
        Human-readable name for the coding scheme.
    """

    coding_type: CodingType
    code_rate: float
    coding_gain_db: float
    name: str = field(default="")


# Pre-built coding scheme instances
UNCODED = CodingScheme(CodingType.UNCODED, code_rate=1.0, coding_gain_db=0.0, name="Uncoded")
CONV_R12_K7 = CodingScheme(
    CodingType.CONVOLUTIONAL, code_rate=0.5, coding_gain_db=5.0, name="Conv R=1/2 K=7"
)
TURBO_R12 = CodingScheme(
    CodingType.TURBO, code_rate=0.5, coding_gain_db=8.0, name="Turbo R=1/2"
)
LDPC_R12 = CodingScheme(
    CodingType.LDPC, code_rate=0.5, coding_gain_db=7.5, name="LDPC R=1/2"
)
LDPC_R34 = CodingScheme(
    CodingType.LDPC, code_rate=0.75, coding_gain_db=6.0, name="LDPC R=3/4"
)
LDPC_R78 = CodingScheme(
    CodingType.LDPC, code_rate=0.875, coding_gain_db=5.0, name="LDPC R=7/8"
)
