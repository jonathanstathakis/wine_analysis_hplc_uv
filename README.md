# Project README



## PCA Modelling

PCA modelling package is [here](src/wine_analysis_hplc_uv/modeling/pca.py)

## EDA decisions

As I progress through my pipelines, EDA will produce certain decisions on how to handle the data. For example, which samples to exclude, time scales, precisions, target wavelengths, and so on. These decisions will be for the most part made in EDA jupyter notebooks, who I will list here alongside the decision made.

| i | Decision                                                     | notebook                                                 |
|---|--------------------------------------------------------------|----------------------------------------------------------|
| 1 | time axis precision is milliseconds                          | [notebook](notebooks/determining_time_precision.ipynb)   |
| 2 | time axis needs to be offset corrected by subtraction of first value | [notebook](notebooks/determining_time_axis_offset.ipynb) |
| 3 | time interval of 0 - 20 mins (after offset correction) to be used | [notebook](notebooks/developing_baseline_subtraction.ipynb) |
| 4 | asls to be used for baseline correction | [notebook](notebooks/developing_baseline_subtraction.ipynb) |
| 5 |  
