## Peak Deconvolution

2023-11-20 10:05:10

Have discovered `hplc-py` which provides a framework for automated peak deconvolution. Problem is that running it on a sample is slow and is producing bad results. trying to figure out why. Options:

- my processing sucks. Specifically the baseline subtraction is not adequate to seperate peak regions
- the test sample sucks - some peaks including the maxima have significant overlap.
- Need to smooth the signals
- need to chunk the signals

Overall, the first port of call is to establish the output. That will be  a DB table. Lets establish that first.

2023-11-20 16:19:25 - that was rough. DB interface is constructed, and ive identified that ASLS baseline correction is insufficient for hplc-py to identify distinct signal regions. I have been experimenting with hplc-py's baseline correction input for the last few hours and have it down to a window of 0.7 to generate isolated peaks.

2023-11-20 18:23:14 - running `fit_peaks` on a sample dataset with baseline correction on is resulting in least squares error:

```
`x0` is infeasible.
  File "/Users/jonathan/Library/Caches/pypoetry/virtualenvs/wine-analysis-hplc-uv-F-SbhWjO-py3.11/lib/python3.11/site-packages/scipy/optimize/_lsq/least_squares.py", line 823, in least_squares
    raise ValueError("`x0` is infeasible.")
  File "/Users/jonathan/Library/Caches/pypoetry/virtualenvs/wine-analysis-hplc-uv-F-SbhWjO-py3.11/lib/python3.11/site-packages/scipy/optimize/_minpack_py.py", line 974, in curve_fit
    res = least_squares(func, p0, jac=jac, bounds=bounds, method=method,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jonathan/Library/Caches/pypoetry/virtualenvs/wine-analysis-hplc-uv-F-SbhWjO-py3.11/lib/python3.11/site-packages/hplc_py/quant.py", line 643, in deconvolve_peaks
    popt, _ = scipy.optimize.curve_fit(self._fit_skewnorms, v['time_range'],
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jonathan/Library/Caches/pypoetry/virtualenvs/wine-analysis-hplc-uv-F-SbhWjO-py3.11/lib/python3.11/site-packages/hplc_py/quant.py", line 772, in fit_peaks
    peak_props = self.deconvolve_peaks(verbose=verbose,
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/peak_deconv/peak_deconv_2.py", line 52, in main
    chm.fit_peaks(approx_peak_width=0.6)
  File "/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/notebooks/peak_deconv/peak_deconv_2.py", line 83, in <module>
    main()
  File "/Users/jonathan/.pyenv/versions/3.11.1/lib/python3.11/runpy.py", line 88, in _run_code
    exec(code, run_globals)
  File "/Users/jonathan/.pyenv/versions/3.11.1/lib/python3.11/runpy.py", line 198, in _run_module_as_main (Current frame)
    return _run_code(code, main_globals, None,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: `x0` is infeasible.
```

On investigation, one of the elements of `x0` is less than the defined lower bound for that feature. It appears to be feature 6. There should only be 4 features per bound array... there is, but the peaks for each window are flattened, thus the bounds are a repeating series of:

0: amplitude
1: location
2: scale
3: skew

So if its the 6th element that is the problem, then its scale.

2023-11-20 19:14:01 - the error appears to be occuring in the 2nd window.

2023-11-21 08:56:11 - This is where we are - sample: "10_2021 john duval wines shiraz concilio" is causing a initial guess of the scale to be lower than the estimated lower bound. Specifically the lower bound is 0.03 repeating, and the initial guess is 0.03060128, a difference of -0.00273205.

Going to the source of the guess and the bounds will be the next step. I also believe that it is the second window which is causing this.

2023-11-21 09:13:35 - trying now with another sample, 111. The same phenomenon of non-continuous window labeling is occuring here too. Specifically with a window size of 0.8, region two occurs in both between 4 and 5 mins and again at 20 - 24 mins. 

2023-11-21 09:34:53 - but then going back to sample 0 that is not occuring until the window size is below 0.8.

Q: What causes the double labeling to occur?

There is no double labeling, they are just using different index ranges for 'interpeak' and 'peak' within the same window df (fuuuuckin questionable) thus if you group by window idx without including the 

Q: Is that causing the scale guess to be lower than the lower bound?

As we can see in the answer to "Q: How is the scale bound and guess calculated?", the initial guess width is calculated as the width / 2 in time units. Thus the measured width of a peak needs to be less than double the sampling frequency, or fucking small.

Q: What is a reasonable `approx_peak_width` value?

from `peak_deconv_2.estimate_peak_widths` the average peak width of 111 is 6.89 observations, or 0.23 mins, which matches visual inspection.

Q: is `approx_peak_width` in time units?

