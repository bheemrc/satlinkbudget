"""Physical and orbital constants for link budget calculations."""

import numpy as np

# Speed of light [m/s]
C_LIGHT: float = 299_792_458.0

# Boltzmann constant [J/K]
BOLTZMANN_J_PER_K: float = 1.380649e-23

# Boltzmann constant [dBW/K/Hz]
BOLTZMANN_DBW: float = float(10.0 * np.log10(BOLTZMANN_J_PER_K))  # -228.6 dBW/K/Hz

# Earth mean equatorial radius [m]
R_EARTH: float = 6_378_137.0

# Earth gravitational parameter [m³/s²]
MU_EARTH: float = 3.986004418e14

# J2 oblateness perturbation coefficient
J2_EARTH: float = 1.08263e-3

# Reference temperature for noise figure [K]
T_REF: float = 290.0
