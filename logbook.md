# Logbook

2023-08-10 07:34:07: have moved this project logs to this file as opposed to "mres_logbook.md". A Jonathan with more time than me can get busy moving relevant sections here.

## pivoting db tables

[link](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py)

## Pivoting DB tables

I will developing a module/query to pivot db tables [here](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py).

the following call produces an acceptable sample set:

``` python
get_data.get_wine_data(
        con,
        samplecode=('124', '130', '125', '133', '174'),
        wavelength=(450,),
        color=('red',) 
    )
```

i am working with a long 'wine_data' table with columns 'wine', 'mins', 'value'. each of the rows is an observation of a 'wine' sample with 'wine' as the primary key. 'mins' and 'value' are numerical columns. 'mins' always ascends from 0 to roughly 54.0, 'value' is variable and contains the intensity values of the instrument recording the signal.

I would like to add an 'obs_num' column to each sample in the long table based on a groupby of the 'wine' column where the 'obs_num' starts at min('mins') and ascends by 1 per row as 'mins' ascends, with the last 'obs_num' value at max('mins')

2023-08-10 09:28:37

To add row numbers to the long table to act as an index for the pivot:

``` sql
SELECT
  wine,
  mins,
  value,
  ROW_NUMBER() OVER (PARTITION BY wine ORDER BY mins) AS obs_num
  FROM wine_data;
```

Ok, so a pivot was achieved with `pivot_wine_data()` [here](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py).

Its a single wavelength, and no minutes. Its too conceptually difficult to continue to persue this in SQL. In the interest of time, I will instead look at batch extraction, or other means of reducing the memory cost.

That being said, this is blazingly fast to return results and produce plots.

2023-08-10 10:51:23

Ok, now that I've established the basis of some tools for working with these large datasets I will go back to working on the preprocessing pipeline.

The wine set i will work on is the same one as above.

Fist step is to produce the dataframes in an appropriate format to work on. This has been achieved by modifying the `pivot_wine_data` function in pca module to produce a dataframe with a heirarchical index of ('wine', \['mins', 'val'\]).

2023-08-10 16:57:19

Getting there. With the help of user **Alex** ive got a method of pivoting the tables out in duckdb prior to moving to Python, making everything lightning fast. However, working with multiindexes is a goddamn pain, and i need to learn how to do that better. Also extracting 'obs_num' with the pivot would be v useful, but currently dont seem to be able to.

[pivot_wine_data](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py) will need a big clean up before we can proceed really, but we're still testing it.

It currently looks like ive still got duplicates in the set somehow, specifically:

98 2020 barone ricasoli chianti classico rocca di ... mins 0 value 0

Which is forcing the dataset to be twice as long as it should be. 72 2021 de bortoli sacred hill cabernet merlot mins 5712.

## Sequence Alignment

2023-08-13 12:19:38

The first stage of the preprocessing pipeline is sequence alignment, specifically Multiple Sequence Alignment (MSA). This is necessary because the chromatograph can have a variation in observation points. What is the variation in observation points?

db long table pivot wine data test: To debug the too long pivot table, try swapping `sample_code` out for `id`, a possibly more reliable primary key.

## Justification of need for MSA

For a time series $y = f(x)$, MSA aligns $x$ of all sequences determined to be related so that they all experience the same variation (none) from the input, and thus all output variation is contained within $f(x)$ unique to that signal.

From what I've seen so far (very little) it is a concern if observation frequencies differ, or start and stop at different times. In my dataset the observation time points differ minutely, and thus the question of whether it is necessary to undertake MSA can be raised. A first touch check of whether I need to could be to observe the point-by-point variance across the included time series. Frankly I'll need to do further research on both time series statistics and MSA.

TODO:

-   [x] identify issue with too long sample.
-   [x] write pivot table test
-   [ ] summarise @brown_2020c 3.05
-   [ ] annotate @brown_2020 3.06 (and make book section item to cite)
-   [ ] research Savitzky-Golay smoothing
-   [ ] research MSA
-   [ ] research time series statistics
-   [ ] restore use of peak alignment module with current data format

## Too long pivot table exploration

Changing samplecode to id has not fixed it. Again, lets identify the culprit.

[This](solve_too_long_pwine_data.ipynb) is a jupyter notebook in which I will perform investigations to determine the cause of these errors.

2023-08-15 07:43:17 Solved - 98 was run on an older method resulting in different run parameters, 72 is an algamation of two samples, only one of which is still in sampletracker. This is layover from when I was validating the avantor column. 98 can be straight up dropped, not worth it to validate the method. 72 is slightly more difficult, but I think ill just drop it too. They have been removed by excluding them from the `get_data` query `AND ((SELECT UNNEST($samplecode)) IS NULL OR st.samplecode IN (SELECT * FROM UNNEST($samplecode))) AND st.samplecode NOT IN ('72','98')`. The [notebook](solve_too_long_pwine_data.ipynb) is now broken because the target samples are no longer retrieved by `get_data`, but if I found a way of making that exclusion optional then it could work again. Not worth the time to worry about atm though.

## Introducing Injection Volume Into the dataset

One factor I overlooked is that the injection of my CUPRAC samples differ, initially they were set to 10uL but after issues with precipitation it was dropped to 5uL. This will affect the heights of the samples as per beer-lambert law. So to adjust for injection volume I need to get the injection volume measurements from the .acaml file, add it to rainbow, and rerun the pipe. Its good to rerun it anyway, keeps it from going stale, so to speak.

2023-08-15 08:47:14: The injection volume can be found in .D/acq.macaml at the XPath `/ACAML/Doc/Content/MethodConfiguration/MethodDescription/Section/Section[3]/Section[4]/Parameter[5]/Value`.

