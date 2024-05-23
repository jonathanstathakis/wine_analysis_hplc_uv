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
