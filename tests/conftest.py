"""Shared test fixtures for satlinkbudget."""

import pytest
import numpy as np


@pytest.fixture
def rng():
    """Reproducible random number generator."""
    return np.random.default_rng(42)