Yes, `approx_peak_width` is the `window` parameter of `correct_baseline`, from the docs it is expressed in dimensions in time. Within the `correct_baseline` function the number of iterations is derived from the inputted window as: `int(((window / self._dt) - 1) / 2)` which is the same as saying the magnitude of samples minus one divided by 2. Why? I dont know.

Q: How is the scale bound and guess calculated?

The guesses are calculated as follows:

amplitude: amplitude of the peak
location: peak location
width (scale): width / 2
skew: 0

bounds are as follows:

amplitude:

lb = 0.1 * amplitude
ub = 10 * amplitude

location:

lb = minimum of time range
ub = maximum of time range

scale:

lb = sampling frequency
ub = (time range max - time range min)/2

skew:

lb = -inf
ub = +inf

So as we can see the issue is that the guess for scale is less than the sampling frequency. What is `window_property['width']`?

window_property['width'] - set as:

`_widths[ind]*self._dt for ind in peak_inds`

`_widths` is the widths in sampling units outputted by `scipy.signal.peak_widths`. `self._dt` is the sampling units. thus `window_property['widths']` is the peak width in the time unit.

In summary..

``
In `_assign_windows`

1. peak widths are found via `scipy.signal.peak_widths`

In `deconvolve_peaks`:

1. widths are converted to time units by multiplication with the sampling freq.
2. width/scale initial guess is defined as the width / 2
3. lb is defined as the sampling frequency
4. ub is defined as: `(window_time_range.max()-window_time_range.min())/2`
5. bounds are passed to `curve_fit`

In `curve_fit`

1. bounds are passed to `least_squares`

In `least_squares`

1. guess is checked against lower and upper bounds to see if in bounds
2. bounds are passed to `trf`

Thats it for transformations.

---

2023-11-21 13:24:50

I need to recreate the problem and identify which specific peak is causing the problem.

2023-11-21 13:33:19

Done, ive established a try except which catches the in bounds error then returns the window number and peak idx alongside the erronous value. What we can see is that the problem is the lower bound of peak 4, which has an initial guess of 0.029991, a lower bound of 0.033333, and thus a difference of -0.003342.

This is with an approximate_peak_width of 1. I estimated that the mean peak widths for this sample were 0.23 mins. Lets plug that in and see what happens.

That actually triggers another error, where now the upper bound of the width is smaller than the lower bound. Again the lb is simply the sampling frequency, and the ub is half the time range.

Going back to the default value of 5 Results in very big windows but the same result of a lower bound lower than the initial guess.

Ok, well at this point it is clear that something is going wrong with the initial guess calculation. Need a sample that actually goes right as a sanity check.

2023-11-21 14:00:43

The documentation suggests that the bound values can be overridden if nessary. For example we just need the lower bound to be 10% smaller.

2023-11-21 16:06:12

After much pain I've managed to get the `param_bounds` parameter working - requires 'scale', rather than 'width', and takes a list of ['lower','upper']. Problem is that as the ratio (`default_width`*ratio) approaches zero, the difference between the guess and lb get smaller, until a new warning occurs:

"warnings.warn('Covariance of the parameters could not be estimated',".

On further investigation of the window properties, we've identified that for example a peak area of 0.25, the peak width of the peak in question is 0.0333333.., or equal to the time step. Increasing `approx_peak_width`

2023-11-21 18:06:34
  
Ive now produced a report df that collects the parameter values for each peak in each window and concatenates them after failure to curve fit.

Now do the same for window properties.

Note: window properties consists of the times of observation, signal, signal area, number of peaks, peak amplitude, location and width for each window in the signal. Converting 'window properties' to a df then making it available in the same way as earlier will enable me to compare the failed peak and the overall windows.

There is also window df.

2023-11-22 10:00:13

Ok so we've ascertained that there was no double labeling, just that the `window_id` index range started again for interpeak and peak rows. Thats one question eliminated.

I think im at a dead end. Lets recreate the problem then post another issue.

2023-11-22 10:15:48 the upper bound I inputted yesturday is way too big, with a value of 26.96. The reason was that I need to calculate it on a peak by peak basis and I was calculating it for the entire signal.

The problem with the 'default' value interface is that for the widths it replaces the values entirely, losing all the nuance of a custom-fit value. Can we just adjust the lower bound calculation?

2023-11-22 11:46:49 - we can, but it resulted in another error - time range upper bound is intruded by the guess at peak ~30.

On reflection, the approx peak width setting of 0.23 is overfitting too much. going back to 0.7 gives a much smoother baseline.

At this point, Im going to migrate to my fork of hply_py and continue work there, I need VCS if im going to make more mods.

2023-11-24 13:17:53 continuing from hplc_py notes, I need to generate the same data - oriada 111, but the raw data not processed.

2023-11-22 13:18:32

Continuing on from XGBoost notes. Have heavily refactored the hplc-py package for clarity of function and debugging. But still getting the same infeasible error. Time to build a bug report.

