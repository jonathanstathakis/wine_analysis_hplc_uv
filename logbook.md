# Logbook

2023-08-10 07:34:07: have moved this project logs to this file as opposed to "mres_logbook.md". A Jonathan with more time than me can get busy moving relevant sections here.

## pivoting db tables

[link](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py)

## Pivoting DB tables

I will developing a module/query to pivot db tables [here](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py).

the following call produces an acceptable sample set:

```python
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

```sql
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

Fist step is to produce the dataframes in an appropriate format to work on. This has been achieved by modifying the `pivot_wine_data` function in pca module to produce a dataframe with a heirarchical index of ('wine', ['mins', 'val']).

2023-08-10 16:57:19

Getting there. With the help of user __Alex__ ive got a method of pivoting the tables out in duckdb prior to moving to Python, making everything lightning fast. However, working with multiindexes is a goddamn pain, and i need to learn how to do that better. Also extracting 'obs_num' with the pivot would be v useful, but currently dont seem to be able to.

[pivot_wine_data](src/wine_analysis_hplc_uv/db_methods/pivot_wine_data.py) will need a big clean up before we can proceed really, but we're still testing it.

It currently looks like ive still got duplicates in the set somehow, specifically:

98         2020 barone ricasoli chianti classico rocca di ... mins      0
                                                              value     0

Which is forcing the dataset to be twice as long as it should be. 72         2021 de bortoli sacred hill cabernet merlot        mins   5712.

##  Sequence Alignment

2023-08-13 12:19:38

The first stage of the preprocessing pipeline is sequence alignment, specifically Multiple Sequence Alignment (MSA). This is necessary because the chromatograph can have a variation in observation points. What is the variation in observation points?

dog walk transcription:

db long table pivot wine data test:

- [ ] multiindex test
- [ ] shape before and after pivot
  - [ ] get counts of unique values `n_unique` in pivot columns (i.e primary key i.e. 'id'), column count `n_col` and row count `n_row`. To calculate the expected shape, divide row count by `n_unique` to get pivot table `n_row`, add `n_unique` to `n_col` to get pivot table `n_col`.
- [ ] cell contents
  - [ ] presence of nulls as `sum_null`. `sum_null` > 1 is an issue.


To debug the too long pivot table, try swapping `sample_code` out for `id`, a possibly more reliable primary key.


## Justification of need for MSA

For a time series $y = f(x)$, MSA aligns $x$ of all sequences determined to be related so that they all experience the same variation (none) from the input, and thus all output variation is contained within $f(x)$ unique to that signal.

From what I've seen so far (very little) it is a concern if observation frequencies differ, or start and stop at different times. In my dataset the observation time points differ minutely, and thus the question of whether it is necessary to undertake MSA can be raised. A first touch check of whether I need to could be to observe the point-by-point variance across the included time series. Frankly I'll need to do further research on both time series statistics and MSA.

TODO:

- [ ] annotate @brown_2020c
- [ ] research MSA
- [ ] research time series statistics
- [ ] finish cleaning up and c