creation-date : 2023-05-05-11:42:56
mod-date : 2023-05-05 11:42:56
tag : 2023, mres, logbook
alias :
---
# MRes Logbook

## Links

[mres homepage](../../001_obsidian_vault/homepages/homepage_wsu_research.md)
[dp paper logbook](../../001_obsidian_vault/mres_logbook/dp_paper_logbook/dp_paper_logbook.md)

<!--  contents -->

## Content

### 2023-05-05

#### Spectra Preparation Prior to Calculation of Euclidean Distance

[observing_spectra_shape_variation](../../../wine_analysis_hplc_uv/prototype_code/observing_spectra_shape_variation.py)

2023-05-06 00:17:44

To apply Euclidean Distance to measure the similarity of two 1D-arrays, the matrices need to be the same size. Thus I need to build a validation and broadcast function prior to every calculation of the distance.

Is it better to broadcast all spectra matrices to the same size before calculation, or pair-wise? For a meaningful result, should avoid broadcasting. Frankly, I need to understand how different the sizes are. Problem is, if I broadcast one, that will significantly increase the magnitude of the distance. Probably better to subset.

To observe the distribution of size differences:

1. Get all sample matrices.
~~2. Form a sequence of pairs of chromatograms without reversable repeats.~~
~~3. iterate through that sequence, for any whose shapes dont match, return the sample names and the shapes.~~

Wrong. Best approach is to get a Series of matrix shapes.

2023-05-06 01:32:40 done. Now to build safeguards. Apart from debertoli it appears that one or two matrices have one more observation than the majority. presumably just a glitch in the machine. To select those which are not like the norm, I will find the mode of the shapes and use that value as the reference. If a matrix is larger than the mode, I will trim it from the end to match the mode shape. If it is 10% less than the mode, I will broadcast with the last recorded value. If it is >10% less than the mode, I will alert the user who can then choose to include or exclude those samples from the selection.

todo:
- [x] calculate mode of matrix shapes.
- [x] implement trim to mode shape function.
- [x] implement pad.
- [x] implement user warning and pad for samples >-10% of mode.

<!-- 2023-05-06 18:32:04 ended up implementing a mode and deviation table, see mres_logbook 2023-05-06-->

#### Further Thoughts on Implementation

2023-05-06 10:15:46

The problem with this implementation so far is that I have been focusing only on the row size, while talking about shape. I need to acknowledge that I am only concerned about row counts at this point, not column counts. Thus I should refocus my code to make this explicit.

I also dont actually know how to implement a subsettnig or padding. Should look into this before writing more code.

I can implement subsetting, or trimming or whatever you want to call it, through slice notation. i.e. [:max_length] where max_length is an integer.

But what about padding? It appears that pd.DataFrame.reindex can be used by defining extended index and columns, then reindexing the dataframe on those with argument `fill_value` = 0.

2023-05-06 11:43:10

Padding is done.

Current workflow is:

1. Get all sample matrices.
2. Get shapes of matrices as a df with index of sample names.
3. rehape the matrices to match the library mode.

Now need to implement the variation test.

1. find all samples whose shape doesnt equal the mode.
2. print their shape.

### 2023-05-06

2023-05-06 14:46:56

first day of the new logbook format. At some point i'll go back and add the old logbook pages in. Today I am in the lab running the 4th freezer runs. I am also working on calculating Euclidean distances of spectrum-chromatogram matrices [here](../prototype_code/observing_spectra_shape_variation.py). While doing this, I have found at least one run that had >11% of the mode of the selected runs. i.e. an aborted run. This raises the question of how many more there are in the dataset.

The function dim_size_deviation_report, currently in  observing_spectra_shape_variation, which is being developed to support the calculation of euclidean distances between SC matrices, will be very helpful in verifying the shape of these matrices. The shape is important because most all matrix operations require that matrices be the same shape.

Anyway, I'll track that aborted run down and expunge it from the library. To do this I'll make sure the filepath is included in the super_table query so it carries through to the report.

The offending file is: "~/0_jono_data/2023-03-14_2021-debortoli-cabernet-merlot_avantor_3.d". I'll just manually delete it from both instrument and local storage.

2023-05-06 15:41:09

Done. No other anomalous runs appeared, so it looks like we're good to proceed. The next stage is to verify the reshape function.

2023-05-06 15:48:21

verified. What now? Now I need to go back to peak_alignment_spectrum_chromatograms and see what we're up to.

2023-05-06 15:59:07

Have introduced observing_spectra_shape_variation.observe_sample_size_mismatch into peak_alignment_spectrum_chromatogram.peak_alignment_spectrum_chromatogram.

