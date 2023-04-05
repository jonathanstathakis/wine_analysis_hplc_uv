"""
Started on 2023-03-30, this is a formalization of the cleaning and correcting of the `agilette.Library.metadata_table` which is generated from the metadata present in the agilent .D files. This will act as a lens, or filter to correct the information from past experiments so as to line it up with the sample tracker table: [mres_2023_hplc_uv_vis_exp_tracker - Google Sheets](https://docs.google.com/spreadsheets/d/15S2wm8t6ol2MRwTzgKTjlTcUgaStNlA22wJmFYhcwAY/edit#gid=347137817).

The motivation is that correcting the source data files is both difficult and may introduce unforseen consequence - for example, I believe the signal binary files carry encoded metadata which is intended to line up with the rest of the files within the .D. Editing the file I source the metadata from may cause those to fall out of sync.

We will have a top level function which will call sub-functions such that more sub-functions can be added over time as more cleaning becomes necessary. This does not seem like a sustainable approach, so the best long-term solution is probably to investigate whether metadata can be rewritten, or whether I should disconnect the metadata and signal files from the source files altogether - probably this one.

As of 2023-04-05 the following needs to be applied:

1. strip
2. 4 digit id's of pattern 0DDR where D is digit and R is repeat need to be sliced to DD.
3. 


"""
import pandas as pd
import numpy as np
import sys

sys.path.append('../')
from agilette.modules.library import Library

def avantor_df_cleaner(df : pd.DataFrame) -> pd.DataFrame:

    # strips cell if column is string datatype.
    df.apply(lambda x : x.str.strip() if pd.api.types.is_string_dtype(x) else x)
            
    return df

def main():
    lib = Library('/Users/jonathan/0_jono_data')
    df = lib.metadata_table
    df = avantor_df_cleaner(df)

main()