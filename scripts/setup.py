def notebook_setup():

    %load_ext autoreload
    %autoreload 2

    import sys

    import os

    # adds root dir 'wine_analyis_hplc_uv' to path.

    sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '../')))

    from agilette import agilette_core as ag

    lib = ag.Agilette('/Users/jonathan/0_jono_data').library