Correlation matrix has been 'successfully constructed, however all pair distances are equal to zero. Problem.

2023-05-06 16:42:50

All sc matrices are filled with zeroes. presumably the resizing function is not putting the original values back in.

2023-05-06 17:05:38

The offending line of code was in observing_spectra_shape_variation.reshape_dataframe:

```python
else:
        new_columns = range(desired_columns)
  ->   df = df.reindex(columns=new_columns, fill_value=0)
```

THe full block does the following:

if no 'desired_rows' provided:
    desired_rows = num_rows of current dataframe

if no 'desired_cols' provided:
    desired_cols = num_cols of current dataframe

if desired_rows < num_rows current df:
    slice df to length equal to desired_rows
else:
    1. make a new index equal to a range of length desired_rows
    2. reindex the df with new_index, fill with zeroes.

Looks lke it should work, however it is causing problems. Since there is no instance where there will be less columns (for now) ill leave it commented out and move on.

2023-05-06 17:39:46

Ok, wine_analysis_hplc_uv repo is up to date..

So the calculated distance values are huge, like 5 digit numbers. It migh be nicer to normalize the absorbance axis to reduce the absolute magnitudes. But how do I do that? Also what is the units of the Euclidean distance? probably the units of the vector.

I will add a normalization of library function here[label](../prototype_code/peak_alignment_spectrum_chromatograms.py) "normalize_library_absorbance"

2023-05-06 18:02:54

Done. Program is running a bit slow considering there are only 5 samples though, should investigate chokepoints with @timeit.

Looks like its the normalization block. Wonder why.

Fixed. Shouldnt be surprised that applymap methods are slow. Replaced with MUCH faster select_dtypes method.

2023-05-06 18:23:45 

#### 2023-05-06 End of Day Summary

What now?

THe fourth freezer run is about to finish, and next I will be initialzing yet another ambient run.

I've run out of time today, and I cannot come in tomorrow as I have other things to do.

On monday I will run the remaining UV/vis samples then swap to PCD on Tuesday.

In the meantime, regarding data processing, we need to verify what the l2 norm matrix is looking at, i.e. where in the pipeline we are. Once verified, need to write a method to pickle the l2 matrix.

Really need to create a DA pipeline / project outline in the homepage that I can refer to. starting to get lost/distracted, need to keep my eye on the ball. Be good to spend half an hour collating project notes from the logbook and etc.

From [dp_paper_logbook](../../001_obsidian_vault/mres_logbook/dp_paper_logbook/dp_paper_logbook.md) Paper Progress - Narrowing the Scope, the current focus is to compare the euclidean distances of samples before and after peak alignment. This should be done within the peak alignment pipeline. What should be done? To start with, display the  euclidean distance matrix before and after alignment.

### 2023-05-08

2023-05-08 10:47:40

Last day of UV/vis.

Todo:
- [x] methanol flush.
- [ ] freezer runs.
- [ ] ambient runs.
- [ ] library sample runs.


#### Realising that the 44min runs arnt at 2.5%

Have realised that the '44min' method was actually at a 3.16(...)% gradient, NOT 2.5%. Great.

Lucky it appears that only the wine degredation study and samples 96 - 100 are affected by this. Now considering that the differnce in gradient isnt HUGE, there is still a potential to align the signals, saving this data. The CUPRAC portion of the wine deg study will need to be run 3.16(...)%/min gradient.

#### 44 min 3.16(...)%/min gradient timetable

|  min  |  A   |  B
-|-|-
| 00:00 | 095% | 005%
| 30:00 | 000% | 100%
| 32:00 | 000% | 100%
| 34:00 | 095% | 005%
| 44:00 | 095% | 005%

#### How to Calculate Gradient

To make it clear, a gradient elution method % gradient should be calculated at the time point prior to the time point where methanol is set to 100%. I.E in the table above, the gradient is calculated at 30 mins, where the difference is from 5% to 100%, or a 95% increase. 95% over 30 mins = 95/30 = +3.16(...) % / min.

Now, in the wine deg, for these samples, we want to cut it at 24 mins rather than 30, or 6 minutes earlier.

y = mx+5 where y is the % methanol, and t is time.

#### 24 min 3.16(...)% / min Timetable

at 24 mins, 3.16(...) = 81% methanol at that time point.

|  min  |  A   |  B  
| 00:00 | 095% | 005%
| 24:00 | 019% | 081%
| 25:00 | 000% | 100%
| 27:00 | 000% | 100%
| 29:00 | 095% | 005%
| 39:00 | 095% | 005%

