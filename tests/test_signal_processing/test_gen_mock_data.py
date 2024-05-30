"""
tests for mock data generatoin
"""

import pytest
from tests.test_signal_processing import gen_mock_data


@pytest.fixture
def mock_skewnorm_signal():
    y = gen_mock_data.gen_mock_skewnorm_convolution()
    return y


def test_gen_mock_skewnorm_convolution(mock_skewnorm_signal):
    """
    test generation of mock signals formed from skew-normal distributions
    """
    pass
