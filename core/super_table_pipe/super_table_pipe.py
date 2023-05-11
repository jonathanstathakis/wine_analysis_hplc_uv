from devtools import project_settings, function_timer as ft

from core.super_table_pipe import selected_avantor_runs
from core.super_table_pipe import chemstation_sample_tracker_join
from core.super_table_pipe import cellartracker_fuzzy_join


@ft.timeit
def super_table_pipe(chemstation_df, sample_tracker_df, cellartracker_df):
    df = (
        chemstation_df.pipe(selected_avantor_runs.selected_avantor_runs)
        .pipe(chemstation_sample_tracker_join, sample_tracker_df)
        .pipe(cellar_tracker_fuzzy_join, cellartracker_df)
    )
    return df


def main():
    metadata_sampletracker_cellartracker_join()


if __name__ == "__main__":
    main()
