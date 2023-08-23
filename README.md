# Project README



## PCA Modelling

PCA modelling package is [here](src/wine_analysis_hplc_uv/modeling/pca.py)

## EDA decisions

As I progress through my pipelines, EDA will produce certain decisions on how to handle the data. For example, which samples to exclude, time scales, precisions, target wavelengths, and so on. These decisions will be for the most part made in EDA jupyter notebooks, who I will list here alongside the decision made.

| i | Decision                                                     | notebook                                                 |
|---|--------------------------------------------------------------|----------------------------------------------------------|
| 1 | time axis precision is milliseconds                          | [notebook](notebooks/determining_time_precision.ipynb)   |
| 2 | time axis needs to be centered by subtraction of first value | [notebook](notebooks/determining_time_axis_offset.ipynb) |
