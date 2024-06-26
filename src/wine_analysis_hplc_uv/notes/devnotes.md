# Development Notes

Notes on project development go here.

2023-09-07 13:18:55 - Have added [nbstripout](https://github.com/kynan/nbstripout) as a pre-commit hook to ensure that notebooks are never commited with output. This hook will check if there is output, and clear it if so, simply requiring you to add the change before commiting again.

## Database IO

### Designing a Query API

2024-05-03 15:24:29

I need specific logic for each table and column type. this is divided into: whether the input is an iterable or a scalar.

what are the modes of operation? If no argument is submitted, dont add a WHERE to the query. if its an iterable, use IN, and if its a scalar, use '='.

further logic is needed for the wavelength and mins columns, where ease of use requires the input of ranges.

I could continue to subset the relation as it is lazily evaluated, but in the interest of reducing the amount of python logic, we will instead use query string generation.

iterate through the options, and if present in the dict, initiate further logic

UPDATE: this approach has been shelved, instead will assemble a full sampleset metadata table and filter on that, not large enough to need further optimization.

2024-05-05 17:39:43

Have decided to establish an ETL orchastration class. It will be superficially modelled after the sklearn Pipeline, in that it will take a list of iniitalised transformation classes and execute them uing a method call "execute_pipeline". The Pipeline will expect the Transform classes to possess a 'run' method which will be the top level class. On calling the Pipeline "execute_pipeline", the Pipeline object will iterate through the Transformer list and call their "run" methods. Each Transformer will also be responsible for providing a cleanup method to undo the action of 'run', in the event of an error. The pipeline will execute each Transformer.run in the order they are provided, and if an error occurs, execute Transformer.cleanup in reverse order.

2024-05-06 08:39:55

The pipeline and two tranformers: BuildSampleMetaData, CSWideToLong are completed and tested.

Now to write a query class. Take a mapping of selection values and return a data table. Have an option to retrieve the chromatogram data or not.

This query class will be found in "queries.py".

# Designing a Query Generator

## of course we could simply the whole thing by simply injecting strings from the filter dict...
## this indicates that we actually need two things - a query generator and a top level user API.
## the query generator will take a dict with keys pointing to the relevent field, iterate through it and generate the query string.

# Simplifying the problem

the problem I am actually trying to solve is sthe slow time joining the metadata with the chromatogram images. We could reduce the complexity by creating the full metadata table as another table then simply filtering on that. Then we dont need to add the filter to the sub tables. Call it 'all_samples_metadata'.

# Useful Regex

2024-05-07 20:01:43

VSCodes 'Find All References' function is untrustworthy. To find imports in the package, use this template "<start of import>^([^\s]+ ).*( .*)<end of import>". See [stack overflow](https://stackoverflow.com/a/76129640/18650135)


# Git

## Recovering Old Deleted Files

[Stack Overflow](https://stackoverflow.com/a/44425132/18650135) has provided a one-liner to recover deleted files:

```sh
git config --global alias.undelete '!sh -c "git checkout $(git rev-list -n 1 HEAD -- $1)^ -- $1" -'
```

Use as  follows:

```sh
git undelete path/to/file.ext
```

And it will add the file back in, at its path. Note: does require a clean repo, or stashing any changes.

# SQL Table Comparisons

2024-05-09 16:08:13

While verifying old tests, I decided to implement a simple comparison function. It should be straight foreward - get two tables, and do a series of comparisons to find similarities and differences, ala polars, pandas compare. But polars doesnt come with a comparison function, and calling for equality of `describe`, for example, where `describe` is used to summarize the functions is both discourged by the devs, and does not contain sufficient information about non numerical columns. Then I found that duckdb comes with a built-in SUMMARIZE method, but no table-to-table equality functions. So I envisioned a join and anti-join strategy, however it quickly became apparent that this was going to be a laborious task, to iterate through and compare each column, and to produce a similiarty/dissimilarity report. So i turned to third party options, and found data-diff. But data-diff was not constructed in the mind of comparing totally dissimilar tables, and furthermore the Python API is not well fleshed out or documented, and the return values are complex, requiring parsing to produce an easy-to-read report. All in all, no solution has worked yet.

The main problem is that descriptions of similarity are arbitrary, as is expected behavior in the face of disimilarity.

The main problem right now is that the generation of the stats dict requires id columns to be designated (?)

I think the best course of action is to relegate `find_diff` to difference summaries and restrict my discussions of difference to booleans.

Essentially, there are different levels of similarity, and different reports on the disimilarity for different levels. 

1. If no columns in common, relegated to comparisons of geometry
2. if column names common, compare datatypes
3. if column names and data types the same, can compare.

Two totally dissimilar tables cannot be compared at all. 

There are set operations built in to duckdb as well.

But how do I finish this in 15 minutes?

polars `assert_frame_equal`. Thats how. Get the tables as frames and call it.

# duckdb

2024-05-09 16:48:52

## Create tables from lists:
```sql
CREATE TABLE testx as SELECT unnest([1,2,3,4,5]) as a, unnest([4,5,4,2,1]) as y;

>>>
┌───────┬───────┐
│   a   │   y   │
│ int32 │ int32 │
├───────┼───────┤
│     1 │     4 │
│     2 │     5 │
│     3 │     4 │
│     4 │     2 │
│     5 │     1 │
└───────┴───────┘
```

If they are different length, the shorter will be empty on table creation.

## Handling Database Connections

2024-05-10 10:07:07

Modeling a programmatic flow while operating on a SQL database from a higher level language requires managing database connections. Connections are made by providing a configuration, a URL, or a filepath. In the case of duckdb, we use filepaths as it is a local-first database. In Pythons, database connections are modeled as objects, who can be passed like any other variable. This then raises the quetion of whether to a pass a live connection object, or the filepath string, and create a connection within every function. As duckdb has no problems creating multiple connection simultaneously for read and write operations (based on personal tests), then the decision becomes arbitrary. There is, however, one cosideration, which is that of performance. According to [this stack overflow thread](https://stackoverflow.com/a/65387376/18650135), creating connection objects within each scope is less perfromant than maintaining one object, and thus "one connection per application (sic.)" is best practice.

TLDR: one connection object per application. Always write applications expecting a connection object, except for the user facing API.

## Refactoring 'notebooks'

2024-05-14 14:27:19 - a lot of development after June last year went into a catch-all 'notebooks' folder. This included preprocessing, dtw, xgboost, pca, etc. This obscured progress, (state of project advancement) behind somewhat arbritrary folder names and orphaned a lot of code as approaches changed throughout time. Furthermore code that should be scripts or modules is currently in notebooks. Further-furthermore, refactoring the code to keep it functioning and testable is currently not possible. Further-further-furthermore, notes and code are not clearly linked, and past refactoring has left hyperlinks without targets, where it appears that pylance does not update markdown hyperlinks in notebooks.
2024-05-14 14:30:50 - Strategy to solve this dilemma is to pool everything together and seperate into modules based on  topic, with supporting notebooks.
2024-05-14 14:31:21 - deadline - end of day.
2024-05-14 14:41:21 - testing the notebooks will require that they function. This is difficult as in many cases I am lacking either input, output or intermediate data.
:2024-05-15 08:49:40 - I spent a lot of time yesturday developing a python api for the data retrieval query. A lot of time, mostly spent in input validation of a nested dict. Towards the end, while coming up with more complicated test cases, it occured to me to simply try joining the sample metadata and chromato-spectral tables together en masse, and see how long that takes. It took less than 20 seconds. Thus any UX improvement through the python API is lost on having to catch any possible edge-case. A better solution would be to simply produce the join table and query out of it.
2024-05-15 08:56:47 - vindication. Querying the large table takes time. For example returning the wine metadata for each row uniquely takes 11.5 seconds. The same query directly on the sample metadata table takes 400 micro seconds.
2024-05-15 09:05:50 - the python API is being dropped in favor of direct sql queries. I can write join several times, its fine.
2024-05-15 09:30:45 - when joining two tables on a column with the same name, use "SELECT *" in combination with "USING" instead of "ON" if you want to avoid duplicating the coloumn. @sql, @sql-joins.
2024-05-15 11:06:51 - Reviewing [time_axis_characterisation_and_normalization](../src/wine_analysis_hplc_uv/notebooks/lib_eda/sample_standardisation/time_axis_characterisation_and_normalization.ipynb) makes it obvious that I really overcomplicate things. In the section 'Measuring Sampling Frequency' I mistake floating point error for real data and derive a method of finding the significant figure of differentation between time points, defining that as the maximum level of precision. Where its obvious from the calculated frequency that two decimal places is sufficient if time is converted from minutes to seconds. The data should in fact be kept in 'seconds'. @EDA, @time_analysis, @frequency, @notebooks
2024-05-15 14:18:36 - Have discovered that sample_metadata is missing 8 samples. Should have 175, only has 163. Furthermore, have discovered that the design of `build_sample_metadata`, makes it even harder to debug than the previous iteration.. @sql, @sample_metadata @samples
2024-05-15 16:57:39 - its all fucked. Nothing is working, everything is too rigid, too brittle.  I have rewritten the sample_metadata build query, but i cant test it because i cant parametrize the table name. Or cant i? I could write a python routine to replace the table name in the query with another and test on that.
2024-05-16 06:36:18 - 'build_sample_metadata' has been gutted, all logic moved to the query, the transformer now simply reads and executes the query kept in 'create_sample_metadata.sql'
2024-05-16 10:51:25 - Almost finished moving the post_build_library state to sql files. Current plan is to manage the state creation and testing through python, but simple executions of sql queries rather than logic on python side. Everything is in macros so that I can unit test and name the output other things such as "tbl_test" etc, as well as limit output to increase speed. Tests should check for correct number of rows, presence of nulls. @build_library, @sql, @duckdb
2024-05-16 10:55:43 - state management is hard, and I need to remember why Im doing this - it needs to be reproducible. And that means that all operations to get to the final state must be automated. Macros appear to be the best way of rendering each stage unit-testable. Unfortantely I cannot pass functions to other functions, nor tables as objects. Is what it is.
2024-05-16 11:17:50 - duckdb notes. `show tables` shows the tables in the current schema. `show` or `show all tables` shows all tables in all schemas. See https://duckdb.org/docs/guides/meta/list_tables.html. @duckdb, @duckdb-notes
2024-05-16 11:32:48 - duckdb notes cont. Moving tables between schemas does not seem directly possible, rather a new table in the destination schema can be created as a copy of the original table, then dropping the original table, if so desired. Not much more verbose than a copy/rename command. @duckdb, @duckdb-notes
2024-05-16 11:34:11 - Managing sql development and state. Ok, i think i have a working flow. Macros are defined in a macro specific file. A number of macros are combined to produce a final macro, which is then called in a state management file that creates the final table. For example the state designated 'post build library', or 'pbl' is created from macros in 'post_build_library_macros.sql', and the state is created by the queries in 'post_build_library_state_create.sql'. This allows for modular development of the individual actions creating the state, allows them to be unit testable, and seperates the actions from the state creation. @duckdb, @mres, @managing-state, @macros
2024-05-16 11:59:08 - sql macro file ordering. Need to define an easy to read order. as the macros are fully functional, they are little more than wrapping each other like an onion. THus there is a time ordering to their existance, and their order in the file needs to reflect that for easy reading. From here I will order them in reverse time order, with the last one first. @sql, @development, @functional-programming
2024-05-16 12:29:29 - Testing the new state creation. The state creation flow mentioned earlier is verified, however I now need a method of testing it. There is sqllogictest, which is recommended by [duckdb](https://duckdb.org/docs/dev/sqllogictest/intro.html) but I cant find a Python intregration, and as my other tests are there I am loathe to change now. Python based unit tests calling the macros in the respective files and testing the output is probably the way to go, at least at this point. Simply put, and in the interest of saving time, just test the output of the 'create' macros. Just use the column count and estimated size from duckdb_tables @sql, @mres, @testing
2024-05-16 16:04:07 - macro integration. it doesnt appear that macros are optimized, they seem to execute in entirety before moving on to the next statement. This means that they are not as useful as previously thought, because for example expensive queries in macros remain unoptimized. The search for testing options continues.. @sql, @duckdb, @macros, @testing
2024-05-16 16:08:59 - TODO: after work, finish the test module, run it on the full dataset.
2024-05-16 23:17:35 - Swapping macros for CTEs. So yeah, doesnt look like macros are the way foreward that I expected. I think we're gna have to do away with the idea of unit testing, and swap to CTEs, as they may be better optimized. Lets test it by recreating the code already written, but with ctes rather than macros. as you can reference ctes in other ctes, the functional nature of the code remains.
2024-05-16 23:57:04 - Observations from CTE implementation. Running the queries up until the melt - before the sample metadata join to add wine names - takes 47 seconds (not writing a table). The macro version runs for > 1 minute. @sql, @sql-macros, @sql-cte, @sql-unpivot
2024-05-17 09:24:31 - Where to develop sql files. Am struggling to find a good flow. vscode has one extension, 'SQLTools', but it doesnt support the current release of DuckDB. DBeaver is ok but the ui is gross, the editing and keybinds are weird, and its handling of sql scripts is not in file? Harlequin was actually really good until i discovered that it doesnt have an autosave feature, and one crash undid 10 minutes of work. Neovim doesnt handle sql by default and i dont want to spend the time on that. And finally, redirecting sql files directly to duckdb results in poor formatting in the native terminal. One thing I hadnt considered, and considering I am all about TDD, was writing in sql files for execution in the python test file. we'll go with that today, so that we have an end. @TDD, @sql, @duckdb, @neovim, @harlequin-sql, @python, @dbeaver, @terminal.
2024-05-17 10:32:12 - finalizing development flow. TDD in python works. furthermore the cte approach with cs long seems much better than macro. Finally, now that we've played a bit more with cross language and platform development, its clear that I need to be creating packages as command line executable first. @tdd, @python, @sql, @cte
2024-05-17 10:34:21 - whats next. I now need to finish testin the cs long query, and then write a script to get to the pbl state, from build library state. I also need to come up with better names for this stuff. @tdd, @mres, @sql, @python, @build_library
2024-05-17 10:39:39 - how to organise the state update. controling the flow of time from 'build library' to 'post build library' is difficult. The individual queries should be seperate to allow unit testing, for example 'sample_metadata' table creation shouldnt depend on 'chromatogram_spectra_long' creation, but how to organise it? This is where python comes in (or another scripting language). I can turn each of the calls into a python object, then call them sequentially, with tests if necessary. @python, @automation, @sql, @build_library
2024-05-17 11:49:40 - modifying query strings for testing. Using simple string substitution to modify queries to make them test-friendly seems to work pretty well. For example modifying a tables name to point to a python run-time relation object.  @tdd, @sql, @duckdb, @testing
2024-05-17 11:50:43 - bringing it all together. The state-setting queries are written and tested, but now I need to establish the flow. What does it need to do? 1. write chromatogram_spectra_long, 2. write sample_metadata, 3. join the wine and sample_num to chromatogram_spectra_long from sample_metadata. I believe we can create relation objects from a selection query in a .sql file then call the table creation with inline sql. Finally, we would need a simple outcome verification function - have these tables been created, do they match expectation. That module could then be called from the command line. @tdd, @build_library, @sql, @duckdb, @mres, @python
2024-05-17 13:57:25 - where ctes go in the query. ctes are part of the select statement, and as such for actions such as 'create table x as ..', the 'create table as..' component goes first, THEN the cte declaration, then the selection. @sql, @sql-syntax, @sql-cte, @sql-create-table
2024-05-17 14:30:31 - updated test flow. use transactions, drop tables / columns, etc, call the script to maek the  change, observe if the change is as expected. then we dont have to worry about modifying the script. @tdd, @sql, @mres, @sql-transactions
2024-05-17 14:31:42 - friday roundup. im out of time, i can do a little bit more after work, but really i wont be able get back to this till monday. WE need to finish testing / devving the pbl script, but we've got the actions now, and we can unit test easily. once thats done, finish cleaning up the notebooks - do that by summarizing the HELL out of them, they are way too verbose to be left as they are. for example the time offset analysis is a 1 liner. doesnt need all of the other dross. have the query to express the distribution as well, but thats it. Reduce each to a paragraph and associated query. @mres, @friday-roundup, @notebooks, @preprocessing, @tdd
2024-05-17 15:44:57 - perfecting the test database. While finishing the testing for the pbl state creation function, I have run into an unexpected stall while trying to add the wine and sample_num columns to chromatogram_spectrum_long. It is not clear why this is happening, and the development cycle is too long. I dont need to test on every single sample, as queries are taking too long to run. As it currently stands, there are about a million rows per sample. reducing the test set to 10 samples will still include 10 million rows. A method of filtering would be to join on sample_metadata after taking a sample from it. TODO: create the sample set, get a list of 10 samples so that you have deterministic outcome, create the queries in 'create_test_schema.sql'.
2024-05-17 23:51:36 - a step back. I dont think I checked the query sequence with a simple limit added. Try that before introducing another table. Also, try the table replacement vs. the update, it might be that the update is more taxing. For the second point - it takes 12 seconds to execute the 'alter table' query, and 24 for the 'as join' query. Altering the table as opposed to completely replacing it takes half the time. The motivation for creating the tes ttable is that there is no select in the query so I cannot limit(?) the query size. But i can limit the size of chromatogram_spectra_long in its creation query. that is the easiest way. Or you could redefine the object structure to output a list of queries, then use execute many rather than iterating .sql.
2024-05-18 00:13:11 - confirming earlier results. confirmed, something odd is happening with the alter table query. However when limiting the table to 10 rows it functions as expected. 1,000,000 rows works as expected, 13 sec execution time. At 10 million rows the slow query behavior reappears, but finishes after 2 minutes 15 seconds. What happens if we use the join approach instead? It takes 1 minute and 15 seconds on 10 million rows, and.. 4 minutes to complete the query on the total dataset. The other option to test is whether its faster on the wide vesrion of the table, and whether it slows down the unpivot. so, todos: 1. add index and try. 2. add names and sample_num before unpivot.
2024-05-18 00:35:07 - benefits of indexes. Apparently indexes can help speed up operations such as joins. Should add some to the tables and see if anything changes. Need to add an index to chromatogram_spectra_long and sample_metadata, both being id. @sql-index, @sql-joins, @mres-build_library
2024-05-18 01:16:07 - results of adding the index. Nothing changed for the join. and the alter table? I cancelled it after 7 minutes. @sql-index, @duckdb, @mres
2024-05-18 02:29:21 - a result? We're now encountering OOM errors while executing the queries in series.
2024-05-18 10:31:58 - todo. fiinish fixing build_library_oop tests, commit them and everything else in pbl.
2024-05-19 00:04:57 a way foreward. A eureka moment. Data aanlysis design and develpment should be functional first. we are for the most part interested in going from state A to state B through a series of transformations, usually of a 1 dimensional array. The properties of the current state are not actually interesting, only the final state, therefore a functional approach removes a lot of overhead. Therefore, a TDD appraoch coupled with functional-first, possibly with a OOP API is how I will proceed. This makes testing easy, as state is very easy to manage, and allows us to wrap the top level functions in whatever structure we need for interfacing with other libraries, such as sci-kit learn transformers. Thus, a final paradigm has emerged. top level transformer functions first, class based apis if necessary, with intermediate state managed by polars pipes. Also, as much duckdb as possible. Or something like that.
2024-05-20 08:46:40 - Finishing deconvolution and integration. Time to bring it all together. To do so, I need to migrate my code from hplc-py to wine_analysis_hplc_uv. Then I need to rebuild the pipe and test it with a sample dataset, then with real data. To simplify things, I want to discard scikit learn for now, and focus on honing the pipeline steps as pure functions, then wrap the pure functions in the scikit learn api downtrack. So by 2pm we'll have some results. Therefore, timeframe: 9 - 10: complete migration, set up environment. 10 - 12: run sampleset, debug. 12 - 1: running real dataset. 1 - 2: clean up. It seems an unrealistically rapid pace, but lets see how we go. Specific notes will be at [Deconvolution Migration](../README.md#deconvolution-migration). @package-management, @deconvolution, @signal-processing, @sklearn
2024-05-21 21:44:16 - back on track. Ok, package seems to be healthy again? and we're now running 3.12. I guess we'll have to run tests to find out.
2024-05-28 15:01:10 - complexity limit. The deconvolution module and its tests have (again) reached an overwhelming level of complexity and spaghetti. Specifically, it appears that p0 is not calculating as expected when run in the `compute_popt` function, and I dont know why, and now I cant find the associated unit test. Even more specifically, I am unsure whether the fixtures are not causing the problem, or whether the range of x is, as it contains both positive and negative values. A quick solution will be to first require that x only contains positives, which removes a whole sleuth of edge conditions. That is now done. Second is to clean up the mock data generation. It needs to be dependent on x, but currently they are hard-coded. I have already written fixtures providing this in `test_curve_fit_param_gen`.. or whatever, so the next solution will be to move that code to the deconv. conftest and use that instead of the hard coding. We are in effect closing the loop. To modularize this, best to create a signal generation function which returns the generated convoluted signal and skew-norm parameters. It will need to:

- Name: skew_norm_convolution
  - description: generate a convolution of random `n` skew norm distributions representing chromatographic peaks based on amplitude, width and skew bounds `amp_bounds`, `width_bounds`, `skew_bounds` defining the parameter space. it requires that all the peaks fit within the space.
  - input: a series of sampling points: `x`, the number of peaks: `n`, the amplitude bounds `amp_bounds`, the width bounds `width_bounds`, the skew bounds `skew_bounds`.
  - output: the convoluted signal `y`, the peak maxima `amp`, the peak locations `loc`, the peak widths `widths`, the peak skews `skew`.
  - notes: how to make sure all the peaks are fully within x? it would require that the entirety of the cdf is within x, or that there is an x intercept before x[-1]. To solve for the opposite - making sure the distribution starts AFTER x, just reverse. An alternative would be to assign each of the distributions along the x array, but then the loc paramter is not direclty related to x. Theres nothing for it but a notebook prototype.

  2024-05-28 16:03:43 - creating a convoluted signal generator. See 'generating_convolted_signals.ipynb'. The combination of location, skew and scale can result in peaks which are incomplete within x. To solve this I would need to constrain the parameter space to produce peaks which fall within x, or more specifically, the convolution must have zero points on either side, some defined boundary between the peaks and the end points. We could for example use a while loop to randomly generate peaks within the bounds, with the exit condition requiring that x units after/before the end points are zero, or within tolerance. Tolerance could be defined with np.isclose.

  - Name: skew_norm_generator
    - description: generate convolutions while the convolution does not match criteria.
    - components: 1. a while loop who generates random skew norms, 2. a random seed generator whose value can be accessed to reproduce the state. 3. condition checker. Atm the condition check merely requires that a % of units either side of the signal are within a tol of zero.

    TODO: build this.

2024-05-28 23:24:39 - is normal distribution scale equal to peak width? As per title. Im not sure about this. Cant find any informatino on the net, so best to just test it. Easiest way will be to generate a pdf then measure it and compare. The answer? related but not equal. The literature is in agreement. The scale is a parameter that describes the spread of the distribution across x, but as the AUC is always 1, increasing scale decreases height.
2024-05-28 23:36:19 - observations of the parameters of the normal distribution. A 'normal' looking distribution has a scale of 10% of the range of x, and location half the range of x. Increasing the scale reduces the y maxima, and vice versa, but it appears that the area is always the same, equal to 1 (before transformation). Hence height and scale are always working in inverse. According to [statisticshowto](https://www.statisticshowto.com/scale-parameter/), in the standard normal distribution, scale is equal to standard deviation, or half the peak width at a height somewhere vaguely above the half height point, depending on the scale. As we recall, the standard deviation is equal to the square root of the  sum of the mean residuals and observations divided by the number of observations. Thus it is clear that the use of peak width measured at a relative height of 1 is not attempting to estimate distribution scale at all, but it is simply an easy means of providing an initial guess. One which I would say is flawed, but enough to produce results. Finding a better means of estimating scale may be a route to increasing the performance. @skew_norm, @deconvolution, @peak_width, @peak_height, @peak_mapping, @mres

2024-05-29 09:54:56 - Role of Scale in the Skew-Normal Distribution. But what is the role of scale in the skew-normal distribution? [wikipedia](https://en.wikipedia.org/wiki/Skew_normal_distribution) it appears that the skew-normal only introduces the skew as a coefficient to the x term, thus the scale role should be the same, modified by skew. So we can assume that half the width at half height is a good approximation of the scale of the peak. Ergo, that measurement should allow an approximation of the peak, decreasing in efficacy as the skew increases. @skew_norm, @scale

2024-05-29 10:01:49 - Observing the Effect of Skew on Peak Width Measurements Through Topographic Methods. I should answer the following questions - how does measured peak width change as skew increases? How does model fit change as skew increases? And what about changing the width measurement height, what effects does that have?

2024-05-29 10:07:36 - How does Measured Peak Width Change with Skew? To answer this, we would need a function to generate the pdf, then measure the peak width of the pdf. The underlying factor is this - measured peak width is dependent on peak prominence, which works for isolated peaks but suffers as peaks become convoluted, because the 'center' of the peak as measured becomes higher and higher (need to confirm this).

2024-05-29 10:08:19 - How Does Model Fit Change with Skew? 
The second question - defining model fit as the difference in auc, plot overlays of the skew norm distribution and the distribution constructed based on the measured width. I guess at this point we use the already defined functions to optimize the fit, otherwise we'd have to use the input parameters to produce a decent fit. Therefore we link back to our actual code. We need a function that takes x and y and estimates the paramters of the convolved peaks. Theeeeerefore, we should just use a 1 peak dataset to complete that function, then add increasinly complicated sets, then conduct the study to investigate fitting edge cases. @python, @probability, @skewnorm, @mres, @deconvolution

TODO:
  - [ ] replace the mock data with a centered 1 peak signal
  - [ ] complete the deonvolution module based on that 1 peak signal
  - [ ] observe how the fit changes for increasingly skewed distributions
  - [ ] observe how the measured width (height) changes for the same

2024-05-29 09:39:30 - musing on estimation of scale through peak width. Cremerlab does not emphasise how precarious that assumption is, as the more convoluted the peak, the less its prominence, and thus the relative height has more weight when compared to an unconvoluted signal. Is that true? Again, I need a means of generating signals in order to explore this. Perhaps it would be beter to use sinosoidal waves

2024-05-29 15:59:13 - absurd day. So I tried to write a short piece on the skew normal distribution, as per the notes above. But where to put the notes? I decided to structure the notes directory as per the tests, mirroring the package. Fine and dandy, but to then enact that structure I had to clean up the notes already present, also fine, but they needed cleaning up a little bit first.. right? and while im going, I might as well delete any unnecessary ones. Oh and why am I in both ipynb and qmd files? Best convert everything to qmd on the way.. wait how do I structure them now, as when rendering the qmd files the directories get cluttered with the html files.. Oh and these dont actually run so I need to fix them to make sure that they have everything that.. wait the production database is not up to date? Ok better run the post build-library pipeline.. wait theres no docs, a bunch of todos, and no clear method of running it? Fucking excellent. But at least the tests were completed, we can execute those as we refactor then see if itll work in prod. OH WAIT, PYTEST CANT COLLECT THE TESTS BECAUSE OF ERORS THROUGHOUT OTHER TESTS!! So now we're fixing random tests so we can refactor the pbl directory to provide a UI. So i can get the prod db up to date so I can finish refactoring documents from 9 months ago so I can finish organising my notes so I can write new notes about the norm distribution so I can finish rewriting the deconvolution module so I can deconvolute my signals so I can bin the peaks so I can compare across the samples so I can write a simple EDA report. New rule - commit anything by 5, on a seperate branch if need be. In fact, it should always be on a seperate branch, manage your dependencies better, no classes, and never do anything like this ever again. @roundup, @project_management, @quarto, @tests, @pbl, @python

2024-05-29 16:34:12 post_build_library in production. Have for the first time successfully execute `pbl_state_creation.update_library` on the production database. A milestone for sure. Have not written it as a standalone script, as its a simple matter to create the connection object and call the function on it. @mres, @duckdb, @post-build-library

2024-05-30 11:29:12 - notes on killing processes. Quarto is very much still in beta, and I am running into a problem where if it fails to render a document half way through, and has a currently open duckdb connection, it is not closing the connection, holding the lock in place. While I could context management to handle the connections, that kills a sense of flow, the whole point of the document. So I needed a means of killing the running process without restarting the computer. In comes bash `kill`, which as it sounds, kills running processes according to their PID, usefully provided by duckdb on `IOException` error. @bash, @duckdb, @quarto, @error, @kill.

2024-05-30 12:29:50 - rewriting dtw notes. The dtw notes are a cesspit of over-abstracted functions, missing data files, pandas multiindex madness and missing documentation. Its going to take days to fix, and ive got hours. even less than that. Tecnically ive got an hour and a half to finish the thesis. lol. it can remain as it is, and will be left to the very end. @dtw, @thesis, @pandas

2024-05-30 12:35:30 - Continuing on note organisation. The rewriting and organising of existing notes is going well, the mirroring of the package structure in the notes directory is promising, and while the conversion to qmd has not been without hiccups, overall i prefer the format to ipynb, plain text is always preferable. One problem is code formatting, but it is a very late stage concern. @quarto, @mres, @progress

2024-05-31 03:51:10 - operations on long tables, or, 175x10^6 rows is too much. As title. Cant do shit, and its wasting all my time. My previous approach was to apply the transformations on selection, adding layers and layers in order to reach the current *state*. it's bullshit though. There has to be an approach that works. What I need is a community that can point me in the right direction. Also how do we make the query work? we first figure out what arithmatic operations DO work, and whether we need to create a temporary table in between operations. Or. Another table. Create a cs table at 256 nm for further operations. At this point in time the deconvolution precludes a 3d dataset, at least until the operation can be expanded to 3 dimensions.

2024-06-04 16:54:36 - tuesday roundup. I've been busy. When I last touched base I was trying to rewrite the time offset correction as a dataset wide arithmatic query that was refusing to complete within an acceptable time. Since then I realised that I was expecting too much of the database and my computer, and have since decided to do the following: TODO: denormalise the time column into a table of mins with sample id and row idx as key. Replace with the row idx in 'cs_long'. Then time based operations can be completed on the 1 time column that is the same for evey wavelength in the sample, rather than trying to compute the same thing for every wavelength in every sample, reducing the size of the operation by the number of wavelengths in each sample, approximately (600-192)/2 * 175 = 35,700, or reducing it by a factor of 6, which will certainly be a managable operation. In the meantime I've been cleaning up my notes and old modules with the intention of bringing those spaces back to life, i.e. have a core signal processing module that contains all the methods required, and get all my notes running again so I can use them to publish. Finally, aggregating all my notes together so that topics emerge, from the topics, articles, chapters etc. Ergo, the package structure needs to be perfectly reflected in the tests structure, and the notes structure, and also the zotero collection structure. Thus the content exists across these four platforms, and they will in essence keep each other in check. Need a note for the function, tests for the function, references for the note. the only thing im missing now is to A: figure out a better view for zotero collections, as you are able to store items within a collection, but subcollections are treated differently - want a file-explorer type display, subcollections and items treated as objects of their containing collection, and b. tests for notebooks to ensure that modifications dont break them.

2024-06-05 11:04:14 - Note taking. Again trying come up with a frictionless note taking process. Atm I am forming an outline from a source and restructuring it as a structure becomes clear. Furthermore, in lieu of being able to form inline links, creating seperate qmd documents and then cross-referencing them seems to be the way to go, but like everything else in quarto its.. janky. I have moved to using author name, short title and year as cite key to give more context, btw. @quarto, @thesis, @note-taking

2024-06-05 11:05:39 - quarto cross referencing and yaml title field. Cant cross reference the yaml title if using that, and the numbering includes the title and then the scond title if you use that instead, so if u want to cross reference, dont use the yaml field. @quarto

2024-06-05 13:26:00 - quarto reference figures and code cells. code cell output is treated like figures, who have a comment pipe syntax for their relationship with the document and referencing, depending on the syntax of the code in question. For python it is "#|", for mermaid "%%|". Quarto scans the code for the comment pipes then acts on the command. For alignment, use `#|layout-align`, for cross-referencing, first label with `#|label: 'a-label'`. See [diagrams](https://quarto.org/docs/authoring/diagrams.html), [cross-references](https://quarto.org/docs/authoring/cross-references.html), [panel-layout](https://quarto.org/docs/reference/cells/cells-jupyter.html#panel-layout), [diagrams, cross-references](https://quarto.org/docs/authoring/diagrams.html#cross-references). Captions are added by specifying `fig-cap`, with a heirarchical `sub-cap` option [subcaptions](https://quarto.rocks/authoring/figures#subcaptions), [figures, subcaptions](https://quarto.org/docs/authoring/figures.html#subcaptions). Note that captions are left aligned by default with no option to change. There are css hacks that promise to modify this, but I have not managed to make it work [alignment of figure captions](https://github.com/quarto-dev/quarto-cli/discussions/7003#discussioncomment-7112704), [center-caption-in-quarto](https://stackoverflow.com/questions/76404758/center-caption-in-quarto).

2024-06-07 08:55:32 - recycling hplc-py. TODO: digest the resolution enhancement notebooks. Then digest the methods.

2024-06-07 08:57:17 - another attempt at proof of concept. Need to develop a rudimentary deconv pipeline THEN fine tune it. As I've experienced for literally the last 6 months though, its not easy, there are too many moving parts. The last attempt (in the hplc-py fork) failed because I tried to be too fancy, and the individual components were not encapsulated enough, which raised the complexity to unmangable levels. A clean, pure function and module based approach is in my opinion the best approach for development, then wrapping everything in a class IF NECESSARY.

2024-06-07 09:01:59 - moving forward. Researching dsp is my best bet at finishing this. But the code contains the results, and the structure, they need to grow in tandem. The notes and the code. The notes, the code and the tests. However, my eyes are starting to give me trouble, as they do every time I start any serious reading. Working on the notes and code alternatively seems to be a good approach, as my eyes dont suffer as much when coding.

2024-06-12 11:49:09 - merging 'moving_notes_writing_deconv' with main. As title, the deconvolution project has been shelved whiel I finish chapter 1. in the interest of avoiding muddying the history, i'll merge to main now.