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

