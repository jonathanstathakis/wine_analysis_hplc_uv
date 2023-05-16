from . import (
    cellartracker_fuzzy_join,
    chemstation_sample_tracker_join,
    selected_avantor_runs,
)
from ...devtools import function_timer as ft, project_settings


@ft.timeit
def super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df, how_chemstation_sampletracker_join: str):
    print("###\n\nSUPER TABLE PIPE\n\n###\n")
    assert not chemstation_df.empty, "chemstation_df is empty\n"
    assert not sample_tracker_df.empty, "sample_tracker_df is empty\n"
    assert not cellartracker_df.empty, "cellartracker_df is empty\n50"
    df = (
        chemstation_df.pipe(selected_avantor_runs.selected_avantor_runs)
        .pipe(chemstation_sample_tracker_join.chemstation_sample_tracker_join, sample_tracker_df, how = how_chemstation_sampletracker_join)
        .pipe(cellartracker_fuzzy_join.cellar_tracker_fuzzy_join, cellartracker_df)
    )
    return df


def main():
    #metadata_sampletracker_cellartracker_join()
    return None


if __name__ == "__main__":
    main()
