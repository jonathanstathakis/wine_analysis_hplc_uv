"""_summary_

TODO:

- [x] sample_tracker_df_builder
- [x] SampleTracker initialisation
- [ ] SampleTracker.df
- [ ] SampleTracker.clean_df
- [ ] SampleTracker.st_to_db
- [ ] SampleTracker.to_sheets
"""

import os
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
from wine_analysis_hplc_uv.sampletracker import sample_tracker_processor
from tests.mytestmethods.mytestmethods import test_report
from wine_analysis_hplc_uv.df_methods import df_methods


def test_sample_tracker():
    tests = [
        (test_sample_tracker_df_builder,),
        (test_sample_tracker_class_init,),
        (test_sample_tracker_df,),
    ]

    test_report(tests)


def get_key():
    return os.environ.get("TEST_SAMPLE_TRACKER_KEY")


def test_sample_tracker_df_builder():
    sample_tracker_df = st_methods.sample_tracker_df_builder()
    assert not sample_tracker_df.empty


def get_SampleTracker(key=get_key()):
    sample_tracker = sample_tracker_processor.SampleTracker(
        sheet_title="test_sample_tracker", key=key
    )
    return sample_tracker


def test_sample_tracker_class_init(key=get_key()):
    st = get_SampleTracker(key)
    return st


def test_sample_tracker_df(key=get_key()) -> None:
    sample_tracker = get_SampleTracker(key=get_key())
    df_methods.test_df(sample_tracker.df)
    return None


def main():
    test_sample_tracker()


if __name__ == "__main__":
    main()
