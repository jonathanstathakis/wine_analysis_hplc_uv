# Project: Wine Data Aggregation

The base note for the project that includes data mining the chemstation files, downloading data from sample tracker and cellar tracker and joining them together in a sql database. As of 2023-06-21 14:18:19 there will be many notes to be added before this paragraph, and below it.

## Cleaning Wine Study Files for Database Entry

2023-05-09 16:31:11

backlink [mres logbook](mres_logbook.md#cleaning-wine-study-files-for-database-entry)

The database requires that new_id be an integer. Why.

2023-05-09 16:52:45

In all honesty, rather than calling it exp_id, should call it experimental_id, or exp_id, and just preserve it. That way I can refer to it when I want to pull up specific experiments..

Done. replaced in all files.

#### Refactoring Build Library

backlink: [mres_logbook](./mres_logbook.md#refactoring-build-library)

Need to rejig the build library pipe, its too difficult to debug, and is too slow. Need to have a permenant database file that is edited, i.e. so the chromatogram-spectrum files arnt loaded every time i exectute.

2023-05-09 23:05:32

TODO:
- [x] refactor as much as possible of the build_db_library pipe to actually be a pipe that is as modular as possible.
- [x] add user input to consent to building each component of the library pipeline.

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

## Fixing Datafile Aggregation Package Imports

2023-05-12 00:27:40

backlink: [mres logbook](mres_logbook.md#fixing-datafile-aggregation-package-imports)

Fixed the package again. Fuck me. So, been wrong all week. The expected structure of a python package is: package_name/package_name/modules. where modules all import from each other via .. relative import syntax. I guess the top level name could be anything, but the natural inclination is to name the top level the name of the app.. but the tools require that the root file has 1 folder to import everything from. After that is established however, it behaves as expected..that is, relative imports to the root folder are achieved by consecutive perids. For example, .. is one level ... is two, .... is three (i assume).

## Making Build_Library Modular for Different Project Demands

[mres logbook](mres_logbook.md#making-build_library-modular-for-different-project-demands)

Due to the nature of the joins, and how it expects samples to be in sampletracker and cellartracker (as a form of validation of the join keys) I'd have to be careful of how it would handle unentered samples, or mislabelled chemstation data, i.e. there is a def tradeoff in time taken to cleanup up the chemstation labelling, and how to even diagnose it. For certain studies, it will be faster to simple exclude the sampletracker and cellartracker modules from the library and isolate those sample into a specific library.

Will make selecting those samples from the total library easier, especially considering that the library should only be for validated samples.

## Build_Library Update

2023-05-16 16:12:00

[mres logbook](mres_logbook.md#)

Library pipe somewhat finished. 174 runs remaining after processing. Might be right..

Left some TODOs at the top of "build_library.py" for prompts for validation code.

## Revisiting XML to JSON File Conversion

2023-05-16 22:28:10

I had completely completely forgotten that i had planned on converting all the xml files in chemstation to .json using xmltodict, as outlined [here](../../001_obsidian_vault/project_chromatogram_converter.md).


## Refactoring wine_analysis_hplc_uv

### wine_analysis_hplc_uv as an Importable Package

2022-05-22 15:00:00

[mres logbook](mres_logbook.md#wine_analysis_hplc_uv-as-an-importable-package)

To create the cuprac data presentation, I want to use tools created in wine_analysis_hplc_uv. Importing by relative paths is not feasible, copy pasting the code is impractical. So now it's time to learn how to create my own Python Packages and add them to $PATH.

2023-05-23 18:29:09

[mres logbook](mres_logbook.md#refactoring-wine_analysis_hplc_uv)

- [x] seperate the 'raw' and 'clean' tables out from a 'raw' and 'clean' section and into their specific modules,he i.e. raw and clean sampletracker at once.
  - [x] sampletracker
  - [x] cellartracker
- [ ] In that core database, load sampletracker and cellartracker tables, cleaned only.

### Refactoring Project

2023-05-24 11:29:50

The codebase has yet again gotten to big to manage, and some fundamental assumptions in how python execution order worked were false, so as such I am going to heavily refactor the code into several independant packages who will import their dependencies with the help of  virtual environments and pip.

#### Refactoring  Update

2023-06-02 12:59:09

Have spend the last 9 days on the following:

  - establishing a ChemstationProcessor to_csv method
  - adding a bulk data_df table to ChemstationProcessor in the form a of a long db table
  - extracting devtools from the wine_analysis_hplc_uv to be a standalone package
  - developing a uv_cuprac comparison plotting package based on dictionary methods
  - developing a template style for plotting
  - rejigged all current package projects to use poetry.
  - and today, started adding pre-commit hooks, i.e. black.

### Sample Tracker Data Entry

2023-06-04 12:00:00

To proceed in data analysis we need clean data. THe messiest data right now is the SampleTracker. This is a good opportunity to develop a SampleTracker class while performing the cleaning.
	
TODO:
- [ ] fill in davy id's
- [ ] fill in open dates
- [ ] remove wine-deg codes from main table

to achieve this, the SampleTracker class needs google api methods, to start with.

I'm just gna merge the main wth the current branch, see what happens, whatever.

2023-06-03 21:00:30

Merge done. Every branch has been folded into main.

Now to keep going with sampletracker development.

2023-06-03 21:55:54

Going for dinner now, when you get back, continue with developing the read, create sheet, write to sheet, delete sheet loop established in `test_sampletracker.test_post_new_sheet`


## Update on SampleTracker Class Development

2023-06-04 12:22:39

[mres_logbook](mres_logbook.md#update-on-sampletracker-class-development)

Sampletracker test is pretty fucked right now. Somewhere between fetching the values from the source sheet and reading the newly written sheet, some of the empty cells get replaced with <NA>. I need to identify wbere that is happening. This has proven non-trivial.

## Update on OOP Refactor of `wine_analysis_hplc_uv`

2023-06-07 12:14:07

[mres_logbook](mres_logbook.md#update-on-oop-refactor-of-wine_analysis_hplc_uv)

SampleTracker is working, now for CellarTracker. Once those two are done, we'll be able to perform some prefunctory descriptive analysis.

CellarTracker should just be an inherited class of CellarTracker with some cleaning and export functionality.

2023-06-07 22:17:49

SampleTracker and MyCellarTracker are done. There is refactoring that should be done, i.e. introducing more multiple inheritance for IO, Exporter class in SampleTracker etc. But time constraints necessitate that I move on. Lessons learnt. The next stage is:

TODO:

- [ ] fill database.
  - [ ] ChemStation
  - [ ] SampleTracker
  - [ ] CellarTracker


## Chemstation Unit Tests

2023-06-08 14:10:57

To get ChemstationProcessor up to scratch I have been developing tests around it. It is verified to run on sample sets, have not tested it on the full dataset yet.

## Rebuilding `Build_Library`

2023-06-09 10:22:51

[mres logbook](mres_logbook.md#rebuilding-build-library)

To rebuild `build_library` with the OOP interfaces, need to:

- [ ] map the current process
- [ ] group any orphaned actions into the classes or super functions
- [ ] integrate the classes into the pipe
- [ ] build tests

### Current Process

2023-06-09 10:26:29

[mres logbook](mres_logbook.md#storing-multi-way-data-in-databases-in-long-form)

- build_db_library(data_lib_path)
  - assert data_lib_path is a directory
  - create a db_filepath named the same as the data lib, placed within the data lib dir.
  - create a db file at db_filepath if none exists
  - delete a pre-defined list of files: "2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_HALO.D", 2023-02-22_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D", "0_2023-04-12_wine-deg-study/startup-sequence-results/",
  - define 'raw' table names.
  - chemstation_to_db(data_lib_path, db_filepath, ch_meta_tblname, ch_sc_tbl_name)
    - initialize chprocess, an object of class ChemstationProcessor
    - activate a .clean_metadata() function of ChemstationProcessor. returns a df
    - ch_to_db() activates ChemstationProcessor.to_db()
  - sampletracker_to_db():

  ...

  doesnt matter. the rest of the file can be dismissed plainly as bad design patterns.

  New structure:
  
  1. clean library
  2. For each class:
   - Initialize class
   - run .to_db()
  3. 'super pipe'
  
What super pipe actually is, is a combination of operations:
- joining tables.
- 'cleaning' the sample tracker wine names to match cellartracker.

1. Establish the location of the database file. This [stack overflow](https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure) post recommends creating a constants file at project root with:

```python

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
```

Which provides an importable object pointing at the project root.

From there I can establish database filepath in a similar fashion.

## Debugging ChemstationProcessor

2023-06-11 15:00:00

[mres logbook](mres_logbook.md#debugging-chemstationprocessor)

A few files have been causing chemstation to throw an error:
  
ERROR:wine_analysis_hplc_uv.chemstation:/Users/jonathan/0_jono_data/mres_data_library/raw_uv/2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D: PCDATA invalid Char value 1, line 10791, column 3 (sample.acaml, line 10791)
ERROR:wine_analysis_hplc_uv.chemstation:/Users/jonathan/0_jono_data/mres_data_library/raw_uv/029.D: xmlParseEntityRef: no name, line 19018, column 33 (sample.acaml, line 19018)

## Storing Multi-way Data in Databases in Long Form

2023-06-11 19:04:08

After some research on how to store 3D data, I found a [post](https://stackoverflow.com/questions/23128266/storing-3d-points-into-a-database) recommending that data is stored in long form, i.e. hash_hey, wavelength, time, absorbance, then pivoted as required. Makes sense as makes the hash key just one more variable of the data point rather than an unchanging addition to the table. So I'll now integrate that into uv_extractor.

To integrate a long form data configuration in to uv_extractor, I will need to write a test. I could either write a specific unit test for the module, or a test for the whole process. Probably better to write a test for the function. It just needs to be pointed at a .UV file. The specific function the melt should occur in is `uv_extractor.uv_data_to_df`, which requires a parsed `rb.DataFile` as input, and outputs a df.

### Chemstation Package Rebuild Update

2023-06-13 15:28:39

[mres logbook](mres_logbook.md#chemstation-package-rebuild-update)

Rebuilt chemstation to massively simplify the code. Pickle and process counter have been removed completely, dataframe formation has been moved to immediately after the end of the multiprocess, and duplicate hash key test has been moved to chemstationprocessor AND a test for it has been built in.

Unfortunately, the swap to immediate dataframe formation has meant that handling errors in file parsing have become non-trivial to handle. This is because the files that fail to parse will not be populated with the same columns as successfully parsed data, thus when it comes time to melt, an exception occurs. In the meantime, I have manually moved the corrupted files to "/Users/jonathan/0_jono_data/corrupt_files/". Either can repair the files or manually extract the data to add to the df.

2023-06-13 15:48:32

Testing chemstation on the full dataset with the new configuration has resulted in breaking several of the tests, presumably because for the way the tests are configured atm, the long form is harder for Python to handle than the wide. It raises two potential problems:

1. There is no absolute method of testing for duplicate hash keys post process. any groupbys will simply merge the hash keys together.

## Establishing DB Insert Procedures

2023-06-14 09:00:00

[mres logbook](mres_logbook.md#establishing-db-insert-proceudures)

Now that build_library is back on track and the db is being correctly populated, we need to look at how we're interacting with the db.

I don't want to build from scratch again at this point, so we need to institute some update routines. If there are two sets, in_db and add_to_db, we want to compare the elements of those two sets, and only add to in_db from add_to_db those that were not already there. The problem with this is that ATM, hash keys are assigned independent of what is in the db. Thus we need to make the hash key generation smarter, and make it take into account keys that are already in the db. Perhaps two seperate primary keys are necessary: an internal primary key for the chemstation instance, and a new hash_key generated during the to_db process. More to the point, an in-process primary key doesn't need to be anything more complicated than a row index because you're guarenteed synchronicity. Any operations that occur post-initializatoin can be accounted for by generating a primary key at that time. The complication that does occur is that the row index corresponding to the metadata does need to be duplicated x times to pair the data_df rows for the join.. so a little bit more complicated than the row index. So its still going to be best to have a counter integrated into the multiprocess in order to keep track of the order of the processed files, then that counter, or a related value, can be assigned as the primary key.

This is ironic considering I just made the primary key generator an inner function, swearing that I'll never need it in another module.

To integrate the counter back in, I need to:

TODO:
- [x] identify what kind of multiprocess I am working with
- [x] identify where the counter would be instantiated.


2023-06-14 09:27:56 

Taking a longer look at how sharing data between processes works, i've decided to leave the hash key generation as it is, and use that for intra-chemstation class joins, and simply add another hash key generation for db additions. But this is a task for another day, EDA needs to be completed.

Task: in `to_db()`, add a primary key generator that checks keys in the current metadata table, skipping any keys that are already there. The keys will then be passed to the metadata and data dataframes before they move to their sepearate process paths. Use the existant hash key as the seed of the generator, and add an empty column `'db_hash_hey'` that is filled with the newly genned key wherever the seed key currently is.
TODO:
- [ ] add a function to get the list of primary keys existant in the db
- [ ] add a primary key generator
- [ ] add a function to check generated keys against the list, (using a while loop) generating until a unique key is produced.
- [ ] add the new `'db_hash_key'` to metadata and data df's.

But as I said, this is a task for another day.

## Reintroducing Cleaning Functions

2023-06-14 10:00:00

[mres logbook](mres_logbook.md#reintroducing-cleaning-functions)

To complete EDA I need to successfully join the cellartracker and metadata tables. To do this I need to reinstantiate the table cleaning routines. But what were they, exactly?

TODO:
- [x] find notes (or make) on cleaning functions

### Chemstation Cleaner

[ch_metadata_tbl_cleaner](/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/chemstation/ch_metadata_tbl_cleaner.py)

The Chemstation cleaner has 5 subfunctions:

- string cleaner
- column renames
- date formatter
- 'id_cleaner' to form 'new_id'.
- drop unwanted runs based on a 'new_id'

### Sample Tracker Cleaner

[sample_tracker_cleaner](/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/sampletracker/sample_tracker_cleaner.py)

- just string cleaner.

### CellarTracker Cleaner

[clean_ct_to_db](/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/cellartracker_methods/clean_ct_to_db.py)

The CellarTracker cleaner functions literally just pertain to cleaning up html characters and replacing the non-vintage code 1001 with np.nan.

So really its only chemstation that needs it.

### How to Apply Cleaning?

It's best to leave the raw tables as they are and simply write to a new table. the table names need to differ enough from the source that they wont get confused during later operations. Prefix with a c and abbreviate the rest of the names.

│ cellar_tracker       │
│ chemstation_metadata │
│ chromatogram_spectra │
│ sample_tracker       |

is the current table names.

The cleaned table names will be:

cellar_tracker : cct
chemstation_metadata : cch_mta
sample_tracker : cst

Let's instantiate sample tracker and cellartracker first.

movements:

1. get table in memory
2. apply cleaning function
3. write to new table.

While I could achieve the simpler cleaning routines such as stripping (trimming) and lowering with SQL queries, for the sake of consistancy, I'll do this in Python.

#### Tests

To test whether they were successful, I will need to test:
- [x] presence of whitespace
- [x] presence of capital letters

##### Whitespace

For whitespace, chatgpt suggests the following:

```python
import pandas as pd
import re

def has_whitespace(column):
    """
    This function checks if a given Series contains strings with leading or trailing whitespace characters.
    """
    # Ensure the column contains strings
    assert pd.api.types.is_string_dtype(column), "Column is not of string type"

    # Check for strings with leading or trailing spaces using regex
    whitespace_mask = column.apply(lambda x: bool(re.match(r'^\s+|\s+$', str(x))))

    # Return True if any leading/trailing whitespace found, False otherwise
    return any(whitespace_mask)

# Apply the function to each column in the DataFrame
result = df.apply(has_whitespace)

assert any(result)
```

With some encouragement, chatgpt has recommended the following (I have modified it slightly), which looks pretty good. It should only applied to a df of string columns, which will necessitate me noting which is which.

##### Uppercase

```python
import pandas as pd

def check_uppercase(column):
    """
    This function checks if a given Series contains strings with uppercase characters.
    """
    # Ensure the column contains strings
    if pd.api.types.is_string_dtype(column):
        # Check for strings with uppercase characters
        has_uppercase = column.apply(lambda x: any(c.isupper() for c in str(x)))
        return any(has_uppercase)

    return False

# Apply the function to each column in the DataFrame
result = df.apply(check_uppercase)

assert result
```

Looks pretty good. I now need to:

TODO:

- [x] set up cleaning testing environment
- [x] apply cleaning functions
- [x] test cleaning functions

 ---

## Cleaner Tests

 2023-06-14 23:46:33

 [mres logbook](mres_logbook.md#cleaner-tests)

TODO:

- [x] cellar_tracker cleaner tests
- [x] sample_tracker cleaner tests
- [ ] chemstation cleaner tests
  
TODO:

- [x] move df focused tests to 'test_methods_df'

2023-06-15 08:56:39

## Identifying Non-Matching Sample IDs

2023-06-15 11:34:51

[mres logbook](mres_logbook.md#identifying-non-matching-ids)

string cleaner, column rename and date formatter have been tested. Now to 'new_id' builder. To test this, I need to identify what we are actually expecting from this function, as the usecase has changed since its original formulation. To do this, get id columns in both chemstation metadata and sample_tracker and compare. Compare using sets and observe where they don't overlap. Do it from the point of view of sample_tracker, i.e. how does chemstation_metadata differ from sample_tracker.

2023-06-15 12:10:48

Using the following expression:

```python
comparison = col2[~(col2.isin(col1))]
```

Where col1 is sample tracker 'id' and col1 is chemstation metadata 'notebook' found the following discrepencies:

5                                        0101
15                                       0211
18                     koerner-nellucio-02-21
21                                       0171
30                                       0191
31                                       0131
37                                       0091
39                                       0071
46                                       0161
53                       stoney-rise-pn_02-21
55                                       0121
56                                       0181
58     2021-debortoli-cabernet-merlot_avantor
62                                       0081
63                           hey-malbec_02-21
68                                       0061
76                                       0151
78                                       0111
83                         crawford-cab_02-21
86                                       0232
91                                       0201
94                                       0051
111                        mt-diff-bannock-pn


(ignore the index nums, just easier to copypaste with)

2023-06-15 14:12:35

4 digit id replacer has been tested. A metadata id, sampletracker id comparer function has been written, [here](/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/tests/test_cleaning/test_cleaning_chemstation/compare_sample_tracker_ch_m.py).

To facilitate debugging and generally better practices, the chemstation cleaner module has been restructured vertically, [here](/Users/jonathan/mres_thesis/wine_analysis_hplc_uv/src/wine_analysis_hplc_uv/chemstation/ch_m_cleaner).

Now, on to the string replacer. It occurs to me that at this point we should finish manually sorting the rest of the data and have a look at the full set to see if there are any more discrepencies. As boring as that sounds.. nvm, looks like that is everything. Bit less than I thought i'd have.. oh well. Great, that's one less job to do.

The previously written code contains all of the string id's except for 'mt-diff-bannock-pn'. To do this in SQL will require [[sql_mattern_matching|matching]] that string in sample_tracker name column.

2023-06-15 14:35:00

Found it. Actually, there should be several more which are not currently turning up:

stoney-rise-pn
crawford-cab
st hugo gsm
torbreck-struie
mt-diff-bannockburn-on
babo-chianti

The reason the others are not showing up is because they match and are therefore masked during the comparison. only mt-diff-bannock-pn shows up because of the typos. Makes life easier. Although we do have one problem.. there are two 116's

Also, the index currently has two 116 values.. so potentially the whole index is out. Easier to change it on sample_tracker than chemstation..

2023-06-15 15:39:48

Further investigation has revealed that:

1. The 'sampled_date' and 'date' values in sample tracker, chemstation metadata dont line up.
2. The run notes arn't extracted successfully by rainbow.

2023-06-15 - [[sc_plot_app|Here]] is a description of my chemstation data viz web app.