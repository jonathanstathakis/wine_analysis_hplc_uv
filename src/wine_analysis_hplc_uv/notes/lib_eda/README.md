## Outline

A EDA report on my wine chromatographic dataset made up of raw UV and CUPRAC detected samples. At first the intention was a simple report to send to my Supervisor but over time has developed into a chapter of my thesis.

The workflow is this: jupyter notebook -> pdf via Quarto. Graphics will be produced via seaborn.

## A little bit of development history

This EDA report was begun on 2023-07-09 as `./lib_eda.ipynb` with methods developed in `/Users/jonathan/uni/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/library_eda/lib_eda/lib_eda.py`. Over time development moved to `./lib_eda_pub.ipynb`. From this point I will be breaking that notebook down into its component sections and reforming it through quarto directly, the intention being that breaking down the sections will make project management easier.

The sections are as follows:

1. Breakdown by Detection Type
2. Variety
3. Type
4. Country