#### Method Update

2023-05-08 12:20:40

New method setup as per timetable above '~\0_jono_methods\0_H2O-MEOH-2_5_37-MINS.M'. Will be using it for the remainder of the deg study. For CUPRAC, will have to set up one with isocratic pump timetable as well.

Speaking of CUPRAC, will have to produce the new samples tomorrow as well. big day.

#### Getting back to It

Last week we [left off](#2023-05-06-end-of-day-summary) finishing up the L2 norm similarity matrix. We need to:

- [ ] make a clear data processing pipeline.
- [ ] Run the full L2 norm matrix module to see how long it takes to run.
[[]]
Once that's done, focus again on the dp paper. After lunch review where we're at with the outline and make a todo list for the week.

First though, I need to revig a project structure. The heirarchy will be:

homepage -> mres -> project -> sub-projects.

[[homepage]] -> [[homepage_wsu_research.md]] -> [[homepage_wine-analysis.md]] -> [[homepage_paper-data-processing-for-chemometrics.md]]

So the homepage_wine-analysis is in ~/wine_analysis_hplc_uv/notes/ but is soft linked in ~/001_obsidian_vault/homepages/ so its visible there too. I am going to move mres_logbook to wine-auth_logbook.md in wine_analysis_hplc_uv/notes/ and add another symlink to its original location.

#### Data Processing Pipeline

We do have the [build_library](../prototype_code/build_library.py) file, but that is intended for database initialization prior to data processing, i.e. phase 1. There are multiple phases to this project and the overall project code will reflect that:

Phase 1: Data Collection and Preprocessing
Phase 2: Data Processing
Phase 3: Data Analysis
Phase 4: Model Building
Phase 5: Results Aggregation and Reporting

Phase 1: is covered by build_library. Need a superstructure file. call it "core.py". It can be the main driver. It is [here](../core.py)

The reason this stuff is needed is because without a heirarchy the project is flat and its uncertain where it begins and finishes, so to speak.

#### Peak Alignment Module

peak_alignment.py has been renamed to peak_alignment_pipe.py, just to better reflect its nature, and aspects of it have been refactored to make it more modular.

##### Acq Date Problem

2023-05-08 15:22:25

Apparently for all the samples I selected to test code on, they all have the same acq_date timestamp, being 2023-04-04 00:00:00.000. Looking at the database super_table acq_date column shows that the lack of HH:MM:SS is consistant across all samples, but the dates do vary. I guess all of these samples were run on the same day.

I will need to investigate why the HH:MM:SS is empty, but its a sub-priority for now. Would definitely be useful for the wine deg analysis..

#### Adding normalization to Peak Alignment Pipe

For the samples:

| #  | wine |
-|-
|  0 | 2021 stoney rise pinot noir              |
|  1 | 2020 yangarra estate shiraz mclaren vale |
|  2 | 2022 alkina grenache kin                 |
|  3 | 2021 babo chianti                        |

The peak alignment is causing a change in the absorbance axis as well as the time axis. Which was not expected. To observe this better I will integrate peak finding into the graphical display.

I desire to have each peak maxima marked on the display, with a hover of its x and y value and peak idx in order from 0 to n.

#### CUPRAC

2023-05-08 18:52:55

1:1:1 mixture

1 M ammonium acetate in water
7.5 mM neocuproine in methanol
10 mM copper chloride dihydrate in water

1. weigh each reagent out for desired final volume.
2. dissolve each, should dissolve instantly.
3. Thats it.

give 20 mins to degas.

#### Final UV run

2023-05-08 18:59:54

13 more samples to set up.

- [x] add to sample tracker
- [ ] add to cellartracker
- [x] set up sequence
- [x] prepare samples.
- [x] get more water for phase A.
- [x] inject.
- [ ] update 'sampled_date' on sampletracker

#### Project Plotting 

Have run into a major problem with Plotly - it doesnt keep marker sizes when zooming in, i.e. zooming in causes the lines and markers to appear the same size relative to the plot window rather than the axis value. This means that when I for example zoom in on a peak interval, there is the disconcerting effect of the marker remaining the same size. Apparently this is a reported feature issue that Plotly does not seem willing to address. Thus we turn to other plotting libraries.

I think we should return to seaborn/matplotlib.

Going to be a bit of a pain to redo the code, but really, there isnt that much to modify. More a problem of relearning matplotlib.

2023-05-08 21:39:46

matplotlib/sns dont play well with interactivity, 3d plots or streamlit. Best to stick with plotly.

[RenaudLN](https://community.plotly.com/t/scattermapbox-fix-radius-of-marker-when-zooming/11630/4) says that using client side callbacks.

 [Emmanuelle](https://community.plotly.com/t/keeping-dot-size-fixed-on-scatterplot/39539/3) says that shapes + an invisible trace will provide the expected behavior, the trace enabling hovering.

### 2023-05-09

2023-05-09 09:22:16

Normalize after baseline subtraction so that the peak maxima is still 1. if normalize before, no difference but the peak maxima is 1 - baseline, bit messy.

2023-05-09 10:51:45 

pipeline is done, but realising that pickle doesnt play nicely with either streamlit or pipelines. Or, the three dont play nicely with each other.

Scenario 1:

pickle whole pipeline, display plots at the end.

drawback - have to store intermediate results, breaking cleanless of pipeline.

Scenario 2:

pickle individual components of pipeline, have option to use or not

drawback - still messy, but better. hard to figure out how to program. Have to pass use_pickle to each pipe. Can use presence of filepath as the bool. If no filepath, make new.

filepath pattern: ~/peak_alignment_pipe_pickles/{pipe}.pk1

#### CUPRAC Conversion

Going to use Jake's column as PCD so first step is to validate it against my column using coffee

- [x] start instrument
- [x] prepare coffe sample
- [x] inject on 38 min method.
- [x] swap columns over.
- [x] thermal equilib column.
- [x] inject on 38 min method.

#### test CUPRAC

- [ ] prepare CUPRAC reagent.
- [ ] plumb cuprac reagent -> degasser -> iso pump.
- [ ] set up CUPRAC method including iso pump
- [ ] test.

#### CUPRAC wine deg

- [ ] prepare vials
- [ ] set methods/sequences.
- [ ] prepare more reagent.
- [ ] start sampling.

1 M ammonium acetate in water
7.5 mM neocuproine in methanol
10 mM copper chloride dihydrate in water

##### CUPRAC purge

very important to purge the CUPRAC lines with methanol after runs to avoid precipitate, consequenlty need to prime wiht CUPRAC before new runs. Generally 5 mins of priming.

11.4 mL / sample. For an ambient run, 11.4 * 5 57 ml + 30 mL for purge etc, so 80 mL of CUPRAC

Make shelf stable reagents in bulk, prep PCD daily 3 x equal parts.

if gna make 1L volume of solution..

see [This python file](../reagent_calculator.py) for a cuprac reagent tabulator for making up quantities.

##### Planning CUPRAC Time Points

It would be useful to have the CUPRAC observation points at the same times as the raw uv/vis. To plan this:

- [x] get the wine data files.
- [ ] clean them to be suitable for database storage
- [ ] for the data files, sort by date, plot date times.

###### Cleaning Wine Study Files for Database Entry

2023-05-09 16:31:11

The database requires that new_id be an integer. Why.

2023-05-09 16:52:45

In all honesty, rather than calling it exp_id, should call it experimental_id, or exp_id, and just preserve it. That way I can refer to it when I want to pull up specific experiments..

Done. replaced in all files.

#### Leak Issues

2023-05-09 17:32:14

Dumb day really, managed to overwrite/delete the first coffee run. On swapping back to my column, had leak issues for an hour stemming from a crushed capillary, which i have replaced. Its too late in the day now to commence runs again, as I will need an hour to do Jakes column. Leave it till Thursday.

#### Refactoring Build Library

Need to rejig the build library pipe, its too difficult to debug, and is too slow. Need to have a permenant database file that is edited, i.e. so the chromatogram-spectrum files arnt loaded every time i exectute.

2023-05-09 23:05:32

Todo:
- [x] refactor as much as possible of the build_library pipe to actually be a pipe that is as modular as possible.
- [ ] add user input to consent to building each component of the library pipeline.

### 2023-05-10

Have started trying to fix the build_library pipeline, but the more i go, the more I realise its broken and fundamentally flawed. Essentially I need to rebuild the whole codebase to be much more modular.

 A sudden realizatoin about how python import statements work during runtime has also led me to understand really HOW to build a python project.

To rebuild the codebase:
- [x] Stash all uncommitted changes.
- [x] create new branch
- [x] stash pop in new branch
- [x] rebuild project outside of prototype directory
- [x] build modular chem station then Sample tracker, then cellartracker tables.

once this is done, commit everything merge branch, merge so we are back to the main branch.

2023-05-10 11:44:55

Rebuild is done, now fixing import statements.

<!-- end_file -->