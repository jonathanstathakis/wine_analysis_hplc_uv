import re
import pandas as pd


def has_whitespace(column):
    """
    This function checks if a given Series contains strings with leading or trailing whitespace characters.
    """
    # Ensure the column contains strings
    assert pd.api.types.is_string_dtype(column), "Column is not of string type"

    # Check for strings with leading or trailing spaces using regex
    whitespace_mask = column.apply(lambda x: bool(re.match(r"^\s+|\s+$", str(x))))

    # Return True if any leading/trailing whitespace found, False otherwise
    return any(whitespace_mask)


def check_uppercase(column):
    """
    Returns True if any elements in the column contain uppercase characters, otherwise False.
    """
    # Ensure the column contains strings
    if pd.api.types.is_string_dtype(column):
        # Check for strings with uppercase characters
        has_uppercase = column.apply(lambda x: any(c.isupper() for c in str(x)))
        return any(has_uppercase)

    return False


def test_df_init(df: pd.DataFrame):
    assert isinstance(df, pd.DataFrame)
