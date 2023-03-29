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

===

Log:

Building a test file in `testing_agilette_library.py` which will contain tests written throughout this process. First need to establish a basic testable workflow focusing on one file.

===

2023-03-29

For the all files option, do need to pass it a path at some point. Stop trying to make it user friendly, make it script friendly.

===

2023-03-29

Python raise

raise an error during run time.

types of errors:

Many.

Useful ones - 

ValueError: input is correct type but wrong value.

TypeError: 

Input is incorrect type.

===

2023-03-29 

Library path validation is complete. Is currently producing a list of the runs to be loaded into Run Dir objects.

Now to:
1. clean up the code.
2. provide documentation to the code.
3. Refactor it into a seperate file.

What about linting?

## Linting in VSCode.

