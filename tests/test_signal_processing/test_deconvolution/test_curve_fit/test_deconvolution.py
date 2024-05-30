"""
Related to test_curve_fit.py, test the deconvolution of a simple dataset, but in this module, we're testing against AUC.

TODO:

- [ ] setup:
    - [ ] get the input signal
    - [ ] get the popt
- [ ] compute the peak signals
- [ ] compute the reconvolution
- [ ] compute the aucs
- [ ] compare the aucs

To avoid dependency problems it will be best to save a popt set to a file, in this way we are testing the performance of these functions alone, and should run the full length test in a third module.
"""

import pytest


@pytest.fixture
def popt():
    pass
