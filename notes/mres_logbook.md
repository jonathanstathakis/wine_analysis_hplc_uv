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

We do have the [build_db_library](../prototype_code/build_db_library.py) file, but that is intended for database initialization prior to data processing, i.e. phase 1. There are multiple phases to this project and the overall project code will reflect that:

Phase 1: Data Collection and Preprocessing
Phase 2: Data Processing
Phase 3: Data Analysis
Phase 4: Model Building
Phase 5: Results Aggregation and Reporting

Phase 1: is covered by build_db_library. Need a superstructure file. call it "core.py". It can be the main driver. It is [here](../core.py)

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
- [x] refactor as much as possible of the build_db_library pipe to actually be a pipe that is as modular as possible.
- [ ] add user input to consent to building each component of the library pipeline.

### 2023-05-10

Have started trying to fix the build_db_library pipeline, but the more i go, the more I realise its broken and fundamentally flawed. Essentially I need to rebuild the whole codebase to be much more modular.

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

2023-05-10 13:01:55

Import statements are updated to the point where chemstation file reading methods are able to run..

### 2023-05-11

2023-05-11 10:04:54

Lab day. To achieve today:

CUPRAC verified.

1. verify jake column matches my column performance using ultimo coffee as comparison standard.

38 min run.

1. [x]  Start up instrument, equilib.
2. [x] Place jakes column in heater as well.
3. [x] prep coffee
4. [x] 30 min later, run 38 min run.
5. [x] swap over to jakes column.
6. [x] 10 min equilib.
7. [x] 30 min run.
8. [x] compare by overlay.
9. [x]  While comparing, setup iso pump.

Iso pump plumbing:

Methanol -> degasser -> iso pump -> detector. See if anything is detected.

to plumb, will need to prepare capillaries.

1. [x] plumb methanol to degasser.
2. [x] plumb degasser to iso pump.
3. [x] purge for 30 mins.
4. [x] After purge, connect to detector, observe detection on flow.
5. [x] verify a ok.
6. [x] connect to radial port of column.
7. [x] observe signal.


#### CUPRAC

1. [x] prepare reagent.
2. [x] swap inlet to CUPRAC
3. [x] start flow, observe signal.
4. [x] inject coffee, observe signal.
5. [x] inject wine, observe signal.

### CUPRAC SOP

#### startup

1. flush iso pump at 2ml/min with CUPRAC reagent.
2. capture outflow in vessel to observe color, looking for blue.
3. meanwhile bin pump, column equilib, 1ml/min.
4. once blue and 1ml/min, iso pump to 0.3ml/min.
5. uncap radial port interface, ensure flow is ejecting.
6. connect iso pump outlet to radial port interface.
7. circulate for 5 mins.
8. start runs.

#### closing SOP
0215 mins.

1. disconnect radial port and iso pump outlet.
2. leave radial port uncapped to flush from bin pump.
3. swap iso pump to methanol.
4. set iso pump to 2ml/min for 10 mins +.
5. recap radial port, off

#### CUPRAC Wine Deg

2023-05-11 16:56:11

todo:
- [x] prepare vials
- [x] prepare methods
- [x] prepare sequences
- [x] prepare file storage.

- [x]  to prepare the vials - same codes, just add c.
- [x] to prepare methods - same methods, just add iso pump, prefix with 'cuprac'.
- [x] to prepare sequences, same as above.
- [x] to prepare the file storage, copy the tree, delete the internal files, prefix with cuprac.

First ambient sqeuence - 

Ive got 200mL of CUPRAC. - 36mL from the three inital runs = 164mL.

(38 min runs + 2mins) * 0.3 = 12mL per run.

164 / 12 = 13.667 runs. Gotta be a multiple of 3, so 12 runs, or 4 time windows, total time = 8 hours.

Wanna space those runs out over time until someone gets in to shutdown the instrument, say 10am tomorrow.

Gotta do the single 3 runs first, so.. say 7:30pm start. 14.5hrs between then and 10pm, close enough to 16. thus I need to double the length of time between the runs.. while controlling for the flow.

12 runs in total, * 12ml CUPRAC per run = 144mL 

time | occurance | sequence | timedelta
  -|-|-|-
  19:30 | start  | 1 | 00
  23:30 | start  | 2 | 4:00
  03:30 | start  | 3 | 4:00
  07:30 | start  | 4 | 4:00
 
 5 freezer repeats

 cn0101 | ce0101
 cn0102 | ce0102
 cn0103 | ce0103
 cn0104 | ce0104
 cn0105 | ce0105
 cn0201 | ce0201
 cn0202 | ce0202
 cn0203 | ce0203
 cn0204 | ce0204
 cn0205 | ce0205
 cn0301 | ce0301
 cn0302 | ce0302
 cn0303 | ce0303
 cn0304 | ce0304
 cn0305 | ce0305
 
 2 ambient repeats

 ca0101
 ca0102
 ca0201
 ca0202
 ca0301 
 ca0302

