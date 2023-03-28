# Reworking How Library, Metadata Table, and Data Table Work

The current behavior frankly is broken, however even in its original form it was lacking in elegance and ran too slowly. The new workflow is as follows:

1. User Provides a list of desired runs to Library. (Default to all, option to provide Sequences as well).
2. Use a loop to generate a list of Run Dir objects.
3. Within that loop, read Run Dir metadata into a 'metadata_dict' list of dicts, and data objects into another list of dicts 'data_obj_dict', with the same key formed from 'acq_date' and 'run name'.
4. Generate 2 respective dataframes with those keys.
5. Display metadata table to user.

That's the first step. Second is if the user desires to load the data.

1. User selects specific data and runs a top level load_data function.
2. 
    i. Load_data will get the data_table whose rows match the index of the selected metadata
    ii. then pass the selected rows to Pool to multiprocess loading the UV data
    iii. then pass back to the dataframe to match the indexes. Specifically pass it back to the data objects who contained the paths to the uv-data files.
3. It will then join the selected metadata table with the loaded data on the primary key column.