import pandas as pd
import streamlit as st


from tests import test_spectra_df
from scripts.core_scripts import hplc_dad_plots


def spectra_display(df: pd.DataFrame):
    tab_line_plot, tab_surface_plot, tab_contour_plot = st.tabs(
        ["line plot", "surface plot", "contour plot"]
    )

    with tab_line_plot:
        st.plotly_chart(hplc_dad_plots.plot_3d_line(df))

    with tab_surface_plot:
        st.plotly_chart(hplc_dad_plots.surface_plot(df))

    with tab_contour_plot:
        st.plotly_chart(hplc_dad_plots.contour_plot(df), downsample_factor=0)

    return None


def main():
    spectra_display(
        test_spectra_df.test_spectra_df().drop(["name_ct", "hash_key"], axis=1)
    )


if __name__ == "__main__":
    main()
