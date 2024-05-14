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