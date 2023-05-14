from . import (
    cellartracker_fuzzy_join,
    chemstation_sample_tracker_join,
    selected_avantor_runs,
)
from ...devtools import function_timer as ft, project_settings


@ft.timeit
def super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df):
    df = (
        chemstation_df.pipe(selected_avantor_runs.selected_avantor_runs)
        .pipe(chemstation_sample_tracker_join, sample_tracker_df)
        .pipe(cellartracker_fuzzy_join, cellartracker_df)
    )
    return df


def main():
    metadata_sampletracker_cellartracker_join()


if __name__ == "__main__":
    main()
