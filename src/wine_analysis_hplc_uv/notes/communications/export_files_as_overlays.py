"""
A module creating a Plotly based viz comparison of the same sample under CUPRAC and raw chromatographic imaging.

Note: the data cannot currently be found at the given locations, and the paths will need to be modified if this module is to be used.
"""

import pandas as pd
import plotly.graph_objs as go


def filepaths():
    # a dict of filepaths grouped by sample
    filedict = {
        "A0101": {
            "cuprac": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0101.D/CA0101_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0101.D/CA0101_data_450.csv",
            },
            "raw_uv": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0101.D/A0101_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0101.D/A0101_data_254.csv",
            },
        },
        "A0201": {
            "cuprac": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0201.D/CA0201_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0201.D/CA0201_data_450.csv",
            },
            "raw_uv": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0201.D/A0201_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0201.D/A0201_data_254.csv",
            },
        },
        "A0301": {
            "cuprac": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0301.D/CA0301_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/CA0301.D/CA0301_data_450.csv",
            },
            "raw_uv": {
                "metadata": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0301.D/A0301_metadata.csv",
                "data": "/Users/jonathan/mres_thesis/raw_uv_cuprac_comparison/files/processed_files/A0301.D/A0301_data_254.csv",
            },
        },
    }

    return filedict


def extract_files(filepathdict: dict):
    pd_dict = filepathdict

    for key, val in filepathdict.items():
        for key2, val2 in val.items():
            for key3, val3 in val2.items():
                pd_dict[key][key2][key3] = pd.read_csv(val3)

    return pd_dict


def overlay_plots(data_dict):
    for samplecode, val1 in data_dict.items():
        data_list = []
        for detectiontype, val2 in val1.items():
            data_list.append(data_dict[samplecode][detectiontype]["data"].iloc[:, 1])

        traces = []
        for data in data_list:
            traces.append(go.Scatter(y=data, name=samplecode + "_" + detectiontype))
        fig = go.Figure(traces)
        fig.show()


def main():
    filedict = filepaths()
    pd_dict = extract_files(filedict)
    overlay_plots(pd_dict)
    return None


if __name__ == "__main__":
    main()