I need to extract the state of the window that is causing the error. That means:

current window index
current peak index
current bounds
current guess

This should be a class.

2023-11-22 15:06:32

Report class 'WindowState' done and operational.

From the report we can see that the second window 4th peak is causing the problem. Can we also generate a plot of the signal?

Thats done from window df, but could also be done from window report..

2023-11-22 15:29:12 - observing peak 4 of window 2, there is no obvious cause for the erronous width allocation..

2023-11-22 19:12:30 I have generated a joined table with all information relevant to a peak and peak window for output. I have also produced a plot display of the id'd peaks in a window, and the estimated widths, in order to gauge how its getting it wrong.

From this we can see that peak 2,2 (window two, peak two) is almost completely subsumed by peak 2,1

2023-11-23 00:12:42 - the window in question is ~1.9 to ~4.9.

first question:

Q1: what happens when we run window 1 only?

Q2: can we tweak window two in such a manner that the peak width is better estimated? The width should be somewhere between..

2023-11-23 23:58:35

There is an abundance of information about the fundamentals of peak deconvolution, namely [this](http://emilygraceripka.com/blog/16) post from Dr. Ripka. There is also a series of detailed tutorials by the University of Maryland [here](https://terpconnect.umd.edu/~toh/spectrum/SignalsAndNoise.html).

From this and the `hplc-py` code we can deduct that `scipy.signal.peak_widths` is the problem, it is underestimating the width of peak (2,2). Sharpening the peak may increase the measured width enough to get it over the default bound. Furthermore, following Ripkas example we could create our own fitting regime, at least to understand the problem.

First thing i need to do is to extract the signal then apply a sharpening filter ( which it appears I will have to define), then experiment with `peak_widths`.

The window is from 2 to 4.5.

2023-11-24 08:59:17

so sharpening the peaks is resulting in a pretty good fit for the majority of the peaks, however we're encountering an undefined error in the first 2 min region, and some of the seriously overlapped peaks in the later areas are not well fit because not all of the component peaks are being detected so the peak that is is being modelled as very skewed. Need to find a compromise. Got all the moving parts here, just need the right combination.

~~2023-11-24 10:02:51 I am trying to produce a subplot of `chm.show()` cut into bins to display different regions. To do this I have had to modify the function to accept a fig and ax object to plot on, and now I have encountered an interesting issue - the output of `fit_peaks` is not de-normalized. Im not sure if thats by design or not, but we should add it in. Best way to do that will be to define the inverse of the normalization function.~~

2023-11-24 12:07:44 - the answer is that the peak df is not peak properties, it is the best fit values. In the case of amplitude it appears that even though the documentation states that it is the amplitude maxima, it appears to be the amplitude of the centroid. I suppose the authors didnt think that the true amplitude was worth reporting when the area is of more interest. How can I get the peak amplitudes? From the reconstructed signals.

2023-11-24 12:38:19 - have added peak maxima to `peak_df` and stored `unmixed_chromatograms` as a DF with the peak id as columns and retention time as index.

2023-11-24 13:11:22 - have pushed all recent modifications to remote. Now to look into optimizing the fit. We've still got the problem with 0 - 2 mins to solve as well..

I want to start over with the raw data prior to resampling and see if that has any effect on the results. To do that best thing will be to install my branch in my main project.2023-11-22 13:18:32

Continuing on from XGBoost notes. Have heavily refactored the hplc-py package for clarity of function and debugging. But still getting the same infeasible error. Time to build a bug report.

I need to extract the state of the window that is causing the error. That means:

current window index
current peak index
current bounds
current guess

This should be a class.

2023-11-22 15:06:32

Report class 'WindowState' done and operational.

From the report we can see that the second window 4th peak is causing the problem. Can we also generate a plot of the signal?

Thats done from window df, but could also be done from window report..

2023-11-22 15:29:12 - observing peak 4 of window 2, there is no obvious cause for the erronous width allocation..

2023-11-22 19:12:30 I have generated a joined table with all information relevant to a peak and peak window for output. I have also produced a plot display of the id'd peaks in a window, and the estimated widths, in order to gauge how its getting it wrong.

From this we can see that peak 2,2 (window two, peak two) is almost completely subsumed by peak 2,1

2023-11-23 00:12:42 - the window in question is ~1.9 to ~4.9.

first question:

Q1: what happens when we run window 1 only?

Q2: can we tweak window two in such a manner that the peak width is better estimated? The width should be somewhere between..

2023-11-23 23:58:35

There is an abundance of information about the fundamentals of peak deconvolution, namely [this](http://emilygraceripka.com/blog/16) post from Dr. Ripka. There is also a series of detailed tutorials by the University of Maryland [here](https://terpconnect.umd.edu/~toh/spectrum/SignalsAndNoise.html).

From this and the `hplc-py` code we can deduct that `scipy.signal.peak_widths` is the problem, it is underestimating the width of peak (2,2). Sharpening the peak may increase the measured width enough to get it over the default bound. Furthermore, following Ripkas example we could create our own fitting regime, at least to understand the problem.

First thing i need to do is to extract the signal then apply a sharpening filter ( which it appears I will have to define), then experiment with `peak_widths`.

The window is from 2 to 4.5.

2023-11-24 08:59:17

so sharpening the peaks is resulting in a pretty good fit for the majority of the peaks, however we're encountering an undefined error in the first 2 min region, and some of the seriously overlapped peaks in the later areas are not well fit because not all of the component peaks are being detected so the peak that is is being modelled as very skewed. Need to find a compromise. Got all the moving parts here, just need the right combination.

~~2023-11-24 10:02:51 I am trying to produce a subplot of `chm.show()` cut into bins to display different regions. To do this I have had to modify the function to accept a fig and ax object to plot on, and now I have encountered an interesting issue - the output of `fit_peaks` is not de-normalized. Im not sure if thats by design or not, but we should add it in. Best way to do that will be to define the inverse of the normalization function.~~

2023-11-24 12:07:44 - the answer is that the peak df is not peak properties, it is the best fit values. In the case of amplitude it appears that even though the documentation states that it is the amplitude maxima, it appears to be the amplitude of the centroid. I suppose the authors didnt think that the true amplitude was worth reporting when the area is of more interest. How can I get the peak amplitudes? From the reconstructed signals.

2023-11-24 12:38:19 - have added peak maxima to `peak_df` and stored `unmixed_chromatograms` as a DF with the peak id as columns and retention time as index.

2023-11-24 13:11:22 - have pushed all recent modifications to remote. Now to look into optimizing the fit. We've still got the problem with 0 - 2 mins to solve as well..

I want to start over with the raw data prior to resampling and see if that has any effect on the results. To do that best thing will be to install my branch in my main project.

2023-11-25 15:31:10 - I have reached a deadline. I need to move onto to modeling the data, which means I need to conclude fine-tuning modeling of data. Thus I need an automated method of managing the deconvolution pipeline, that is, the deconvolution of samples as they are inputted, and whose interaction with the modeling is currently undefined. Generally we're expecting out of bounds initial guesses due to lack of peak definition, but other issues such as windows being too large may occur as well. Realistically we need windows to contain less than 10 peaks, as more than that appears to cause the optimization to run for an inpractical amount of time.

So, to automate that process we need to define the following:

- what constitutes a successful deconvolution?
- how do we handle errors?
- how do we monitor the process?
- how do we report outcomes?

A successful deconvolution will simply be one without errors that takes less than a minute to run, and within the bounds of defined number of attempts before erroring out.

So that needs:

- monitor number of peaks in a window - if more than 10, abort the attempt. this means we need to contain the window assignment to a separate process. That means we need to produce a means of monitoring exactly what is guiding the window assignment.
- A timer: 1 minute countdown.
- iterator limit - if exceeded, error out.

We will need to establish a grid search for both the window assignment and deconvolution. How can I implement one? We say grid search, we mean a combination of hyperparamters. Then we jsut need to iterate through the parameters (preferably random) and measure the outcome.

Problem Breakdown:
1. baseline correction - optimal = smooth as possible while maximising number of inflection points with a zero minima.
 1. hyperparameters?
 2. optimization metric?
 3. viz - plot of the raw, plot of the projection, plot of the correction
1. window asignment - optimal = 4 max peaks per window.
  1. hyperparameters?
  2. Output - the assigned windows along the time axis, say 5 bins.
  3. Output - display of the algorithm finding the windows (however that works)
  4. Implement - while mean ratio window/peak < 0.25, continue
2. Observe and control peak deconvolution - optimal = completes in less than 1 minute.
  1. hyperparameters?
  2. viz - `Chromatogram.show()` again binned into ~5.
  3. if error, viz of error param, say scale, show the measured width vs the minimum centered on the peak, amp the same etc.

Grid search - take all the parameters as dicts, calculate the combination without repeats. [more itertools](https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.distinct_combinations) has `distinct_combinations` for that purpose.

Ok. Lets do this.

Baseline correction first.

2023-11-26 00:42:16 - Looking at the hplc-py code again, a major issue has been coupling between the methods, going off some of the basics of the SOLID principle, i will convert all methods to take the df as input rather than depending on an internal object, thus the df can be monitored internally, and also manage internal passing of the data. also, i will instantiate the baeline correction, window assignment and fit peaks classes as objects of Chromatogram, rather than inheritance, providing a namespace between the three modules. this should further aid in decoupling the modules and providing clarity of function.