import os
import sys

sys.path.append("/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests")

from wine_analysis_hplc_uv.sampletracker import sample_tracker_methods as st_methods
from wine_analysis_hplc_uv.sampletracker import sampletrackerprocesser
from tests.mytestmethods.mytestmethods import test_report


def get_key():
    return os.environ.get("TEST_SAMPLE_TRACKER_KEY")


def test_sample_tracker():
    tests = [(test_sample_tracker_df_builder,), (test_sample_tracker_class_init,)]

    test_report(tests)


def test_sample_tracker_df_builder():
    sample_tracker_df = st_methods.sample_tracker_df_builder()
    assert not sample_tracker_df.empty


def test_sample_tracker_class_init(key=get_key()):
    sample_tracker = sampletrackerprocesser.SampleTracker(
        sheet_title="test_sample_tracker", key=key
    )


def main():
    test_sample_tracker()


if __name__ == "__main__":
    main()