2023-05-11 18:12:42

Start the first run.

2023-05-11 19:13:39

second wine started.

2023-05-11 20:08:15

third wine started.

Have applied black to the whole 'wine_analysis_hplc_uv' project dir to autolint. Too much to check all, but a brief skim looked hopeful.

todo before I leave today:
- [x] top up cuprac
- [x] top up methanol
- [x] top up h2O
- [x] start overnight sequence.
- [x] clean up lab.

2023-05-11 20:57:47

ambient run first Sequence started.

Did a 100% methanol flush after the shiraz run and saw something come off the column. Seems as though the 2 min method flushes are not enough. increased the flush to 4min, bumping it up to 40 minutes, for each run. Since there are 24 runs itll now consume 0.6 * 24 = 14.4 ml extra. Just to double check, 24 runs * 40 minutes * 0.3 ml/min = 288 mls = 302.4..

2023-05-11 23:11:46

after starting the sequence (and topping up the bin pump phase solutions) there was a sawtooth pressure curve observed with an amplitude of ~100 psi. not great. see if it cleared up over the run.

2023-05-12 00:27:40

Fixed the package again. Fuck me. So, been wrong all week. The expected structure of a python package is: package_name/package_name/modules. where modules all import from each other via .. relative import syntax. I guess the top level name could be anything, but the natural inclination is to name the top level the name of the app.. but the tools require that the root file has 1 folder to import everything from. After that is established however, it behaves as expected..that is, relative imports to the root folder are achieved by consecutive perids. For example, .. is one level ... is two, .... is three (i assume)

### 2023-05-12

2023-05-12 10:24:37

[SOP](#closing-sop)

2023-05-12 11:50:50

Overnight sequence failed due to "not ready timeout". No clear indication of why, but the shutdown macro was not enabled, so the instrument kept running regardless.

Start work at 16:00, need to be at denistone station at 14:45. Need to go home first and groom, say 14:00. Currently 11:44. Gives me 1.5 hours.

2L of H2O at 0.95 ml/min provides me with 31 hours of runtime, btw.

Assuming that I am running 40 or so wines over the next 48 hours, I need to prep  864mL of CUPRAC reagents..

Start up has 7 minutes to go, need to:
- [x] prep 120mL of cuprac reagent.
[SOP](#closing-sop)
- [x] prep cuprac. 30 mins.
- [x] startup [SOP](#cuprac-sop) 30 mins.
- [x] run wine 3 ambient.

So apparently precipitate formed and blocked the crud filter prior to the detector, causing the sequence to fail to engage. Because the shutdown macro was not enabled, the instrument just kept running.

The solution is to drop the injection volume down to 5uL injection.

Tommorow ill be running approx 40 runs, which is 33.6 hours of runtime. at 0.3ml/min, that is 604mL of cuprac.

gna make a litre of each.

2023-05-12 13:11:30

|           |   molar_mass |   final_conc |   required_vol |   moles |   mass (g) |
|:----------|-------------:|-------------:|---------------:|--------:|-----------:|
| cop_chlor |       170.48 |        0.01  |              1 |   0.01  |    01.7048 |
| neocup    |       208.26 |        0.075 |              1 |   0.075 |    15.6195 |
| amac      |        77.08 |        1     |              1 |   1     |    77.08   |

2023-05-12 14:06:26

Exiting lab.

I have started another run of ca0301, as I leave. I have asked corey to shut down the instrument once its done.

I have created ramp_up methods and sequences specific to CUPRAC which include the isopump being at 0.3ml/min steady. See how that goes.

I have prepared 3 x 1L volumetric flasks for CUPRAC reagent. Will ceate tomorrow, just needs a flush out with its specific solvent.

Saturday:
- [x] pick up samples from davy and colin.

Monday:
- [ ] prepare cuprac reagents.
- [ ] setup sequence.
- [ ] run samples.
- [ ] enter samples into sample_tracker/cellartracker.

### 2023-05-13

2023-05-13 16:01:00

Finalize chemstation code.

The proecss is as follows, and I want to write it so that each sub-process 'surfaces' in the main function.

2023-05-13 17:03:53

One thing I introduced was the capability to check the db if files were already in there. Problem with this is that the write queries drop the table by default. So the table dropping needs to not occur.

Thus we need to write append functions.


<!-- end_file -->