2023-08-15 09:06:02": Problem - Injection volume is stored in `acq.macaml`, which is currently not parsed by rainbow. The secondary problem is that `parse_metadata` is setup to only read from one type of file, with a case-like setup of serial IF clauses each with their own return statement. My solution will be to add a `acq.macaml` parse as the first block within `parse_metadata`. This way we will avoid changing the logic.

2023-08-15 12:20:37: Got it. The generated xpath was incorrect, it should have read: `/MethodConfiguration/MethodDescription/Section/Section[1]/Section[2]/Parameter[2]/Value` Had to manually locate it by starting with a root xpath and iterating through the returned children, adding more to the path and iterating again until i reached my goal. I have added some documentation, a test based on previously generated 094.D metadata, have commited and pushed. Now I will generate a library in a new db and check the injection volume distribution. 2023-08-15 15:36:47: Testing the modifications on my dataset through chemstation tests (which have been updated as pytest format and added to tests dir) have revealed that the xpath developed from 094 is not universal. Fun. I will now try to develop one for 116.D 

2023-08-15 17:28:17: Ok, for a set of 4 DD (data dirs .D) I have shown that half of them work with the 116.D xpath, and half with the 094.D. Since both 116.D and 094.D are in the sampleset.. thats not really saying much. Time to expand it to the full set.

2023-08-16 13:10:20: Discovered that there were at least 5 different absolute xpaths to Injection Volume depending on the sample in question. Scrapped absolute paths for a relative approach based on `.findall()` and filtering by parameter. This approach has been verified on the whole dataset, tested and commited. The results of this study are [here](tests/testing_inj_vol.ipynb), awhere we found that no CUPRAC samples in the current dataset were collected with a 10uL injection volume. It was good to verify though. 2023-08-16 14:38:30: `build_library` has been validated, rerun with injection volume update. verified, changes have been commited. Back to.. whatever i was doing?

## MSA

### MSA reading notes

| @listgarten_2004 | A MSA study proposing a novel HMM model with an example of application on TIC LC-MS 2D signal dataset.|

## Revitalizing the peak alignment pipe

[The peak alignment pipe](src/wine_analysis_hplc_uv/signal_processing/peak_alignment/peak_alignment_pipe.py) has been revitalized using a mock dataset shaped into the same structure as the pipe originally expected. tHis has been done to then rewrite the pipe to match the new multiindexed approach. While working on this though I started wondering about dataframe schema validation for pipes, a solution to the ever-present problem of how to ensure the input of a pipe is appropriate for it. Turns out many others have encountered the same problem, and that there many dataframe validation packages out there, including [pandera](https://pandera.readthedocs.io/en/stable/index.html). It looks promising, but perhaps overkill. Specifically, in order to handle a variable number and name of columns, they would need to be regex-matchable, as as [described here](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html#column-regex-pattern-matching).

So I think we'll write a prefunctory validation function based on the properties of the multiindex. Specifically, we're talking about the dataframe resulting from the `pivot_wine_data` function.

2023-08-22 11:42:11: lets peel it back even more than that. Just make sure the multiindex names are correct.

2023-08-23 09:52:28: Multiindex dataframe validation has been established as `check_dataframe_props`, currently stored [here](tests/test_preprocessing/test_baseline_subtraction.py). It checks that the column index level names match expectation, and that for the vars level, the columns ['mins','values'] are in the right order for X number of sample columns. There is also a list of TODO features to add to make it more specific.

2023-08-23 13:47:09:

The time has come to adapt the rest of the peak alignment pipeline, however, the first thing to do is to produce a sample dataset. Operations like the baseline calculation are very time-consuming, so decimation is key to a quick development cycle. Ideally it will be a process that will decimate from the baseline as much as possible while preserving all peaks. I should develop this in a jupyter notebook where I can also place my notes about decimation processes.

## EDA decisions

I have reached a point where I need to start keeping a formal track of decisions made during EDA. These will be kept the [README](README.md#eda-decisions), with links to the associated notebook justifying the decision.

## Time axis offset

I have discovered that each samples time axis reliably follows a frequeny of 2.5Hz (assuming that is the setting), but is offset by a specific value given by the first value. Subtracting the first value from every value in the time axis column corrects the offset so that every observation is now at the same time value. Refer to [this notebook](./notebooks/determining_time_axis_offset.ipynb) for the specifics and proof.

## Higher dimensional dataframe plotting

To plot 2D data in a high-dimensional (multiindex columns) dataframe, need to shed the higher level labels to be able to refer to the specific columns, i.e. 'mins', and 'value'. In a pipe:

```python
...
.groupby(['level1','level2',...,'leveln'],axis=1)
.apply(lambda grp: display(grp.droplevel(axis=1, level=['level1','level2',...,'leveln']).plot(x='colx',y='coly')))
...
```

## Time Series Characterization and Compression

2023-08-29 10:50:22

My experiments to characterize the time axis of my dataset and develop some unification methods has resulted in a OOP API for time axis unification [here](src/wine_analysis_hplc_uv/signal_processing/mindex_signal_processing.py). The report can be found [here](notebooks/time_series_characterization_and_compression/time_axis_characterisation_and_compression.ipynb).

The long and short of it is that all the time series require a small amount of adjustment prior to higher level processing, and that it is feasible that a 80% compression size across the datasets can be achieved.

In the interest of speeding up development, I should consider processing the entire dataset and storing it in a seperate database file, as the compression will drastically increase extraction time.

In the meantime I will continue with my adaption of the peak alignment module to mindex format.