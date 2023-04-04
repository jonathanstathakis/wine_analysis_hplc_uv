from fuzzywuzzy import fuzz, process
import pandas as pd

def join_dfs_with_fuzzy(df1 : pd.DataFrame, df2 : pd.DataFrame, join_key : str) -> pd.DataFrame:

    def fuzzy_match(s1 : pd.Series, s2 : pd.Series) -> tuple:
        return fuzz.token_set_ratio(s1, s2)
    
    df1[join_key] = df1[join_key].apply(lambda x: process.extractOne(x, df2['join_key'], scorer = fuzzy_match))

    # the above code produces a tuple of: ('matched_string', 'match score', 'matched_string_indice'). Usually it's two return values, but using scorer=fuzzy.token_sort_ratio or scorer=fuzz.token_set_ratio returns the index as well.

    df1['join_key_matched'] = df1['join_key_match'].apply(lambda x: x[0] if x[1] > 65 else None)
    df1['join_key_similarity'] = df1['join_key_match'].apply(lambda x : x[1] if x[1] > 65 else None)
    df1.drop(columns = ['join_key_match'], inplace = True)
    merged_df = pd.merge(df1, df2, left_on='join_key_matched', right_on='join_key', how = 'left')

    return merged_df