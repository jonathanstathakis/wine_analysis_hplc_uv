---
date: 2024-06-08
---

# Project TODO Outline

A tracker for todo tasks.

- Chapter 1: Data Acquisition and Raw Dataset Description / Interpretation
  - Reincarnate experimental
  - Reincarnate dataset by metadata analysis
  - analyse raw data - total number of 'prominent' peaks and clustering (and where the clustering is) over varietal and detection method.
  - write up:
    1. outline
    2. by section
    3. final pass.

- Chapter 2: Data Processing by Deconvolution, Analysis by deconvoluted peak areas
  - subsections:
   - baseline subtraction:
    - notes
    - code module
  - smoothing
    - notes
    - code module
  - signal sharpening
    - notes
    - code module
  - dtw alignment
    - notes
    - code module
  - deconvolution
    - notes
    - code module
  - alignment by binning
    - notes
    - code module
  - data analysis post deconvolution
    1. compare results to raw data analysis. I.e. look at the same samples, same peaks and observe how the data has changed.
    2. analyse across varietal classes with selected representative from each varietal.
      - representative based on highest correlation within class (varietal).
    3. Analyse between detection methods across varietal classes
    4. analyse within class (varietal)
    5. perform a basic clustering analysis.
    

- Chapter 3: Classification by XGBoost.

