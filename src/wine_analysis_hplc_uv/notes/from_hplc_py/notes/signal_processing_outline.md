
## Chapter 3: Signal Processing

Goal: Process the signal to reveal the pure peaks.

The requirements are as follows:

1. flat baseline = 0 at the ends of the signal.
2. no peaks below 1 mAU in signal.
3. all evident shoulders, peaks are sufficiently resolved, sharpened etc.

### Notes

[Notes - Signal Processing](./notes_signal_processing.ipynb)

### Logbook

- [How to Optimize Windowing](optimize_windowing.ipynb)
- [Preprocessing: Smoothing and Sharpening 1](logbook_preprocesing_1_smoothing_sharpening_1.ipynb)
- [Preprocessing: Smoothing and Sharpening 2](preprocessing_rounding_floats.ipynb)
- [Preprocessing: Baseline Correction with BEADS](logbook_preprocessing_2_beads.ipynb)
- [Preprocessing: Floating Point Errors](logbook_preprocessing_rounding_floats.ipynb)

#### Sectionsz

- [ ] [Intro](./ch_signal-processing_intro.ipynb)
- [ ] [Peak Detection](./ch_signal-processing_signal-mapping.ipynb)
- [ ] [Signal Windowing](ch_signal-processing_signal-windowing.ipynb)
- [ ] [Handling Floating Point Error](ch_signal-processing_signal-windowing.ipynb)
- [ ] [Resolution Improvement by Derivative transformation](ch_signal-processing_derivative-transformation.ipynb)
- [ ] [Smoothing](ch_signal-processing_smoothing.ipynb)
- [ ] [Baseline Correction](./ch_signal-processing_baseline-correction.ipynb)
- [ ] [Deconvolution](./ch_signal-processing_deconvolution.ipynb) 
- [ ] [Programmatic Signal Processing Pipelines](./ch_signal-processing_pipeline.ipynb)
- [ ] [Conclusion] NTS: will create when everything else in this chapter is written.

## Notes from Signal Processing

2024-04-22 10:49:13

1. Its better to resolution enhance before baseline subtraction as it gives you a buffer between the signal and zero, avoiding complications that arise from dipping below it. *Updated* 2024-04-24 10:45:59: It depends on your goal. if it is, as is my primary goal, to create zero points for windowing, then subtraction first is important as it gets you 99% of the way there. If it is my secondary goal, which is shoulder -> peak transformation, then not subtracting followed by subtraction is better because you can use a heftier weighting then baseline subtract to finish it off.